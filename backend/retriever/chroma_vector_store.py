import os
import uuid
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from docx import Document
import hashlib
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    """ChromaDB-based vector store for document storage and retrieval"""
    
    def __init__(self, collection_name: str = "insightflow_documents", persist_directory: str = "./data/chroma_db"):
        """Initialize ChromaDB vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaVectorStore initialized with collection: {collection_name}")
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using SentenceTransformer"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def _extract_text_from_pdf(self, file_content: bytes, filename: str) -> str:
        """Extract text from PDF file"""
        try:
            from io import BytesIO
            pdf_file = BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filename}: {e}")
            raise
    
    def _extract_text_from_docx(self, file_content: bytes, filename: str) -> str:
        """Extract text from DOCX file"""
        try:
            from io import BytesIO
            docx_file = BytesIO(file_content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {filename}: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to end at a sentence or word boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_space = chunk.rfind(' ')
                if last_period > chunk_size - 100:
                    end = start + last_period + 1
                elif last_space > chunk_size - 100:
                    end = start + last_space
                chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def add_document_from_file(self, file_content: bytes, filename: str, file_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add document from file content
        
        Args:
            file_content: Raw file content as bytes
            filename: Name of the file
            file_type: Type of file (pdf, txt, docx)
            metadata: Additional metadata
            
        Returns:
            Dict with processing results
        """
        try:
            # Extract text based on file type
            if file_type.lower() == 'pdf':
                text = self._extract_text_from_pdf(file_content, filename)
            elif file_type.lower() == 'docx':
                text = self._extract_text_from_docx(file_content, filename)
            elif file_type.lower() in ['txt', 'text']:
                text = file_content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            if not text.strip():
                raise ValueError(f"No text content found in {filename}")
            
            # Generate document ID
            content_hash = hashlib.md5(file_content).hexdigest()
            document_id = f"{filename}_{content_hash[:8]}"
            
            # Check if document already exists
            existing = self.collection.get(ids=[document_id])
            if existing['ids']:
                logger.warning(f"Document {filename} already exists, updating...")
                self.collection.delete(ids=[document_id])
            
            # Chunk text
            chunks = self._chunk_text(text)
            
            # Prepare data for ChromaDB
            chunk_ids = []
            chunk_texts = []
            chunk_metadatas = []
            
            base_metadata = {
                "filename": filename,
                "file_type": file_type,
                "document_id": document_id,
                "upload_time": datetime.now().isoformat(),
                "file_size": len(file_content),
                "total_chunks": len(chunks),
                **(metadata or {})
            }
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_metadata = {
                    **base_metadata,
                    "chunk_index": i,
                    "chunk_text_length": len(chunk)
                }
                
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk)
                chunk_metadatas.append(chunk_metadata)
            
            # Generate embeddings
            embeddings = self._generate_embeddings(chunk_texts)
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                metadatas=chunk_metadatas,
                embeddings=embeddings
            )
            
            result = {
                "status": "success",
                "document_id": document_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": len(file_content),
                "text_length": len(text),
                "chunks_created": len(chunks),
                "upload_time": base_metadata["upload_time"]
            }
            
            logger.info(f"Successfully added document {filename} with {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error adding document {filename}: {e}")
            return {
                "status": "error",
                "filename": filename,
                "error": str(e)
            }
    
    def similarity_search(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of similar document chunks
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embeddings([query])[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": 1.0 - results['distances'][0][i],  # Convert distance to similarity
                    "distance": results['distances'][0][i]
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all chunks for this document
            results = self.collection.get(where={"document_id": document_id})
            
            if not results['ids']:
                logger.warning(f"Document {document_id} not found")
                return False
            
            # Delete all chunks
            self.collection.delete(ids=results['ids'])
            
            logger.info(f"Successfully deleted document {document_id} with {len(results['ids'])} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the vector store
        
        Returns:
            List of document metadata
        """
        try:
            # Get all items from collection
            results = self.collection.get(include=["metadatas"])
            
            # Group by document_id
            documents = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('document_id')
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": metadata.get('filename'),
                        "file_type": metadata.get('file_type'),
                        "upload_time": metadata.get('upload_time'),
                        "file_size": metadata.get('file_size'),
                        "total_chunks": metadata.get('total_chunks', 0),
                        "chunk_count": 0
                    }
                documents[doc_id]["chunk_count"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            # Get collection info
            count = self.collection.count()
            documents = self.list_documents()
            
            # Calculate statistics
            total_size = sum(doc.get('file_size', 0) for doc in documents)
            file_types = {}
            for doc in documents:
                file_type = doc.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "total_documents": len(documents),
                "total_size_bytes": total_size,
                "file_types": file_types,
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dimension": 384,  # all-MiniLM-L6-v2 dimension
                "database_type": "ChromaDB"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def reset_collection(self) -> bool:
        """Reset (clear) the entire collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate the collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Successfully reset collection {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False
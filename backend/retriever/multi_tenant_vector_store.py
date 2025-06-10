"""
Multi-tenant vector store with organization isolation
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import uuid
import logging
from langchain.schema import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
import hashlib
import os

logger = logging.getLogger(__name__)

class MultiTenantVectorStore:
    """
    Vector store with complete organization isolation
    Each organization gets its own ChromaDB collection
    """
    
    def __init__(self, persist_directory: str = "./data/multitenant_chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"✅ Multi-tenant ChromaDB initialized at {persist_directory}")
        except Exception as e:
            logger.error(f"❌ Error initializing ChromaDB: {e}")
            raise
    
    def get_collection_name(self, org_id: uuid.UUID) -> str:
        """Generate consistent collection name for organization"""
        # Create a short, consistent identifier from org_id
        org_str = str(org_id).replace('-', '')
        hash_obj = hashlib.md5(org_str.encode())
        short_hash = hash_obj.hexdigest()[:8]
        
        return f"org_{short_hash}_docs"
    
    def get_org_collection(self, org_id: uuid.UUID):
        """Get or create collection for specific organization"""
        collection_name = self.get_collection_name(org_id)
        
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            logger.debug(f"Retrieved existing collection: {collection_name}")
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"org_id": str(org_id)}
            )
            logger.info(f"Created new collection: {collection_name} for org {org_id}")
        
        return collection
    
    def add_documents(
        self, 
        org_id: uuid.UUID, 
        documents: List[Document], 
        document_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Add documents to organization's vector store
        
        Args:
            org_id: Organization UUID
            documents: List of Document objects (chunks)
            document_id: UUID of the source document
            
        Returns:
            Processing results
        """
        try:
            collection = self.get_org_collection(org_id)
            
            # Prepare data for ChromaDB
            texts = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(documents):
                # Create unique ID for each chunk
                chunk_id = f"{document_id}_{i}"
                
                texts.append(doc.page_content)
                metadata = {
                    "document_id": str(document_id),
                    "org_id": str(org_id),
                    "chunk_index": i,
                    "source": doc.metadata.get("source", "unknown"),
                    **doc.metadata
                }
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)
            
            # Add to ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} chunks for document {document_id} in org {org_id}")
            
            return {
                "success": True,
                "chunks_added": len(documents),
                "document_id": str(document_id),
                "collection_name": collection.name
            }
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks_added": 0
            }
    
    def search(
        self, 
        org_id: uuid.UUID, 
        query: str, 
        n_results: int = 5,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search within organization's documents
        
        Args:
            org_id: Organization UUID
            query: Search query
            n_results: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with metadata
        """
        try:
            collection = self.get_org_collection(org_id)
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses L2 distance)
                    similarity_score = 1 / (1 + distance)
                    
                    # Filter by similarity threshold
                    if similarity_score >= similarity_threshold:
                        search_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity_score": similarity_score,
                            "rank": i + 1
                        })
            
            logger.debug(f"Search in org {org_id}: {len(search_results)} results for '{query}'")
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def delete_document(self, org_id: uuid.UUID, document_id: uuid.UUID) -> Dict[str, Any]:
        """Delete all chunks for a specific document"""
        try:
            collection = self.get_org_collection(org_id)
            
            # Find all chunks for this document
            results = collection.get(
                where={"document_id": str(document_id)},
                include=['documents']
            )
            
            if results['ids']:
                # Delete all chunks
                collection.delete(ids=results['ids'])
                
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
                
                return {
                    "success": True,
                    "chunks_deleted": len(results['ids'])
                }
            else:
                return {
                    "success": True,
                    "chunks_deleted": 0,
                    "message": "No chunks found for document"
                }
                
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_org_stats(self, org_id: uuid.UUID) -> Dict[str, Any]:
        """Get statistics for organization's vector store"""
        try:
            collection = self.get_org_collection(org_id)
            
            # Get total count
            total_chunks = collection.count()
            
            # Get unique documents count
            all_metadata = collection.get(include=['metadatas'])
            unique_docs = set()
            
            if all_metadata['metadatas']:
                for metadata in all_metadata['metadatas']:
                    if 'document_id' in metadata:
                        unique_docs.add(metadata['document_id'])
            
            return {
                "total_chunks": total_chunks,
                "unique_documents": len(unique_docs),
                "collection_name": collection.name,
                "org_id": str(org_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting org stats: {e}")
            return {
                "total_chunks": 0,
                "unique_documents": 0,
                "error": str(e)
            }
    
    def clear_organization_data(self, org_id: uuid.UUID) -> Dict[str, Any]:
        """Clear all data for an organization (dangerous operation)"""
        try:
            collection_name = self.get_collection_name(org_id)
            
            # Delete the entire collection
            self.client.delete_collection(name=collection_name)
            
            logger.warning(f"Deleted entire collection for org {org_id}")
            
            return {
                "success": True,
                "message": f"All data cleared for organization {org_id}"
            }
            
        except Exception as e:
            logger.error(f"Error clearing organization data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_organizations(self) -> List[Dict[str, Any]]:
        """List all organizations with vector data"""
        try:
            collections = self.client.list_collections()
            org_info = []
            
            for collection in collections:
                if collection.name.startswith("org_") and collection.name.endswith("_docs"):
                    # Extract org info
                    stats = {
                        "collection_name": collection.name,
                        "total_chunks": collection.count(),
                        "metadata": collection.metadata or {}
                    }
                    org_info.append(stats)
            
            return org_info
            
        except Exception as e:
            logger.error(f"Error listing organizations: {e}")
            return []

# Global instance for dependency injection
multi_tenant_vector_store = MultiTenantVectorStore()

def get_vector_store() -> MultiTenantVectorStore:
    """Dependency for getting vector store instance"""
    return multi_tenant_vector_store
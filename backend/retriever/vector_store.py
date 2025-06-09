from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from langchain.embeddings.base import Embeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pickle
import os


class VectorStore:
    def __init__(self, embedding_model: Optional[Embeddings] = None):
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.index = None
        self.documents = []
        self.document_metadata = []
        self.dimension = None
        
    def _get_embedding_dimension(self):
        """Get the dimension of embeddings from the model"""
        if self.dimension is None:
            test_embedding = self.embedding_model.embed_query("test")
            self.dimension = len(test_embedding)
        return self.dimension
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store"""
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        split_docs = []
        for doc in documents:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                split_docs.append(Document(
                    page_content=chunk,
                    metadata=doc.metadata
                ))
        
        # Generate embeddings
        texts = [doc.page_content for doc in split_docs]
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Initialize or update FAISS index
        dimension = self._get_embedding_dimension()
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        self.documents.extend(split_docs)
        self.document_metadata.extend([
            {
                **doc.metadata,
                'chunk_id': len(self.documents) + i,
                'content': doc.page_content
            }
            for i, doc in enumerate(split_docs)
        ])
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.index is None:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)
        query_vector = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Search
        scores, indices = self.index.search(query_vector, k)
        
        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)
                })
        
        return results
    
    def save(self, path: str):
        """Save the vector store to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        
        # Save documents and metadata
        with open(os.path.join(path, "documents.pkl"), "wb") as f:
            pickle.dump({
                'documents': self.documents,
                'document_metadata': self.document_metadata,
                'dimension': self.dimension
            }, f)
    
    def load(self, path: str):
        """Load the vector store from disk"""
        # Load FAISS index
        index_path = os.path.join(path, "index.faiss")
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        
        # Load documents and metadata
        docs_path = os.path.join(path, "documents.pkl")
        if os.path.exists(docs_path):
            with open(docs_path, "rb") as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.document_metadata = data['document_metadata']
                self.dimension = data['dimension']


class MockVectorStore:
    """Mock vector store for demonstration purposes"""
    
    def __init__(self):
        self.mock_documents = [
            {
                'content': """Canada's tax system for freelancers operates on a self-employment basis. 
                Freelancers must report all income as business income on their tax returns. 
                This includes income from contracts, consulting, and any other freelance work.""",
                'metadata': {'source': 'canada_tax_guide.pdf', 'page': 15},
                'score': 0.95
            },
            {
                'content': """Business expenses for Canadian freelancers can include home office costs, 
                equipment purchases, software subscriptions, professional development courses, 
                and travel expenses related to business activities.""",
                'metadata': {'source': 'business_expenses_canada.pdf', 'page': 23},
                'score': 0.89
            },
            {
                'content': """GST/HST registration is required for freelancers whose annual income 
                exceeds $30,000. Once registered, you must charge and remit GST/HST on your services.""",
                'metadata': {'source': 'gst_hst_guide.pdf', 'page': 7},
                'score': 0.82
            },
            {
                'content': """Record keeping is crucial for freelancers. The Canada Revenue Agency 
                requires detailed records of all business income and expenses for at least 6 years.""",
                'metadata': {'source': 'cra_record_keeping.pdf', 'page': 12},
                'score': 0.78
            },
            {
                'content': """Quarterly tax installments may be required for freelancers with significant 
                income to avoid penalties at year-end. This helps spread the tax burden throughout the year.""",
                'metadata': {'source': 'tax_installments.pdf', 'page': 5},
                'score': 0.75
            }
        ]
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Mock similarity search that returns relevant documents based on keywords"""
        query_lower = query.lower()
        
        # Simple keyword matching for demo
        scored_docs = []
        for doc in self.mock_documents:
            score = 0.0
            content_lower = doc['content'].lower()
            
            # Boost score based on keyword matches
            if 'tax' in query_lower and 'tax' in content_lower:
                score += 0.3
            if 'freelance' in query_lower and 'freelance' in content_lower:
                score += 0.3
            if 'canada' in query_lower and 'canada' in content_lower:
                score += 0.2
            if 'business' in query_lower and 'business' in content_lower:
                score += 0.2
            if 'income' in query_lower and 'income' in content_lower:
                score += 0.2
            
            # Add base score from document
            score += doc['score'] * 0.3
            
            scored_docs.append({
                **doc,
                'score': min(score, 1.0)  # Cap at 1.0
            })
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        return scored_docs[:k]
    
    def add_documents(self, documents: List[Document]):
        """Mock method for adding documents"""
        pass
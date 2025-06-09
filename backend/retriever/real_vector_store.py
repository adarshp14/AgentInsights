from typing import List, Dict, Any, Optional
import faiss
import numpy as np
import os
import pickle
import logging
from pathlib import Path
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
import PyPDF2
import io

logger = logging.getLogger(__name__)


class RealVectorStore:
    def __init__(self, embedding_model: Embeddings):
        self.embedding_model = embedding_model
        self.index = None
        self.documents = []
        self.document_metadata = []
        self.dimension = None
        self.store_path = "data/vector_store"
        
        # Create data directory if it doesn't exist
        Path(self.store_path).mkdir(parents=True, exist_ok=True)
        
        # Try to load existing store
        self._load_store()
        
        # If no store exists, initialize with sample documents
        if not self.documents:
            self._initialize_sample_documents()
    
    def _get_embedding_dimension(self):
        """Get the dimension of embeddings from the model"""
        if self.dimension is None:
            test_embedding = self.embedding_model.embed_query("test")
            self.dimension = len(test_embedding)
        return self.dimension
    
    def _initialize_sample_documents(self):
        """Initialize with sample tax documents for demonstration"""
        sample_docs = [
            Document(
                page_content="""
                Canada's tax system for freelancers and self-employed individuals requires careful attention to several key areas. 
                As a freelancer, you are considered to be running a business, which means you must report all income as business income on your tax return.
                
                Business Income Reporting:
                - All payments received for services must be reported
                - Income is reported in the year it was earned, not necessarily when paid
                - Keep detailed records of all income sources
                - Use Form T2125 (Statement of Business or Professional Activities)
                
                The Canada Revenue Agency (CRA) requires comprehensive documentation of all business activities.
                """,
                metadata={"source": "Canada_Tax_Guide_Freelancers.pdf", "page": 1, "type": "tax_guide"}
            ),
            Document(
                page_content="""
                Business Expenses for Canadian Freelancers:
                
                Deductible expenses can significantly reduce your tax burden. Common deductible expenses include:
                
                Home Office Expenses:
                - Portion of rent or mortgage interest
                - Property taxes (proportional)
                - Utilities (electricity, heating, internet)
                - Home insurance (business portion)
                
                Equipment and Supplies:
                - Computer hardware and software
                - Office furniture and equipment
                - Professional tools and equipment
                - Office supplies and materials
                
                Professional Development:
                - Courses and training related to your business
                - Professional memberships and licenses
                - Books and publications for business use
                - Conference and seminar fees
                
                Travel and Transportation:
                - Business-related travel expenses
                - Vehicle expenses for business use
                - Public transportation for business purposes
                - Accommodation and meals during business travel (50% of meal costs)
                """,
                metadata={"source": "Business_Expenses_Guide.pdf", "page": 3, "type": "expense_guide"}
            ),
            Document(
                page_content="""
                GST/HST Registration Requirements for Freelancers:
                
                Registration Threshold:
                - Mandatory registration if annual income exceeds $30,000
                - Voluntary registration possible below this threshold
                - Registration applies to total business income, not per client
                
                Benefits of Registration:
                - Ability to claim Input Tax Credits (ITCs)
                - Recover GST/HST paid on business expenses
                - Professional credibility with larger clients
                
                Obligations After Registration:
                - Charge GST/HST on taxable supplies
                - File regular GST/HST returns (monthly, quarterly, or annually)
                - Remit collected GST/HST to CRA
                - Maintain detailed records of all transactions
                
                Current Rates (2024):
                - GST: 5% (federal)
                - HST: 13% (Ontario), 15% (Maritime provinces)
                - GST + PST: varies by province
                """,
                metadata={"source": "GST_HST_Guide.pdf", "page": 7, "type": "tax_regulation"}
            ),
            Document(
                page_content="""
                Record Keeping Requirements for Self-Employed Individuals:
                
                The Canada Revenue Agency requires self-employed individuals to maintain comprehensive records:
                
                Required Documentation:
                - All invoices and receipts for business income
                - Bank statements showing business transactions
                - Credit card statements for business expenses
                - Contracts and agreements with clients
                - Proof of business-related expenses
                
                Retention Period:
                - Minimum 6 years from the end of the tax year
                - Longer if there are ongoing disputes or audits
                - Digital copies are acceptable if clearly readable
                
                Best Practices:
                - Separate business and personal finances
                - Use accounting software or detailed spreadsheets
                - Scan and backup physical receipts
                - Regular reconciliation of accounts
                - Monthly expense categorization
                
                Penalties for inadequate records can include denied deductions and additional audits.
                """,
                metadata={"source": "Record_Keeping_Requirements.pdf", "page": 12, "type": "compliance_guide"}
            ),
            Document(
                page_content="""
                Tax Installment Payments for Self-Employed Individuals:
                
                When Required:
                - If you owe more than $3,000 in taxes for the current year and either of the two previous years
                - Helps avoid large tax bills and interest charges at year-end
                
                Payment Schedule:
                - Four payments per year: March 15, June 15, September 15, December 15
                - Amount based on previous year's taxes or current year estimate
                
                Calculation Methods:
                1. No-calculation option: Pay 1/4 of last year's total tax
                2. Prior-year option: Based on second preceding year
                3. Current-year option: Estimate current year's tax (requires careful calculation)
                
                Benefits:
                - Spreads tax burden throughout the year
                - Avoids interest and penalty charges
                - Better cash flow management
                - Reduces year-end tax stress
                
                The CRA will send installment reminders, but it's your responsibility to make payments even if you don't receive them.
                """,
                metadata={"source": "Tax_Installments_Guide.pdf", "page": 5, "type": "payment_guide"}
            )
        ]
        
        logger.info("Initializing vector store with sample documents")
        self.add_documents(sample_docs)
        self.save_store()
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store"""
        if not documents:
            return
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        split_docs = []
        for doc in documents:
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                split_docs.append(Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_id": f"{doc.metadata.get('source', 'unknown')}_{i}",
                        "chunk_index": i
                    }
                ))
        
        if not split_docs:
            return
            
        # Generate embeddings
        texts = [doc.page_content for doc in split_docs]
        
        try:
            embeddings = self.embedding_model.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return
        
        # Initialize or update FAISS index
        dimension = self._get_embedding_dimension()
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        start_id = len(self.documents)
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        self.documents.extend(split_docs)
        for i, doc in enumerate(split_docs):
            self.document_metadata.append({
                **doc.metadata,
                'doc_id': start_id + i,
                'content': doc.page_content,
                'content_length': len(doc.page_content)
            })
        
        logger.info(f"Added {len(split_docs)} document chunks to vector store")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.index is None or len(self.documents) == 0:
            logger.warning("Vector store is empty")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)
            query_vector = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.index.search(query_vector, min(k, len(self.documents)))
            
            # Return results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents) and idx >= 0:
                    doc = self.documents[idx]
                    metadata = self.document_metadata[idx] if idx < len(self.document_metadata) else {}
                    
                    results.append({
                        'content': doc.page_content,
                        'metadata': metadata,
                        'score': float(score)
                    })
            
            # Sort by score (higher is better for cosine similarity)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Found {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def add_document_from_text(self, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a document from raw text"""
        if not text.strip():
            return False
            
        metadata = metadata or {}
        doc = Document(page_content=text, metadata=metadata)
        self.add_documents([doc])
        return True
    
    def add_document_from_pdf(self, pdf_content: bytes, filename: str) -> bool:
        """Add a document from PDF content"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += page.extract_text()
            
            if text_content.strip():
                metadata = {
                    "source": filename,
                    "type": "uploaded_pdf",
                    "pages": len(pdf_reader.pages)
                }
                
                return self.add_document_from_text(text_content, metadata)
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            
        return False
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        sources = {}
        total_chars = 0
        
        for metadata in self.document_metadata:
            source = metadata.get('source', 'unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
            total_chars += metadata.get('content_length', 0)
        
        return {
            "total_documents": len(self.documents),
            "total_sources": len(sources),
            "sources": sources,
            "total_characters": total_chars,
            "average_chunk_size": total_chars // len(self.documents) if self.documents else 0,
            "index_dimension": self.dimension
        }
    
    def save_store(self):
        """Save the vector store to disk"""
        try:
            # Save FAISS index
            if self.index is not None:
                faiss.write_index(self.index, os.path.join(self.store_path, "index.faiss"))
            
            # Save documents and metadata
            with open(os.path.join(self.store_path, "documents.pkl"), "wb") as f:
                pickle.dump({
                    'documents': self.documents,
                    'document_metadata': self.document_metadata,
                    'dimension': self.dimension
                }, f)
                
            logger.info("Vector store saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def _load_store(self):
        """Load the vector store from disk"""
        try:
            # Load FAISS index
            index_path = os.path.join(self.store_path, "index.faiss")
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            
            # Load documents and metadata
            docs_path = os.path.join(self.store_path, "documents.pkl")
            if os.path.exists(docs_path):
                with open(docs_path, "rb") as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.document_metadata = data.get('document_metadata', [])
                    self.dimension = data.get('dimension')
                    
                logger.info(f"Loaded vector store with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            # Reset to empty state
            self.index = None
            self.documents = []
            self.document_metadata = []
            self.dimension = None
    
    def clear_store(self):
        """Clear all documents from the store"""
        self.index = None
        self.documents = []
        self.document_metadata = []
        self.dimension = None
        
        # Remove saved files
        try:
            index_path = os.path.join(self.store_path, "index.faiss")
            docs_path = os.path.join(self.store_path, "documents.pkl")
            
            if os.path.exists(index_path):
                os.remove(index_path)
            if os.path.exists(docs_path):
                os.remove(docs_path)
                
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
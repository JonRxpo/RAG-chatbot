import os
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from pypdf import PdfReader
import hashlib

load_dotenv()

class DocumentIngestion:
    def __init__(self, documents_path="documents", persist_directory="chroma_db"):
        self.documents_path = Path(documents_path)
        self.persist_directory = persist_directory
        
        print("Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def load_documents(self):
        documents = []
        
        print(f"\nLoading PDF documents from {self.documents_path}...")
        
        pdf_files = list(self.documents_path.glob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in documents folder!")
            return documents
        
        for file_path in pdf_files:
            try:
                reader = PdfReader(str(file_path))
                
                full_text = ""
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- Page {page_num} ---\n{text}"
                
                if not full_text.strip():
                    print(f"  Skipping {file_path.name}: No text extracted")
                    continue
                
                metadata = {
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "total_pages": len(reader.pages)
                }
                
                doc = Document(page_content=full_text, metadata=metadata)
                documents.append(doc)
                
                print(f"  Loaded: {file_path.name} ({len(reader.pages)} pages)")
                
            except Exception as e:
                print(f"  Error loading {file_path.name}: {e}")
        
        print(f"\nSuccessfully loaded {len(documents)} PDF documents")
        return documents
    
    def chunk_documents(self, documents):
        print("\nChunking documents...")
        
        chunks = self.text_splitter.split_documents(documents)
        
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            if '--- Page' in chunk.page_content:
                try:
                    page_marker = chunk.page_content.split('--- Page')[1].split('---')[0].strip()
                    chunk.metadata['page_reference'] = f"Page {page_marker}"
                except:
                    chunk.metadata['page_reference'] = "Unknown"
            
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_vectorstore(self, chunks):
        print("\nCreating vector store...")
        print("(This may take several minutes for embeddings generation...)")
        
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
            print(f"  Deleted old vector store")
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="customer_service_docs"
        )
        
        print(f"Vector store created with {len(chunks)} embeddings")
        print(f"Persisted to: {self.persist_directory}")
        
        return vectorstore
    
    def run_ingestion(self):
        print("="*60)
        print("STARTING PDF DOCUMENT INGESTION PIPELINE")
        print("="*60)
        
        documents = self.load_documents()
        
        if not documents:
            print("No documents found! Please add PDF files to the 'documents' folder.")
            return None
        
        chunks = self.chunk_documents(documents)
        vectorstore = self.create_vectorstore(chunks)
        
        print("\n" + "="*60)
        print("INGESTION COMPLETE!")
        print("="*60)
        print(f"Total PDF documents processed: {len(documents)}")
        print(f"Total chunks created: {len(chunks)}")
        print(f"Vector store location: {self.persist_directory}")
        
        return vectorstore

def main():
    ingestion = DocumentIngestion()
    vectorstore = ingestion.run_ingestion()
    
    if vectorstore:
        print("\nReady for retrieval and question answering!")
    else:
        print("\nIngestion failed. Please check errors above.")

if __name__ == "__main__":
    main()
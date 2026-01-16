# RAG Chatbot 

A Retrieval-Augmented Generation (RAG) chatbot that answers questions using curated financial, healthcare, and supply chain documents.

## Live Demo

**Try it here:** https://rag-chatbot-jonrafuna.streamlit.app/

## Features

### Must-Have Features 
19 professional PDF documents (4,489 chunks)
Vector search with ChromaDB
Answer generation with Claude Sonnet 4
Citation tracking (document + page + chunk)
"I don't know" handling for questions outside knowledge base
Streamlit web interface

### Nice-to-Have Features 
1. **Conversation Memory** - Chat history persists during session
2. **Metadata Filters** - Filter documents by industry (Finance, Healthcare, Supply Chain)
3. **Observability Dashboard** - Real-time statistics including:
   - Total queries and success rate
   - Average response time
   - Queries by category
   - Most used documents

## Dataset

**Industries:** Finance & Banking, Healthcare, Supply Chain

**Documents:**
- **Financial reports:** JPMorgan, Citi, Goldman Sachs, Wells Fargo, Federal Reserve
- **Healthcare:** CVS Health, UnitedHealth, Johnson & Johnson
- **Supply Chain:** FedEx, UPS, World Bank
- **Government:** Federal Reserve, Department of Healthcare

## Setup

### Prerequisites
- Python 3.13+
- Claude API key from [Anthropic Console](https://console.anthropic.com)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JonRxpo/rag-chatbot.git
cd rag-chatbot
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
ANTHROPIC_API_KEY=your_api_key_here
```

5. Documents are already included in the repository (19 professional PDFs in `documents/` folder)

## Usage

### 1. Ingest Documents
```bash
python ingestion.py
```

This will:
- Load 19 PDF documents
- Extract and chunk text (4,489 chunks created)
- Generate embeddings using sentence-transformers
- Index in ChromaDB vector database
- Takes ~5-10 minutes

### 2. Test RAG System (Optional)
```bash
python rag_system.py
```

Runs 5 test questions to verify the system works correctly.

### 3. Run Streamlit App
```bash
streamlit run app.py
```

Opens the chatbot interface at `http://localhost:8501`

## Project Structure
```
rag-chatbot/
├── documents/          # 19 professional PDF documents
├── chroma_db/          # Vector database (generated after ingestion)
├── ingestion.py        # Document processing pipeline
├── rag_system.py       # RAG retrieval & generation logic
├── app.py              # Streamlit UI with filters and dashboard
├── requirements.txt    # Python dependencies
├── .env                # API keys (not in repo)
├── .gitignore
└── README.md
```

## Technical Details

- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2 (384-dim, local)
- **Vector Store:** ChromaDB with HNSW indexing
- **LLM:** Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Text Splitting:** RecursiveCharacterTextSplitter
  - Chunk size: 1000 tokens
  - Chunk overlap: 100 tokens
- **Retrieval:** Top-5 similarity search with cosine similarity
- **UI Framework:** Streamlit

## Features Walkthrough

### Metadata Filters
Filter documents by industry category to search only relevant documents:
- Finance & Banking (8 documents)
- Healthcare (6 documents)  
- Supply Chain (5 documents)

### Observability Dashboard
Real-time metrics displayed in sidebar:
- Total queries executed
- Success rate (answered vs "I don't know")
- Average response time
- Queries by category breakdown
- Most frequently used documents

### Citation System
Every answer includes:
- Source document name
- Page reference (when available)
- Chunk ID for traceability
- Expandable "View Sources" section

## Requirements Met

Document ingestion pipeline (load → clean → chunk → embed → index)  
Vector search retriever (Top-5)  
Answer generation with citations  
"I don't know" handling  
19 documents, 4,489+ chunks  
Citations include document name + chunk/page reference  
Simple UI (Streamlit)  
Conversation memory (short-term)  
Metadata filters  
Observability dashboard  

## Example Queries

Try asking:
- "What were JPMorgan's financial highlights in 2024?"
- "What does the Federal Reserve say about financial stability risks?"
- "What are UPS's main service offerings?"
- "Tell me about CVS Health's business operations"



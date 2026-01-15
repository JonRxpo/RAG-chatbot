# RAG Chatbot - Giga Academy Project

A Retrieval-Augmented Generation (RAG) chatbot that answers questions using curated financial, healthcare, and supply chain documents.

## Features

19 professional PDF documents (4,489 chunks)
Vector search with ChromaDB
Answer generation with Claude Sonnet 4
Citation tracking (document + page + chunk)
"I don't know" handling for questions outside knowledge base

## Dataset

**Industries:** Finance & Banking, Healthcare, Supply Chain

**Documents:**

- Financial reports: JPMorgan, Citi, Goldman Sachs, Wells Fargo
- Healthcare: CVS Health, UnitedHealth, Johnson & Johnson
- Supply Chain: FedEx, UPS, World Bank
- Government: Federal Reserve, Department of Healthcare

## Setup

### Prerequisites

- Python 3.13+
- Claude API key

### Installation

1. Clone the repository

2. Create virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
```


## Usage

### 1. Ingest Documents

```bash
python ingestion.py
```

### 2. Test RAG System

```bash
python rag_system.py
```

### 3. Run Streamlit App

```bash
streamlit run app.py
```

## Project Structure

```
rag-chatbot/
├── documents/          # PDF documents 
├── chroma_db/          # Vector database (not in repo)
├── ingestion.py        # Document processing pipeline
├── rag_system.py       # RAG retrieval & generation
├── app.py              # Streamlit UI 
├── requirements.txt    # Python dependencies
├── .env               # API keys (not in repo)
├── .gitignore
└── README.md
```

## Technical Details

- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2 (local, free)
- **Vector Store:** ChromaDB
- **LLM:** Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Chunk Size:** 1000 tokens, 100 overlap
- **Retrieval:** Top-5 similarity search

import streamlit as st
import os
from dotenv import load_dotenv
from rag_system import RAGSystem
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="💬",
    layout="wide"
)

DOCUMENT_CATEGORIES = {
    "Finance & Banking": [
        "jpmorganchase_financial-highlights-2024.pdf",
        "jpmorganchase_annualreport.pdf",
        "jpmorganchase_corporate-data-and-shareholder-information-2023.pdf",
        "citi-2024-annual-report.pdf",
        "goldmansachs_shareholders_letter.pdf",
        "wellsfargo_investor_presentation.pdf",
        "financial-stability-report-20251107.pdf",
        "federalreserve_mprfullreport.pdf"
    ],
    "Healthcare": [
        "CVS-Health-2025-Proxy.pdf",
        "UNH_Q1-2024_Form-10-Q.pdf",
        "UNH-Reports-Q1-2025-Results-Revises-Full-Year-Guidance.pdf",
        "Johnson-Johnson-2024-Annual-Report.pdf",
        "departament-of-healthcare-annual-report.pdf",
        "quick-definitions-health-expenditure.pdf"
    ],
    "Supply Chain": [
        "Fedex-Annual-Report.pdf",
        "UPS-annualreport.pdf",
        "roadsafety-annual-report.pdf",
        "World Bank Group Annual Report 2025.pdf",
        "OGD-2023-annual-report.pdf"
    ]
}

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'rag_system' not in st.session_state:
        with st.spinner("Loading RAG system..."):
            st.session_state.rag_system = RAGSystem(top_k=5)
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    if 'total_response_time' not in st.session_state:
        st.session_state.total_response_time = 0
    if 'category_stats' not in st.session_state:
        st.session_state.category_stats = {cat: 0 for cat in DOCUMENT_CATEGORIES.keys()}
    if 'document_usage' not in st.session_state:
        st.session_state.document_usage = {}
    if 'successful_queries' not in st.session_state:
        st.session_state.successful_queries = 0

def build_filter(selected_categories):
    if not selected_categories or len(selected_categories) == len(DOCUMENT_CATEGORIES):
        return None
    
    allowed_docs = []
    for category in selected_categories:
        allowed_docs.extend(DOCUMENT_CATEGORIES[category])
    
    return {"source": {"$in": allowed_docs}}

def main():
    initialize_session_state()
    
    st.title("RAG Chatbot - Financial & Business Documents")
    st.markdown("Ask questions about financial reports, healthcare, and supply chain documents.")
    
    with st.sidebar:
        st.header("Filters")
        
        selected_categories = st.multiselect(
            "Select Document Categories",
            options=list(DOCUMENT_CATEGORIES.keys()),
            default=list(DOCUMENT_CATEGORIES.keys()),
            help="Filter documents by industry category"
        )
        
        if selected_categories and len(selected_categories) < len(DOCUMENT_CATEGORIES):
            st.info(f"Filtering: {', '.join(selected_categories)}")
        
        st.divider()
        
        st.header("About")
        st.markdown("""
        This chatbot uses Retrieval-Augmented Generation (RAG) to answer questions based on:
        - **19 professional documents**
        - **4,489+ chunks** indexed
        - **Industries:** Finance, Healthcare, Supply Chain
        """)
        
        st.divider()
        
        st.header("Observability Dashboard")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", st.session_state.query_count)
        with col2:
            if st.session_state.query_count > 0:
                success_rate = (st.session_state.successful_queries / st.session_state.query_count) * 100
                st.metric("Success Rate", f"{success_rate:.0f}%")
        
        if st.session_state.query_count > 0:
            avg_time = st.session_state.total_response_time / st.session_state.query_count
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        
        st.subheader("Queries by Category")
        for category, count in st.session_state.category_stats.items():
            if count > 0:
                st.metric(category, count)
        
        if st.session_state.document_usage:
            st.subheader("Most Used Documents")
            sorted_docs = sorted(st.session_state.document_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            for doc, count in sorted_docs:
                doc_name = doc.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
                st.text(f"{doc_name[:30]}... ({count})")
        
        st.divider()
        
        st.header("Documents")
        for category, docs in DOCUMENT_CATEGORIES.items():
            with st.expander(f"{category} ({len(docs)} docs)"):
                for doc in docs:
                    usage_count = st.session_state.document_usage.get(doc, 0)
                    doc_display = doc.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
                    if usage_count > 0:
                        st.markdown(f"- {doc_display} *({usage_count} uses)*")
                    else:
                        st.markdown(f"- {doc_display}")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.query_count = 0
            st.session_state.total_response_time = 0
            st.session_state.category_stats = {cat: 0 for cat in DOCUMENT_CATEGORIES.keys()}
            st.session_state.document_usage = {}
            st.session_state.successful_queries = 0
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("View Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**[{source['source_num']}]** {source['document']} - {source['page_reference']} (Chunk {source['chunk_id']})")
    
    if prompt := st.chat_input("Ask a question about the documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                start_time = datetime.now()
                
                filter_dict = build_filter(selected_categories)
                result = st.session_state.rag_system.answer_question(prompt, filter_dict=filter_dict)
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                st.session_state.query_count += 1
                st.session_state.total_response_time += response_time
                
                if "I don't have that information" not in result['answer']:
                    st.session_state.successful_queries += 1
                
                for source in result['sources']:
                    doc_name = source['document']
                    
                    for category, docs in DOCUMENT_CATEGORIES.items():
                        if doc_name in docs:
                            st.session_state.category_stats[category] += 1
                            break
                    
                    if doc_name in st.session_state.document_usage:
                        st.session_state.document_usage[doc_name] += 1
                    else:
                        st.session_state.document_usage[doc_name] = 1
                
                st.markdown(result['answer'])
                
                with st.expander("View Sources"):
                    for source in result['sources']:
                        st.markdown(f"**[{source['source_num']}]** {source['document']} - {source['page_reference']} (Chunk {source['chunk_id']})")
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result['answer'],
            "sources": result['sources']
        })
        
        st.rerun()

if __name__ == "__main__":
    main()
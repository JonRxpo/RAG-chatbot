import os
from dotenv import load_dotenv
from anthropic import Anthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

class RAGSystem:
    def __init__(self, persist_directory="chroma_db", top_k=5):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        
        print("Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        print("Loading vector store...")
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="customer_service_docs"
        )
        
        self.top_k = top_k
        print(f"RAG System initialized (retrieving top {top_k} chunks)")
    
    def retrieve_context(self, query):
        results = self.vectorstore.similarity_search_with_score(query, k=self.top_k)
        
        context_parts = []
        sources = []
        
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            chunk_id = doc.metadata.get('chunk_id', 'N/A')
            page_ref = doc.metadata.get('page_reference', 'N/A')
            content = doc.page_content
            
            context_parts.append(
                f"[Source {i}: {source}, Chunk {chunk_id}, {page_ref}]\n{content}\n"
            )
            
            sources.append({
                'source_num': i,
                'document': source,
                'chunk_id': chunk_id,
                'page_reference': page_ref,
                'relevance_score': float(score)
            })
        
        context = "\n---\n".join(context_parts)
        return context, sources
    
    def generate_answer(self, query, context, sources):
        prompt = f"""You are a helpful assistant that answers questions based on financial, healthcare, and business documents.

IMPORTANT INSTRUCTIONS:
1. Answer the question using ONLY the information in the provided context
2. ALWAYS cite your sources using the format [Source X] where X is the source number
3. If the information is NOT in the provided context, you MUST respond with: "I don't have that information in my knowledge base."
4. Do not make up or infer information not explicitly stated in the context
5. Be clear, concise, and professional
6. Include relevant document names and page references when citing
7. NEVER return an empty response - always provide an answer or state you don't have the information

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION: {query}

Please provide your answer with proper citations:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = message.content[0].text.strip()
            
            if not answer:
                return "I don't have that information in my knowledge base."
            
            return answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def answer_question(self, query):
        print(f"\n{'='*60}")
        print(f"Question: {query}")
        print(f"{'='*60}\n")
        
        print("Retrieving relevant information...")
        context, sources = self.retrieve_context(query)
        print(f"Found {len(sources)} relevant chunks\n")
        
        print("Generating answer with Claude...")
        answer = self.generate_answer(query, context, sources)
        
        print(f"\n{'='*60}")
        print("ANSWER:")
        print(f"{'='*60}")
        print(answer)
        
        print(f"\n{'='*60}")
        print("SOURCES:")
        print(f"{'='*60}")
        for source in sources:
            print(f"  [{source['source_num']}] {source['document']} - {source['page_reference']} (Chunk {source['chunk_id']})")
        
        return {
            'question': query,
            'answer': answer,
            'sources': sources
        }

def main():
    rag = RAGSystem(top_k=5)
    
    test_questions = [
        "What were JPMorgan's key financial highlights in 2024?",
        "What are the main business segments of CVS Health?",
        "What does the Federal Reserve report say about financial stability risks?",
        "What are UPS's main service offerings according to their annual report?",
        "What is the capital of Mars?"
    ]
    
    print("\n" + "="*60)
    print("TESTING RAG SYSTEM WITH SAMPLE QUESTIONS")
    print("="*60)
    
    for question in test_questions:
        result = rag.answer_question(question)
        print("\n" + "="*60 + "\n")
        input("Press Enter to continue to next question...")
    
    print("\nAll tests complete!")

if __name__ == "__main__":
    main()
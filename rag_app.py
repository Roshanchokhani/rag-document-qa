#!/usr/bin/env python3

import streamlit as st
import sys
sys.path.append('src')

from data_loader import DataLoader
from text_chunker import TextChunker
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, VECTOR_DB_DIR
import requests
import json
import time
from typing import List, Dict, Tuple
import os

# Page configuration
st.set_page_config(
    page_title="RAG Document Q&A System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .answer-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .similarity-score {
        font-weight: bold;
        color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitRAG:
    """Streamlit RAG Application"""
    
    def __init__(self):
        self.model = "sentence-transformers/all-MiniLM-L6-v2"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.chunks = []
        
    def load_documents(self):
        """Load and process documents"""
        if 'chunks_loaded' not in st.session_state:
            with st.spinner("Loading and processing documents..."):
                loader = DataLoader(RAW_DATA_DIR)
                documents = loader.load_documents_from_directory()
                
                if not documents:
                    st.error("No documents found in the data/raw directory!")
                    return []
                
                chunker = TextChunker(chunk_size=600, chunk_overlap=100)
                chunks = chunker.process_documents(documents, "recursive")
                self.chunks = chunker.validate_chunks(chunks)
                
                st.session_state.chunks_loaded = True
                st.session_state.chunks = self.chunks
                st.session_state.document_count = len(documents)
                
                return self.chunks
        else:
            self.chunks = st.session_state.chunks
            return self.chunks
    
    def search_similar_chunks(self, query: str, api_token: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Find most similar chunks using HuggingFace API"""
        if not self.chunks:
            return []
        
        chunk_texts = [chunk['content'] for chunk in self.chunks]
        
        payload = {
            "inputs": {
                "source_sentence": query,
                "sentences": chunk_texts
            }
        }
        
        headers = {"Authorization": f"Bearer {api_token}"}
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                similarities = response.json()
                
                # Pair chunks with similarity scores
                chunk_similarity_pairs = list(zip(self.chunks, similarities))
                
                # Sort by similarity (highest first)
                chunk_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
                
                return chunk_similarity_pairs[:top_k]
                
            elif response.status_code == 503:
                st.warning("⏳ Model is loading. Please wait a moment and try again.")
                return []
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Error calling API: {e}")
            return []

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 RAG Document Q&A System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize RAG system
    rag = StreamlitRAG()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Token input
        api_token = st.text_input(
            "🔑 HuggingFace API Token",
            type="password",
            help="Enter your HuggingFace API token. Get one at https://huggingface.co/settings/tokens"
        )
        
        st.markdown("---")
        
        # Document loading
        st.header("📚 Document Processing")
        
        if st.button("🔄 Load Documents", type="primary"):
            chunks = rag.load_documents()
            if chunks:
                st.success(f"✅ Loaded {len(chunks)} chunks from {st.session_state.get('document_count', 0)} documents")
        
        # Show document status
        if 'chunks_loaded' in st.session_state:
            st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
            st.write("📊 **Document Status:**")
            st.write(f"- Documents: {st.session_state.get('document_count', 0)}")
            st.write(f"- Chunks: {len(st.session_state.get('chunks', []))}")
            st.write("- Status: ✅ Ready")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Settings
        st.header("🎛️ Search Settings")
        top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)
        min_similarity = st.slider("Minimum similarity threshold", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
        
        st.markdown("---")
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = [
            "What is RAG?",
            "What technologies are used?",
            "How does the system work?",
            "What are the main features?",
            "What is machine learning?"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(f"📝 {question}", key=f"sample_{i}"):
                st.session_state.query = question
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your Question")
        
        # Query input
        query = st.text_input(
            "Enter your question:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., What is RAG? How does the system work?",
            key="query_input"
        )
        
        # Search button
        search_button = st.button("🔍 Search", type="primary", disabled=not (api_token and query))
        
        if search_button and api_token and query:
            # Load documents if not already loaded
            if 'chunks_loaded' not in st.session_state:
                chunks = rag.load_documents()
                if not chunks:
                    st.stop()
            else:
                rag.chunks = st.session_state.chunks
            
            # Search for similar chunks
            with st.spinner("🔍 Searching for relevant information..."):
                similar_chunks = rag.search_similar_chunks(query, api_token, top_k)
            
            if similar_chunks:
                # Filter by minimum similarity
                filtered_chunks = [(chunk, score) for chunk, score in similar_chunks if score >= min_similarity]
                
                if filtered_chunks:
                    st.success(f"✅ Found {len(filtered_chunks)} relevant results!")
                    
                    # Generate answer
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown("### 📄 **Answer:**")
                    
                    # Create response from top chunks
                    answer_parts = []
                    for i, (chunk, score) in enumerate(filtered_chunks[:3], 1):
                        answer_parts.append(f"**{i}.** {chunk['content'][:300]}... *[From: {chunk['filename']}]*")
                    
                    st.markdown("\n\n".join(answer_parts))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show detailed results
                    st.markdown("### 🔍 **Detailed Search Results:**")
                    
                    for i, (chunk, score) in enumerate(filtered_chunks, 1):
                        with st.expander(f"Result {i}: {chunk['filename']} (Similarity: {score:.3f})"):
                            st.markdown(f'<div class="source-box">', unsafe_allow_html=True)
                            st.markdown(f"**📁 Source:** `{chunk['filename']}`")
                            st.markdown(f"**📊 Similarity Score:** <span class='similarity-score'>{score:.3f}</span>", unsafe_allow_html=True)
                            st.markdown(f"**📄 Content:**")
                            st.write(chunk['content'])
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to session state for history
                    if 'search_history' not in st.session_state:
                        st.session_state.search_history = []
                    
                    st.session_state.search_history.append({
                        'query': query,
                        'results_count': len(filtered_chunks),
                        'top_score': filtered_chunks[0][1] if filtered_chunks else 0
                    })
                    
                else:
                    st.warning(f"⚠️ No results found above similarity threshold of {min_similarity:.1f}")
                    st.info("💡 Try lowering the similarity threshold or rephrasing your question.")
            else:
                st.error("❌ No results found. Please check your API token and try again.")
    
    with col2:
        st.header("📈 Statistics")
        
        if 'chunks_loaded' in st.session_state:
            # Document statistics
            st.metric("Documents Loaded", st.session_state.get('document_count', 0))
            st.metric("Text Chunks", len(st.session_state.get('chunks', [])))
            
            # Search history
            if 'search_history' in st.session_state and st.session_state.search_history:
                st.markdown("### 📊 Recent Searches")
                for i, search in enumerate(reversed(st.session_state.search_history[-5:]), 1):
                    st.markdown(f"**{i}.** {search['query'][:30]}...")
                    st.markdown(f"   Results: {search['results_count']}, Best Score: {search['top_score']:.3f}")
        
        # Help section
        st.markdown("---")
        st.header("❓ Help")
        st.markdown("""
        **How to use:**
        1. Enter your HuggingFace API token
        2. Click "Load Documents" 
        3. Type your question
        4. Click "Search"
        
        **Tips:**
        - Use specific questions for better results
        - Try the sample questions first
        - Adjust similarity threshold if needed
        """)

if __name__ == "__main__":
    main()
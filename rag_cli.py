#!/usr/bin/env python3

import sys
sys.path.append('src')

from data_loader import DataLoader
from text_chunker import TextChunker
from config.config import RAW_DATA_DIR
import requests
import json
import time
from typing import List, Dict, Tuple

class InteractiveRAG:
    """Interactive command-line RAG system"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.model = "sentence-transformers/all-MiniLM-L6-v2"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.chunks = []
        self.loaded = False
        
    def load_documents(self):
        """Load and process documents"""
        if self.loaded:
            return True
            
        print("📄 Loading documents...")
        loader = DataLoader(RAW_DATA_DIR)
        documents = loader.load_documents_from_directory()
        
        if not documents:
            print("❌ No documents found!")
            return False
        
        print("🔗 Chunking documents...")
        chunker = TextChunker(chunk_size=600, chunk_overlap=100)
        chunks = chunker.process_documents(documents, "recursive")
        self.chunks = chunker.validate_chunks(chunks)
        
        print(f"✅ Loaded {len(documents)} documents, created {len(self.chunks)} chunks")
        self.loaded = True
        return True
    
    def search_and_answer(self, query: str, top_k: int = 5) -> bool:
        """Search for answer and display results"""
        if not self.loaded:
            print("❌ Documents not loaded. Please load documents first.")
            return False
        
        print(f"\n🔍 Searching for: '{query}'")
        print("⏳ Please wait...")
        
        # Prepare API call
        chunk_texts = [chunk['content'] for chunk in self.chunks]
        payload = {
            "inputs": {
                "source_sentence": query,
                "sentences": chunk_texts
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                similarities = response.json()
                
                # Pair and sort results
                chunk_similarity_pairs = list(zip(self.chunks, similarities))
                chunk_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
                
                # Display results
                top_results = chunk_similarity_pairs[:top_k]
                self.display_results(query, top_results)
                return True
                
            elif response.status_code == 503:
                print("⏳ Model is loading. Please wait and try again.")
                return False
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"💥 Error: {e}")
            return False
    
    def display_results(self, query: str, results: List[Tuple[Dict, float]]):
        """Display search results in a formatted way"""
        print(f"\n{'='*60}")
        print(f"🤔 Question: {query}")
        print(f"{'='*60}")
        
        # Filter results with decent similarity
        good_results = [(chunk, score) for chunk, score in results if score > 0.3]
        
        if good_results:
            print(f"\n📝 Answer based on {len(good_results)} relevant sources:")
            print("-" * 60)
            
            for i, (chunk, score) in enumerate(good_results[:3], 1):
                print(f"\n{i}. From '{chunk['filename']}' (Similarity: {score:.3f}):")
                print(f"   {chunk['content'][:300]}...")
            
            print(f"\n{'─'*60}")
            print("📊 All Search Results:")
            
            for i, (chunk, score) in enumerate(results, 1):
                status = "✅" if score > 0.3 else "⚠️" if score > 0.2 else "❌"
                print(f"   {i}. {status} {score:.3f} | {chunk['filename'][:30]} | {chunk['content'][:50]}...")
        else:
            print("\n❌ No highly relevant results found.")
            print("💡 Try rephrasing your question or asking about different topics.")
            
            # Show top results anyway
            print(f"\n🔍 Top {min(3, len(results))} results (lower relevance):")
            for i, (chunk, score) in enumerate(results[:3], 1):
                print(f"   {i}. Score: {score:.3f} | {chunk['filename']}")
                print(f"      {chunk['content'][:100]}...")
    
    def run_interactive(self):
        """Run interactive command-line interface"""
        print("\n🤖 Welcome to RAG Document Q&A System!")
        print("=" * 50)
        
        # Load documents
        if not self.load_documents():
            return
        
        print(f"\n💡 Sample questions to try:")
        sample_questions = [
            "What is RAG?",
            "What technologies are used?",
            "How does the system work?",
            "What are the main features?",
            "What is machine learning?"
        ]
        
        for i, q in enumerate(sample_questions, 1):
            print(f"   {i}. {q}")
        
        print(f"\n{'='*50}")
        print("💬 Start asking questions! (Type 'quit' to exit)")
        print("="*50)
        
        while True:
            try:
                query = input("\n🤔 Your question: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye! Thanks for using the RAG system!")
                    break
                
                if query.lower() in ['help', 'h']:
                    self.show_help()
                    continue
                
                if query.lower() == 'stats':
                    self.show_stats()
                    continue
                
                # Process the question
                success = self.search_and_answer(query)
                
                if not success:
                    print("❌ Search failed. Please try again.")
                
                print(f"\n{'─'*50}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
    
    def show_help(self):
        """Show help information"""
        print(f"\n📚 Help Information:")
        print("─" * 30)
        print("Commands:")
        print("  help, h    - Show this help")
        print("  stats      - Show system statistics")
        print("  quit, q    - Exit the system")
        print("\nTips:")
        print("  • Ask specific questions for better results")
        print("  • Try different phrasings if results aren't good")
        print("  • Questions about your documents work best")
    
    def show_stats(self):
        """Show system statistics"""
        print(f"\n📊 System Statistics:")
        print("─" * 30)
        print(f"Documents loaded: {self.loaded}")
        if self.loaded:
            print(f"Total chunks: {len(self.chunks)}")
            filenames = list(set(chunk['filename'] for chunk in self.chunks))
            print(f"Source files: {len(filenames)}")
            for filename in filenames[:5]:  # Show first 5 files
                chunk_count = sum(1 for chunk in self.chunks if chunk['filename'] == filename)
                print(f"  • {filename}: {chunk_count} chunks")
            if len(filenames) > 5:
                print(f"  • ... and {len(filenames) - 5} more files")

def main():
    """Main function"""
    print("🔑 RAG System Setup")
    print("=" * 30)
    
    # Get API token
    api_token = input("Enter your HuggingFace API token: ").strip()
    
    if not api_token:
        print("❌ No API token provided. Exiting...")
        return
    
    # Initialize and run RAG system
    rag = InteractiveRAG(api_token)
    rag.run_interactive()

if __name__ == "__main__":
    main()
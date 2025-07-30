import requests
import json
import time
import numpy as np
from typing import List, Dict, Optional
import pickle
import os
from pathlib import Path

class HuggingFaceEmbeddings:
    """Generate embeddings using HuggingFace Inference API (Free)"""
    
    def __init__(self, api_token: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.api_token = api_token
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        
    def generate_single_embedding(self, text: str, max_retries: int = 3) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        payload = {"inputs": text}
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0] if isinstance(result[0], list) else result
                    return result
                    
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"⏳ Model loading, waiting 20 seconds... (attempt {attempt + 1})")
                    time.sleep(20)
                    continue
                    
                elif response.status_code == 429:
                    # Rate limit, wait and retry
                    print(f"⚠️ Rate limit hit, waiting 60 seconds... (attempt {attempt + 1})")
                    time.sleep(60)
                    continue
                    
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"🔄 Network error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
                
        return None
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 1) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts with rate limiting"""
        embeddings = []
        
        print(f"🚀 Generating embeddings for {len(texts)} texts...")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for j, text in enumerate(batch):
                print(f"📝 Processing {i + j + 1}/{len(texts)}: {text[:50]}...")
                
                embedding = self.generate_single_embedding(text)
                embeddings.append(embedding)
                
                # Rate limiting - wait between requests
                if i + j < len(texts) - 1:  # Don't wait after the last request
                    time.sleep(1)  # 1 second between requests to be safe
                    
            print(f"✅ Completed batch {i//batch_size + 1}")
            
        successful = sum(1 for e in embeddings if e is not None)
        print(f"🎯 Successfully generated {successful}/{len(texts)} embeddings")
        
        return embeddings

class SimpleVectorStore:
    """Simple in-memory vector store for testing"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.embeddings = []
        self.metadata = []
        self.storage_path = storage_path
        
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Add chunks and their embeddings to the store"""
        for chunk, embedding in zip(chunks, embeddings):
            if embedding is not None:  # Only add successful embeddings
                self.embeddings.append(embedding)
                self.metadata.append(chunk)
        
        print(f"📚 Added {len(self.embeddings)} documents to vector store")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
        except:
            return 0.0
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for most similar documents"""
        if not self.embeddings:
            return []
        
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            similarities.append((similarity, i))
        
        # Sort by similarity (highest first)
        similarities.sort(reverse=True)
        
        results = []
        for similarity, idx in similarities[:top_k]:
            result = self.metadata[idx].copy()
            result['similarity_score'] = similarity
            results.append(result)
        
        return results
    
    def save(self, filepath: Path):
        """Save vector store to disk"""
        data = {
            'embeddings': self.embeddings,
            'metadata': self.metadata
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Vector store saved to {filepath}")
    
    def load(self, filepath: Path):
        """Load vector store from disk"""
        if filepath.exists():
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.embeddings = data['embeddings']
            self.metadata = data['metadata']
            
            print(f"📁 Vector store loaded from {filepath}")
            print(f"📊 Loaded {len(self.embeddings)} embeddings")
            return True
        return False
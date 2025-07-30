from typing import List, Dict
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter

class TextChunker:
    """Handles text chunking with various strategies"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def recursive_chunk(self, text: str) -> List[str]:
        """Split text using recursive character splitting"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        return splitter.split_text(text)
    
    def semantic_chunk(self, text: str) -> List[str]:
        """Split text by semantic boundaries (paragraphs, sentences)"""
        # Split by double newlines first (paragraphs)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph itself is too long, split by sentences
                if len(paragraph) > self.chunk_size:
                    sentences = re.split(r'[.!?]+', paragraph)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        if len(temp_chunk) + len(sentence) <= self.chunk_size:
                            temp_chunk += sentence + ". "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sentence + ". "
                    
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def fixed_size_chunk(self, text: str) -> List[str]:
        """Split text into fixed-size chunks with overlap"""
        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator=" "
        )
        return splitter.split_text(text)
    
    def chunk_by_headers(self, text: str) -> List[Dict]:
        """Split text by markdown-style headers"""
        # Find headers (lines starting with #)
        lines = text.split('\n')
        chunks = []
        current_section = ""
        current_header = "Introduction"
        
        for line in lines:
            if re.match(r'^#{1,6}\s', line):
                # Save previous section
                if current_section.strip():
                    chunks.append({
                        'content': current_section.strip(),
                        'header': current_header,
                        'section_type': 'header_based'
                    })
                
                # Start new section
                current_header = re.sub(r'^#{1,6}\s', '', line)
                current_section = line + '\n'
            else:
                current_section += line + '\n'
        
        # Add the last section
        if current_section.strip():
            chunks.append({
                'content': current_section.strip(),
                'header': current_header,
                'section_type': 'header_based'
            })
        
        return chunks
    
    def process_documents(self, documents: List[Dict], chunking_method: str = "recursive") -> List[Dict]:
        """Process multiple documents and return chunks with metadata"""
        all_chunks = []
        
        for doc in documents:
            text = doc.get('content', '')
            
            if chunking_method == "recursive":
                chunks = self.recursive_chunk(text)
            elif chunking_method == "semantic":
                chunks = self.semantic_chunk(text)
            elif chunking_method == "fixed":
                chunks = self.fixed_size_chunk(text)
            elif chunking_method == "headers":
                header_chunks = self.chunk_by_headers(text)
                for chunk_data in header_chunks:
                    all_chunks.append({
                        'content': chunk_data['content'],
                        'source': doc.get('source', ''),
                        'filename': doc.get('filename', ''),
                        'file_type': doc.get('file_type', ''),
                        'chunk_index': len(all_chunks),
                        'header': chunk_data.get('header', ''),
                        'chunking_method': chunking_method
                    })
                continue
            else:
                chunks = self.recursive_chunk(text)  # Default fallback
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Skip very short chunks
                    all_chunks.append({
                        'content': chunk,
                        'source': doc.get('source', ''),
                        'filename': doc.get('filename', ''),
                        'file_type': doc.get('file_type', ''),
                        'chunk_index': len(all_chunks),
                        'chunking_method': chunking_method
                    })
        
        return all_chunks
    
    def validate_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Validate and filter chunks based on quality metrics"""
        valid_chunks = []
        
        for chunk in chunks:
            content = chunk.get('content', '')
            
            # Quality checks
            if len(content) < 50:  # Too short
                continue
            
            if content.count(' ') < 5:  # Not enough words
                continue
            
            if not re.search(r'[.!?]', content):  # No sentence endings
                continue
            
            # Check for reasonable text (not just numbers/symbols)
            word_chars = len(re.findall(r'[a-zA-Z]', content))
            if word_chars / len(content) < 0.5:
                continue
            
            valid_chunks.append(chunk)
        
        return valid_chunks
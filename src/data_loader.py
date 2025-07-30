import os
import PyPDF2
import docx
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict
import re

class DataLoader:
    """Handles loading and preprocessing of various document formats"""
    
    def __init__(self, raw_data_dir: Path):
        self.raw_data_dir = Path(raw_data_dir)
        
    def load_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            return ""
    
    def load_docx(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error loading DOCX {file_path}: {e}")
            return ""
    
    def load_txt(self, file_path: str) -> str:
        """Load plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading TXT {file_path}: {e}")
            return ""
    
    def load_web_page(self, url: str) -> str:
        """Scrape text from web pages"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error loading webpage {url}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Remove very short lines
        lines = text.split('\n')
        lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(lines).strip()
    
    def load_documents_from_directory(self) -> List[Dict]:
        """Load all documents from the raw data directory"""
        documents = []
        
        for file_path in self.raw_data_dir.rglob('*'):
            if file_path.is_file():
                text = ""
                file_ext = file_path.suffix.lower()
                
                if file_ext == '.pdf':
                    text = self.load_pdf(str(file_path))
                elif file_ext == '.docx':
                    text = self.load_docx(str(file_path))
                elif file_ext == '.txt':
                    text = self.load_txt(str(file_path))
                
                if text:
                    cleaned_text = self.clean_text(text)
                    if cleaned_text:
                        documents.append({
                            'content': cleaned_text,
                            'source': str(file_path),
                            'filename': file_path.name,
                            'file_type': file_ext
                        })
        
        return documents
    
    def load_from_urls(self, urls: List[str]) -> List[Dict]:
        """Load documents from a list of URLs"""
        documents = []
        
        for url in urls:
            text = self.load_web_page(url)
            if text:
                cleaned_text = self.clean_text(text)
                if cleaned_text:
                    documents.append({
                        'content': cleaned_text,
                        'source': url,
                        'filename': url.split('/')[-1] or 'webpage',
                        'file_type': 'web'
                    })
        
        return documents
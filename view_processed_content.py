#!/usr/bin/env python3

import sys
sys.path.append('src')

from data_loader import DataLoader
from config.config import RAW_DATA_DIR

def view_pdf_content():
    """View the full processed content of the PDF"""
    
    loader = DataLoader(RAW_DATA_DIR)
    documents = loader.load_documents_from_directory()
    
    # Find the PDF document
    pdf_doc = None
    for doc in documents:
        if 'Virtua Intelligence' in doc['filename']:
            pdf_doc = doc
            break
    
    if not pdf_doc:
        print("❌ PDF document not found!")
        return
    
    print("📄 Virtua Intelligence PDF - Full Processed Content")
    print("=" * 60)
    print(f"Filename: {pdf_doc['filename']}")
    print(f"Source: {pdf_doc['source']}")
    print(f"Content Length: {len(pdf_doc['content'])} characters")
    print(f"Word Count: {len(pdf_doc['content'].split())} words")
    print("-" * 60)
    print("FULL CONTENT:")
    print("-" * 60)
    print(pdf_doc['content'])
    print("-" * 60)
    print("✅ Content display complete")

if __name__ == "__main__":
    view_pdf_content()
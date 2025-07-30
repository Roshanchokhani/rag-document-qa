import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_DB_DIR = DATA_DIR / "vectors"

# Model configurations
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gpt-3.5-turbo"  # or your preferred model

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Vector database settings
VECTOR_DB_NAME = "rag_knowledge_base"
TOP_K_RETRIEVAL = 5

# API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, VECTOR_DB_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
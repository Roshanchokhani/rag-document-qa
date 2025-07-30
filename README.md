# 🤖 RAG Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) system that allows users to ask questions about their documents using AI. Built with Python, Streamlit, and HuggingFace APIs.

## ✨ Features

- 📄 **Multi-format Document Support**: PDF, Word, Text files
- 🧠 **Intelligent Text Chunking**: Smart document segmentation
- 🔍 **Semantic Search**: HuggingFace-powered similarity search
- 🌐 **Web Interface**: Beautiful Streamlit UI
- 💻 **CLI Interface**: Command-line tool for power users
- 📊 **Source Attribution**: Always cites document sources
- ⚡ **Real-time Processing**: Fast query responses
- 🆓 **Free to Use**: No expensive API costs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- HuggingFace account (free) - [Sign up here](https://huggingface.co/join)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rag-document-qa.git
   cd rag-document-qa
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your documents**
   ```bash
   # Place your PDF, Word, or text files in:
   data/raw/
   ```

4. **Get HuggingFace API Token**
   - Visit [HuggingFace Settings](https://huggingface.co/settings/tokens)
   - Create a new token with "Write" permissions
   - Copy the token for use in the application

### Usage

#### Web Interface (Recommended)
```bash
streamlit run rag_app.py
```
- Open your browser to `http://localhost:8501`
- Enter your HuggingFace API token
- Click "Load Documents"
- Start asking questions!

#### Command Line Interface
```bash
python3 rag_cli.py
```

## 📁 Project Structure

```
rag-document-qa/
├── config/
│   └── config.py              # Configuration settings
├── src/
│   ├── data_loader.py         # Document loading & preprocessing
│   ├── text_chunker.py        # Text chunking strategies
│   └── embedding_generator.py # Embedding utilities
├── data/
│   ├── raw/                   # Your input documents
│   ├── processed/             # Processed data cache
│   └── vectors/               # Vector storage (if used)
├── rag_app.py                 # Streamlit web interface
├── rag_cli.py                 # Command line interface
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container config
└── README.md                  # This file
```

## 🛠️ How It Works

1. **Document Processing**: Loads and cleans documents from various formats
2. **Text Chunking**: Splits documents into semantically meaningful chunks
3. **Query Processing**: Uses HuggingFace API for similarity search
4. **Response Generation**: Returns relevant chunks with source attribution

## 🌐 Deployment

### Docker
```bash
# Build image
docker build -t rag-qa-system .

# Run container
docker run -p 8501:8501 rag-qa-system
```

### Heroku
```bash
# Install Heroku CLI, then:
heroku create your-rag-app
git push heroku main
```

## 🔧 Configuration

Key settings in `config/config.py`:
- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RETRIEVAL`: Number of results returned (default: 5)

## 📊 Sample Questions

Try asking questions like:
- "What is this document about?"
- "What are the main features?"
- "How does the system work?"
- "What technologies are mentioned?"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [HuggingFace](https://huggingface.co/) for embedding APIs
- [Streamlit](https://streamlit.io/) for the web framework
- [LangChain](https://langchain.com/) for text processing utilities

## 📧 Support

If you have questions or need help:
- 🐛 [Open an issue](https://github.com/yourusername/rag-document-qa/issues)
- 💬 [Start a discussion](https://github.com/yourusername/rag-document-qa/discussions)

---

**⭐ Star this repo if you find it helpful!**
# 🚀 Deployment Guide

This guide covers deploying your RAG Document Q&A System to various platforms.

## 📋 Prerequisites

- Git installed
- Docker installed (for containerized deployments)
- GitHub account
- HuggingFace account with API token

## 🐙 GitHub Setup

### 1. Create GitHub Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: RAG Document Q&A System"

# Add GitHub remote (replace with your username)
git remote add origin https://github.com/yourusername/rag-document-qa.git

# Push to GitHub
git push -u origin main
```

### 2. Set up GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `HEROKU_API_KEY`: Your Heroku API key
- `HEROKU_APP_NAME`: Your Heroku app name
- `HEROKU_EMAIL`: Your Heroku account email
- `HUGGINGFACE_API_TOKEN`: Your HuggingFace API token

## 🐳 Docker Deployment

### Local Docker Build
```bash
# Build the image
docker build -t rag-qa-system .

# Run locally
docker run -p 8501:8501 -e HUGGINGFACE_API_TOKEN=your_token rag-qa-system

# Access at http://localhost:8501
```

### Docker Compose (Optional)
```yaml
# docker-compose.yml
version: '3.8'
services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - HUGGINGFACE_API_TOKEN=${HUGGINGFACE_API_TOKEN}
    volumes:
      - ./data:/app/data
```

## ☁️ Cloud Deployment Options

### Option 1: Heroku (Recommended for beginners)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-rag-app-name

# Set stack to container
heroku stack:set container -a your-rag-app-name

# Set environment variables
heroku config:set HUGGINGFACE_API_TOKEN=your_token -a your-rag-app-name

# Deploy
git push heroku main
```

### Option 2: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Option 3: Render

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `streamlit run rag_app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add environment variables

### Option 4: Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file: `rag_app.py`
4. Add secrets in advanced settings

## 🔧 Environment Variables

Set these environment variables in your deployment platform:

```env
HUGGINGFACE_API_TOKEN=your_token_here
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow will automatically:

1. **Test** code on multiple Python versions
2. **Security scan** with Bandit
3. **Build** Docker image
4. **Deploy** to Heroku on main branch push

### Manual Deployment Trigger

```bash
# Create and push a tag to trigger deployment
git tag v1.0.0
git push origin v1.0.0
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint
```bash
# Test system health
python health_check.py
```

### Application Logs
```bash
# Heroku logs
heroku logs --tail -a your-app-name

# Docker logs
docker logs container_name
```

## 🔐 Security Considerations

1. **Never commit API keys** to the repository
2. **Use environment variables** for all secrets
3. **Enable branch protection** on main branch
4. **Require PR reviews** before merging
5. **Run security scans** regularly

## 🚨 Troubleshooting

### Common Issues

**Issue**: Streamlit not accessible
```bash
# Solution: Check port binding
streamlit run rag_app.py --server.port=$PORT --server.address=0.0.0.0
```

**Issue**: Module import errors
```bash
# Solution: Check PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH
```

**Issue**: HuggingFace API errors
```bash
# Solution: Verify token permissions
curl -H "Authorization: Bearer $HUGGINGFACE_API_TOKEN" \
     https://huggingface.co/api/whoami
```

## 📈 Scaling Considerations

For production use, consider:

1. **Load balancer** for multiple instances
2. **Redis caching** for frequently accessed data
3. **Database** for user sessions and analytics
4. **CDN** for static assets
5. **Monitoring** with tools like New Relic or DataDog

## 🎯 Next Steps

After successful deployment:

1. Set up custom domain
2. Add SSL certificate
3. Implement user authentication
4. Add usage analytics
5. Set up automated backups

---

**🎉 Congratulations! Your RAG system is now deployed and accessible to users worldwide!**
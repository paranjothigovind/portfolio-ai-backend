#!/bin/bash

# RAG Backend Setup Script
echo "🚀 Setting up RAG Backend Environment..."

# Check if Python 3.13 is available
if ! command -v python3.13 &> /dev/null; then
    echo "❌ Python 3.13 is not installed. Please install Python 3.13 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3.13 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install fastapi==0.116.1 uvicorn[standard]==0.35.0 sentence-transformers==5.1.0 faiss-cpu==1.12.0 transformers==4.56.0 torch==2.8.0 pydantic==2.11.7 python-multipart==0.0.20 openai==1.52.0 python-dotenv==1.0.1

# Test installation
echo "🧪 Testing installation..."
python test_installation.py

echo "✅ Setup complete! Virtual environment is ready."
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

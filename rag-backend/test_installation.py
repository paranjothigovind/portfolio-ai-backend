#!/usr/bin/env python3
"""
Simple test script to verify the RAG backend installation and basic functionality.
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def check_imports():
    """Check if required packages can be imported"""
    packages = [
        'fastapi',
        'uvicorn',
        'sentence_transformers',
        'faiss',
        'transformers',
        'torch',
        'pydantic'
    ]
    
    print("\nChecking package imports...")
    all_imports_ok = True
    
    for package in packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                print(f"❌ {package} - Not found")
                all_imports_ok = False
            else:
                print(f"✅ {package} - OK")
        except ImportError as e:
            print(f"❌ {package} - Import error: {e}")
            all_imports_ok = False
    
    return all_imports_ok

def check_requirements():
    """Check if requirements.txt exists"""
    print("\nChecking requirements.txt...")
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            print("✅ requirements.txt found")
            print(f"Contents:\n{requirements}")
            return True
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def main():
    """Run all checks"""
    print("🧪 RAG Backend Installation Test")
    print("=" * 50)
    
    success = True
    success &= check_python_version()
    success &= check_requirements()
    success &= check_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All checks passed! The RAG backend is ready to use.")
        print("\nTo start the server:")
        print("  cd rag-backend")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ Some checks failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return success

if __name__ == "__main__":
    main()

#!/bin/bash
# LockByte Installation Script

echo "🔒 LockByte - Secure Credential Management & Password Security Platform"
echo "========================================================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ -z "$PYTHON_VERSION" ]]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version >= 3.8
if [[ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]]; then
    echo "❌ Python 3.8 or higher required. Found $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv --prompt lockbyte

# Activate virtual environment
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
elif [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test installation
echo "🧪 Testing installation..."
python3 -c "import argon2; import cryptography; import PySide6"
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to verify dependencies"
    exit 1
fi

# Make main.py executable
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    chmod +x run.sh
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run LockByte:"
echo "  On Linux/Mac: ./run.sh"
echo "  On Windows: run.bat"
echo "  Or directly: python -m app.main"
echo ""
echo "📚 Documentation: docs/"
echo "🔬 Run tests: python -m pytest tests/ -v"
echo ""
echo "🔒 Your vault will be created at: ~/.lockbyte/vault.db"
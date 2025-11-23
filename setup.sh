#!/bin/bash
# Setup script for Data Quality Framework

set -e

echo "=========================================="
echo "Data Quality Framework - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9 or higher is required"
    exit 1
fi
echo "   ✅ Python version OK"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "   ✅ Dependencies installed"
echo ""

# Install package in development mode
echo "🔧 Installing package in development mode..."
pip install -e .
echo "   ✅ Package installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data reports logs config
mkdir -p reports
touch reports/.gitkeep
echo "   ✅ Directories created"
echo ""

# Copy example config if needed
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "   ✅ .env file created (please update with your credentials)"
else
    echo "   .env file already exists"
fi
echo ""

# Run tests to verify installation
echo "🧪 Running tests..."
if pytest tests/ -v --tb=short; then
    echo "   ✅ All tests passed"
else
    echo "   ⚠️  Some tests failed (this is OK for initial setup)"
fi
echo ""

# Display next steps
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Try the quick examples:"
echo "   python examples/basic_profiling.py"
echo "   python examples/custom_validators.py"
echo ""
echo "3. Run the dashboard:"
echo "   streamlit run dashboard/app.py"
echo ""
echo "4. Or use Docker:"
echo "   docker-compose -f docker/docker-compose.yml up -d"
echo ""
echo "5. Use the CLI:"
echo "   dqf profile data/customers.csv --output report.html"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - QUICKSTART.md - Quick start guide"
echo "   - examples/ - Usage examples"
echo ""
echo "🎉 Happy data quality checking!"
echo "=========================================="

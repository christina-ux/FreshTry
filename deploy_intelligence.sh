#!/bin/bash

# Live Intelligence Feed Pro - Deployment Script
# Simple deployment for the Live Intelligence Feed system

echo "🚀 Deploying Live Intelligence Feed Pro..."
echo "============================================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the repository root."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install additional intelligence dependencies
echo "📦 Installing additional dependencies..."
pip install feedparser python-jose[cryptography] passlib pdfkit markdown

# Create required directories
echo "📁 Creating directories..."
mkdir -p data/converted data/reports data/uploads data/zta data/integrations data/dashboard data/sample config

# Generate sample data
echo "🎲 Generating sample data..."
python -c "from intelligence.sample_data import populate_sample_data; populate_sample_data()"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file to add your API keys (OpenAI, Anthropic, etc.)"
fi

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌟 To start the Live Intelligence Feed system:"
echo ""
echo "1. 🔧 Configure API keys:"
echo "   Edit .env file and add your OpenAI/Anthropic API keys"
echo ""
echo "2. 🚀 Start the API server:"
echo "   python main.py api --port 8001 --reload"
echo ""
echo "3. 📊 Start the dashboard (in another terminal):"
echo "   streamlit run intelligence_dashboard.py --server.port 8502"
echo ""
echo "4. 🌐 Access the system:"
echo "   • API Documentation: http://localhost:8001/docs"
echo "   • Intelligence Dashboard: http://localhost:8502"
echo ""
echo "🔥 Features Available:"
echo "   • ✅ Real-time intelligence collection from RSS feeds"
echo "   • ✅ AI-powered memo generation (WSJ/McKinsey style)"
echo "   • ✅ Self-evolving tripwire system"
echo "   • ✅ User action tracking and learning"
echo "   • ✅ Professional packaging and monetization"
echo "   • ✅ Live feeds with categorization"
echo "   • ✅ Risk assessment and scoring"
echo ""
echo "📚 Sample Data:"
echo "   • 50 sample intelligence items generated"
echo "   • 100 sample user actions for learning system"
echo "   • 1 sample professional memo"
echo ""
echo "🎯 API Endpoints:"
echo "   • GET  /api/intelligence/status - System status"
echo "   • GET  /api/intelligence/feeds - List feeds"
echo "   • POST /api/intelligence/collect - Trigger collection"
echo "   • POST /api/intelligence/memo/generate - Generate memo"
echo "   • POST /api/intelligence/action/track - Track user action"
echo "   • GET  /api/intelligence/learning/health - Learning metrics"
echo ""
echo "📖 For more details, see:"
echo "   • config/intelligence_config.yaml - Configuration"
echo "   • data/sample/ - Sample data files"
echo "   • README.md - Full documentation"
echo ""
echo "🎉 Happy Intelligence Feeding!"
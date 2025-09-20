#!/bin/bash

# PolicyEdgeAI Setup Script

echo "Setting up PolicyEdgeAI..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    echo "Error: Unsupported operating system."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create required directories
echo "Creating required directories..."
mkdir -p data/converted data/reports data/uploads data/zta data/integrations data/dashboard

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. Please edit it to add your OpenAI API key."
fi

# Generate default ZTA mappings
echo "Generating default ZTA mappings..."
python main.py zta --generate-default

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Edit the .env file to add your OpenAI API key"
echo "2. Activate the virtual environment (if not already activated):"
echo "   $ source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo ""
echo "3. Start the application:"
echo "   $ python main.py api --reload"
echo ""
echo "4. Open your browser and navigate to:"
echo "   http://localhost:8000"
echo ""
echo "For detailed usage instructions, see the README.md file."
echo "Enjoy using PolicyEdgeAI!"
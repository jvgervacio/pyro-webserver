#!/bin/bash

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    # Create a new virtual environment
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install requirements if not already installed
if ! command -v pip >/dev/null; then
    echo "pip not found. Please make sure Python and pip are installed."
    exit 1
fi

#  install requirements if not already installed headless
pip install -r requirements.txt

# Run the application
python app.py

#!/bin/bash

# Ubuntu Development Environment Manager Launcher
# Simple script to run the application

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check if we're in a virtual environment or have system packages
if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "Warning: PyQt5 not found. Installing requirements..."
    
    # Try to install in virtual environment first
    if [ -d "$DIR/venv" ]; then
        echo "Using existing virtual environment..."
        source "$DIR/venv/bin/activate"
    else
        echo "Creating virtual environment..."
        python3 -m venv "$DIR/venv"
        source "$DIR/venv/bin/activate"
        pip install --upgrade pip
    fi
    
    # Install requirements
    if [ -f "$DIR/requirements.txt" ]; then
        pip install -r "$DIR/requirements.txt"
    else
        pip install PyQt5 PyYAML
    fi
fi

# Check for backend availability
echo "Checking backend availability..."

MULTIPASS_AVAILABLE=false
LXD_AVAILABLE=false

if command -v multipass &> /dev/null; then
    if multipass version &> /dev/null; then
        MULTIPASS_AVAILABLE=true
        echo "✓ Multipass is available"
    fi
else
    echo "✗ Multipass not found. Install with: sudo snap install multipass"
fi

if command -v lxc &> /dev/null; then
    if lxc version &> /dev/null 2>&1; then
        LXD_AVAILABLE=true
        echo "✓ LXD is available"
    fi
else
    echo "✗ LXD not found. Install with: sudo apt install lxd"
fi

if [ "$MULTIPASS_AVAILABLE" = false ] && [ "$LXD_AVAILABLE" = false ]; then
    echo ""
    echo "Warning: No backends available!"
    echo "Please install at least one backend:"
    echo "  Multipass: sudo snap install multipass"
    echo "  LXD: sudo apt install lxd && sudo usermod -a -G lxd \$USER"
    echo ""
    echo "The application will still start but you won't be able to create environments."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the application
echo "Starting Ubuntu Development Environment Manager..."
cd "$DIR"
python3 main.py "$@"

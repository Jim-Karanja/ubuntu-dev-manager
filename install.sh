#!/bin/bash

# Ubuntu Development Environment Manager Installation Script

set -e

echo "Ubuntu Development Environment Manager - Installation"
echo "======================================================"

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "Error: This installer requires apt package manager (Ubuntu/Debian)"
    exit 1
fi

# Check for sudo access
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root."
    echo "It will ask for sudo permission when needed."
    exit 1
fi

echo "Installing system dependencies..."

# Install Python and Qt dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-pyqt5 python3-pyqt5.qtwidgets

echo "Setting up Python virtual environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install --upgrade pip
pip install -r requirements.txt

echo "Checking backends..."

# Check and optionally install backends
INSTALL_MULTIPASS=false
INSTALL_LXD=false

if ! command -v multipass &> /dev/null; then
    echo ""
    echo "Multipass is not installed."
    read -p "Would you like to install Multipass? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        INSTALL_MULTIPASS=true
    fi
fi

if ! command -v lxc &> /dev/null; then
    echo ""
    echo "LXD is not installed."
    read -p "Would you like to install LXD? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        INSTALL_LXD=true
    fi
fi

# Install selected backends
if [ "$INSTALL_MULTIPASS" = true ]; then
    echo "Installing Multipass..."
    sudo snap install multipass
fi

if [ "$INSTALL_LXD" = true ]; then
    echo "Installing LXD..."
    sudo apt install -y lxd
    sudo usermod -a -G lxd $USER
    echo "Note: You'll need to log out and back in for LXD group membership to take effect."
    
    echo "Initializing LXD..."
    # Check if lxd is already initialized
    if ! lxc network list &> /dev/null; then
        sudo lxd init --auto
    fi
fi

# Make run script executable
chmod +x run.sh

echo ""
echo "Installation completed!"
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""

# Optionally install desktop entry
read -p "Would you like to install the desktop entry for easy launching? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Update the Exec path in the desktop file
    sed -i "s|Exec=.*|Exec=$(pwd)/run.sh|" ubuntu-dev-manager.desktop
    
    # Install desktop entry
    mkdir -p ~/.local/share/applications
    cp ubuntu-dev-manager.desktop ~/.local/share/applications/
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database ~/.local/share/applications/
    fi
    
    echo "Desktop entry installed. The application should now appear in your application menu."
fi

echo ""
echo "Setup complete! You can now:"
echo "1. Run './run.sh' from this directory"
echo "2. Find 'Ubuntu Dev Environment Manager' in your applications menu"
echo ""

if [ "$INSTALL_LXD" = true ]; then
    echo "Important: If you installed LXD, please log out and log back in"
    echo "for the group membership changes to take effect."
fi

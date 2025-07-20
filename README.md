# Ubuntu Development Environment Manager

A GUI tool for managing isolated development environments using Multipass and LXD on Ubuntu Desktop.

## Features

- **Multiple Backend Support**: Works with both Multipass (VMs) and LXD (containers)
- **Environment Templates**: Pre-configured templates for popular development stacks:
  - Node.js Development
  - Python Development  
  - Go Development
  - Rust Development
  - Java Development
  - Docker Development
  - Full Stack Web Development
  - Data Science Environment
  - DevOps Environment
- **Directory Mounting**: Mount host directories into guest environments
- **Resource Management**: Configure CPU, memory, and disk resources
- **GUI Interface**: User-friendly Qt-based interface
- **Environment Lifecycle**: Create, start, stop, and delete environments
- **Shell Access**: Direct shell access to running environments

## Why This Tool?

Canonical cares about making Ubuntu the best OS for developers. This tool addresses common developer pain points:

- **Isolation**: Keep different project dependencies separate
- **Reproducibility**: Consistent environments across team members
- **Flexibility**: Switch between different language stacks easily
- **Integration**: Seamless integration with Canonical's virtualization technologies

## Prerequisites

### Ubuntu Desktop 20.04+ with:

**For Multipass backend:**
```bash
sudo apt update
sudo apt install snapd
sudo snap install multipass
```

**For LXD backend:**
```bash
sudo apt update
sudo apt install lxd
sudo usermod -a -G lxd $USER
# Log out and log back in for group changes to take effect
lxd init --auto
```

**Python and Qt dependencies:**
```bash
sudo apt install python3 python3-pip python3-venv
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets
```

## Installation

### Method 1: Install from Source

```bash
# Clone or download the project
git clone https://github.com/canonical/ubuntu-dev-manager.git
cd ubuntu-dev-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

### Method 2: System Installation

```bash
# Install system-wide
sudo python3 setup.py install

# Run from anywhere
ubuntu-dev-manager
```

## Usage

### Starting the Application

```bash
# If installed from source
cd ubuntu-dev-manager
python3 main.py

# If installed system-wide
ubuntu-dev-manager
```

### Creating an Environment

1. Click **"Create Environment"**
2. Choose a name for your environment
3. Select backend (Multipass or LXD)
4. Pick a template (e.g., "Node.js Development")
5. Configure resources (CPU, memory, disk)
6. Add directory mounts if needed
7. Click **"Create"**

The tool will:
- Create the VM/container
- Install the template packages
- Run setup scripts
- Mount specified directories

### Managing Environments

- **Start**: Select an environment and click "Start"
- **Stop**: Select a running environment and click "Stop"  
- **Shell**: Open a terminal to a running environment
- **Delete**: Remove an environment (must be stopped first)

### Directory Mounting

When creating an environment, you can mount host directories:
- **Host Path**: Directory on your Ubuntu desktop
- **Guest Path**: Where it appears in the environment
- Example: Mount `~/Projects` to `/home/ubuntu/projects`

### Templates

#### Available Templates

1. **Ubuntu Basic** - Essential development tools
2. **Node.js Development** - Node.js, npm, yarn, TypeScript
3. **Python Development** - Python 3, pip, virtualenv, common packages
4. **Go Development** - Latest Go version and tools
5. **Rust Development** - Rust toolchain with cargo
6. **Java Development** - OpenJDK, Maven, Gradle
7. **Docker Development** - Docker CE and Docker Compose
8. **Full Stack Web** - Node.js + Python + database clients
9. **Data Science** - Python with Jupyter, pandas, ML libraries
10. **DevOps** - Docker, Kubernetes, Terraform, AWS CLI

#### Template Features

Each template automatically:
- Installs required packages
- Configures the environment
- Sets up development directories
- Configures basic git settings

## Configuration

Settings are stored in `~/.config/ubuntu-dev-manager/config.json`:

- **Default Backend**: Choose multipass or lxd
- **Default Resources**: CPU, memory, disk defaults
- **Terminal Emulator**: Preferred terminal for shell access

Access via **Tools → Settings** in the application.

## Architecture

```
ubuntu-dev-manager/
├── main.py                 # Main GUI application
├── environment_manager.py  # Multipass/LXD operations
├── templates.py            # Environment templates
├── config_manager.py       # Configuration handling
├── requirements.txt        # Python dependencies
├── setup.py               # Installation script
└── README.md              # This file
```

### Key Components

- **DevEnvironmentGUI**: Main Qt application window
- **EnvironmentManager**: Handles backend operations
- **EnvironmentTemplates**: Template definitions
- **ConfigManager**: Application settings

## Development

### Running in Development Mode

```bash
# Clone the repository
git clone https://github.com/canonical/ubuntu-dev-manager.git
cd ubuntu-dev-manager

# Create development environment
python3 -m venv dev-env
source dev-env/bin/activate

# Install in development mode
pip install -e .

# Run with debug logging
PYTHONPATH=. python3 main.py
```

### Adding Custom Templates

Templates are defined in `templates.py`. Each template has:

```python
"template-id": {
    "name": "Display Name",
    "description": "Template description",
    "base_image": "22.04",  # Ubuntu version or LXD image
    "packages": ["pkg1", "pkg2"],  # apt packages
    "setup_script": """
        # Shell commands to run after package installation
    """
}
```

### Backend Support

The tool abstracts Multipass and LXD operations:

- **Multipass**: Creates Ubuntu VMs with full isolation
- **LXD**: Creates Ubuntu containers with shared kernel

Both backends support:
- Resource limits (CPU, memory, disk)
- Directory mounting
- Network access
- Package installation

## Troubleshooting

### Common Issues

**"Backend not available" error:**
```bash
# For Multipass
sudo snap install multipass

# For LXD  
sudo apt install lxd
sudo usermod -a -G lxd $USER
# Log out and back in
lxd init --auto
```

**"No suitable terminal emulator found":**
```bash
# Install a supported terminal
sudo apt install gnome-terminal  # or konsole, xterm, alacritty
```

**Permission errors with LXD:**
```bash
# Add user to lxd group
sudo usermod -a -G lxd $USER
# Log out and log back in
```

**PyQt5 import errors:**
```bash
# Install Qt5 dependencies
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets
# Or via pip in virtual environment
pip install PyQt5
```

### Logs and Debugging

- Application logs appear in the GUI log panel
- Enable debug logging via settings
- Check system logs for backend issues:
  ```bash
  # Multipass logs
  multipass logs
  
  # LXD logs  
  lxc info --debug
  ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Test with both Multipass and LXD backends
- Update templates when adding new language support

## License

GPL-3.0 License. See LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions  
- **Documentation**: This README and inline code comments

## Roadmap

- [ ] Support for custom base images
- [ ] Environment export/import
- [ ] VS Code integration
- [ ] Snap package distribution
- [ ] Network configuration options
- [ ] Environment snapshots
- [ ] CI/CD integration templates

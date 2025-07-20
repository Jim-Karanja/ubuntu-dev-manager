"""
Environment Templates - Predefined development environment configurations
"""

from typing import Dict, Any


class EnvironmentTemplates:
    def __init__(self):
        self.templates = {
            "ubuntu-basic": {
                "name": "Ubuntu Basic",
                "description": "Basic Ubuntu environment with essential development tools",
                "base_image": "22.04",
                "packages": [
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common", "apt-transport-https"
                ],
                "setup_script": """
                    # Set up basic development environment
                    git config --global init.defaultBranch main
                    echo 'export EDITOR=vim' >> ~/.bashrc
                """
            },
            
            "nodejs-dev": {
                "name": "Node.js Development",
                "description": "Complete Node.js development environment with npm, yarn, and common tools",
                "base_image": "22.04",
                "packages": [
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common"
                ],
                "setup_script": """
                    # Install Node.js via NodeSource repository
                    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                    apt-get install -y nodejs
                    
                    # Install Yarn
                    npm install -g yarn
                    
                    # Install common global packages
                    npm install -g typescript ts-node eslint prettier nodemon
                    
                    # Create project directory
                    mkdir -p /home/ubuntu/projects
                    chown ubuntu:ubuntu /home/ubuntu/projects
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "python-dev": {
                "name": "Python Development",
                "description": "Python development environment with pip, virtualenv, and popular packages",
                "base_image": "22.04",
                "packages": [
                    "python3", "python3-pip", "python3-venv", "python3-dev",
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common"
                ],
                "setup_script": """
                    # Upgrade pip
                    python3 -m pip install --upgrade pip
                    
                    # Install common Python packages
                    pip3 install virtualenv pipenv poetry
                    pip3 install requests flask django fastapi
                    pip3 install numpy pandas matplotlib jupyter
                    pip3 install pytest black flake8 mypy
                    
                    # Create project directory
                    mkdir -p /home/ubuntu/projects
                    chown ubuntu:ubuntu /home/ubuntu/projects
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "go-dev": {
                "name": "Go Development",
                "description": "Go development environment with latest Go version and common tools",
                "base_image": "22.04",
                "packages": [
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common"
                ],
                "setup_script": """
                    # Install Go
                    GO_VERSION=$(curl -s https://api.github.com/repos/golang/go/releases/latest | grep -o 'go[0-9.]*\\.linux-amd64\\.tar\\.gz' | head -1)
                    wget https://golang.org/dl/$GO_VERSION
                    rm -rf /usr/local/go && tar -C /usr/local -xzf $GO_VERSION
                    rm $GO_VERSION
                    
                    # Set up Go environment
                    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/environment
                    echo 'export GOPATH=/home/ubuntu/go' >> /etc/environment
                    echo 'export PATH=$PATH:/usr/local/go/bin:/home/ubuntu/go/bin' >> /home/ubuntu/.bashrc
                    
                    # Create Go workspace
                    sudo -u ubuntu mkdir -p /home/ubuntu/go/{bin,src,pkg}
                    
                    # Install common Go tools
                    sudo -u ubuntu bash -c 'export PATH=$PATH:/usr/local/go/bin && go install golang.org/x/tools/gopls@latest'
                    sudo -u ubuntu bash -c 'export PATH=$PATH:/usr/local/go/bin && go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest'
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "rust-dev": {
                "name": "Rust Development",
                "description": "Rust development environment with rustc, cargo, and common tools",
                "base_image": "22.04",
                "packages": [
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common", "pkg-config", "libssl-dev"
                ],
                "setup_script": """
                    # Install Rust
                    sudo -u ubuntu bash -c 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
                    sudo -u ubuntu bash -c 'source ~/.cargo/env && rustup component add rust-analyzer'
                    
                    # Add cargo to PATH
                    echo 'source ~/.cargo/env' >> /home/ubuntu/.bashrc
                    
                    # Create projects directory
                    sudo -u ubuntu mkdir -p /home/ubuntu/projects
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "java-dev": {
                "name": "Java Development",
                "description": "Java development environment with OpenJDK, Maven, and Gradle",
                "base_image": "22.04",
                "packages": [
                    "openjdk-17-jdk", "maven", "gradle",
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common"
                ],
                "setup_script": """
                    # Set JAVA_HOME
                    echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /etc/environment
                    echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /home/ubuntu/.bashrc
                    
                    # Create projects directory
                    mkdir -p /home/ubuntu/projects
                    chown ubuntu:ubuntu /home/ubuntu/projects
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "docker-dev": {
                "name": "Docker Development",
                "description": "Development environment with Docker and Docker Compose",
                "base_image": "22.04",
                "packages": [
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common", "apt-transport-https",
                    "ca-certificates", "gnupg", "lsb-release"
                ],
                "setup_script": """
                    # Install Docker
                    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                    apt-get update
                    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                    
                    # Add ubuntu user to docker group
                    usermod -aG docker ubuntu
                    
                    # Install Docker Compose (standalone)
                    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\\K(.*)(?=")')
                    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                    
                    # Create projects directory
                    mkdir -p /home/ubuntu/projects
                    chown ubuntu:ubuntu /home/ubuntu/projects
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "web-dev": {
                "name": "Full Stack Web Development",
                "description": "Complete web development environment with Node.js, Python, and database tools",
                "base_image": "22.04",
                "packages": [
                    "python3", "python3-pip", "python3-venv", "python3-dev",
                    "postgresql-client", "mysql-client", "redis-tools",
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common"
                ],
                "setup_script": """
                    # Install Node.js
                    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                    apt-get install -y nodejs
                    
                    # Install Yarn and global packages
                    npm install -g yarn typescript eslint prettier
                    npm install -g @vue/cli create-react-app @angular/cli
                    
                    # Install Python packages
                    pip3 install --upgrade pip
                    pip3 install django flask fastapi sqlalchemy alembic
                    pip3 install requests beautifulsoup4 scrapy
                    pip3 install pytest black flake8
                    
                    # Create project directories
                    mkdir -p /home/ubuntu/{projects,databases}
                    chown ubuntu:ubuntu /home/ubuntu/{projects,databases}
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "data-science": {
                "name": "Data Science Environment",
                "description": "Python-based data science environment with Jupyter, pandas, and ML libraries",
                "base_image": "22.04",
                "packages": [
                    "python3", "python3-pip", "python3-venv", "python3-dev",
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common",
                    "libhdf5-dev", "libnetcdf-dev", "pkg-config"
                ],
                "setup_script": """
                    # Upgrade pip
                    pip3 install --upgrade pip
                    
                    # Install core data science packages
                    pip3 install numpy pandas matplotlib seaborn plotly
                    pip3 install scipy scikit-learn statsmodels
                    pip3 install jupyter jupyterlab notebook
                    pip3 install h5py tables xarray
                    
                    # Install ML frameworks
                    pip3 install tensorflow torch torchvision
                    pip3 install xgboost lightgbm catboost
                    
                    # Install additional tools
                    pip3 install pytest black flake8 mypy
                    pip3 install requests beautifulsoup4 openpyxl
                    
                    # Create project directories
                    mkdir -p /home/ubuntu/{projects,datasets,notebooks}
                    chown ubuntu:ubuntu /home/ubuntu/{projects,datasets,notebooks}
                    
                    # Configure Jupyter
                    sudo -u ubuntu jupyter notebook --generate-config
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            },
            
            "devops": {
                "name": "DevOps Environment",
                "description": "DevOps environment with Docker, Kubernetes tools, Terraform, and monitoring",
                "base_image": "22.04",
                "packages": [
                    "curl", "wget", "git", "vim", "htop", "tree", "unzip",
                    "build-essential", "software-properties-common", "apt-transport-https",
                    "ca-certificates", "gnupg", "lsb-release", "jq"
                ],
                "setup_script": """
                    # Install Docker
                    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                    apt-get update
                    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                    usermod -aG docker ubuntu
                    
                    # Install kubectl
                    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
                    
                    # Install Terraform
                    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
                    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
                    apt-get update && apt-get install -y terraform
                    
                    # Install Helm
                    curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | tee /usr/share/keyrings/helm.gpg > /dev/null
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list
                    apt-get update && apt-get install -y helm
                    
                    # Install AWS CLI
                    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                    unzip awscliv2.zip && ./aws/install && rm -rf aws awscliv2.zip
                    
                    # Create project directories
                    mkdir -p /home/ubuntu/{projects,infrastructure,configs}
                    chown ubuntu:ubuntu /home/ubuntu/{projects,infrastructure,configs}
                    
                    # Set up basic git config
                    sudo -u ubuntu git config --global init.defaultBranch main
                """
            }
        }
    
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all available templates"""
        return self.templates
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific template by ID"""
        return self.templates.get(template_id)
    
    def get_template_names(self) -> Dict[str, str]:
        """Get template IDs mapped to their display names"""
        return {template_id: template["name"] for template_id, template in self.templates.items()}
    
    def add_custom_template(self, template_id: str, template_config: Dict[str, Any]):
        """Add a custom template"""
        required_fields = ["name", "description", "base_image"]
        
        for field in required_fields:
            if field not in template_config:
                raise ValueError(f"Template missing required field: {field}")
        
        self.templates[template_id] = template_config
    
    def remove_template(self, template_id: str):
        """Remove a template"""
        if template_id in self.templates:
            del self.templates[template_id]
        else:
            raise ValueError(f"Template {template_id} not found")

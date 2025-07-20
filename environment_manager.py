"""
Environment Manager - Handles Multipass/LXD operations
"""

import json
import subprocess
import os
import re
from typing import Dict, List, Optional
from pathlib import Path


class EnvironmentManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "ubuntu-dev-manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.environments_file = self.config_dir / "environments.json"
        
    def _load_environments_config(self) -> Dict:
        """Load environment configurations from file"""
        if self.environments_file.exists():
            try:
                with open(self.environments_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_environments_config(self, config: Dict):
        """Save environment configurations to file"""
        try:
            with open(self.environments_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save environment config: {e}")
    
    def _run_command(self, cmd: List[str], capture_output=True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=capture_output, 
                text=True, 
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}\nError: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(f"Command not found: {cmd[0]}")
    
    def _check_backend_available(self, backend: str) -> bool:
        """Check if a backend is available"""
        try:
            if backend == "multipass":
                self._run_command(["multipass", "version"])
            elif backend == "lxd":
                self._run_command(["lxc", "version"])
            return True
        except RuntimeError:
            return False
    
    def list_environments(self) -> List[Dict]:
        """List all environments from both backends"""
        environments = []
        
        # Get Multipass instances
        if self._check_backend_available("multipass"):
            try:
                result = self._run_command(["multipass", "list", "--format", "json"])
                multipass_data = json.loads(result.stdout)
                
                for instance in multipass_data.get("list", []):
                    env = {
                        "name": instance["name"],
                        "status": instance["state"].title(),
                        "backend": "multipass",
                        "ip": instance.get("ipv4", ["Not available"])[0] if instance.get("ipv4") else "Not available",
                        "template": self._get_environment_template(instance["name"]),
                        "mounts": self._get_multipass_mounts(instance["name"])
                    }
                    environments.append(env)
                    
            except (RuntimeError, json.JSONDecodeError, KeyError):
                pass  # Skip if multipass is not available or fails
        
        # Get LXD containers
        if self._check_backend_available("lxd"):
            try:
                result = self._run_command(["lxc", "list", "--format", "json"])
                lxd_data = json.loads(result.stdout)
                
                for container in lxd_data:
                    status = container["status"].title()
                    if status == "Stopped":
                        status = "Stopped"
                    elif status == "Running":
                        status = "Running"
                    
                    # Get IP address
                    ip = "Not available"
                    if container["state"] and container["state"]["network"]:
                        for interface, data in container["state"]["network"].items():
                            if interface != "lo" and data["addresses"]:
                                for addr in data["addresses"]:
                                    if addr["family"] == "inet":
                                        ip = addr["address"]
                                        break
                                if ip != "Not available":
                                    break
                    
                    env = {
                        "name": container["name"],
                        "status": status,
                        "backend": "lxd",
                        "ip": ip,
                        "template": self._get_environment_template(container["name"]),
                        "mounts": self._get_lxd_mounts(container["name"])
                    }
                    environments.append(env)
                    
            except (RuntimeError, json.JSONDecodeError, KeyError):
                pass  # Skip if lxd is not available or fails
        
        return environments
    
    def _get_environment_template(self, name: str) -> str:
        """Get the template used for an environment"""
        config = self._load_environments_config()
        return config.get(name, {}).get("template", "Unknown")
    
    def _get_multipass_mounts(self, name: str) -> List[Dict]:
        """Get mount information for a Multipass instance"""
        try:
            result = self._run_command(["multipass", "info", name, "--format", "json"])
            info_data = json.loads(result.stdout)
            
            mounts = []
            instance_info = info_data.get("info", {}).get(name, {})
            mount_info = instance_info.get("mounts", {})
            
            for guest_path, mount_data in mount_info.items():
                mounts.append({
                    "host": mount_data.get("source_path", "Unknown"),
                    "guest": guest_path
                })
                
            return mounts
        except (RuntimeError, json.JSONDecodeError, KeyError):
            return []
    
    def _get_lxd_mounts(self, name: str) -> List[Dict]:
        """Get mount information for an LXD container"""
        try:
            result = self._run_command(["lxc", "config", "show", name])
            # Parse the YAML-like output to extract device mounts
            mounts = []
            
            # This is a simplified parser - in practice you might want to use PyYAML
            lines = result.stdout.split('\n')
            in_devices = False
            current_device = None
            
            for line in lines:
                if line.strip() == 'devices:':
                    in_devices = True
                    continue
                
                if in_devices:
                    if line.startswith('  ') and ':' in line and not line.startswith('    '):
                        current_device = line.strip().replace(':', '')
                        continue
                    
                    if line.startswith('    type: disk') and current_device:
                        # This is a disk device, likely a mount
                        continue
                    
                    if line.startswith('    source:') and current_device:
                        source = line.split('source:', 1)[1].strip()
                        # Look for the path in the next few lines
                        continue
                    
                    if line.startswith('    path:') and current_device:
                        path = line.split('path:', 1)[1].strip()
                        # We would need the source from above
                        continue
            
            return mounts
        except RuntimeError:
            return []
    
    def create_environment(self, config: Dict):
        """Create a new environment"""
        name = config["name"]
        backend = config["backend"]
        template_id = config["template"]
        mounts = config.get("mounts", [])
        resources = config.get("resources", {})
        
        if not name:
            raise ValueError("Environment name is required")
        
        if not self._check_backend_available(backend):
            raise RuntimeError(f"Backend {backend} is not available")
        
        # Get template configuration
        from templates import EnvironmentTemplates
        templates = EnvironmentTemplates()
        template = templates.get_template(template_id)
        
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        try:
            if backend == "multipass":
                self._create_multipass_environment(name, template, mounts, resources)
            elif backend == "lxd":
                self._create_lxd_environment(name, template, mounts, resources)
            else:
                raise ValueError(f"Unsupported backend: {backend}")
            
            # Save environment configuration
            env_config = self._load_environments_config()
            env_config[name] = {
                "template": template_id,
                "backend": backend,
                "created": True
            }
            self._save_environments_config(env_config)
            
        except Exception as e:
            raise RuntimeError(f"Failed to create environment: {e}")
    
    def _create_multipass_environment(self, name: str, template: Dict, mounts: List[Dict], resources: Dict):
        """Create a Multipass environment"""
        cmd = ["multipass", "launch"]
        
        # Add resource constraints
        if resources.get("cpus"):
            cmd.extend(["--cpus", str(resources["cpus"])])
        if resources.get("memory"):
            cmd.extend(["--memory", resources["memory"]])
        if resources.get("disk"):
            cmd.extend(["--disk", resources["disk"]])
        
        # Use the base image specified in template
        base_image = template.get("base_image", "22.04")
        cmd.extend([base_image, "--name", name])
        
        # Create the instance
        self._run_command(cmd)
        
        # Wait for it to be ready
        self._run_command(["multipass", "exec", name, "--", "cloud-init", "status", "--wait"])
        
        # Set up directory mounts
        for mount in mounts:
            mount_cmd = ["multipass", "mount", mount["host"], f"{name}:{mount['guest']}"]
            self._run_command(mount_cmd)
        
        # Install template packages and run setup script
        self._setup_environment(name, template, "multipass")
    
    def _create_lxd_environment(self, name: str, template: Dict, mounts: List[Dict], resources: Dict):
        """Create an LXD environment"""
        # Launch container
        base_image = template.get("base_image", "ubuntu:22.04")
        cmd = ["lxc", "launch", base_image, name]
        self._run_command(cmd)
        
        # Configure resources
        if resources.get("cpus"):
            self._run_command(["lxc", "config", "set", name, f"limits.cpu={resources['cpus']}"])
        if resources.get("memory"):
            self._run_command(["lxc", "config", "set", name, f"limits.memory={resources['memory']}"])
        
        # Wait for container to be ready
        self._run_command(["lxc", "exec", name, "--", "cloud-init", "status", "--wait"])
        
        # Set up directory mounts
        for i, mount in enumerate(mounts):
            device_name = f"mount{i}"
            self._run_command([
                "lxc", "config", "device", "add", name, device_name, "disk",
                f"source={mount['host']}", f"path={mount['guest']}"
            ])
        
        # Install template packages and run setup script
        self._setup_environment(name, template, "lxd")
    
    def _setup_environment(self, name: str, template: Dict, backend: str):
        """Set up the environment with template packages and configuration"""
        packages = template.get("packages", [])
        setup_script = template.get("setup_script", "")
        
        if backend == "multipass":
            exec_cmd = ["multipass", "exec", name, "--"]
        elif backend == "lxd":
            exec_cmd = ["lxc", "exec", name, "--"]
        else:
            raise ValueError(f"Unsupported backend: {backend}")
        
        # Update package list
        self._run_command(exec_cmd + ["apt", "update"])
        
        # Install packages
        if packages:
            install_cmd = exec_cmd + ["apt", "install", "-y"] + packages
            self._run_command(install_cmd)
        
        # Run setup script if provided
        if setup_script:
            script_lines = setup_script.strip().split('\n')
            for line in script_lines:
                if line.strip():
                    self._run_command(exec_cmd + ["bash", "-c", line.strip()])
    
    def start_environment(self, name: str):
        """Start an environment"""
        environments = self.list_environments()
        env = next((e for e in environments if e["name"] == name), None)
        
        if not env:
            raise RuntimeError(f"Environment '{name}' not found")
        
        if env["status"] == "Running":
            return  # Already running
        
        backend = env["backend"]
        
        try:
            if backend == "multipass":
                self._run_command(["multipass", "start", name])
            elif backend == "lxd":
                self._run_command(["lxc", "start", name])
        except RuntimeError as e:
            raise RuntimeError(f"Failed to start environment: {e}")
    
    def stop_environment(self, name: str):
        """Stop an environment"""
        environments = self.list_environments()
        env = next((e for e in environments if e["name"] == name), None)
        
        if not env:
            raise RuntimeError(f"Environment '{name}' not found")
        
        if env["status"] == "Stopped":
            return  # Already stopped
        
        backend = env["backend"]
        
        try:
            if backend == "multipass":
                self._run_command(["multipass", "stop", name])
            elif backend == "lxd":
                self._run_command(["lxc", "stop", name])
        except RuntimeError as e:
            raise RuntimeError(f"Failed to stop environment: {e}")
    
    def delete_environment(self, name: str):
        """Delete an environment"""
        environments = self.list_environments()
        env = next((e for e in environments if e["name"] == name), None)
        
        if not env:
            raise RuntimeError(f"Environment '{name}' not found")
        
        backend = env["backend"]
        
        try:
            if backend == "multipass":
                # Stop first if running
                if env["status"] == "Running":
                    self._run_command(["multipass", "stop", name])
                self._run_command(["multipass", "delete", name])
                self._run_command(["multipass", "purge"])
            elif backend == "lxd":
                # Stop first if running
                if env["status"] == "Running":
                    self._run_command(["lxc", "stop", name])
                self._run_command(["lxc", "delete", name])
            
            # Remove from configuration
            env_config = self._load_environments_config()
            if name in env_config:
                del env_config[name]
                self._save_environments_config(env_config)
                
        except RuntimeError as e:
            raise RuntimeError(f"Failed to delete environment: {e}")
    
    def open_shell(self, name: str):
        """Open a shell to an environment"""
        environments = self.list_environments()
        env = next((e for e in environments if e["name"] == name), None)
        
        if not env:
            raise RuntimeError(f"Environment '{name}' not found")
        
        if env["status"] != "Running":
            raise RuntimeError(f"Environment '{name}' is not running")
        
        backend = env["backend"]
        
        try:
            # Open in a new terminal window
            terminal_cmd = None
            
            # Try common terminal emulators
            terminals = [
                ["gnome-terminal", "--", "bash", "-c"],
                ["konsole", "-e", "bash", "-c"],
                ["xterm", "-e", "bash", "-c"],
                ["alacritty", "-e", "bash", "-c"],
                ["wezterm", "start", "bash", "-c"]
            ]
            
            for term_cmd in terminals:
                try:
                    # Test if terminal is available
                    subprocess.run([term_cmd[0], "--version"], 
                                   capture_output=True, check=True)
                    terminal_cmd = term_cmd
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not terminal_cmd:
                raise RuntimeError("No suitable terminal emulator found")
            
            if backend == "multipass":
                shell_cmd = f"multipass shell {name}"
            elif backend == "lxd":
                shell_cmd = f"lxc exec {name} -- /bin/bash"
            
            # Execute in background
            full_cmd = terminal_cmd + [f"{shell_cmd}; exec bash"]
            subprocess.Popen(full_cmd, start_new_session=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to open shell: {e}")
    
    def get_environment_info(self, name: str) -> Dict:
        """Get detailed information about an environment"""
        environments = self.list_environments()
        env = next((e for e in environments if e["name"] == name), None)
        
        if not env:
            raise RuntimeError(f"Environment '{name}' not found")
        
        backend = env["backend"]
        
        try:
            if backend == "multipass":
                result = self._run_command(["multipass", "info", name, "--format", "json"])
                info_data = json.loads(result.stdout)
                return info_data.get("info", {}).get(name, {})
            elif backend == "lxd":
                result = self._run_command(["lxc", "info", name])
                # Parse the output (simplified)
                return {"raw_info": result.stdout}
        except (RuntimeError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to get environment info: {e}")

#!/usr/bin/env python3
"""
Ubuntu Desktop Development Environment Manager
A GUI tool for managing isolated development environments using Multipass/LXD
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("PyQt5 not found. Please install it with: pip install PyQt5")
    sys.exit(1)

from environment_manager import EnvironmentManager
from templates import EnvironmentTemplates
from config_manager import ConfigManager


class DevEnvironmentGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.env_manager = EnvironmentManager()
        self.templates = EnvironmentTemplates()
        self.config = ConfigManager()
        
        self.setWindowTitle("Ubuntu Development Environment Manager")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon.fromTheme("applications-development"))
        
        self.init_ui()
        self.refresh_environments()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Environment list and controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Environment details and logs
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Menu bar
        self.create_menu_bar()
        
    def create_left_panel(self):
        """Create the left panel with environment list and controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Development Environments")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Environment list
        self.env_list = QListWidget()
        self.env_list.itemSelectionChanged.connect(self.on_environment_selected)
        layout.addWidget(self.env_list)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.create_btn = QPushButton("Create Environment")
        self.create_btn.clicked.connect(self.create_environment_dialog)
        self.create_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")
        button_layout.addWidget(self.create_btn)
        
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_environment)
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_environment)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.shell_btn = QPushButton("Open Shell")
        self.shell_btn.clicked.connect(self.open_shell)
        self.shell_btn.setEnabled(False)
        button_layout.addWidget(self.shell_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_environment)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return panel
        
    def create_right_panel(self):
        """Create the right panel with environment details and logs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Environment details
        details_group = QGroupBox("Environment Details")
        details_layout = QFormLayout(details_group)
        
        self.name_label = QLabel("-")
        self.status_label = QLabel("-")
        self.template_label = QLabel("-")
        self.ip_label = QLabel("-")
        self.mounts_label = QLabel("-")
        
        details_layout.addRow("Name:", self.name_label)
        details_layout.addRow("Status:", self.status_label)
        details_layout.addRow("Template:", self.template_label)
        details_layout.addRow("IP Address:", self.ip_label)
        details_layout.addRow("Mounts:", self.mounts_label)
        
        layout.addWidget(details_group)
        
        # Logs
        logs_group = QGroupBox("Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        logs_layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(self.clear_logs_btn)
        log_controls.addStretch()
        logs_layout.addLayout(log_controls)
        
        layout.addWidget(logs_group)
        
        return panel
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        refresh_action = QAction('Refresh', self)
        refresh_action.triggered.connect(self.refresh_environments)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def refresh_environments(self):
        """Refresh the list of environments"""
        self.log("Refreshing environment list...")
        try:
            environments = self.env_manager.list_environments()
            self.env_list.clear()
            
            for env in environments:
                item = QListWidgetItem(env['name'])
                item.setData(Qt.UserRole, env)
                
                # Set icon based on status
                if env['status'] == 'Running':
                    item.setIcon(QIcon.fromTheme("media-playback-start"))
                elif env['status'] == 'Stopped':
                    item.setIcon(QIcon.fromTheme("media-playback-pause"))
                else:
                    item.setIcon(QIcon.fromTheme("dialog-question"))
                    
                self.env_list.addItem(item)
                
            self.log(f"Found {len(environments)} environments")
            
        except Exception as e:
            self.log(f"Error refreshing environments: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to refresh environments:\n{str(e)}")
            
    def on_environment_selected(self):
        """Handle environment selection"""
        current_item = self.env_list.currentItem()
        if current_item:
            env_data = current_item.data(Qt.UserRole)
            self.update_environment_details(env_data)
            
            # Enable/disable buttons based on status
            is_running = env_data['status'] == 'Running'
            is_stopped = env_data['status'] == 'Stopped'
            
            self.start_btn.setEnabled(is_stopped)
            self.stop_btn.setEnabled(is_running)
            self.shell_btn.setEnabled(is_running)
            self.delete_btn.setEnabled(is_stopped)
        else:
            self.clear_environment_details()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.shell_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            
    def update_environment_details(self, env_data):
        """Update the environment details panel"""
        self.name_label.setText(env_data['name'])
        self.status_label.setText(env_data['status'])
        self.template_label.setText(env_data.get('template', 'Unknown'))
        self.ip_label.setText(env_data.get('ip', 'Not available'))
        
        mounts = env_data.get('mounts', [])
        if mounts:
            mounts_text = '\n'.join([f"{m['host']} → {m['guest']}" for m in mounts])
        else:
            mounts_text = "None"
        self.mounts_label.setText(mounts_text)
        
    def clear_environment_details(self):
        """Clear the environment details panel"""
        for label in [self.name_label, self.status_label, self.template_label, 
                     self.ip_label, self.mounts_label]:
            label.setText("-")
            
    def create_environment_dialog(self):
        """Open the create environment dialog"""
        dialog = CreateEnvironmentDialog(self.templates, self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            env_config = dialog.get_config()
            self.create_environment(env_config)
            
    def create_environment(self, config):
        """Create a new environment"""
        self.log(f"Creating environment '{config['name']}'...")
        self.create_btn.setEnabled(False)
        
        def create_worker():
            try:
                self.env_manager.create_environment(config)
                QTimer.singleShot(0, lambda: self.on_environment_created(config['name']))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.on_environment_error(f"Creation failed: {str(e)}"))
                
        threading.Thread(target=create_worker, daemon=True).start()
        
    def on_environment_created(self, name):
        """Handle successful environment creation"""
        self.log(f"Environment '{name}' created successfully")
        self.create_btn.setEnabled(True)
        self.refresh_environments()
        
    def on_environment_error(self, error_msg):
        """Handle environment operation error"""
        self.log(error_msg)
        self.create_btn.setEnabled(True)
        QMessageBox.warning(self, "Error", error_msg)
        
    def start_environment(self):
        """Start the selected environment"""
        current_item = self.env_list.currentItem()
        if current_item:
            env_data = current_item.data(Qt.UserRole)
            self.log(f"Starting environment '{env_data['name']}'...")
            
            def start_worker():
                try:
                    self.env_manager.start_environment(env_data['name'])
                    QTimer.singleShot(0, lambda: self.on_environment_started(env_data['name']))
                except Exception as e:
                    QTimer.singleShot(0, lambda: self.on_environment_error(f"Start failed: {str(e)}"))
                    
            threading.Thread(target=start_worker, daemon=True).start()
            
    def on_environment_started(self, name):
        """Handle successful environment start"""
        self.log(f"Environment '{name}' started successfully")
        self.refresh_environments()
        
    def stop_environment(self):
        """Stop the selected environment"""
        current_item = self.env_list.currentItem()
        if current_item:
            env_data = current_item.data(Qt.UserRole)
            self.log(f"Stopping environment '{env_data['name']}'...")
            
            def stop_worker():
                try:
                    self.env_manager.stop_environment(env_data['name'])
                    QTimer.singleShot(0, lambda: self.on_environment_stopped(env_data['name']))
                except Exception as e:
                    QTimer.singleShot(0, lambda: self.on_environment_error(f"Stop failed: {str(e)}"))
                    
            threading.Thread(target=stop_worker, daemon=True).start()
            
    def on_environment_stopped(self, name):
        """Handle successful environment stop"""
        self.log(f"Environment '{name}' stopped successfully")
        self.refresh_environments()
        
    def delete_environment(self):
        """Delete the selected environment"""
        current_item = self.env_list.currentItem()
        if current_item:
            env_data = current_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, 
                "Confirm Deletion", 
                f"Are you sure you want to delete environment '{env_data['name']}'?\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.log(f"Deleting environment '{env_data['name']}'...")
                
                def delete_worker():
                    try:
                        self.env_manager.delete_environment(env_data['name'])
                        QTimer.singleShot(0, lambda: self.on_environment_deleted(env_data['name']))
                    except Exception as e:
                        QTimer.singleShot(0, lambda: self.on_environment_error(f"Delete failed: {str(e)}"))
                        
                threading.Thread(target=delete_worker, daemon=True).start()
                
    def on_environment_deleted(self, name):
        """Handle successful environment deletion"""
        self.log(f"Environment '{name}' deleted successfully")
        self.refresh_environments()
        
    def open_shell(self):
        """Open a shell to the selected environment"""
        current_item = self.env_list.currentItem()
        if current_item:
            env_data = current_item.data(Qt.UserRole)
            try:
                self.env_manager.open_shell(env_data['name'])
                self.log(f"Opened shell for environment '{env_data['name']}'")
            except Exception as e:
                self.log(f"Failed to open shell: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to open shell:\n{str(e)}")
                
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self.config, self)
        dialog.exec_()
        
    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About Ubuntu Development Environment Manager",
            """
            <h3>Ubuntu Development Environment Manager</h3>
            <p>A GUI tool for managing isolated development environments using Multipass/LXD</p>
            <p><b>Version:</b> 1.0.0</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Create isolated development environments</li>
                <li>Pre-configured templates for popular languages</li>
                <li>Host directory mounting</li>
                <li>Easy environment management</li>
            </ul>
            <p><b>Built for:</b> Ubuntu Desktop Developers</p>
            """
        )
        
    def log(self, message):
        """Add a message to the log"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        self.statusBar().showMessage(message)
        
    def clear_logs(self):
        """Clear the log text"""
        self.log_text.clear()


class CreateEnvironmentDialog(QDialog):
    def __init__(self, templates, config, parent=None):
        super().__init__(parent)
        self.templates = templates
        self.config = config
        self.setWindowTitle("Create New Environment")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter environment name")
        basic_layout.addRow("Name:", self.name_edit)
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["multipass", "lxd"])
        self.backend_combo.currentTextChanged.connect(self.on_backend_changed)
        basic_layout.addRow("Backend:", self.backend_combo)
        
        layout.addWidget(basic_group)
        
        # Template selection
        template_group = QGroupBox("Template")
        template_layout = QVBoxLayout(template_group)
        
        self.template_combo = QComboBox()
        self.populate_templates()
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_layout.addWidget(self.template_combo)
        
        self.template_desc = QLabel()
        self.template_desc.setWordWrap(True)
        self.template_desc.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        template_layout.addWidget(self.template_desc)
        
        layout.addWidget(template_group)
        
        # Directory mounts
        mounts_group = QGroupBox("Directory Mounts")
        mounts_layout = QVBoxLayout(mounts_group)
        
        self.mounts_list = QListWidget()
        mounts_layout.addWidget(self.mounts_list)
        
        mount_controls = QHBoxLayout()
        self.add_mount_btn = QPushButton("Add Mount")
        self.add_mount_btn.clicked.connect(self.add_mount)
        mount_controls.addWidget(self.add_mount_btn)
        
        self.remove_mount_btn = QPushButton("Remove Mount")
        self.remove_mount_btn.clicked.connect(self.remove_mount)
        mount_controls.addWidget(self.remove_mount_btn)
        
        mount_controls.addStretch()
        mounts_layout.addLayout(mount_controls)
        
        layout.addWidget(mounts_group)
        
        # Resource settings
        resources_group = QGroupBox("Resources")
        resources_layout = QFormLayout(resources_group)
        
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 16)
        self.cpu_spin.setValue(2)
        resources_layout.addRow("CPUs:", self.cpu_spin)
        
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(512, 16384)
        self.memory_spin.setValue(2048)
        self.memory_spin.setSuffix(" MB")
        resources_layout.addRow("Memory:", self.memory_spin)
        
        self.disk_spin = QSpinBox()
        self.disk_spin.setRange(5, 100)
        self.disk_spin.setValue(10)
        self.disk_spin.setSuffix(" GB")
        resources_layout.addRow("Disk:", self.disk_spin)
        
        layout.addWidget(resources_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create")
        create_btn.setDefault(True)
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; }")
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        # Set initial template description
        self.on_template_changed()
        
    def populate_templates(self):
        """Populate the template combo box"""
        templates = self.templates.get_all_templates()
        for template_id, template in templates.items():
            self.template_combo.addItem(template['name'], template_id)
            
    def on_backend_changed(self):
        """Handle backend selection change"""
        backend = self.backend_combo.currentText()
        # Update available templates or settings based on backend
        pass
        
    def on_template_changed(self):
        """Handle template selection change"""
        template_id = self.template_combo.currentData()
        if template_id:
            template = self.templates.get_template(template_id)
            if template:
                self.template_desc.setText(template.get('description', ''))
                
    def add_mount(self):
        """Add a directory mount"""
        dialog = AddMountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            host_path, guest_path = dialog.get_paths()
            mount_text = f"{host_path} → {guest_path}"
            
            item = QListWidgetItem(mount_text)
            item.setData(Qt.UserRole, {'host': host_path, 'guest': guest_path})
            self.mounts_list.addItem(item)
            
    def remove_mount(self):
        """Remove selected directory mount"""
        current_row = self.mounts_list.currentRow()
        if current_row >= 0:
            self.mounts_list.takeItem(current_row)
            
    def get_config(self):
        """Get the environment configuration"""
        mounts = []
        for i in range(self.mounts_list.count()):
            item = self.mounts_list.item(i)
            mounts.append(item.data(Qt.UserRole))
            
        return {
            'name': self.name_edit.text().strip(),
            'backend': self.backend_combo.currentText(),
            'template': self.template_combo.currentData(),
            'mounts': mounts,
            'resources': {
                'cpus': self.cpu_spin.value(),
                'memory': f"{self.memory_spin.value()}M",
                'disk': f"{self.disk_spin.value()}G"
            }
        }


class AddMountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Directory Mount")
        self.setModal(True)
        self.resize(500, 150)
        self.init_ui()
        
    def init_ui(self):
        layout = QFormLayout(self)
        
        # Host path
        host_layout = QHBoxLayout()
        self.host_edit = QLineEdit()
        host_layout.addWidget(self.host_edit)
        
        host_browse_btn = QPushButton("Browse")
        host_browse_btn.clicked.connect(self.browse_host_path)
        host_layout.addWidget(host_browse_btn)
        
        layout.addRow("Host Path:", host_layout)
        
        # Guest path
        self.guest_edit = QLineEdit()
        self.guest_edit.setPlaceholderText("/home/ubuntu/project")
        layout.addRow("Guest Path:", self.guest_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addRow(button_layout)
        
    def browse_host_path(self):
        """Browse for host directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Host Directory")
        if path:
            self.host_edit.setText(path)
            
            # Auto-suggest guest path
            if not self.guest_edit.text():
                dir_name = os.path.basename(path)
                self.guest_edit.setText(f"/home/ubuntu/{dir_name}")
                
    def get_paths(self):
        """Get the host and guest paths"""
        return self.host_edit.text().strip(), self.guest_edit.text().strip()


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Default backend
        backend_group = QGroupBox("Default Backend")
        backend_layout = QVBoxLayout(backend_group)
        
        self.multipass_radio = QRadioButton("Multipass")
        self.lxd_radio = QRadioButton("LXD")
        
        default_backend = self.config.get('default_backend', 'multipass')
        if default_backend == 'multipass':
            self.multipass_radio.setChecked(True)
        else:
            self.lxd_radio.setChecked(True)
            
        backend_layout.addWidget(self.multipass_radio)
        backend_layout.addWidget(self.lxd_radio)
        layout.addWidget(backend_group)
        
        # Default resources
        resources_group = QGroupBox("Default Resources")
        resources_layout = QFormLayout(resources_group)
        
        self.default_cpu_spin = QSpinBox()
        self.default_cpu_spin.setRange(1, 16)
        self.default_cpu_spin.setValue(self.config.get('default_cpus', 2))
        resources_layout.addRow("CPUs:", self.default_cpu_spin)
        
        self.default_memory_spin = QSpinBox()
        self.default_memory_spin.setRange(512, 16384)
        self.default_memory_spin.setValue(self.config.get('default_memory', 2048))
        self.default_memory_spin.setSuffix(" MB")
        resources_layout.addRow("Memory:", self.default_memory_spin)
        
        layout.addWidget(resources_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def save_settings(self):
        """Save the settings"""
        settings = {
            'default_backend': 'multipass' if self.multipass_radio.isChecked() else 'lxd',
            'default_cpus': self.default_cpu_spin.value(),
            'default_memory': self.default_memory_spin.value()
        }
        
        self.config.update(settings)
        self.config.save()
        self.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Ubuntu Dev Environment Manager")
    app.setOrganizationName("Canonical")
    
    # Set application icon
    app.setWindowIcon(QIcon.fromTheme("applications-development"))
    
    window = DevEnvironmentGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Setup script for Ubuntu Development Environment Manager
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ubuntu-dev-manager",
    version="1.0.0",
    author="Ubuntu Developer",
    author_email="dev@canonical.com",
    description="A GUI tool for managing isolated development environments using Multipass/LXD",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/canonical/ubuntu-dev-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GPL License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ubuntu-dev-manager=main:main",
        ],
        "gui_scripts": [
            "ubuntu-dev-manager-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
)

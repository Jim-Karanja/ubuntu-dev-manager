# Contributing to Ubuntu Development Environment Manager

Thank you for your interest in contributing to the Ubuntu Development Environment Manager! This project aims to make Ubuntu the best platform for developers by providing an intuitive GUI for managing isolated development environments.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ubuntu-dev-manager.git
   cd ubuntu-dev-manager
   ```
3. **Set up the development environment**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and modular

### Testing
- Test your changes with both Multipass and LXD backends
- Ensure the GUI remains responsive during long operations
- Test environment creation, management, and deletion
- Verify directory mounting works correctly

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 50 characters
- Add more details in the body if needed

Example:
```
Add Rust development template

- Include rustc, cargo, and rust-analyzer
- Set up project directory structure  
- Configure PATH for cargo binaries
```

## Types of Contributions

### Environment Templates
We welcome new environment templates! Each template should:
- Include commonly used packages for the language/framework
- Set up a reasonable directory structure
- Configure environment variables
- Include development tools (linters, formatters, etc.)

### Bug Fixes
- Check existing issues before creating new ones
- Include steps to reproduce the bug
- Test your fix thoroughly

### Features
- Discuss new features in issues before implementing
- Keep the UI simple and intuitive
- Ensure features work with both backends

### Documentation
- Keep README.md up to date
- Add inline code documentation
- Update installation instructions if needed

## Submitting Changes

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test them

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

## Pull Request Guidelines

- Provide a clear description of what your PR does
- Include screenshots for UI changes
- Test instructions for reviewers
- Reference any related issues

## Code Review Process

- All submissions require review before merging
- Reviewers may request changes
- Address feedback promptly
- Maintain a respectful tone in discussions

## Community

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Focus on constructive feedback

## Questions?

- Open an issue for bugs or feature requests
- Use discussions for general questions
- Tag maintainers for urgent issues

Thank you for contributing to making Ubuntu the best development platform!

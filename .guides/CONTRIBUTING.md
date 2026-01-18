# Contributing to Project Eirene

Thank you for your interest in contributing to Project Eirene! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/eirene.git
   cd eirene
   ```

2. **Set up development environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style and patterns
   - Add tests for new functionality

3. **Run tests**
   ```bash
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Write docstrings for all classes and functions
- Keep functions focused and single-purpose

## Testing Guidelines

- Write unit tests for all new functionality
- Aim for high test coverage (>80%)
- Use pytest fixtures for common test setup
- Mock external API calls in tests

## Commit Message Format

Use conventional commits format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update README.md if adding new functionality
5. Request review from maintainers

## Questions?

Open an issue for questions or discussions about contributions.

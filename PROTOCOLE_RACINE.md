# Fluxgym-coach Development Protocol

> **Note**: This document is also available in [French](PROTOCOLE_RACINE.fr.md).

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Table of Contents
1. [Communication](#1-communication)
2. [Technical Standards](#2-technical-standards)
3. [Version Control](#3-version-control)
4. [Development Workflow](#4-development-workflow)
5. [Code Quality](#5-code-quality)
6. [Documentation](#6-documentation)
7. [Security](#7-security)
8. [Project Specifics](#8-project-specifics)

## 1. Communication

### General Principles
- **Language**: English (except for code and technical identifiers)
- **Style**: Professional yet approachable
- **Update Frequency**: Continuous, throughout development
- **Time Zone**: UTC+1 (Paris) is the reference timezone

### Recommended Tools
- **Task Tracking**: [GitHub Issues](https://github.com/Nehwon/fluxgym-coach/issues)
- **Code Review**: GitHub Pull Requests
- **Documentation**: Markdown in repository
- **Communication**: Asynchronous first, with clear documentation

### Communication Rules
- Always provide context in issue descriptions
- Reference related issues/PRs using `#issue_number`
- Document important decisions in `DECISIONS.md`
- Keep discussions focused and actionable
- Use clear, descriptive titles for issues and PRs

## 2. Technical Standards

### Core Technologies
- **Python**: 3.8+
- **Image Processing**: Pillow, OpenCV
- **API**: REST with FastAPI
- **Caching**: Custom implementation with file-based storage

### Development Environment
- **Python Version**: 3.8+ (see `.python-version`)
- **Package Management**: `pip` with `requirements.txt` and `setup.py`
- **Virtual Environment**: Recommended (venv, pipenv, or conda)
- **Linting**: flake8, black, mypy
- **Testing**: pytest with coverage

### Dependencies
- Keep dependencies to a minimum
- Document all dependencies in `requirements.txt`
- Pin production dependencies in `setup.py`
- Use `requirements-dev.txt` for development dependencies

## 3. Version Control

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features and enhancements
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

### Commit Guidelines
- Follow [Conventional Commits](https://www.conventionalcommits.org/)
- Use the present tense ("Add feature" not "Added feature")
- Keep commits atomic and focused
- Reference issues in commit messages (e.g., `#123`)

### Pull Requests
- Keep PRs small and focused
- Include relevant tests
- Update documentation as needed
- Request reviews from at least one maintainer
- All tests must pass before merging

## 4. Development Workflow

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'feat: add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Review Process
1. Create a draft PR early for feedback
2. Request reviews from relevant team members
3. Address all review comments
4. Ensure CI checks pass
5. Get at least one approval before merging

## 5. Code Quality

### Testing
- Write unit tests for all new code
- Aim for at least 80% test coverage
- Use fixtures and parametrized tests when appropriate
- Run tests locally before pushing

### Linting and Formatting
- Use `black` for code formatting
- Run `flake8` for static analysis
- Use `mypy` for type checking
- Pre-commit hooks are recommended

### Performance
- Profile code before optimizing
- Document performance considerations
- Use appropriate data structures
- Consider memory usage for large image processing

## 6. Documentation

### Code Documentation
- Follow Google-style docstrings
- Document all public APIs
- Include type hints for all function signatures
- Document exceptions that may be raised

### Project Documentation
- Keep `README.md` up to date
- Document architecture decisions in `DECISIONS.md`
- Update `CHANGELOG.md` for each release
- Document environment variables in `.env.example`

## 7. Security

### General Principles
- Never commit sensitive data
- Use environment variables for configuration
- Keep dependencies up to date
- Follow the principle of least privilege

### Authentication
- Use secure token-based authentication
- Implement proper session management
- Validate all user inputs
- Sanitize outputs to prevent XSS

### Dependencies
- Regularly audit dependencies for vulnerabilities
- Use Dependabot or similar tools
- Pin all dependencies to specific versions
- Document security-related dependencies

## 8. Project Specifics

### Image Processing
- Support common image formats (PNG, JPEG, WEBP)
- Handle large images efficiently
- Implement proper error handling for malformed images
- Document memory requirements

### Caching
- Use consistent cache keys
- Implement cache invalidation
- Document cache behavior
- Consider cache size limits

### Error Handling
- Use appropriate exception types
- Provide helpful error messages
- Log errors with sufficient context
- Implement graceful degradation

## 3. Version Control

### Basic Principles
- **Git** as version control system
- **Branching Strategy**: Git Flow
- **Commit Messages**: Follow Conventional Commits specification

### Branch Naming
- `feature/`: New features
- `bugfix/`: Bug fixes
- `hotfix/`: Critical production fixes
- `release/`: Release preparation

## 4. Docker and Containerization

### Container Standards
- Use official images when possible
- Multi-stage builds for production
- Keep images small and secure

### Docker Compose
- Use for local development
- Document all services in `docker-compose.yml`
- Include health checks

## 5. Development Best Practices

### Code Style
- Follow language-specific style guides
- Use linters and formatters
- Document complex logic

### Testing
- Write tests for new features
- Maintain test coverage
- Include integration and unit tests

## 6. Documentation

### Code Documentation
- Document all public APIs
- Include examples in documentation
- Keep documentation up-to-date

### Project Documentation
- Maintain `README.md` with setup instructions
- Document architecture decisions
- Keep changelog updated

## 7. Troubleshooting

### Common Issues
1. **Docker issues**: Check logs with `docker-compose logs`
2. **Dependency errors**: Verify versions with `poetry check`
3. **Configuration issues**: Check config files and environment variables

### Logging
- Use Python's `logging` module
- Include appropriate log levels
- Log to both console and file in production

## 8. Project Specifics

### Batch Processing Guidelines

#### Image Batch Processing
- **Order Preservation**: Always maintain the original order of input images in the results
- **Error Handling**: Handle individual image failures gracefully without failing the entire batch
- **Performance**: Process images in batches when possible, with a fallback to individual processing
- **Logging**: Include detailed logging for batch operations to facilitate debugging

#### Cache Management
- **Cache Keys**: Generate consistent cache keys using file hashes and processing parameters
- **Cache Invalidation**: Implement proper cache invalidation when processing parameters change
- **Cache Persistence**: Support both in-memory (session) and on-disk caching
- **Cache Verification**: Always verify cached files exist before using them

### Code Organization
- Keep batch processing logic separate from individual image processing
- Use clear naming conventions for batch-related functions and variables
- Document batch size limitations and performance considerations

### Repository Structure
- `src/`: Source code
  - `fluxgym_coach/`: Main package
    - `image_enhancement.py`: Core image processing and batch operations
    - `image_cache.py`: Cache management implementation
    - `utils/`: Utility modules
- `tests/`: Test files
  - `test_batch_processing.py`: Tests for batch operations
  - `test_image_cache.py`: Tests for cache functionality
- `docs/`: Documentation
  - `PROJET.md`: Current project plan and task tracking
  - `PROTOCOLE_RACINE.md`: Development protocol (this file)
- `scripts/`: Utility scripts
  - `test_*.py`: Test scripts for specific functionality

### Development Workflow
1. Create a feature branch
2. Develop and test locally
3. Open a pull request
4. Address review comments
5. Merge after approval

### Deployment
- Automated deployment with CI/CD
- Blue-green deployment strategy
- Rollback plan in place

---
*© 2024 Nehwon - All Rights Reserved*

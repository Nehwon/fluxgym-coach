# Fluxgym-coach Development Protocol

## Table of Contents
1. [Communication](#1-communication)
2. [Technical Standards](#2-technical-standards)
3. [Version Control](#3-version-control)
4. [Docker and Containerization](#4-docker-and-containerization)
5. [Development Best Practices](#5-development-best-practices)
6. [Documentation](#6-documentation)
7. [Troubleshooting](#7-troubleshooting)
8. [Project Specifics](#8-project-specifics)

## 1. Communication

### General Principles
- **Language**: English (except for code and technical identifiers)
- **Style**: Professional yet casual
- **Update Frequency**: Continuous, throughout development

### Recommended Tools
- Task Tracking: Gitea Issues or equivalent
- Asynchronous Communication: Email or team messaging tool
- Meetings: Shared calendar with predefined agenda

### Communication Rules
- Always mention project context
- Use clear references to tickets or issues
- Document important decisions in `DECISIONS.md`

## 2. Technical Standards

### Languages and Frameworks
- **Python**: PEP 8, static typing with mypy
- **JavaScript/TypeScript**: ESLint, Prettier
- **Other Languages**: Follow community standards

### Code Quality
- Unit tests with minimum 80% coverage
- Mandatory code review before merging (Pull Request)
- Continuous integration with test and linting verification

### Security
- Never store sensitive data in plain text in code
- Use environment variables for sensitive configurations
- Regularly update dependencies to fix known vulnerabilities

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

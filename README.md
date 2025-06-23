# Fluxgym-coach

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-100%25-success)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/Nehwon/fluxgym-coach/releases/tag/v0.1.0)

Image dataset preparation assistant for Fluxgym

## 📋 Description

Fluxgym-coach is a powerful tool designed to facilitate the preparation and optimization of image datasets for Fluxgym. It automates common image processing tasks, offering advanced enhancement features, cache management, and batch processing capabilities.

With its intelligent caching system, Fluxgym-coach optimizes performance by avoiding unnecessary reprocessing, while providing great flexibility through its comprehensive command-line interface.

## ✨ Key Features

### 🚀 Image Enhancement
- **Batch Processing**: Efficiently process multiple images in a single operation
- **Intelligent Upscaling**: Increase resolution up to 4x
- **Automatic Colorization**: Detect and colorize black and white images
- **N/B Detection**: Intelligent grayscale image identification
- **Format Conversion**: Support for PNG, JPG, WebP, and more
- **Proportional Resizing**: Maintain aspect ratios

### ⚡ Performance Optimization
- **Smart Caching System**: Avoids unnecessary reprocessing
  - File fingerprinting with `xxhash`
  - Parameter-aware cache keys
  - Automatic cleanup of invalid entries
  - Persistent disk cache between sessions
  - Cache usage statistics

### 🛠️ Command Line Interface
- Comprehensive cache control options
- Verbose mode for debugging
- Robust error handling with clear messages
- Progress bar for long-running operations

## 📦 Requirements

### System
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Core Dependencies
- `Pillow`: Image processing
- `numpy`: Numerical computations
- `requests`: HTTP requests
- `python-multipart`: File uploads
- `xxhash`: Fast fingerprinting

### Development
- `pytest`: Test execution
- `black`: Code formatting
- `mypy`: Type checking
- `pytest-cov`: Test coverage
- `pytest-httpx`: HTTP request mocking for tests
- `codecov`: Code coverage reporting

> **Note**: For image enhancement, a running Stable Diffusion WebUI Forge server is required.

## 🧪 Running Tests

### Unit Tests

To run the test suite:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=fluxgym_coach --cov-report=term-missing

# Run type checking
mypy .
```

### Integration Tests

Integration tests require a mock Stable Diffusion API server. The test suite includes mocks for the API responses.

```bash
# Run all tests including integration tests
pytest tests/

# Run only integration tests
pytest tests/integration/
```

## 🔄 Continuous Integration

The project uses GitHub Actions for CI/CD. The workflow includes:

- Running tests on Python 3.9, 3.10, and 3.11
- Code coverage reporting
- Linting with flake8
- Type checking with mypy

The CI pipeline runs on every push to main/master/develop branches and on pull requests.

### Code Coverage

Code coverage is tracked and reported to Codecov. The build will fail if coverage drops below 80%.

To view coverage reports locally:

```bash
# Generate HTML coverage report
pytest --cov=fluxgym_coach --cov-report=html

# Open the report in your browser
xdg-open htmlcov/index.html  # Linux
# or
open htmlcov/index.html      # macOS
# or
start htmlcov/index.html     # Windows
```

## 🚀 Installation

### Prerequisites

- Stable Diffusion WebUI Forge must be installed and running for image enhancement
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone git@github.com:Nehwon/fluxgym-coach.git
   cd fluxgym-coach
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## 🛠️ Usage

### Basic Command

```bash
fluxgym-coach process --input path/to/input --output path/to/output
```

### Cache Options

The cache system can be controlled with the following options:

- `--no-cache`: Disable the cache completely
- `--force-reprocess`: Force reprocessing of all images
- `--cache-dir PATH`: Specify a custom cache directory
- `--clean-cache`: Clean the cache before execution
- `--verbose`: Enable detailed logging

## 🤝 Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

2. Run tests before committing:
   ```bash
   pytest
   mypy .
   black .
   flake8
   ```

3. The CI pipeline will run additional checks on your pull request.

## 📝 Development Protocol

Please refer to [PROTOCOL.md](PROTOCOL.md) for our development guidelines and contribution process.

## 📄 License

This project is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for details.

---
*© 2024 Nehwon - All Rights Reserved*

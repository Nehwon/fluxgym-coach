# Fluxgym-coach

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-100%25-success)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-0.2.1-blue)](https://github.com/Nehwon/fluxgym-coach/releases/tag/v0.2.1)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/Nehwon/fluxgym-coach/tree/main/docs)

Image dataset preparation and enhancement tool for Fluxgym with AI-powered upscaling and batch processing.

## 🌍 Available Documentation

- [English Documentation](README.en.md)
- [Documentation en français](README.fr.md)
- [Changelog](CHANGELOG.md) / [Journal des modifications](CHANGELOG.fr.md)
- [Project Status](PROJECT_STATUS.md) / [État du Projet](ETAT_DU_PROJET.md)
- [Development Protocol](PROTOCOLE_RACINE.md) / [Protocole de Développement](PROTOCOLE_RACINE.fr.md)

## 🚀 Features

- **AI-Powered Image Enhancement**
  - High-quality upscaling using Stable Diffusion Forge
  - Batch processing for multiple images
  - Automatic black & white detection and colorization
  - Smart caching system for improved performance

- **Advanced Processing**
  - Support for multiple image formats (PNG, JPEG, WEBP)
  - Configurable upscaling parameters
  - Granular error handling
  - Detailed progress logging

- **Developer Friendly**
  - Type hints throughout the codebase
  - Comprehensive test suite
  - Clean and consistent code style
  - Detailed API documentation

## 📦 Prerequisites

- Python 3.8 or higher
- Stable Diffusion WebUI Forge server (for image enhancement)
- Required Python packages (see `setup.py` for complete list):
  - `requests`: For HTTP requests
  - `Pillow`: For image processing
  - `python-multipart`: For file uploads
  - `xxhash`: For fast file fingerprinting
  - `tqdm`: For progress bars

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Nehwon/fluxgym-coach.git
cd fluxgym-coach

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

## 🧪 Running Tests

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

## 📚 Documentation

### Project Structure

```
fluxgym-coach/
├── docs/                    # Documentation files
│   ├── releases/           # Release notes
│   └── image_enhancement.md # Module documentation
├── fluxgym_coach/          # Main package
│   ├── __init__.py
│   ├── image_enhancement.py # Core enhancement logic
│   └── utils/              # Utility modules
├── tests/                  # Test files
├── CHANGELOG.md            # English changelog
├── CHANGELOG.fr.md         # French changelog
├── README.md               # This file
└── setup.py                # Package configuration
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contribution Guidelines](PROTOCOLE_RACINE.md#contribution-guidelines) before submitting pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

*© 2024 Fluxgym Team - All Rights Reserved*
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

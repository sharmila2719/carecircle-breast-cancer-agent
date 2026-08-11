# Contributing to CareCircle

Thank you for your interest in contributing to CareCircle! This project aims to improve breast cancer early detection through AI-powered screening coordination.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/carecircle-breast-cancer-agent.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r requirements.txt && pip install -e ".[dev]"`
5. Create a branch: `git checkout -b feature/your-feature`

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Maximum line length: 100 characters
- Format with `black`: `black src/ tests/`
- Lint with `ruff`: `ruff check src/ tests/`

### Testing
- Write tests for new features
- Run tests: `pytest tests/ -v`
- Maintain test coverage above 80%

### Commit Messages
- Use clear, descriptive commit messages
- Format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore

## Areas for Contribution

- Adding new screening tools
- Improving risk assessment models
- Multi-language support for patient education
- Integration with EHR systems
- Accessibility improvements
- Documentation improvements

## Code of Conduct

Be respectful, inclusive, and constructive. This project serves a healthcare purpose, and we maintain high standards for accuracy and empathy.

## Questions?

Open an issue or reach out to the maintainers.

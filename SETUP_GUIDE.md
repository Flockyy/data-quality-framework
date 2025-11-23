# UV and Modern Tooling Setup Guide

This project uses modern Python development tools for improved performance and developer experience.

## 🚀 Quick Start

### 1. Install UV (Fast Python Package Installer)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (pip):**
```bash
pip install uv
```

### 2. Install Project Dependencies

```bash
# Install the package in development mode with all dev dependencies
uv pip install -e ".[dev]"
```

### 3. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

## 🛠️ Development Tools

### Ruff - Ultra-Fast Linter and Formatter

Ruff replaces multiple tools (Black, Flake8, isort) with a single, blazing-fast tool written in Rust.

**Check code:**
```bash
ruff check dqf tests examples
```

**Auto-fix issues:**
```bash
ruff check --fix dqf tests examples
```

**Format code:**
```bash
ruff format dqf tests examples
```

**Check format (CI):**
```bash
ruff format --check dqf tests examples
```

### Pre-commit - Automated Code Quality Checks

Pre-commit runs checks automatically before each commit.

**Manual run:**
```bash
pre-commit run --all-files
```

**Update hooks:**
```bash
pre-commit autoupdate
```

**Skip hooks (when needed):**
```bash
git commit --no-verify
```

### Makefile Commands

We provide convenient make commands for common tasks:

```bash
# Show all available commands
make help

# Install dependencies
make install          # Production dependencies
make install-dev      # Development dependencies

# Set up development environment
make dev-setup        # Install dev deps + pre-commit hooks

# Code quality
make lint             # Run ruff linter
make lint-fix         # Auto-fix linting issues
make format           # Format code with ruff
make format-check     # Check if code is formatted
make typecheck        # Run mypy type checker
make security         # Run bandit security scanner

# Testing
make test             # Run tests
make test-cov         # Run tests with coverage report
make test-parallel    # Run tests in parallel

# Combined checks (like CI)
make check            # Run lint + format-check + typecheck + test

# Cleanup
make clean            # Remove build artifacts
```

## 📦 Why UV?

UV is 10-100x faster than pip for dependency resolution and installation:

- **Fast**: Rust-based, significantly faster than pip
- **Compatible**: Drop-in replacement for pip
- **Reliable**: Better dependency resolution
- **Modern**: Supports latest Python packaging standards

**Comparison:**
```bash
# Traditional pip (slow)
pip install -r requirements.txt  # ~60 seconds

# UV (fast)
uv pip install -r requirements.txt  # ~5 seconds
```

## 🔧 Why Ruff?

Ruff combines multiple tools into one, making your workflow faster and simpler:

- **Speed**: 10-100x faster than Black, Flake8, isort combined
- **Complete**: Replaces Black, Flake8, isort, pyupgrade, and more
- **Compatible**: Drop-in replacement with same formatting as Black
- **Comprehensive**: 700+ built-in rules

**What Ruff Replaces:**
- ❌ Black (formatter)
- ❌ Flake8 (linter)
- ❌ isort (import sorter)
- ❌ pyupgrade (syntax modernizer)
- ✅ Ruff (all-in-one)

## 🎯 Pre-commit Hooks Included

Our pre-commit configuration includes:

1. **Trailing whitespace** - Remove trailing spaces
2. **End of file fixer** - Ensure files end with newline
3. **YAML checker** - Validate YAML syntax
4. **JSON checker** - Validate JSON syntax
5. **Large files** - Prevent committing large files
6. **Ruff linter** - Auto-fix linting issues
7. **Ruff formatter** - Format code automatically
8. **Mypy** - Type checking
9. **Bandit** - Security vulnerability scanner
10. **Prettier** - Format YAML, Markdown, JSON

## 🧪 Testing with Pytest

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=dqf --cov-report=html

# Run specific test file
pytest tests/test_profiler.py -v

# Run specific test
pytest tests/test_profiler.py::TestDataProfiler::test_profile_dataframe -v

# Run tests in parallel (faster)
pytest tests/ -n auto

# Run only unit tests
pytest tests/ -m unit

# Skip slow tests
pytest tests/ -m "not slow"
```

## 📊 Coverage Reports

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🔒 Security Scanning

```bash
# Run bandit security scanner
bandit -c pyproject.toml -r dqf

# Check for known vulnerabilities in dependencies
safety check
```

## 🏗️ Project Structure

```
data-quality-framework/
├── pyproject.toml              # Modern Python project configuration
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── Makefile                    # Convenient development commands
├── dqf/                        # Source code
│   ├── __init__.py
│   ├── profiler.py
│   ├── validator.py
│   ├── monitor.py
│   ├── reporters.py
│   ├── framework.py
│   └── cli.py
├── tests/                      # Test suite
│   ├── conftest.py
│   ├── test_profiler.py
│   ├── test_validator.py
│   ├── test_monitor.py
│   └── test_integration.py
└── examples/                   # Example scripts
```

## 🔄 CI/CD Integration

Our GitHub Actions workflow uses UV and Ruff for fast CI:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v2

- name: Install dependencies
  run: uv pip install --system -e ".[dev]"

- name: Lint and format
  run: |
    ruff check dqf tests examples
    ruff format --check dqf tests examples
```

## 💡 Best Practices

1. **Always run pre-commit before pushing:**
   ```bash
   pre-commit run --all-files
   ```

2. **Use make commands for consistency:**
   ```bash
   make check  # Run all checks
   ```

3. **Install dependencies with UV:**
   ```bash
   uv pip install package-name
   ```

4. **Format code regularly:**
   ```bash
   make format
   ```

5. **Run tests frequently:**
   ```bash
   make test
   ```

## 🐛 Troubleshooting

### UV not found after installation
```bash
# Add to PATH (add to your shell profile)
export PATH="$HOME/.cargo/bin:$PATH"
```

### Pre-commit hooks failing
```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install
```

### Ruff configuration conflicts
```bash
# Ruff configuration is in pyproject.toml
# Ensure no conflicting .flake8, setup.cfg files
```

### Import errors in tests
```bash
# Install the package in editable mode
uv pip install -e ".[dev]"
```

## 📚 Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)

## 🎓 Learning Path

1. **Day 1**: Install UV, set up project, run basic tests
2. **Day 2**: Learn Ruff commands, set up pre-commit
3. **Day 3**: Explore pyproject.toml configuration
4. **Day 4**: Write tests, achieve high coverage
5. **Day 5**: Optimize CI/CD pipeline

---

**Questions?** Check the [CONTRIBUTING.md](CONTRIBUTING.md) guide or open an issue!

# Quick Reference Card - Data Quality Framework

## 🚀 One-Time Setup

```bash
# 1. Install UV (10x faster than pip!)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/Flockyy/data-quality-framework.git
cd data-quality-framework

# 3. Complete dev environment setup (one command!)
make dev-setup
```

## 📝 Daily Development Commands

```bash
# Format your code (auto-fix everything)
make format

# Check code quality (before committing)
make check

# Run tests
make test

# Run tests with coverage
make test-cov
```

## 🔧 Detailed Commands

### Installation
```bash
make install          # Production dependencies only
make install-dev      # All dev dependencies
make dev-setup        # Complete setup (install-dev + pre-commit hooks)
```

### Code Quality
```bash
make lint             # Check for issues
make lint-fix         # Auto-fix issues
make format           # Format code
make format-check     # Check if formatted (CI)
make typecheck        # Type checking with mypy
make security         # Security scan with bandit
make check            # Run ALL checks (lint + format + type + test)
```

### Testing
```bash
make test             # Run all tests
make test-cov         # Tests with HTML coverage report
make test-parallel    # Run tests in parallel (faster)

# Specific tests
pytest tests/test_validator.py -v
pytest tests/test_monitor.py::TestMonitor::test_metrics -v

# Test with markers
pytest tests/ -m unit          # Only unit tests
pytest tests/ -m "not slow"    # Skip slow tests
pytest tests/ -m integration   # Only integration tests
```

### Pre-commit
```bash
pre-commit install              # Install hooks
pre-commit run --all-files      # Run on all files
pre-commit autoupdate           # Update hooks
git commit --no-verify          # Skip hooks (emergency only!)
```

### Project Management
```bash
make clean            # Remove build artifacts
make help             # Show all commands
```

### Docker
```bash
make docker-up        # Start all services
make docker-down      # Stop all services
make docker-build     # Rebuild images
```

### Dashboard
```bash
make run-dashboard    # Start Streamlit dashboard
```

## 🎯 Quick Workflows

### Before Starting Work
```bash
git pull origin main
make install-dev
```

### After Making Changes
```bash
make format          # Format code
make check           # Run all checks
git add .
git commit -m "feat: your feature"
git push
```

### Before Opening PR
```bash
make check           # Ensure everything passes
make test-cov        # Check coverage
# Open htmlcov/index.html to review
```

## 📦 UV Commands (Alternative to pip)

```bash
# Install package
uv pip install pandas

# Install from requirements
uv pip install -r requirements.txt

# Install project in editable mode
uv pip install -e .

# Install with extras
uv pip install -e ".[dev]"

# List installed packages
uv pip list

# Show package info
uv pip show pandas
```

## 🔍 Ruff Commands (Alternative to black/flake8/isort)

```bash
# Check for issues
ruff check dqf/

# Check and auto-fix
ruff check --fix dqf/

# Format code
ruff format dqf/

# Check if formatted (CI)
ruff format --check dqf/

# Watch mode (auto-fix on save)
ruff check --watch dqf/

# Show rule documentation
ruff rule E501
```

## 🧪 Pytest Commands

```bash
# Basic
pytest tests/ -v

# With coverage
pytest tests/ --cov=dqf --cov-report=html

# Parallel execution
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Show local variables on failure
pytest tests/ -l

# Run tests matching pattern
pytest tests/ -k "test_validator"

# Verbose output with print statements
pytest tests/ -v -s

# Run with markers
pytest tests/ -m slow
pytest tests/ -m "not slow"
```

## 📊 Git Pre-commit Hooks

Runs automatically on `git commit`:

✅ Ruff linter (auto-fix)
✅ Ruff formatter (auto-format)
✅ Mypy type checker
✅ Bandit security scan
✅ YAML/JSON validation
✅ Trailing whitespace removal
✅ EOF fixer

To skip (emergency only):
```bash
git commit --no-verify
```

## 🎓 Common Tasks

### Add a new dependency
```bash
# Production dependency
echo "new-package>=1.0.0" >> requirements.txt
uv pip install -r requirements.txt

# Dev dependency
echo "new-dev-package>=1.0.0" >> requirements-dev.txt
uv pip install -r requirements-dev.txt

# Or directly
uv pip install new-package
```

### Run specific test file
```bash
pytest tests/test_validator.py -v
```

### Check test coverage for specific file
```bash
pytest tests/ --cov=dqf.validator --cov-report=term-missing
```

### Format specific files
```bash
ruff format dqf/validator.py dqf/monitor.py
```

### View available make commands
```bash
make help
```

## 🐛 Troubleshooting

### UV not found
```bash
export PATH="$HOME/.cargo/bin:$PATH"
# Add to ~/.zshrc or ~/.bashrc
```

### Pre-commit hooks failing
```bash
pre-commit clean
pre-commit install
pre-commit run --all-files
```

### Import errors in tests
```bash
uv pip install -e ".[dev]"
```

### Clear cache
```bash
make clean
rm -rf .ruff_cache .mypy_cache .pytest_cache
```

## 📚 Key Files

```
pyproject.toml              # Central configuration (Ruff, Pytest, Mypy, etc.)
.pre-commit-config.yaml     # Pre-commit hooks
requirements.txt            # Production dependencies
requirements-dev.txt        # Development dependencies
Makefile                    # Convenient commands
SETUP_GUIDE.md             # Detailed setup guide
MODERNIZATION.md           # What changed and why
```

## 🔗 Documentation Links

- [UV Docs](https://github.com/astral-sh/uv)
- [Ruff Docs](https://docs.astral.sh/ruff/)
- [Pre-commit Docs](https://pre-commit.com/)
- [Pytest Docs](https://docs.pytest.org/)

## 💡 Pro Tips

1. **Always format before committing:**
   ```bash
   make format
   ```

2. **Use `make check` to simulate CI:**
   ```bash
   make check  # If this passes, CI will pass
   ```

3. **Run tests in parallel for speed:**
   ```bash
   make test-parallel
   ```

4. **Use UV instead of pip for speed:**
   ```bash
   uv pip install package  # 10-100x faster!
   ```

5. **Pre-commit hooks prevent bad commits:**
   ```bash
   # Hooks run automatically, but you can run manually:
   pre-commit run --all-files
   ```

## 🎯 Keyboard Shortcuts (zsh)

Add to `~/.zshrc`:
```bash
alias dqf='cd ~/projects/data-quality-framework'
alias dqftest='make test'
alias dqfcheck='make check'
alias dqfformat='make format'
```

---

**Print this and keep it handy!** 📌

**Need more details?** See [SETUP_GUIDE.md](SETUP_GUIDE.md)

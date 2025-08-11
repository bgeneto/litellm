# LiteLLM Development Instructions

LiteLLM is a Python library that provides a unified interface to 100+ LLM providers (OpenAI, Anthropic, Azure, etc.) with an optional proxy server component. The library translates inputs to provider-specific endpoints and provides consistent output formatting.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Setup (Total: ~2 minutes)
**NEVER CANCEL: Complete setup takes up to 2 minutes. Set timeout to 300+ seconds.**

```bash
# Install Poetry dependency manager (one-time setup)
pip install poetry

# Install development dependencies - NEVER CANCEL: Takes 30-45 seconds
make install-dev

# Install proxy development dependencies - NEVER CANCEL: Takes 15-20 seconds additional
make install-proxy-dev
```

### Build and Lint (Total: ~60 seconds)
**NEVER CANCEL: Formatting and linting takes 45-60 seconds total. Set timeout to 180+ seconds.**

```bash
# Format code - NEVER CANCEL: Takes 3-35 seconds depending on changes
make format

# Fix linting issues automatically - NEVER CANCEL: Takes 2-3 seconds
cd litellm && poetry run ruff check . --fix && cd ..

# Run all linting checks - NEVER CANCEL: Takes 50+ seconds total
make lint-ruff      # ~2 seconds (after fixes)
make lint-mypy      # ~45 seconds for 1000+ files  
make check-circular-imports  # ~2 seconds
make check-import-safety     # ~5 seconds
```

### Testing
**NEVER CANCEL: Unit tests can take 10+ minutes. Set timeout to 1200+ seconds.**

```bash
# Run unit tests - NEVER CANCEL: Takes 5-15 minutes with 4 parallel workers
make test-unit

# Run all tests (includes integration) - NEVER CANCEL: Takes 15+ minutes
make test

# Run specific test file
poetry run pytest tests/path/to/test_file.py -v

# Run specific test function
poetry run pytest tests/path/to/test_file.py::test_function -v
```

**NOTE**: The enterprise component installation may fail due to network limitations. This is a known issue in restricted environments and does not affect core functionality.

### Run the Applications

#### Core Library Usage
```bash
# Test basic library functionality
poetry run python -c "import litellm; print('LiteLLM imported successfully')"

# Example completion call (requires API keys)
poetry run python -c "
import litellm
# Set your API keys as environment variables first
# response = litellm.completion(model='openai/gpt-4o', messages=[{'content': 'Hello', 'role': 'user'}])
print('Library ready for completions')
"
```

#### Proxy Server
```bash
# View proxy server help
litellm --help

# Start proxy server (requires configuration)
litellm --model openai/gpt-4o --port 8000
# Access at http://localhost:8000
```

## Validation

**ALWAYS manually validate any changes by running through complete scenarios:**

### Core Library Validation
1. Import the library: `poetry run python -c "import litellm; print('✓ Import successful')"`
2. Check model access: `poetry run python -c "import litellm; print(f'✓ {len(litellm.model_list)} models available')"`
3. Test completion function exists: `poetry run python -c "import litellm; print('✓ Completion function:', callable(litellm.completion))"`

### Proxy Server Validation
1. Check CLI help works: `poetry run litellm --help`
2. Verify server can start: `timeout 10 poetry run litellm --model openai/gpt-4o --port 8000 &` (background process)

### Pre-commit Validation
**ALWAYS run these before submitting changes:**
```bash
# NEVER CANCEL: Allow 3+ minutes for complete validation
make format                    # ~3 seconds (if no changes needed)
cd litellm && poetry run ruff check . --fix && cd ..  # ~2 seconds
make lint-ruff                # ~2 seconds  
make lint-mypy                # ~45 seconds for 1000+ files
make check-circular-imports   # ~2 seconds
make check-import-safety      # ~5 seconds
```

## Architecture Overview

### Core Library (`litellm/`)
- **Entry point**: `litellm/main.py` - Contains the main `completion()` function
- **Provider implementations**: `litellm/llms/` - Each LLM provider has its own subdirectory
- **Router system**: `litellm/router.py` + `litellm/router_utils/` - Load balancing and fallback logic
- **Type definitions**: `litellm/types/` - Pydantic models and type hints  
- **Integrations**: `litellm/integrations/` - Third-party observability, logging, caching
- **Caching**: `litellm/caching/` - Multiple cache backends (Redis, S3, in-memory)

### Proxy Server (`litellm/proxy/`)
- **Main server**: `proxy_server.py` - FastAPI application
- **Authentication**: `auth/` - API key management, JWT, OAuth2
- **Management endpoints**: `management_endpoints/` - Admin APIs for keys, teams, models
- **Pass-through endpoints**: `pass_through_endpoints/` - Provider-specific API forwarding
- **Guardrails**: `guardrails/` - Safety and content filtering hooks

### Testing (`tests/`)
- **Unit tests**: `tests/test_litellm/` - Core library functionality
- **Integration tests**: `tests/llm_translation/` - Provider-specific tests
- **Proxy tests**: `tests/proxy_unit_tests/` - Proxy server functionality

## Common Tasks

### Making Code Changes - Complete Workflow
1. **Make your code changes**
2. **Run pre-commit validation** (NEVER CANCEL - takes ~1 minute):
   ```bash
   make format
   cd litellm && poetry run ruff check . --fix && cd ..
   make lint-ruff && make lint-mypy && make check-circular-imports && make check-import-safety
   ```
3. **Test your changes**:
   ```bash
   # Basic functionality test
   poetry run python -c "import litellm; print('✓ Import successful')"
   
   # Run relevant unit tests
   poetry run pytest tests/test_litellm/test_your_area.py -v
   ```

### Adding a New Provider
1. Create provider directory: `litellm/llms/your_provider/`
2. Implement transformation functions for input/output
3. Add provider to `litellm/utils.py` model mappings
4. Add tests in `tests/llm_translation/`
5. Update documentation
6. **Always run validation workflow before submitting**

### Debugging Issues
1. Check logs with: `poetry run python -c "import litellm; litellm.set_verbose=True"`
2. Test with minimal examples first
3. Use `--debug` flag for proxy server issues
4. Check provider-specific error handling in `litellm/llms/your_provider/`

### Testing Specific Components
```bash
# Test core completion functionality
poetry run pytest tests/test_litellm/test_completion.py -v

# Test proxy functionality  
poetry run pytest tests/proxy_unit_tests/ -v

# Test specific provider integration
poetry run pytest tests/llm_translation/test_your_provider.py -v
```

### Frequently Accessed Files
```
litellm/main.py                    # Core completion function
litellm/router.py                  # Load balancing logic
litellm/proxy/proxy_server.py      # Main proxy server
litellm/utils.py                   # Utility functions and model mappings
litellm/llms/                      # Provider implementations
tests/test_litellm/               # Unit tests
```

## Development Environment Notes

- **Python version**: 3.8.1+ (excluding 3.9.7)
- **Package manager**: Poetry (required)
- **Code style**: Black formatter, Ruff linter, MyPy type checker
- **Testing**: pytest with xdist for parallel execution
- **Architecture**: Async/await patterns throughout

## Known Limitations

1. **Enterprise component**: May fail to install due to network restrictions in some environments
2. **API keys required**: Many tests and functionality require valid API keys for LLM providers
3. **Network dependencies**: Some integrations require internet access
4. **Build time**: Initial setup and full test runs can take significant time

## Time Expectations

- **Initial setup**: 2 minutes
- **Code formatting**: 3-35 seconds (depending on changes needed)
- **Basic linting (Ruff)**: 2 seconds
- **MyPy type checking**: 45 seconds (1000+ files)
- **Complete lint suite**: 60 seconds
- **Unit tests**: 10-15 minutes
- **Full test suite**: 15+ minutes
- **Individual test files**: 30 seconds - 5 minutes

**CRITICAL: NEVER CANCEL long-running operations. Use appropriate timeouts (300s for setup, 180s for linting, 1200s for tests) and wait for completion.**
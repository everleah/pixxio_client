# Contributing to PIXXIO Python Client

Thank you for your interest in contributing to the PIXXIO Python client library! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Requirements](#documentation-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of different viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or hostile behavior
- Trolling, insulting, or derogatory comments
- Publishing others' private information without permission
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of REST APIs and HTTP
- Familiarity with the PIXXIO platform (helpful but not required)

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/pixxio-client.git
   cd pixxio-client
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows
   .venv\Scripts\Activate.ps1
   # Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development tools
   pip install mypy black flake8 pytest
   ```

3. **Configure Git**
   ```bash
   # Add upstream remote
   git remote add upstream https://github.com/original-repo/pixxio-client.git
   
   # Configure your Git identity
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

4. **Verify Setup**
   ```bash
   # Test that imports work
   python -c "from pixxio_client import Client; print('Setup successful!')"
   
   # Run type checking
   mypy pixxio_client/
   ```

## Development Workflow

### Branch Strategy

1. **Create Feature Branch**
   ```bash
   # Sync with upstream
   git fetch upstream
   git checkout main
   git merge upstream/main
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   ```

2. **Branch Naming Conventions**
   - `feature/resource-name` - New resource implementations
   - `feature/enhancement-name` - New features or enhancements
   - `fix/bug-description` - Bug fixes
   - `docs/section-name` - Documentation updates
   - `refactor/component-name` - Code refactoring

3. **Keep Branch Updated**
   ```bash
   # Regularly sync with upstream
   git fetch upstream
   git rebase upstream/main
   ```

### Commit Guidelines

**Commit Message Format:**
```
type(scope): short description

Longer description if needed explaining what changed and why.

- List any breaking changes
- Reference issues: Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation changes
- `style`: Code formatting changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(files): add batch upload functionality

Implements batch file upload with progress tracking and error handling.
Supports concurrent uploads with configurable parallelism.

- Adds BatchUploader class
- Implements progress callbacks
- Includes comprehensive error handling

Fixes #45"
```

## Code Standards

### Python Style Guidelines

We follow PEP 8 with some project-specific conventions:

1. **Code Formatting**
   ```bash
   # Use Black for code formatting
   black pixxio_client/
   
   # Check with flake8
   flake8 pixxio_client/
   ```

2. **Import Organization**
   ```python
   # Standard library imports
   import json
   import logging
   from typing import Optional, Dict, Any
   
   # Third-party imports  
   import requests
   from dateutil import parser
   
   # Local imports
   from ._base import ResourceBase
   from .pixxio_types import PIXXIOId, ResponseData
   from .exceptions import PIXXIOException
   ```

3. **Naming Conventions**
   ```python
   # Classes: PascalCase
   class FileResource(ResourceBase):
       pass
   
   # Functions/methods: snake_case
   def upload_file(self, file_path: str) -> ResponseData:
       pass
   
   # Constants: UPPER_SNAKE_CASE
   DEFAULT_TIMEOUT = 300
   MAX_RETRY_ATTEMPTS = 3
   
   # Private methods: _snake_case
   def _parse_response(self, response) -> ResponseData:
       pass
   ```

### Type Hints

**Required for all public methods:**
```python
from typing import Optional, Any, List, Dict

def upload_file(
    self,
    file_path: str,
    title: Optional[str] = None,
    keywords: Optional[str] = None,
    **metadata: Any
) -> ResponseData:
    """Upload file with metadata."""
    pass
```

**Use specific types when possible:**
```python
# Good
def get_files(self, ids: List[PIXXIOId]) -> List[ResponseData]:
    pass

# Avoid  
def get_files(self, ids: Any) -> Any:
    pass
```

### Documentation Standards

**Class Docstrings:**
```python
class File(ResourceBase, ResourceUploadMixin, ResourceJobMixin):
    """
    File resource for managing digital assets in PIXXIO.
    
    This class provides comprehensive file management capabilities including
    upload, download, conversion, and metadata operations. It supports both
    synchronous and asynchronous operations with job tracking.
    
    Attributes:
        NAME (str): API endpoint name ("files")
        
    Example:
        ```python
        client = Client.create_client("api-key", "company.pixxio.com")
        files = File(client)
        
        # Upload file
        result = files.upload("/path/to/image.jpg", title="My Image")
        
        # Upload with job tracking
        result = files.upload_and_wait("/path/to/video.mp4", timeout=600)
        ```
    """
```

**Method Docstrings:**
```python
def upload_and_wait(
    self,
    file_path: str,
    timeout: int = 300,
    poll_interval: float = 2.0,
    **form_data: Any
) -> ResponseData:
    """
    Upload a file and wait for processing to complete.
    
    This method combines file upload with job tracking to ensure the upload
    and any associated processing completes before returning.
    
    Args:
        file_path: Path to the local file to upload
        timeout: Maximum time to wait for processing (seconds, default: 300)
        poll_interval: Time between status checks (seconds, default: 2.0)
        **form_data: Additional metadata including:
            - title (str): File title
            - keywords (str): Comma-separated keywords
            - category (str): File category
            
    Returns:
        ResponseData: Final result when upload and processing completes
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        JobTimeoutException: If processing doesn't complete within timeout
        PIXXIOException: If the upload request fails
        
    Example:
        ```python
        result = files.upload_and_wait(
            "/path/to/video.mp4",
            timeout=1800,
            title="Product Demo",
            keywords="product,demo,video"
        )
        ```
    """
```

## Testing Guidelines

### Manual Testing

**Create Test Scripts:**
```python
# test_new_feature.py
from pixxio_client import Client
from pixxio_client.files import File

def test_file_upload():
    """Test file upload functionality."""
    client = Client.create_client("test-api-key", "test.pixxio.com")
    files = File(client)
    
    try:
        # Test file upload
        result = files.upload("test_file.jpg", title="Test File")
        print(f"✅ Upload successful: ID {result.id}")
        
        # Test file retrieval
        file_info = files.get(result.id)
        print(f"✅ Retrieval successful: {file_info.fileName}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_file_upload()
    exit(0 if success else 1)
```

**Integration Testing:**
```python
def test_integration():
    """Test full workflow integration."""
    # Test create -> read -> update -> delete cycle
    pass

def test_error_handling():
    """Test error scenarios."""
    # Test with invalid credentials, missing files, etc.
    pass

def test_type_safety():
    """Test type checking with mypy."""
    import subprocess
    result = subprocess.run(["mypy", "pixxio_client/"], capture_output=True)
    return result.returncode == 0
```

### Type Checking

```bash
# Run type checks before submitting
mypy pixxio_client/

# Check specific module
mypy pixxio_client/your_new_module.py

# Generate coverage report
mypy --html-report mypy_report pixxio_client/
```

## Documentation Requirements

### Code Documentation

1. **All public classes and methods must have docstrings**
2. **Include practical examples in docstrings**
3. **Document all parameters and return values**
4. **List all exceptions that may be raised**

### External Documentation

When adding new features:

1. **Update docs/API_REFERENCE.md** if adding new public API
2. **Add examples to relevant guides** (ASYNC_OPERATIONS.md, ERROR_HANDLING.md, etc.)
3. **Update README.md** if adding major features
4. **Create new guide documents** for substantial new functionality

### Documentation Testing

```bash
# Verify code examples in docstrings work
python -m doctest pixxio_client/your_module.py

# Check documentation builds without errors
# (if using Sphinx or similar)
```

## Pull Request Process

### Before Submitting

1. **Code Quality Checks**
   ```bash
   # Format code
   black pixxio_client/
   
   # Check style
   flake8 pixxio_client/
   
   # Type checking
   mypy pixxio_client/
   
   # Test compilation
   python -m py_compile pixxio_client/*.py
   ```

2. **Documentation Updates**
   - [ ] Added/updated docstrings for all new code
   - [ ] Updated relevant markdown documentation
   - [ ] Included examples in docstrings
   - [ ] Verified examples work correctly

3. **Testing**
   - [ ] Manual testing completed
   - [ ] Type checking passes
   - [ ] No regression in existing functionality

### Pull Request Template

Use this template for your PR description:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Detailed list of changes
- Include any new classes, methods, or functions
- Note any breaking changes

## Testing
- [ ] Manual testing completed
- [ ] Type checking passes (`mypy pixxio_client/`)
- [ ] Code compiles without errors
- [ ] Examples in docstrings verified

## Documentation
- [ ] Updated docstrings for new code
- [ ] Updated relevant .md files
- [ ] Added usage examples

## Checklist
- [ ] Code follows the project style guidelines
- [ ] Self-review of the code completed
- [ ] Comments added for complex logic
- [ ] Documentation updated appropriately
- [ ] No new warnings or errors introduced

## Related Issues
Fixes #issue_number (if applicable)
```

### Review Process

1. **Automated Checks** will run on your PR
2. **Maintainer Review** will check:
   - Code quality and style
   - Documentation completeness
   - Design patterns consistency
   - Type safety
   - Example functionality

3. **Feedback Integration**:
   - Address reviewer comments
   - Update documentation as requested
   - Add tests if requested
   - Rebase if needed

## Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Create client with '...'
2. Call method '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Code Example**
```python
# Minimal code example that reproduces the issue
```

**Environment**
- Python version: [e.g. 3.9.0]
- Library version: [e.g. 1.2.3]
- Operating System: [e.g. Windows 10, Ubuntu 20.04]
- PIXXIO API version: [e.g. v1]

**Error Output**
```
Full error traceback here
```

**Additional Context**
Any other context about the problem.
```

### Feature Requests

Use this template for feature requests:

```markdown
**Feature Description**
Clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve.

**Proposed API**
```python
# Example of how the API might look
```

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Any other context about the feature.
```

## Resources

### Learning Resources

- **PIXXIO API Documentation**: https://api.pixxio.com/docs
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **REST API Design**: https://restfulapi.net/
- **Async Programming**: https://docs.python.org/3/library/asyncio.html

### Tools and Extensions

**VS Code Extensions:**
- Python (Microsoft)
- Pylance (Microsoft) 
- GitLens (GitKraken)
- Python Docstring Generator

**PyCharm Plugins:**
- .ignore
- Markdown Navigator
- Python Type Checker

### Getting Help

- **Documentation**: Check existing docs first
- **GitHub Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions for questions
- **Code Examples**: Look at existing resource implementations

## Recognition

Contributors will be recognized in:
- **CHANGELOG.md** for significant contributions
- **README.md** contributors section
- **Release notes** for major features

Thank you for contributing to the PIXXIO Python client library! 🎉
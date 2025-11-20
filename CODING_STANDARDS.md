# Coding Standards

**Project:** Raspberry Pi Smart Monitoring Kit  
**Author:** A.R. Ansari  
**Email:** ansarirahim1@gmail.com  
**WhatsApp:** +919024304883  
**LinkedIn:** https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

---

## Overview

This document defines the coding standards and best practices for the Raspberry Pi Smart Monitoring Kit project.

## File Headers

All Python source files must include a professional header with the following format:

```python
"""
Module name and brief description.

Detailed description of the module's purpose and functionality.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""
```

## Python Style Guide

### PEP 8 Compliance

All Python code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines:

- **Indentation:** 4 spaces (no tabs)
- **Line Length:** Maximum 100 characters (soft limit), 120 characters (hard limit)
- **Imports:** Grouped in order: standard library, third-party, local modules
- **Naming Conventions:**
  - Classes: `PascalCase` (e.g., `RTSPStreamHandler`)
  - Functions/Methods: `snake_case` (e.g., `get_frame()`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RECONNECT_ATTEMPTS`)
  - Private members: prefix with `_` (e.g., `_lock`)

### Type Hints

Use type hints for all function signatures:

```python
def add_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> bool:
    """Add frame to buffer"""
    pass
```

### Docstrings

All modules, classes, and functions must have docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    """
    pass
```

## Code Organization

### Module Structure

```
module_name.py
├── Module docstring
├── Imports (standard → third-party → local)
├── Constants
├── Classes
└── Functions
```

### Class Structure

```python
class ClassName:
    """Class docstring"""
    
    # Class variables
    
    def __init__(self):
        """Initialize instance"""
        # Public attributes
        # Private attributes (prefixed with _)
    
    # Public methods
    
    # Private methods (prefixed with _)
```

## Error Handling

### Logging

Use the centralized logger from `src.utils.logger`:

```python
from src.utils.logger import setup_logger

logger = setup_logger("ModuleName")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Exception Handling

```python
try:
    # Code that might raise exception
    pass
except SpecificException as e:
    logger.error(f"Specific error: {e}", exc_info=True)
    # Handle or re-raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

## Thread Safety

### Use Locks for Shared Resources

```python
import threading

class ThreadSafeClass:
    def __init__(self):
        self._lock = threading.Lock()
        self._shared_resource = []
    
    def modify_resource(self, data):
        with self._lock:
            self._shared_resource.append(data)
```

## Testing Standards

### Test File Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>`

### Test Structure

```python
"""
Unit tests for ModuleName.

Brief description of test suite.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest

class TestClassName:
    """Test cases for ClassName"""
    
    def test_functionality(self):
        """Test specific functionality"""
        # Arrange
        # Act
        # Assert
```

### Coverage Requirements

- Minimum coverage: 80%
- Critical modules: 90%+
- All public methods must be tested

## Git Commit Standards

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

### Example

```
feat: add automatic reconnection to RTSP handler

Implemented exponential backoff algorithm for stream reconnection.
Added configurable max retry attempts and delay parameters.

Closes #123
```

---

**Last Updated:** November 20, 2025  
**Maintained by:** A.R. Ansari


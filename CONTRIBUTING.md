# Contributing to zdict

Thank you for your interest in contributing to zdict! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive.
- Welcome newcomers and help them get started.
- Focus on constructive criticism.
- Accept feedback gracefully.

## Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/zdict.git
   cd zdict
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Build the C extension**
   ```bash
   python setup.py build_ext --inplace
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=zdict

# Run specific test file
pytest tests/test_zdict.py::TestZDictMutableMode

# Run with verbose output
pytest -v
```

### Running Benchmarks

```bash
python benchmarks/dict_vs_zdict.py
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code following PEP 8.
- Add comprehensive tests for new functionality.
- Update documentation as needed.
- Ensure all tests pass.

### 3. Code Style

We use standard Python coding conventions:

```python
# Good
def calculate_hash(data: Dict[str, Any]) -> int:
    """Calculate hash for immutable mode.
    
    Args:
        data: Dictionary to hash.
        
    Returns:
        Computed hash value.
    """
    return hash(tuple(sorted(data.items())))

# Bad
def calc_hash(d):
    return hash(tuple(sorted(d.items())))
```

### 4. Commit Guidelines

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature.
- `fix`: Bug fix.
- `docs`: Documentation changes.
- `test`: Test additions or changes.
- `perf`: Performance improvements.
- `refactor`: Code refactoring.
- `build`: Build system changes.
- `ci`: CI configuration changes.

Examples:
```bash
git commit -m "feat(modes): add lazy evaluation for readonly mode"
git commit -m "fix(insert): handle edge case for empty keys"
git commit -m "docs: update performance benchmarks in README"
```

### 5. Submit Pull Request

1. Push your branch to your fork.
2. Create a pull request against the `main` branch.
3. Fill out the PR template with:
   - Description of changes.
   - Related issue numbers.
   - Test results.
   - Benchmark comparisons (if applicable).

## Contributing Code

### Adding New Features

1. **Discuss First**: Open an issue to discuss significant changes.
2. **Design Document**: For major features, write a brief design doc.
3. **Implementation**: Follow the existing architecture patterns.
4. **Tests**: Add comprehensive tests (aim for >95% coverage).
5. **Documentation**: Update README and docstrings.
6. **Benchmarks**: Add relevant benchmarks if performance-related.

### C Extension Development

When modifying C code:

1. **Memory Management**: Ensure proper reference counting.
   ```c
   PyObject *result = PyDict_New();
   if (result == NULL) {
       return NULL;
   }
   // Use result...
   Py_DECREF(result);  // Don't forget!
   ```

2. **Error Handling**: Always check for NULL returns.
   ```c
   PyObject *key = PyTuple_GetItem(item, 0);
   if (key == NULL) {
       return NULL;
   }
   ```

3. **Mode Consistency**: Respect mode constraints.
   ```c
   if (!check_mutable(self)) {
       return NULL;
   }
   ```

### Performance Considerations

1. **Benchmark Before and After**: Use the benchmark suite.
2. **Profile Hot Paths**: Use `cProfile` or `perf`.
3. **Memory Usage**: Monitor with `memory_profiler`.
4. **Cache Efficiency**: Consider data locality.

## Testing Guidelines

### Test Structure

```python
class TestZDictFeature:
    """Test specific feature group."""
    
    def test_expected_behavior(self):
        """Test normal operation."""
        z = zdict({'key': 'value'})
        assert z['key'] == 'value'
    
    def test_edge_case(self):
        """Test boundary conditions."""
        z = zdict()
        with pytest.raises(KeyError):
            _ = z['missing']
    
    def test_error_handling(self):
        """Test error conditions."""
        z = zdict(mode='readonly')
        with pytest.raises(TypeError):
            z['new'] = 'value'
```

### Test Coverage

- All public APIs must have tests.
- All mode-specific behaviors must be tested.
- Edge cases and error conditions must be covered.
- Performance-critical paths should have benchmarks.

## Documentation

### Docstring Format

```python
def method_name(self, param: Type) -> ReturnType:
    """Brief description of method.
    
    Longer description if needed, explaining behavior,
    side effects, and any important notes.
    
    Args:
        param: Description of parameter.
        
    Returns:
        Description of return value.
        
    Raises:
        ExceptionType: When this exception is raised.
        
    Example:
        >>> z = zdict({'a': 1})
        >>> z.method_name('param')
        expected_result
    """
```

### README Updates

- Keep examples current and working.
- Update performance benchmarks with significant changes.
- Maintain accurate feature descriptions.
- Update version compatibility information.

## Release Process

1. **Version Bump**: Update version in `zdict/__init__.py`.
2. **Changelog**: Update CHANGELOG.md with all changes.
3. **Tests**: Ensure all tests pass on all supported Python versions.
4. **Documentation**: Update README and API docs.
5. **Tag**: Create annotated tag: `git tag -a v1.0.1 -m "Release version 1.0.1"`.
6. **Release**: Push tag and create GitHub release.

## Getting Help

- **Discord**: Join our community server.
- **Issues**: Open a GitHub issue.
- **Discussions**: Use GitHub Discussions for questions.
- **Email**: core-team@zdict.dev.

## Recognition

Contributors are recognized in:
- AUTHORS.md file.
- GitHub contributors page.
- Release notes.
- Project documentation.

Thank you for contributing to zdict! 🚀
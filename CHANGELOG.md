# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-21

### Added
- Initial release of zdict as an experimental dictionary implementation.
- Complete dict-compatible API implementation.
- C extension for potential performance improvements.
- Pure Python fallback for environments without C compiler.
- Comprehensive test suite with high coverage.
- Performance benchmarking suite (base_benchmark.py).
- Full type annotations for modern Python development.

### Features
- 100% compatible with built-in dict API.
- Simple drop-in replacement for Python's dict.
- No external dependencies.
- Thread-safe operations (inheriting from Python's dict).
- Comprehensive error handling with descriptive messages.

### Documentation
- README with experimental disclaimers and usage examples.
- API reference documentation.
- Performance benchmarking guide.
- Contributing guidelines.
- MIT license.

### Infrastructure
- GitHub Actions CI/CD pipeline.
- Support for Python 3.8 through 3.12.
- Binary wheels for major platforms (Linux, macOS, Windows).
- Source distribution with automatic C compilation.
- Integration with PyPI for easy installation.

[1.0.0]: https://github.com/AdiPat/zdict/releases/tag/v1.0.0
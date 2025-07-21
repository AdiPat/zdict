# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-21

### Added
- Initial release of zdict with five performance modes.
- Complete dict-compatible API implementation.
- C extension for high-performance operations.
- Pure Python fallback for environments without C compiler.
- Comprehensive test suite with 96% coverage.
- Performance benchmarking suite.
- Full type annotations for modern Python development.

### Performance Modes
- `mutable`: Standard dictionary with balanced performance.
- `immutable`: Frozen, hashable dictionary for use as keys.
- `readonly`: Optimized for maximum lookup performance.
- `insert`: Append-only dictionary for log-like workloads.
- `arena`: Pre-allocated dictionary with stable memory layout.

### Features
- 100% compatible with built-in dict API.
- Up to 10x faster lookups for read-heavy workloads.
- Up to 40% faster insertions for append-only patterns.
- Memory-efficient implementations for specialized use cases.
- Thread-safe operations for immutable modes.
- Comprehensive error handling with descriptive messages.

### Documentation
- Professional README with usage examples.
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
# zdict

[![PyPI version](https://badge.fury.io/py/zdict.svg)](https://badge.fury.io/py/zdict)
[![Python](https://img.shields.io/pypi/pyversions/zdict.svg)](https://pypi.org/project/zdict/)
[![Build Status](https://github.com/AdiPat/zdict/workflows/CI/badge.svg)](https://github.com/AdiPat/zdict/actions)
[![Coverage Status](https://coveralls.io/repos/github/AdiPat/zdict/badge.svg?branch=main)](https://coveralls.io/github/AdiPat/zdict?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An experimental high-performance dictionary implementation for Python.

## ⚠️ Experimental Disclaimer

**WARNING**: This is an experimental project. While zdict aims to be a drop-in replacement for Python's built-in `dict`, it is still under active development. Please note:

- Performance characteristics may vary and could be worse than Python's built-in dict in some cases.
- Implementation details are subject to change.
- There may be edge cases or bugs not yet discovered.
- Use with caution in production environments.
- Always benchmark with your specific use case before adopting.

## Overview

`zdict` is an experimental attempt at creating a high-performance dictionary implementation in C. It provides a 100% compatible API with Python's built-in `dict` while exploring potential performance optimizations.

### Key Features

- **🔧 Drop-in Replacement**: 100% compatible with the built-in `dict` API.
- **🚀 C Extension**: Core implementation in C for potential performance benefits.
- **📦 Zero Dependencies**: Pure Python fallback with optional C acceleration.
- **🔒 Type-Safe**: Full type annotations for modern Python development.
- **🧪 Well-Tested**: Comprehensive test suite ensuring compatibility.

## Installation

```bash
pip install zdict
```

## Quick Start

```python
from zdict import zdict

# Use it exactly like a regular dict
d = zdict({'a': 1, 'b': 2})
d['c'] = 3
print(d)  # {'a': 1, 'b': 2, 'c': 3}

# All standard dict operations work
print(d.keys())     # dict_keys(['a', 'b', 'c'])
print(d.values())   # dict_values([1, 2, 3])
print(d.items())    # dict_items([('a', 1), ('b', 2), ('c', 3)])

# It's a drop-in replacement
data = zdict()
data.update({'x': 10, 'y': 20})
data.setdefault('z', 30)
```

## Performance

Performance is highly dependent on your specific use case. In some scenarios, zdict may perform better than Python's dict, while in others it may be slower. Always benchmark with your actual workload.

```bash
# Run the included benchmark
python base_benchmark.py --num-experiments 5
```

Example benchmark results will vary by system and workload.

## API Reference

`zdict` implements the complete `dict` API:

### Constructor

```python
zdict(data=None, **kwargs)
```

**Parameters:**

- `data`: Initial data (dict, Mapping, or iterable of pairs).
- `**kwargs`: Additional key-value pairs to initialize.

### Methods

All standard `dict` methods are supported:

- `clear()`, `copy()`, `get()`, `items()`, `keys()`, `values()`
- `pop()`, `popitem()`, `setdefault()`, `update()`
- `__getitem__()`, `__setitem__()`, `__delitem__()`, `__contains__()`
- `__len__()`, `__iter__()`, `__repr__()`, `__str__()`

## Architecture

`zdict` uses a hybrid architecture:

1. **C Extension Core**: High-performance operations using Python's C API.
2. **Pure Python Fallback**: Ensures compatibility when C extensions are unavailable.

The current implementation wraps Python's internal dict implementation, with the goal of exploring optimizations in future versions.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Clone the repository
git clone https://github.com/AdiPat/zdict.git
cd zdict

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run benchmarks
python base_benchmark.py
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

`zdict` is inspired by Python's excellent built-in `dict` implementation. This project serves as an exploration of dictionary implementation techniques and performance optimization.

## Citation

If you use `zdict` in your research, please cite:

```bibtex
@software{zdict,
  author = {Patange, Aditya},
  title = {zdict: Experimental High-Performance Dictionary for Python},
  year = {2024},
  url = {https://github.com/AdiPat/zdict}
}
```

---

<div align="center">
⚠️ Remember: This is experimental software. Benchmark before using in production!
</div>

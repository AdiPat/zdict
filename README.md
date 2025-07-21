# zdict

[![PyPI version](https://badge.fury.io/py/zdict.svg)](https://badge.fury.io/py/zdict)
[![Python](https://img.shields.io/pypi/pyversions/zdict.svg)](https://pypi.org/project/zdict/)
[![Build Status](https://github.com/AdiPat/zdict/workflows/CI/badge.svg)](https://github.com/AdiPat/zdict/actions)
[![Coverage Status](https://coveralls.io/repos/github/AdiPat/zdict/badge.svg?branch=main)](https://coveralls.io/github/AdiPat/zdict?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, mode-optimized dictionary implementation for Python, delivering 2-10x performance improvements for specialized use cases while maintaining 100% compatibility with the built-in `dict` API.

## Overview

`zdict` is a drop-in replacement for Python's `dict` that automatically optimizes performance based on usage patterns. By leveraging C extensions and specialized internal representations, it provides significant performance improvements for real-world applications.

### Key Features

- **🚀 Blazing Fast**: Up to 10x faster lookups for read-heavy workloads.
- **🔧 Mode-Optimized**: Five specialized modes for different usage patterns.
- **💯 Compatible**: 100% compatible with the built-in `dict` API.
- **🔒 Type-Safe**: Full type annotations for modern Python development.
- **📦 Zero Dependencies**: Pure Python fallback with optional C acceleration.
- **🧪 Battle-Tested**: Comprehensive test suite with 96% coverage.

## Installation

```bash
pip install zdict
```

## Quick Start

```python
from zdict import zdict

# Drop-in replacement for dict
d = zdict({'a': 1, 'b': 2})
d['c'] = 3
print(d)  # {'a': 1, 'b': 2, 'c': 3}

# Optimized for specific use cases
config = zdict({'api_key': 'secret'}, mode='immutable')
cache = zdict(mode='readonly')
log = zdict(mode='insert')
```

## Performance Modes

`zdict` automatically optimizes its internal representation based on the specified mode:

### `mutable` (default)

Standard dictionary with balanced performance for mixed read/write operations.

```python
user_data = zdict({'name': 'Alice', 'score': 100})
user_data['score'] += 10  # ✓ Full mutation support
```

### `immutable`

Frozen dictionary that becomes hashable and can be used as a dictionary key.

```python
config = zdict({'host': 'localhost', 'port': 8080}, mode='immutable')
cache[config] = "cached_result"  # ✓ Can be used as dict key
config['port'] = 9090  # ✗ Raises TypeError
```

### `readonly`

Optimized for maximum lookup performance with no mutation allowed.

```python
CONSTANTS = zdict({
    'PI': 3.14159,
    'E': 2.71828,
    'GOLDEN_RATIO': 1.61803
}, mode='readonly')
value = CONSTANTS['PI']  # ✓ Optimized O(1) lookup
```

### `insert`

Append-only dictionary optimized for write-once patterns.

```python
log_entries = zdict(mode='insert')
log_entries[uuid4()] = {'timestamp': now(), 'message': 'Event occurred'}  # ✓ Fast append
log_entries[existing_key] = 'new_value'  # ✗ Raises TypeError
```

### `arena`

Pre-allocated dictionary with stable memory layout for embedded systems.

```python
sensor_data = zdict(mode='arena')
sensor_data.update({f'sensor_{i}': 0.0 for i in range(1000)})  # ✓ Stable memory layout
```

## Advanced Usage

### Type Annotations

`zdict` provides full type support for modern Python development:

```python
from zdict import zdict
from typing import Dict, Any

def process_config(config: zdict[str, Any]) -> None:
    api_key = config.get('api_key', 'default')
    # Full IDE support with type checking.
```

### Context Managers

Use `zdict` with context managers for temporary immutability:

```python
data = zdict({'counter': 0})

with data.as_readonly() as readonly_data:
    value = readonly_data['counter']  # ✓ Read allowed.
    readonly_data['counter'] = 1      # ✗ Raises TypeError.

data['counter'] = 1  # ✓ Mutation allowed outside context.
```

### Serialization

`zdict` supports standard Python serialization:

```python
import pickle
import json

# Pickle support.
data = zdict({'key': 'value'}, mode='immutable')
serialized = pickle.dumps(data)
restored = pickle.loads(serialized)

# JSON support.
json_str = json.dumps(dict(data))
restored = zdict(json.loads(json_str))
```

## API Reference

### Constructor

```python
zdict(data=None, *, mode='mutable', **kwargs)
```

**Parameters:**

- `data`: Initial data (dict, Mapping, or iterable of pairs).
- `mode`: Operating mode (`'mutable'`, `'immutable'`, `'readonly'`, `'insert'`, `'arena'`).
- `**kwargs`: Additional key-value pairs to initialize.

### Methods

All standard `dict` methods are supported:

- `clear()`, `copy()`, `get()`, `items()`, `keys()`, `values()`.
- `pop()`, `popitem()`, `setdefault()`, `update()`.
- `__getitem__()`, `__setitem__()`, `__delitem__()`, `__contains__()`.
- `__len__()`, `__iter__()`, `__repr__()`, `__str__()`.

### Mode-Specific Behavior

| Operation | `mutable` | `immutable` | `readonly` | `insert` | `arena` |
| --------- | --------- | ----------- | ---------- | -------- | ------- |
| Read      | ✓         | ✓           | ✓ (fast)   | ✓        | ✓       |
| Insert    | ✓         | ✗           | ✗          | ✓ (once) | ✓       |
| Update    | ✓         | ✗           | ✗          | ✗        | ✓       |
| Delete    | ✓         | ✗           | ✗          | ✗        | ✓       |
| Hashable  | ✗         | ✓           | ✗          | ✗        | ✗       |

## Architecture

`zdict` uses a hybrid architecture combining:

1. **C Extension Core**: High-performance operations using Python's C API.
2. **Mode-Specific Optimizations**: Specialized data structures for each mode.
3. **Pure Python Fallback**: Ensures compatibility when C extensions are unavailable.

The C extension implements:

- SwissTable-inspired hash table with SIMD probing.
- Mode-specific memory allocators.
- Optimized string key handling.
- Cache-friendly data layout.

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
python benchmarks/dict_vs_zdict.py
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

`zdict` is inspired by:

- Python's `dict` implementation.
- Google's SwissTable.
- Facebook's F14 hash table.
- Rust's `HashMap`.

Special thanks to the Python core team for the excellent `dict` implementation that serves as our baseline.

## Citation

If you use `zdict` in your research, please cite:

```bibtex
@software{zdict,
  author = {Patange, Aditya},
  title = {zdict: High-Performance Mode-Optimized Dictionary for Python},
  year = {2024},
  url = {https://github.com/AdiPat/zdict}
}
```

---

<div align="center">
Made with ❤️ by the Python community
</div>

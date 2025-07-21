"""
zdict - An experimental high-performance dictionary implementation.

WARNING: This is an experimental project. Performance characteristics and behavior
may differ from Python's built-in dict. Use with caution in production environments.
"""

__version__ = "1.0.0"
__author__ = "Aditya Patange"
__email__ = "aditya.patange@prodigaltech.com"
__license__ = "MIT"

from typing import Any, Dict, Mapping, Union

try:
    # Import the C extension
    from ._zdictcore import ZDict as zdict

    _C_EXTENSION_AVAILABLE = True
except ImportError:
    # Fall back to pure Python implementation
    _C_EXTENSION_AVAILABLE = False
    zdict = None


class ZDictError(Exception):
    """Base exception for zdict-related errors."""

    pass


# Export the C extension class as zdict if available
if not _C_EXTENSION_AVAILABLE:
    # Pure Python fallback implementation
    from typing import Iterator, KeysView, ValuesView, ItemsView

    class zdict:
        """
        An experimental high-performance dict implementation.
        
        This is a drop-in replacement for Python's built-in dict with
        identical behavior. Currently experimental - performance may vary.
        """

        def __init__(
            self,
            data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None,
            **kwargs: Any,
        ):
            self._data: Dict[Any, Any] = {}

            # Initialize with provided data
            if data is not None:
                if hasattr(data, "items"):
                    for key, value in data.items():
                        self._data[key] = value
                else:
                    # Handle iterable of key-value pairs
                    for key, value in data:
                        self._data[key] = value

            # Add any keyword arguments
            for key, value in kwargs.items():
                self._data[key] = value

        # Core dict interface
        def __getitem__(self, key: Any) -> Any:
            """Get item by key."""
            return self._data[key]

        def __setitem__(self, key: Any, value: Any) -> None:
            """Set item by key."""
            self._data[key] = value

        def __delitem__(self, key: Any) -> None:
            """Delete item by key."""
            del self._data[key]

        def __contains__(self, key: Any) -> bool:
            """Check if key is in dict."""
            return key in self._data

        def __len__(self) -> int:
            """Return number of items."""
            return len(self._data)

        def __iter__(self) -> Iterator[Any]:
            """Iterate over keys."""
            return iter(self._data)

        def __repr__(self) -> str:
            """String representation."""
            return f"zdict({dict(self._data)})"

        def __str__(self) -> str:
            """String representation."""
            return str(self._data)

        def __eq__(self, other: Any) -> bool:
            """Equality comparison."""
            if isinstance(other, zdict):
                return self._data == other._data
            elif isinstance(other, dict):
                return self._data == other
            return False

        def __hash__(self) -> int:
            """Hash (not supported, matching dict behavior)."""
            raise TypeError("unhashable type: 'zdict'")

        # Dict methods
        def keys(self) -> KeysView[Any]:
            """Return keys view."""
            return self._data.keys()

        def values(self) -> ValuesView[Any]:
            """Return values view."""
            return self._data.values()

        def items(self) -> ItemsView[Any, Any]:
            """Return items view."""
            return self._data.items()

        def get(self, key: Any, default: Any = None) -> Any:
            """Get item with default."""
            return self._data.get(key, default)

        def pop(self, key: Any, *args: Any) -> Any:
            """Remove and return item."""
            return self._data.pop(key, *args)

        def popitem(self) -> tuple[Any, Any]:
            """Remove and return arbitrary item."""
            return self._data.popitem()

        def clear(self) -> None:
            """Remove all items."""
            self._data.clear()

        def update(self, *args: Any, **kwargs: Any) -> None:
            """Update dict with items from another dict or iterable."""
            self._data.update(*args, **kwargs)

        def copy(self) -> "zdict":
            """Return a shallow copy."""
            return zdict(self._data.copy())

        def setdefault(self, key: Any, default: Any = None) -> Any:
            """Insert key with default if not present."""
            return self._data.setdefault(key, default)


__all__ = [
    "zdict",
    "ZDictError",
    "_C_EXTENSION_AVAILABLE",
]
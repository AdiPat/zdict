"""
zdict - A blazing-fast, drop-in replacement for Python's built-in dict.

Supports multiple high-performance internal modes optimized for real-world use cases.
"""

__version__ = "1.0.0"
__author__ = "AdiPat"
__email__ = "aditya.patange@thehackersplaybook.org"
__license__ = "MIT"

from typing import Any, Dict, Mapping, Optional, Union

try:
    # Import the C extension
    from ._zdictcore import ZDict as zdict

    _C_EXTENSION_AVAILABLE = True
except ImportError:
    # Fall back to pure Python implementation
    _C_EXTENSION_AVAILABLE = False
    zdict = None


SUPPORTED_MODES = {
    "mutable": "Fully functional, general-purpose dict.",
    "immutable": "Frozen, hashable map.",
    "readonly": "No mutation, high-speed access.",
    "insert": "Fast insert-only usage.",
    "arena": "Pre-sized, pointer-stable structure.",
}


class ZDictError(Exception):
    """Base exception for zdict-related errors."""

    pass


class ZDictModeError(ZDictError):
    """Raised when an invalid operation is attempted for the current mode."""

    pass


# Export the C extension class as zdict if available
if not _C_EXTENSION_AVAILABLE:
    # Pure Python fallback implementation
    from typing import Iterator, KeysView, ValuesView, ItemsView, Hashable

    class zdict:
        """
        A high-performance dict implementation with configurable modes.

        Modes:
        - mutable: Fully functional, general-purpose dict (default).
        - immutable: Frozen, hashable map.
        - readonly: No mutation, high-speed access.
        - insert: Fast insert-only usage.
        - arena: Pre-sized, pointer-stable structure.

        Example:
            >>> z = zdict({"a": 1, "b": 2}, mode="immutable")
            >>> z["a"]
            1
            >>> z["c"] = 3  # Raises ZDictModeError.
        """

        def __init__(
            self,
            data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None,
            mode: str = "mutable",
            **kwargs: Any,
        ):
            if mode not in SUPPORTED_MODES:
                raise ValueError(
                    f"Unsupported mode '{mode}'. Supported modes: {list(SUPPORTED_MODES.keys())}"
                )

            self._mode = mode
            self._data: Dict[Any, Any] = {}
            self._hash: Optional[int] = None

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

            # For immutable mode, compute hash once
            if mode == "immutable":
                self._compute_hash()

        def _compute_hash(self) -> None:
            """Compute hash for immutable mode."""
            if self._mode == "immutable":
                items = tuple(sorted(self._data.items()))
                self._hash = hash(items)

        def _check_mutable(self) -> None:
            """Check if mutation is allowed in current mode."""
            if self._mode in ("immutable", "readonly", "insert"):
                raise ZDictModeError(f"Cannot modify zdict in '{self._mode}' mode")

        def _check_insertable(self) -> None:
            """Check if insertion is allowed in current mode."""
            if self._mode == "readonly":
                raise ZDictModeError(f"Cannot insert into zdict in '{self._mode}' mode")
            elif self._mode == "immutable":
                raise ZDictModeError(f"Cannot modify zdict in '{self._mode}' mode")

        # Core dict interface
        def __getitem__(self, key: Any) -> Any:
            """Get item by key."""
            return self._data[key]

        def __setitem__(self, key: Any, value: Any) -> None:
            """Set item by key."""
            if self._mode == "insert" and key in self._data:
                raise ZDictModeError("Cannot update existing keys in 'insert' mode")

            self._check_insertable()
            self._data[key] = value

        def __delitem__(self, key: Any) -> None:
            """Delete item by key."""
            self._check_mutable()
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
            return f"zdict({dict(self._data)}, mode='{self._mode}')"

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
            """Hash for immutable mode."""
            if self._mode == "immutable":
                if self._hash is None:
                    self._compute_hash()
                return self._hash
            else:
                raise TypeError(f"unhashable type: 'zdict' (mode='{self._mode}')")

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
            self._check_mutable()
            return self._data.pop(key, *args)

        def popitem(self) -> tuple[Any, Any]:
            """Remove and return arbitrary item."""
            self._check_mutable()
            return self._data.popitem()

        def clear(self) -> None:
            """Remove all items."""
            self._check_mutable()
            self._data.clear()

        def update(self, *args: Any, **kwargs: Any) -> None:
            """Update dict with items from another dict or iterable."""
            if self._mode == "readonly":
                raise ZDictModeError("Cannot update zdict in 'readonly' mode")
            elif self._mode == "immutable":
                raise ZDictModeError("Cannot modify zdict in 'immutable' mode")
            elif self._mode == "insert":
                # In insert mode, check that we're not updating existing keys
                update_data = {}
                if args:
                    if len(args) > 1:
                        raise TypeError("update expected at most 1 argument")
                    other = args[0]
                    if hasattr(other, "items"):
                        for key, value in other.items():
                            update_data[key] = value
                    else:
                        for key, value in other:
                            update_data[key] = value

                for key, value in kwargs.items():
                    update_data[key] = value

                for key in update_data:
                    if key in self._data:
                        raise ZDictModeError(
                            "Cannot update existing keys in 'insert' mode"
                        )

                self._data.update(update_data)
            else:
                self._data.update(*args, **kwargs)

        def copy(self) -> "zdict":
            """Return a shallow copy."""
            return zdict(self._data.copy(), mode=self._mode)

        def setdefault(self, key: Any, default: Any = None) -> Any:
            """Insert key with default if not present."""
            if key not in self._data:
                self._check_insertable()
            return self._data.setdefault(key, default)

        # Properties
        @property
        def mode(self) -> str:
            """Return the current mode."""
            return self._mode


# Convenience functions
def mutable_zdict(
    data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None, **kwargs: Any
) -> zdict:
    """Create a mutable zdict."""
    return zdict(data, mode="mutable", **kwargs)


def immutable_zdict(
    data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None, **kwargs: Any
) -> zdict:
    """Create an immutable zdict."""
    return zdict(data, mode="immutable", **kwargs)


def readonly_zdict(
    data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None, **kwargs: Any
) -> zdict:
    """Create a readonly zdict."""
    return zdict(data, mode="readonly", **kwargs)


def insert_zdict(
    data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None, **kwargs: Any
) -> zdict:
    """Create an insert-only zdict."""
    return zdict(data, mode="insert", **kwargs)


def arena_zdict(
    data: Union[Dict[Any, Any], Mapping[Any, Any], None] = None, **kwargs: Any
) -> zdict:
    """Create an arena zdict."""
    return zdict(data, mode="arena", **kwargs)


__all__ = [
    "zdict",
    "ZDictError",
    "ZDictModeError",
    "mutable_zdict",
    "immutable_zdict",
    "readonly_zdict",
    "insert_zdict",
    "arena_zdict",
    "SUPPORTED_MODES",
]

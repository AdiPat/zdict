"""
Comprehensive test suite for zdict.
"""

import pytest
from typing import Any

from zdict import zdict, ZDictError


class TestZDictBasics:
    """Test basic zdict functionality."""
    
    def test_creation_empty(self):
        """Test creating empty zdict."""
        z = zdict()
        assert len(z) == 0
    
    def test_creation_with_dict(self):
        """Test creating zdict from dict."""
        data = {"a": 1, "b": 2}
        z = zdict(data)
        assert len(z) == 2
        assert z["a"] == 1
        assert z["b"] == 2
    
    def test_creation_with_kwargs(self):
        """Test creating zdict with kwargs."""
        z = zdict(a=1, b=2)
        assert len(z) == 2
        assert z["a"] == 1
        assert z["b"] == 2
    
    
    def test_repr(self):
        """Test string representation."""
        z = zdict({"a": 1})
        assert "zdict" in repr(z)
    
    def test_str(self):
        """Test string conversion."""
        z = zdict({"a": 1})
        assert str(z) == "{'a': 1}"


class TestZDictOperations:
    """Test zdict operations and methods."""
    
    def test_getitem_setitem(self):
        """Test get/set operations."""
        z = zdict()
        z["key"] = "value"
        assert z["key"] == "value"
    
    def test_delitem(self):
        """Test deletion."""
        z = zdict({"a": 1, "b": 2})
        del z["a"]
        assert "a" not in z
        assert len(z) == 1
    
    def test_contains(self):
        """Test membership testing."""
        z = zdict({"a": 1})
        assert "a" in z
        assert "b" not in z
    
    def test_iteration(self):
        """Test iteration over keys."""
        z = zdict({"a": 1, "b": 2})
        keys = list(z)
        assert set(keys) == {"a", "b"}
    
    def test_keys_values_items(self):
        """Test view methods."""
        z = zdict({"a": 1, "b": 2})
        assert set(z.keys()) == {"a", "b"}
        assert set(z.values()) == {1, 2}
        assert set(z.items()) == {("a", 1), ("b", 2)}
    
    def test_get(self):
        """Test get method."""
        z = zdict({"a": 1})
        assert z.get("a") == 1
        assert z.get("b") is None
        assert z.get("b", "default") == "default"
    
    def test_pop(self):
        """Test pop method."""
        z = zdict({"a": 1, "b": 2})
        value = z.pop("a")
        assert value == 1
        assert "a" not in z
        
        with pytest.raises(KeyError):
            z.pop("nonexistent")
        
        assert z.pop("nonexistent", "default") == "default"
    
    def test_popitem(self):
        """Test popitem method."""
        z = zdict({"a": 1})
        key, value = z.popitem()
        assert key == "a"
        assert value == 1
        assert len(z) == 0
    
    def test_clear(self):
        """Test clear method."""
        z = zdict({"a": 1, "b": 2})
        z.clear()
        assert len(z) == 0
    
    def test_update(self):
        """Test update method."""
        z = zdict({"a": 1})
        z.update({"b": 2, "c": 3})
        assert len(z) == 3
        assert z["b"] == 2
        assert z["c"] == 3
        
        z.update([("d", 4)]) 
        assert z["d"] == 4
        
        z.update(e=5)
        assert z["e"] == 5
    
    def test_copy(self):
        """Test copy method."""
        z = zdict({"a": 1, "b": 2})
        z_copy = z.copy()
        assert z_copy == z
        assert z_copy is not z
    
    def test_setdefault(self):
        """Test setdefault method."""
        z = zdict({"a": 1})
        assert z.setdefault("a", 99) == 1
        assert z.setdefault("b", 2) == 2
        assert z["b"] == 2
    
    def test_equality(self):
        """Test equality comparison."""
        z1 = zdict({"a": 1, "b": 2})
        z2 = zdict({"a": 1, "b": 2})
        regular_dict = {"a": 1, "b": 2}
        
        assert z1 == z2
        assert z1 == regular_dict
        assert z1 != {"a": 1}
        assert z1 != "not a dict"

class TestZDictEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_keyerror_on_missing_key(self):
        """Test KeyError is raised for missing keys."""
        z = zdict()
        with pytest.raises(KeyError):
            _ = z["missing"]
    
    def test_empty_popitem_error(self):
        """Test popitem on empty dict raises error."""
        z = zdict()
        with pytest.raises(KeyError):
            z.popitem()
    
    
    def test_creation_from_iterable(self):
        """Test creating zdict from iterable of pairs."""
        data = [("a", 1), ("b", 2)]
        z = zdict(data)
        assert z["a"] == 1
        assert z["b"] == 2
    
    def test_hashable(self):
        """Test that zdict is not hashable (like regular dict)."""
        z = zdict({"a": 1})
        with pytest.raises(TypeError, match="unhashable"):
            hash(z)


if __name__ == "__main__":
    pytest.main([__file__])
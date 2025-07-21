"""
Comprehensive test suite for zdict.
"""

import pytest
from typing import Any

from zdict import (
    zdict, 
    ZDictError, 
    ZDictModeError,
    mutable_zdict,
    immutable_zdict,
    readonly_zdict,
    insert_zdict, 
    arena_zdict,
    SUPPORTED_MODES,
    _C_EXTENSION_AVAILABLE
)

# C extension uses TypeError instead of ZDictModeError  
ModeError = TypeError if _C_EXTENSION_AVAILABLE else ZDictModeError


class TestZDictBasics:
    """Test basic zdict functionality."""
    
    def test_creation_empty(self):
        """Test creating empty zdict."""
        z = zdict()
        assert len(z) == 0
        assert z.mode == "mutable"
    
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
    
    def test_creation_with_mode(self):
        """Test creating zdict with specific mode."""
        z = zdict({"a": 1}, mode="immutable")
        assert z.mode == "immutable"
    
    def test_invalid_mode(self):
        """Test creating zdict with invalid mode."""
        with pytest.raises(ValueError, match="Unsupported mode"):
            zdict(mode="invalid")
    
    def test_repr(self):
        """Test string representation."""
        z = zdict({"a": 1}, mode="mutable")
        assert "zdict" in repr(z)
        assert "mutable" in repr(z)
    
    def test_str(self):
        """Test string conversion."""
        z = zdict({"a": 1})
        assert str(z) == "{'a': 1}"


class TestZDictMutableMode:
    """Test mutable mode functionality."""
    
    def test_getitem_setitem(self):
        """Test get/set operations."""
        z = zdict(mode="mutable")
        z["key"] = "value"
        assert z["key"] == "value"
    
    def test_delitem(self):
        """Test deletion."""
        z = zdict({"a": 1, "b": 2}, mode="mutable")
        del z["a"]
        assert "a" not in z
        assert len(z) == 1
    
    def test_contains(self):
        """Test membership testing."""
        z = zdict({"a": 1}, mode="mutable")
        assert "a" in z
        assert "b" not in z
    
    def test_iteration(self):
        """Test iteration over keys."""
        z = zdict({"a": 1, "b": 2}, mode="mutable")
        keys = list(z)
        assert set(keys) == {"a", "b"}
    
    def test_keys_values_items(self):
        """Test view methods."""
        z = zdict({"a": 1, "b": 2}, mode="mutable")
        assert set(z.keys()) == {"a", "b"}
        assert set(z.values()) == {1, 2}
        assert set(z.items()) == {("a", 1), ("b", 2)}
    
    def test_get(self):
        """Test get method."""
        z = zdict({"a": 1}, mode="mutable")
        assert z.get("a") == 1
        assert z.get("b") is None
        assert z.get("b", "default") == "default"
    
    def test_pop(self):
        """Test pop method."""
        z = zdict({"a": 1, "b": 2}, mode="mutable")
        value = z.pop("a")
        assert value == 1
        assert "a" not in z
        
        with pytest.raises(KeyError):
            z.pop("nonexistent")
        
        assert z.pop("nonexistent", "default") == "default"
    
    def test_popitem(self):
        """Test popitem method."""
        z = zdict({"a": 1}, mode="mutable")
        key, value = z.popitem()
        assert key == "a"
        assert value == 1
        assert len(z) == 0
    
    def test_clear(self):
        """Test clear method."""
        z = zdict({"a": 1, "b": 2}, mode="mutable")
        z.clear()
        assert len(z) == 0
    
    def test_update(self):
        """Test update method."""
        z = zdict({"a": 1}, mode="mutable")
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
        z = zdict({"a": 1, "b": 2}, mode="mutable")
        z_copy = z.copy()
        assert z_copy == z
        assert z_copy is not z
        assert z_copy.mode == z.mode
    
    def test_setdefault(self):
        """Test setdefault method."""
        z = zdict({"a": 1}, mode="mutable")
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


class TestZDictImmutableMode:
    """Test immutable mode functionality."""
    
    def test_creation(self):
        """Test creating immutable zdict."""
        z = zdict({"a": 1, "b": 2}, mode="immutable")
        assert z.mode == "immutable"
        assert z["a"] == 1
    
    def test_hashable(self):
        """Test that immutable zdict is hashable."""
        z = zdict({"a": 1, "b": 2}, mode="immutable")
        hash_value = hash(z)
        assert isinstance(hash_value, int)
        
        # Same data should have same hash
        z2 = zdict({"a": 1, "b": 2}, mode="immutable")
        assert hash(z) == hash(z2)
    
    def test_can_be_dict_key(self):
        """Test that immutable zdict can be used as dict key."""
        z = zdict({"a": 1}, mode="immutable")
        d = {z: "value"}
        assert d[z] == "value"
    
    def test_mutation_forbidden(self):
        """Test that mutation operations raise errors."""
        z = zdict({"a": 1}, mode="immutable")
        
        with pytest.raises(ModeError):
            z["b"] = 2
        
        with pytest.raises(ModeError):
            del z["a"]
        
        with pytest.raises(ModeError):
            z.clear()
        
        with pytest.raises(ModeError):
            z.pop("a")
        
        with pytest.raises(ModeError):
            z.popitem()
        
        with pytest.raises(ModeError):
            z.update({"b": 2})
    
    def test_read_operations_work(self):
        """Test that read operations still work."""
        z = zdict({"a": 1, "b": 2}, mode="immutable")
        assert z["a"] == 1
        assert "a" in z
        assert len(z) == 2
        assert list(z.keys()) == ["a", "b"]
        assert z.get("a") == 1
    
    def test_mutable_hash_error(self):
        """Test that mutable modes can't be hashed."""
        z = zdict({"a": 1}, mode="mutable")
        with pytest.raises(TypeError, match="unhashable"):
            hash(z)


class TestZDictReadonlyMode:
    """Test readonly mode functionality."""
    
    def test_creation(self):
        """Test creating readonly zdict."""
        z = zdict({"a": 1, "b": 2}, mode="readonly")
        assert z.mode == "readonly"
        assert z["a"] == 1
    
    def test_mutation_forbidden(self):
        """Test that mutation operations raise errors."""
        z = zdict({"a": 1}, mode="readonly")
        
        with pytest.raises(ModeError):
            z["b"] = 2
        
        with pytest.raises(ModeError):
            del z["a"]
        
        with pytest.raises(ModeError):
            z.clear()
        
        with pytest.raises(ModeError):
            z.pop("a")
        
        with pytest.raises(ModeError):
            z.update({"b": 2})
    
    def test_not_hashable(self):
        """Test that readonly zdict is not hashable."""
        z = zdict({"a": 1}, mode="readonly")
        with pytest.raises(TypeError, match="unhashable"):
            hash(z)


class TestZDictInsertMode:
    """Test insert-only mode functionality."""
    
    def test_creation(self):
        """Test creating insert-only zdict."""
        z = zdict({"a": 1}, mode="insert")
        assert z.mode == "insert"
        assert z["a"] == 1
    
    def test_insert_new_keys(self):
        """Test inserting new keys works."""
        z = zdict(mode="insert")
        z["a"] = 1
        z["b"] = 2
        assert z["a"] == 1
        assert z["b"] == 2
    
    def test_update_existing_forbidden(self):
        """Test that updating existing keys is forbidden."""
        z = zdict({"a": 1}, mode="insert")
        
        with pytest.raises(ModeError, match="Cannot update existing keys"):
            z["a"] = 2
    
    def test_deletion_forbidden(self):
        """Test that deletion is forbidden."""
        z = zdict({"a": 1}, mode="insert")
        
        with pytest.raises(ModeError):
            del z["a"]
        
        with pytest.raises(ModeError):
            z.pop("a")
        
        with pytest.raises(ModeError):
            z.clear()
    
    def test_update_with_new_keys(self):
        """Test update with new keys works."""
        z = zdict({"a": 1}, mode="insert")
        z.update({"b": 2, "c": 3})
        assert z["b"] == 2
        assert z["c"] == 3
    
    def test_update_with_existing_keys_forbidden(self):
        """Test update with existing keys is forbidden."""
        z = zdict({"a": 1}, mode="insert")
        
        with pytest.raises(ModeError, match="Cannot update existing keys"):
            z.update({"a": 2, "b": 3})


class TestZDictArenaMode:
    """Test arena mode functionality."""
    
    def test_creation(self):
        """Test creating arena zdict."""
        z = zdict({"a": 1, "b": 2}, mode="arena")
        assert z.mode == "arena"
        assert z["a"] == 1
    
    def test_behaves_like_mutable(self):
        """Test that arena mode behaves like mutable for now."""
        z = zdict(mode="arena")
        z["a"] = 1
        z["a"] = 2  # Should allow updates
        del z["a"]
        assert len(z) == 0


class TestConvenienceFunctions:
    """Test convenience factory functions."""
    
    def test_mutable_zdict(self):
        """Test mutable_zdict function."""
        z = mutable_zdict({"a": 1})
        assert z.mode == "mutable"
        assert z["a"] == 1
    
    def test_immutable_zdict(self):
        """Test immutable_zdict function."""
        z = immutable_zdict({"a": 1})
        assert z.mode == "immutable"
        assert z["a"] == 1
        assert isinstance(hash(z), int)
    
    def test_readonly_zdict(self):
        """Test readonly_zdict function."""
        z = readonly_zdict({"a": 1})
        assert z.mode == "readonly"
        assert z["a"] == 1
    
    def test_insert_zdict(self):
        """Test insert_zdict function."""
        z = insert_zdict({"a": 1})
        assert z.mode == "insert"
        assert z["a"] == 1
    
    def test_arena_zdict(self):
        """Test arena_zdict function."""
        z = arena_zdict({"a": 1})
        assert z.mode == "arena"
        assert z["a"] == 1


class TestZDictEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_keyerror_on_missing_key(self):
        """Test KeyError is raised for missing keys."""
        z = zdict()
        with pytest.raises(KeyError):
            _ = z["missing"]
    
    def test_empty_popitem_error(self):
        """Test popitem on empty dict raises error."""
        z = zdict(mode="mutable")
        with pytest.raises(KeyError):
            z.popitem()
    
    def test_supported_modes_constant(self):
        """Test SUPPORTED_MODES constant."""
        assert "mutable" in SUPPORTED_MODES
        assert "immutable" in SUPPORTED_MODES
        assert "readonly" in SUPPORTED_MODES
        assert "insert" in SUPPORTED_MODES
        assert "arena" in SUPPORTED_MODES
    
    def test_creation_from_iterable(self):
        """Test creating zdict from iterable of pairs."""
        data = [("a", 1), ("b", 2)]
        z = zdict(data)
        assert z["a"] == 1
        assert z["b"] == 2
    
    def test_setdefault_insert_mode(self):
        """Test setdefault in insert mode."""
        z = zdict({"a": 1}, mode="insert")
        assert z.setdefault("a", 99) == 1  # Existing key
        assert z.setdefault("b", 2) == 2   # New key
        assert z["b"] == 2
    
    def test_setdefault_readonly_mode(self):
        """Test setdefault in readonly mode."""
        z = zdict({"a": 1}, mode="readonly")
        assert z.setdefault("a", 99) == 1  # Existing key should work
        
        with pytest.raises(ModeError):
            z.setdefault("b", 2)  # New key should fail


if __name__ == "__main__":
    pytest.main([__file__])
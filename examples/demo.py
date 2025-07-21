#!/usr/bin/env python3
"""
zdict Demo - Basic usage and performance comparison.
"""

import time
from zdict import zdict, _C_EXTENSION_AVAILABLE


def separator(title):
    """Print a formatted separator."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def demo_basic_usage():
    """Demonstrate basic dict-compatible usage."""
    separator("Basic Usage - Drop-in Replacement")
    
    # Creating a zdict
    data = zdict({'name': 'Alice', 'age': 30, 'city': 'NYC'})
    print(f"Created: {data}")
    
    # Standard dict operations
    data['email'] = 'alice@example.com'
    print(f"After adding email: {data}")
    
    # Check membership
    print(f"Has 'name' key: {'name' in data}")
    print(f"Has 'phone' key: {'phone' in data}")
    
    # Iteration
    print("\nIterating over items:")
    for key, value in data.items():
        print(f"  {key}: {value}")


def demo_dict_methods():
    """Demonstrate various dict methods."""
    separator("Dictionary Methods")
    
    # Create sample data
    d = zdict({'a': 1, 'b': 2, 'c': 3})
    print(f"Original: {d}")
    
    # get() method
    print(f"\nget('a'): {d.get('a')}")
    print(f"get('z', 99): {d.get('z', 99)}")
    
    # pop() method
    value = d.pop('b')
    print(f"\nAfter pop('b'): {d}, popped value: {value}")
    
    # update() method
    d.update({'d': 4, 'e': 5})
    print(f"After update: {d}")
    
    # setdefault() method
    d.setdefault('f', 6)
    d.setdefault('a', 100)  # Won't change existing value
    print(f"After setdefault: {d}")
    
    # copy() method
    d_copy = d.copy()
    d_copy['g'] = 7
    print(f"\nOriginal after copy modification: {d}")
    print(f"Copy: {d_copy}")


def demo_performance_comparison():
    """Compare performance with built-in dict."""
    separator("Performance Comparison")
    
    print("⚠️  Note: This is a simple demo. Use base_benchmark.py for detailed analysis.\n")
    
    # Test data
    test_size = 10000
    test_data = {f'key_{i}': f'value_{i}' for i in range(test_size)}
    
    # Time dict creation
    start = time.perf_counter()
    regular = dict(test_data)
    dict_time = time.perf_counter() - start
    
    start = time.perf_counter()
    z = zdict(test_data)
    zdict_time = time.perf_counter() - start
    
    print(f"Creation time ({test_size} items):")
    print(f"  dict:  {dict_time*1000:.2f} ms")
    print(f"  zdict: {zdict_time*1000:.2f} ms")
    
    # Time lookups
    lookup_keys = list(test_data.keys())[:100]
    
    start = time.perf_counter()
    for _ in range(1000):
        for key in lookup_keys:
            _ = regular[key]
    dict_lookup_time = time.perf_counter() - start
    
    start = time.perf_counter()
    for _ in range(1000):
        for key in lookup_keys:
            _ = z[key]
    zdict_lookup_time = time.perf_counter() - start
    
    print(f"\nLookup time (100k lookups):")
    print(f"  dict:  {dict_lookup_time*1000:.2f} ms")
    print(f"  zdict: {zdict_lookup_time*1000:.2f} ms")


def demo_type_compatibility():
    """Demonstrate type compatibility with dict."""
    separator("Type Compatibility")
    
    z = zdict({'x': 1, 'y': 2})
    d = {'x': 1, 'y': 2}
    
    # Equality comparison
    print(f"zdict == dict: {z == d}")
    print(f"dict == zdict: {d == z}")
    
    # Can be used where dict is expected
    def process_dict(data: dict) -> int:
        return sum(data.values())
    
    print(f"\nPassing zdict to function expecting dict:")
    print(f"Sum of values: {process_dict(z)}")
    
    # JSON serialization (via dict conversion)
    import json
    json_str = json.dumps(dict(z))
    print(f"\nJSON serialization: {json_str}")


def main():
    """Run all demonstrations."""
    print("🚀 zdict Demo - Experimental Dictionary Implementation")
    print(f"C Extension Available: {_C_EXTENSION_AVAILABLE}")
    
    demo_basic_usage()
    demo_dict_methods()
    demo_type_compatibility()
    demo_performance_comparison()
    
    separator("Demo Complete!")
    print("\n⚠️  Remember: zdict is experimental. Always benchmark with your use case!")
    print("Run 'python base_benchmark.py --num-experiments 5' for detailed performance analysis.")
    print("\nFor more information, visit: https://github.com/AdiPat/zdict")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
zdict Demo - Showcasing performance modes and features.
"""

import time
from uuid import uuid4
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


def demo_immutable_mode():
    """Demonstrate immutable mode features."""
    separator("Immutable Mode - Hashable Dictionaries")
    
    # Create immutable zdict
    config1 = zdict({'host': 'localhost', 'port': 8080}, mode='immutable')
    config2 = zdict({'host': 'localhost', 'port': 8080}, mode='immutable')
    
    print(f"Config 1: {config1}")
    print(f"Config 2: {config2}")
    print(f"Configs are equal: {config1 == config2}")
    print(f"Same hash: {hash(config1) == hash(config2)}")
    
    # Use as dict key
    cache = {}
    cache[config1] = "cached_connection"
    print(f"\nUsing as dict key: {cache}")
    
    # Immutability demonstration
    try:
        config1['port'] = 9090
    except TypeError as e:
        print(f"\nCannot modify: {e}")


def demo_readonly_performance():
    """Demonstrate readonly mode performance."""
    separator("Readonly Mode - Optimized Lookups")
    
    # Create large dataset
    size = 10000
    data = {f'key_{i}': f'value_{i}' for i in range(size)}
    
    # Regular dict
    regular = dict(data)
    
    # Readonly zdict
    readonly = zdict(data, mode='readonly')
    
    # Benchmark lookups
    lookup_keys = [f'key_{i}' for i in range(0, size, 100)]
    
    # Time regular dict
    start = time.perf_counter()
    for _ in range(1000):
        for key in lookup_keys:
            _ = regular[key]
    regular_time = time.perf_counter() - start
    
    # Time readonly zdict
    start = time.perf_counter()
    for _ in range(1000):
        for key in lookup_keys:
            _ = readonly[key]
    readonly_time = time.perf_counter() - start
    
    print(f"Dataset size: {size:,} items")
    print(f"Regular dict time: {regular_time:.4f}s")
    print(f"Readonly zdict time: {readonly_time:.4f}s")
    print(f"Performance gain: {regular_time/readonly_time:.2f}x")


def demo_insert_mode():
    """Demonstrate insert-only mode."""
    separator("Insert Mode - Append-Only Operations")
    
    # Create log storage
    log = zdict(mode='insert')
    
    # Add log entries
    for i in range(5):
        entry_id = str(uuid4())
        log[entry_id] = {
            'timestamp': time.time(),
            'message': f'Event {i} occurred',
            'level': 'INFO'
        }
        print(f"Added log entry: {entry_id[:8]}...")
    
    print(f"\nTotal entries: {len(log)}")
    
    # Try to update (will fail)
    first_key = next(iter(log))
    try:
        log[first_key] = {'modified': True}
    except TypeError as e:
        print(f"\nCannot update: {e}")


def demo_arena_mode():
    """Demonstrate arena mode."""
    separator("Arena Mode - Pre-allocated Memory")
    
    # Create sensor data storage
    sensors = zdict(mode='arena')
    
    # Initialize with sensor readings
    sensor_count = 100
    for i in range(sensor_count):
        sensors[f'sensor_{i:03d}'] = {
            'temperature': 20.0 + i * 0.1,
            'humidity': 45.0 + i * 0.2,
            'pressure': 1013.25
        }
    
    print(f"Initialized {sensor_count} sensors")
    print(f"Sample reading: sensor_050 = {sensors['sensor_050']}")
    
    # Update readings (allowed in arena mode)
    sensors['sensor_050']['temperature'] = 25.5
    print(f"Updated reading: sensor_050 = {sensors['sensor_050']}")


def demo_performance_comparison():
    """Compare performance across modes."""
    separator("Performance Comparison")
    
    # Test data
    test_size = 5000
    test_data = {f'key_{i}': f'value_{i}' for i in range(test_size)}
    
    modes = ['mutable', 'immutable', 'readonly', 'insert', 'arena']
    results = {}
    
    print(f"Testing with {test_size:,} items...\n")
    
    for mode in modes:
        # Create zdict
        if mode == 'insert':
            z = zdict(mode=mode)
            # Time insertions
            start = time.perf_counter()
            for k, v in test_data.items():
                z[k] = v
            creation_time = time.perf_counter() - start
        else:
            start = time.perf_counter()
            z = zdict(test_data, mode=mode)
            creation_time = time.perf_counter() - start
        
        # Time lookups
        lookup_keys = list(test_data.keys())[:100]
        start = time.perf_counter()
        for _ in range(1000):
            for key in lookup_keys:
                _ = z[key]
        lookup_time = time.perf_counter() - start
        
        results[mode] = {
            'creation': creation_time,
            'lookup': lookup_time
        }
    
    # Display results
    print(f"{'Mode':<12} {'Creation (ms)':<15} {'Lookup (ms)':<15}")
    print("-" * 42)
    for mode, times in results.items():
        print(f"{mode:<12} {times['creation']*1000:<15.2f} {times['lookup']*1000:<15.2f}")


def main():
    """Run all demonstrations."""
    print("🚀 zdict Demo - High-Performance Dictionary Implementation")
    print(f"C Extension Available: {_C_EXTENSION_AVAILABLE}")
    
    demo_basic_usage()
    demo_immutable_mode()
    demo_readonly_performance()
    demo_insert_mode()
    demo_arena_mode()
    demo_performance_comparison()
    
    separator("Demo Complete!")
    print("\nFor more information, visit: https://github.com/AdiPat/zdict")


if __name__ == "__main__":
    main()
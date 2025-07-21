"""
Benchmark suite comparing zdict performance against built-in dict and other implementations.
"""

import time
import sys
import statistics
from typing import Dict, Any, List, Callable
import gc

try:
    import pyperf  # type: ignore[import]
    PYPERF_AVAILABLE = True
except ImportError:
    PYPERF_AVAILABLE = False

try:
    import immutables  # type: ignore[import]
    IMMUTABLES_AVAILABLE = True
except ImportError:
    IMMUTABLES_AVAILABLE = False

try:
    import frozendict  # type: ignore[import]
    FROZENDICT_AVAILABLE = True
except ImportError:
    FROZENDICT_AVAILABLE = False

from zdict import zdict, mutable_zdict, immutable_zdict, readonly_zdict, insert_zdict


def time_function(func: Callable, iterations: int = 1000) -> float:
    """Time a function over multiple iterations."""
    times = []
    for _ in range(iterations):
        gc.collect()  # Minimize GC effects
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)
    
    return statistics.mean(times)


def benchmark_lookup_performance():
    """Benchmark lookup performance across different sizes."""
    print("=== Lookup Performance Benchmark ===")
    
    sizes = [1, 10, 100, 1000, 10000]
    
    for size in sizes:
        print(f"\nSize: {size} elements")
        
        # Create test data
        data = {f"key_{i}": i for i in range(size)}
        lookup_key = f"key_{size//2}"  # Middle key
        
        # Test implementations
        implementations = [
            ("dict", dict(data)),
            ("zdict(mutable)", zdict(data, mode="mutable")),
            ("zdict(readonly)", zdict(data, mode="readonly")),
            ("zdict(immutable)", zdict(data, mode="immutable")),
        ]
        
        if IMMUTABLES_AVAILABLE:
            implementations.append(("immutables.Map", immutables.Map(data)))
        
        if FROZENDICT_AVAILABLE:
            implementations.append(("frozendict", frozendict.frozendict(data)))
        
        results = []
        for name, impl in implementations:
            def lookup_test():
                return impl[lookup_key]
            
            avg_time = time_function(lookup_test, iterations=10000)
            results.append((name, avg_time))
        
        # Sort by performance
        results.sort(key=lambda x: x[1])
        
        print(f"{'Implementation':<20} {'Time (μs)':<12} {'Relative':<10}")
        print("-" * 45)
        
        baseline_time = results[0][1]
        for name, avg_time in results:
            relative = avg_time / baseline_time
            print(f"{name:<20} {avg_time*1e6:<12.2f} {relative:<10.2f}x")


def benchmark_insertion_performance():
    """Benchmark insertion performance."""
    print("\n=== Insertion Performance Benchmark ===")
    
    sizes = [100, 1000, 10000]
    
    for size in sizes:
        print(f"\nInserting {size} elements")
        
        implementations = [
            ("dict", lambda: dict()),
            ("zdict(mutable)", lambda: zdict(mode="mutable")),
            ("zdict(insert)", lambda: zdict(mode="insert")),
        ]
        
        results = []
        for name, factory in implementations:
            def insert_test():
                d = factory()
                for i in range(size):
                    d[f"key_{i}"] = i
                return d
            
            avg_time = time_function(insert_test, iterations=100)
            results.append((name, avg_time))
        
        results.sort(key=lambda x: x[1])
        
        print(f"{'Implementation':<20} {'Time (ms)':<12} {'Relative':<10}")
        print("-" * 45)
        
        baseline_time = results[0][1]
        for name, avg_time in results:
            relative = avg_time / baseline_time
            print(f"{name:<20} {avg_time*1e3:<12.2f} {relative:<10.2f}x")


def benchmark_update_performance():
    """Benchmark update performance."""
    print("\n=== Update Performance Benchmark ===")
    
    base_size = 1000
    update_size = 500
    
    # Create test data
    base_data = {f"key_{i}": i for i in range(base_size)}
    update_data = {f"new_key_{i}": i for i in range(update_size)}
    
    implementations = [
        ("dict", dict(base_data)),
        ("zdict(mutable)", zdict(base_data, mode="mutable")),
    ]
    
    results = []
    for name, impl in implementations:
        def update_test():
            d = impl.copy()
            d.update(update_data)
            return d
        
        avg_time = time_function(update_test, iterations=1000)
        results.append((name, avg_time))
    
    results.sort(key=lambda x: x[1])
    
    print(f"{'Implementation':<20} {'Time (μs)':<12} {'Relative':<10}")
    print("-" * 45)
    
    baseline_time = results[0][1]
    for name, avg_time in results:
        relative = avg_time / baseline_time
        print(f"{name:<20} {avg_time*1e6:<12.2f} {relative:<10.2f}x")


def benchmark_memory_usage():
    """Benchmark memory usage (simplified)."""
    print("\n=== Memory Usage Benchmark ===")
    
    size = 10000
    data = {f"key_{i}": i for i in range(size)}
    
    implementations = [
        ("dict", dict(data)),
        ("zdict(mutable)", zdict(data, mode="mutable")),
        ("zdict(readonly)", zdict(data, mode="readonly")),
        ("zdict(immutable)", zdict(data, mode="immutable")),
    ]
    
    print(f"Memory usage comparison for {size} elements:")
    print("(Note: This is a simplified estimate)")
    
    for name, impl in implementations:
        # Simple size estimation
        print(f"{name:<20} ~{sys.getsizeof(impl)} bytes")


def benchmark_iteration_performance():
    """Benchmark iteration performance."""
    print("\n=== Iteration Performance Benchmark ===")
    
    size = 10000
    data = {f"key_{i}": i for i in range(size)}
    
    implementations = [
        ("dict", dict(data)),
        ("zdict(mutable)", zdict(data, mode="mutable")),
        ("zdict(readonly)", zdict(data, mode="readonly")),
    ]
    
    # Test different iteration patterns
    patterns = [
        ("keys()", lambda d: list(d.keys())),
        ("values()", lambda d: list(d.values())),
        ("items()", lambda d: list(d.items())),
        ("iter keys", lambda d: [k for k in d]),
    ]
    
    for pattern_name, pattern_func in patterns:
        print(f"\nIteration pattern: {pattern_name}")
        
        results = []
        for name, impl in implementations:
            def iter_test():
                return pattern_func(impl)
            
            avg_time = time_function(iter_test, iterations=100)
            results.append((name, avg_time))
        
        results.sort(key=lambda x: x[1])
        
        print(f"{'Implementation':<20} {'Time (ms)':<12} {'Relative':<10}")
        print("-" * 45)
        
        baseline_time = results[0][1]
        for name, avg_time in results:
            relative = avg_time / baseline_time
            print(f"{name:<20} {avg_time*1e3:<12.2f} {relative:<10.2f}x")


def run_workload_benchmarks():
    """Run specific workload benchmarks."""
    print("\n=== Workload-Specific Benchmarks ===")
    
    # JSON-like workload
    print("\nJSON-like parsing workload:")
    json_data = {
        "users": [
            {"id": i, "name": f"user_{i}", "active": i % 2 == 0}
            for i in range(1000)
        ],
        "metadata": {"count": 1000, "version": "1.0"},
        "config": {"debug": True, "timeout": 30}
    }
    
    def json_workload(factory):
        def test():
            d = factory()
            d["users"] = json_data["users"]
            d["metadata"] = json_data["metadata"] 
            d["config"] = json_data["config"]
            
            # Access patterns
            user_count = len(d["users"])
            is_debug = d["config"]["debug"]
            version = d["metadata"]["version"]
            
            return user_count, is_debug, version
        return test
    
    implementations = [
        ("dict", lambda: dict()),
        ("zdict(mutable)", lambda: zdict(mode="mutable")),
        ("zdict(readonly)", lambda: readonly_zdict(json_data)),
    ]
    
    results = []
    for name, factory in implementations:
        if "readonly" in name:
            # For readonly, just test access
            def test():
                d = factory()
                user_count = len(d["users"])
                is_debug = d["config"]["debug"]
                version = d["metadata"]["version"]
                return user_count, is_debug, version
        else:
            test = json_workload(factory)
        
        avg_time = time_function(test, iterations=1000)
        results.append((name, avg_time))
    
    results.sort(key=lambda x: x[1])
    
    print(f"{'Implementation':<20} {'Time (μs)':<12} {'Relative':<10}")
    print("-" * 45)
    
    baseline_time = results[0][1]
    for name, avg_time in results:
        relative = avg_time / baseline_time
        print(f"{name:<20} {avg_time*1e6:<12.2f} {relative:<10.2f}x")


def main():
    """Run all benchmarks."""
    print("🚀 zdict Performance Benchmark Suite")
    print("=" * 50)
    
    if not PYPERF_AVAILABLE:
        print("Note: pyperf not available, using simplified timing")
    if not IMMUTABLES_AVAILABLE:
        print("Note: immutables not available, skipping immutables.Map tests")
    if not FROZENDICT_AVAILABLE:
        print("Note: frozendict not available, skipping frozendict tests")
    
    print()
    
    benchmark_lookup_performance()
    benchmark_insertion_performance()
    benchmark_update_performance()
    benchmark_iteration_performance()
    benchmark_memory_usage()
    run_workload_benchmarks()
    
    print("\n" + "=" * 50)
    print("Benchmark complete! 🎯")
    print("\nNote: Results may vary based on system configuration.")
    print("For production benchmarking, consider using pyperf and profiling tools.")


if __name__ == "__main__":
    main()
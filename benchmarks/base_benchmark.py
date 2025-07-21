#!/usr/bin/env python3
"""
Simple benchmark comparing dict vs zdict performance.
Tests insertion and lookup operations with configurable parameters.
"""

import time
import random
import argparse
import gc
from statistics import mean, stdev

# Import zdict
from zdict import zdict, _C_EXTENSION_AVAILABLE


def benchmark_insertions(dict_type, num_insertions):
    """Benchmark insertion of n entries into an empty dict."""
    # Prepare data
    keys = [f"key_{i:06d}" for i in range(num_insertions)]
    values = [f"value_{i:06d}" for i in range(num_insertions)]

    # Force garbage collection
    gc.collect()

    # Time the insertions
    start_time = time.perf_counter()

    if dict_type == dict:
        d = dict()
        for k, v in zip(keys, values):
            d[k] = v
    else:
        d = zdict()
        for k, v in zip(keys, values):
            d[k] = v

    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time_per_op = total_time / num_insertions

    return d, total_time, avg_time_per_op


def benchmark_lookups(d, num_lookups, num_keys):
    """Benchmark random lookups with coverage of all keys."""
    keys = list(d.keys())
    lookup_times = []

    # Create lookup sequence
    lookups_per_key = num_lookups // num_keys
    extra_lookups = num_lookups % num_keys

    lookup_sequence = []
    for key in keys:
        # Random count between 0 and 10 for each key
        count = random.randint(0, 10)
        lookup_sequence.extend([key] * count)

    # Shuffle to randomize access pattern
    random.shuffle(lookup_sequence)

    # Ensure we have exactly num_lookups
    if len(lookup_sequence) > num_lookups:
        lookup_sequence = lookup_sequence[:num_lookups]
    else:
        # Add more random lookups to reach num_lookups
        while len(lookup_sequence) < num_lookups:
            lookup_sequence.append(random.choice(keys))

    # Benchmark lookups
    gc.collect()

    # Measure individual operations for worst/best case
    for key in lookup_sequence[:1000]:  # Sample first 1000 for individual timing
        start = time.perf_counter()
        _ = d[key]
        end = time.perf_counter()
        lookup_times.append(end - start)

    # Measure total time for all lookups
    start_time = time.perf_counter()
    for key in lookup_sequence:
        _ = d[key]
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time_per_op = total_time / num_lookups

    if lookup_times:
        worst_case = max(lookup_times)
        best_case = min(lookup_times)
    else:
        worst_case = avg_time_per_op
        best_case = avg_time_per_op

    return total_time, avg_time_per_op, worst_case, best_case


def main():
    parser = argparse.ArgumentParser(description="Benchmark dict vs zdict")
    parser.add_argument(
        "--insertions",
        type=int,
        default=100000,
        help="Number of insertions (default: 100k)",
    )
    parser.add_argument(
        "--lookups", type=int, default=500000, help="Number of lookups (default: 500k)"
    )
    parser.add_argument(
        "--num-experiments",
        type=int,
        default=1,
        help="Number of experiments to run and average (default: 1)",
    )
    args = parser.parse_args()

    print(f"🚀 dict vs zdict Performance Benchmark")
    print(f"=" * 60)
    print(f"Implementation: {'C Extension' if _C_EXTENSION_AVAILABLE else 'Pure Python Fallback'}")
    print(f"Insertions: {args.insertions:,}")
    print(f"Lookups: {args.lookups:,}")
    print(f"Experiments: {args.num_experiments}")
    print()

    # Storage for results across experiments
    dict_insert_avgs = []
    dict_lookup_avgs = []
    dict_worsts = []
    dict_bests = []

    zdict_insert_avgs = []
    zdict_lookup_avgs = []
    zdict_worsts = []
    zdict_bests = []

    # Run experiments
    for exp_num in range(args.num_experiments):
        if args.num_experiments > 1:
            print(f"\n📊 Running experiment {exp_num + 1}/{args.num_experiments}...")

        # Benchmark dict
        print("  Testing dict...")
        dict_instance, dict_insert_total, dict_insert_avg = benchmark_insertions(
            dict, args.insertions
        )
        dict_lookup_total, dict_lookup_avg, dict_worst, dict_best = benchmark_lookups(
            dict_instance, args.lookups, args.insertions
        )

        dict_insert_avgs.append(dict_insert_avg)
        dict_lookup_avgs.append(dict_lookup_avg)
        dict_worsts.append(dict_worst)
        dict_bests.append(dict_best)

        # Benchmark zdict
        print("  Testing zdict...")
        zdict_instance, zdict_insert_total, zdict_insert_avg = benchmark_insertions(
            zdict, args.insertions
        )
        zdict_lookup_total, zdict_lookup_avg, zdict_worst, zdict_best = (
            benchmark_lookups(zdict_instance, args.lookups, args.insertions)
        )

        zdict_insert_avgs.append(zdict_insert_avg)
        zdict_lookup_avgs.append(zdict_lookup_avg)
        zdict_worsts.append(zdict_worst)
        zdict_bests.append(zdict_best)

    # Calculate averages
    dict_insert_avg = mean(dict_insert_avgs)
    dict_lookup_avg = mean(dict_lookup_avgs)
    dict_worst = mean(dict_worsts)
    dict_best = mean(dict_bests)

    zdict_insert_avg = mean(zdict_insert_avgs)
    zdict_lookup_avg = mean(zdict_lookup_avgs)
    zdict_worst = mean(zdict_worsts)
    zdict_best = mean(zdict_bests)

    # Calculate performance deltas
    insert_delta = ((dict_insert_avg - zdict_insert_avg) / dict_insert_avg) * 100
    lookup_delta = ((dict_lookup_avg - zdict_lookup_avg) / dict_lookup_avg) * 100
    worst_case_delta = ((dict_worst - zdict_worst) / dict_worst) * 100
    best_case_delta = (
        ((dict_best - zdict_best) / dict_best) * 100 if dict_best != 0 else 0
    )

    # Print results
    print("\n" + "=" * 60)
    print("📈 RESULTS")
    if args.num_experiments > 1:
        print(f"(Averaged over {args.num_experiments} experiments)")
    print("=" * 60)

    print("\n🔹 INSERTION PERFORMANCE (per operation):")
    print(f"  dict:   {dict_insert_avg * 1e9:.0f} ns", end="")
    if args.num_experiments > 1 and len(dict_insert_avgs) > 1:
        print(f" (±{stdev(dict_insert_avgs) * 1e9:.0f})")
    else:
        print()
    print(f"  zdict:  {zdict_insert_avg * 1e9:.0f} ns", end="")
    if args.num_experiments > 1 and len(zdict_insert_avgs) > 1:
        print(f" (±{stdev(zdict_insert_avgs) * 1e9:.0f})")
    else:
        print()
    print(f"  Performance delta: {insert_delta:+.1f}%")

    print("\n🔹 LOOKUP PERFORMANCE (per operation):")
    print(f"  dict:   {dict_lookup_avg * 1e9:.0f} ns", end="")
    if args.num_experiments > 1 and len(dict_lookup_avgs) > 1:
        print(f" (±{stdev(dict_lookup_avgs) * 1e9:.0f})")
    else:
        print()
    print(f"  zdict:  {zdict_lookup_avg * 1e9:.0f} ns", end="")
    if args.num_experiments > 1 and len(zdict_lookup_avgs) > 1:
        print(f" (±{stdev(zdict_lookup_avgs) * 1e9:.0f})")
    else:
        print()
    print(f"  Performance delta: {lookup_delta:+.1f}%")

    print("\n🔹 WORST CASE LOOKUP:")
    print(f"  dict:   {dict_worst * 1e9:.0f} ns")
    print(f"  zdict:  {zdict_worst * 1e9:.0f} ns")
    print(f"  Performance delta: {worst_case_delta:+.1f}%")

    print("\n🔹 BEST CASE LOOKUP:")
    print(f"  dict:   {dict_best * 1e9:.0f} ns")
    print(f"  zdict:  {zdict_best * 1e9:.0f} ns")
    print(f"  Performance delta: {best_case_delta:+.1f}%")

    print("\n🔹 NET PERFORMANCE:")
    overall_delta = (insert_delta + lookup_delta) / 2
    if overall_delta > 0:
        print(f"  ✅ zdict is {overall_delta:.1f}% faster overall")
    else:
        print(f"  ❌ zdict is {-overall_delta:.1f}% slower overall")


if __name__ == "__main__":
    main()

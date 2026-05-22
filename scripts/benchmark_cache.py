#!/usr/bin/env python3
"""
Benchmark: JSON caching performance in data_loader.py

Compares repeated calls to load_all_projects() before and after caching.
The cache eliminates disk I/O after the first read.
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import load_all_projects, clear_cache


def benchmark_cached_access(iterations=1000):
    """Benchmark repeated access with caching enabled."""
    # Warmup - first call populates cache
    clear_cache()
    load_all_projects()

    start = time.perf_counter()
    for _ in range(iterations):
        load_all_projects()
    elapsed = time.perf_counter() - start

    return elapsed


def benchmark_uncached_access(iterations=100):
    """
    Simulate uncached access by clearing cache before each read.
    Note: Using fewer iterations since this is much slower.
    """
    start = time.perf_counter()
    for _ in range(iterations):
        clear_cache()
        load_all_projects()
    elapsed = time.perf_counter() - start

    return elapsed


def main():
    print("=" * 60)
    print("Benchmark: data_loader.py JSON caching performance")
    print("=" * 60)

    # Benchmark cached access
    cached_iters = 10000
    cached_time = benchmark_cached_access(cached_iters)
    cached_avg = (cached_time / cached_iters) * 1e6  # microseconds

    print(f"\nCached access ({cached_iters:,} iterations):")
    print(f"  Total time: {cached_time:.4f}s")
    print(f"  Avg per call: {cached_avg:.2f} µs")

    # Benchmark uncached access
    uncached_iters = 100
    uncached_time = benchmark_uncached_access(uncached_iters)
    uncached_avg = (uncached_time / uncached_iters) * 1e6  # microseconds

    print(f"\nUncached access ({uncached_iters:,} iterations):")
    print(f"  Total time: {uncached_time:.4f}s")
    print(f"  Avg per call: {uncached_avg:.2f} µs")

    # Calculate speedup
    speedup = uncached_avg / cached_avg
    print(f"\n{'=' * 60}")
    print(f"Speedup: {speedup:.1f}x faster with caching")
    print(f"Time saved per call: {uncached_avg - cached_avg:.0f} µs")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())

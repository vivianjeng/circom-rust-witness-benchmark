#!/usr/bin/env python3
"""Benchmark witness generation time for C++, JS, and Rust."""

import subprocess
import time
import sys
from pathlib import Path

CIRCUIT_DIR = sys.argv[1] if len(sys.argv) > 1 else "circuit-registry/multiplier2"
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 10


def run_timed(cmd, cwd=None):
    start = time.perf_counter()
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (time.perf_counter() - start) * 1000


def benchmark(name, cmd, cwd=None):
    times = [run_timed(cmd, cwd=cwd) for _ in range(RUNS)]
    avg, mn, mx = sum(times) / len(times), min(times), max(times)
    print(f"  avg: {avg:8.2f} ms  min: {mn:8.2f} ms  max: {mx:8.2f} ms")


rust_bin = str(Path(f"{CIRCUIT_DIR}/multiplier2_rust/target/release/examples/witness").resolve())

print(f"=== Witness Generation Benchmark ({RUNS} runs) ===")
print(f"Circuit: {CIRCUIT_DIR}")
print()

print("[C++]")
benchmark("C++", ["./multiplier2", "../input.json", "witness.wtns"], cwd=f"{CIRCUIT_DIR}/multiplier2_cpp")

print("[JS]")
benchmark("JS", ["node", "generate_witness.js", "multiplier2.wasm", "../input.json", "witness.wtns"], cwd=f"{CIRCUIT_DIR}/multiplier2_js")

print("[Rust]")
benchmark("Rust", [rust_bin])

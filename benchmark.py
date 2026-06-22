#!/usr/bin/env python3
"""Benchmark witness generation time for C++, JS, and Rust across circuits."""

import subprocess
import time
import sys
from pathlib import Path

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 5

CIRCUITS = [
    {"label": "multiplier2",        "dir": "circuit-registry/multiplier2", "name": "multiplier2"},
    {"label": "keccak256_256_test", "dir": "circuit-registry/keccak256",   "name": "keccak256_256_test"},
    {"label": "rsa",                "dir": "circuit-registry/rsa",          "name": "main_c"},
]


def run_timed(cmd, cwd=None):
    start = time.perf_counter()
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (time.perf_counter() - start) * 1000


def benchmark(cmd, cwd=None):
    times = [run_timed(cmd, cwd=cwd) for _ in range(RUNS)]
    return sum(times) / len(times), min(times), max(times)


print(f"=== Witness Generation Benchmark ({RUNS} runs) ===\n")
print(f"{'Circuit':<22} {'Method':<6} {'avg':>10}  {'min':>10}  {'max':>10}")
print("-" * 64)

for circuit in CIRCUITS:
    label, d, name = circuit["label"], circuit["dir"], circuit["name"]
    input_json = str(Path(f"{d}/input.json").resolve())
    rust_bin = str(Path(f"{d}/{name}_rust/target/release/examples/witness").resolve())

    avg, mn, mx = benchmark([f"./{name}", "../input.json", "witness.wtns"], cwd=f"{d}/{name}_cpp")
    print(f"{label:<22} {'C++':<6} {avg:>9.2f}ms  {mn:>9.2f}ms  {mx:>9.2f}ms")

    avg, mn, mx = benchmark(["node", "generate_witness.js", f"{name}.wasm", "../input.json", "witness.wtns"], cwd=f"{d}/{name}_js")
    print(f"{'':22} {'JS':<6} {avg:>9.2f}ms  {mn:>9.2f}ms  {mx:>9.2f}ms")

    avg, mn, mx = benchmark([rust_bin, input_json])
    print(f"{'':22} {'Rust':<6} {avg:>9.2f}ms  {mn:>9.2f}ms  {mx:>9.2f}ms")
    print()

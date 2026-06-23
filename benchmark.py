#!/usr/bin/env python3
"""Benchmark witness generation time for C++, JS, Rust, and Rust-WASM across circuits."""

import subprocess
import time
import sys
from pathlib import Path

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 5

CIRCUITS = [
    {"label": "multiplier2",        "dir": "circuit-registry/multiplier2", "name": "multiplier2",        "wasm_dir": "multiplier2", "wasm_name": "multiplier2_wasm"},
    {"label": "keccak256_256_test", "dir": "circuit-registry/keccak256",   "name": "keccak256_256_test", "wasm_dir": "keccak256",   "wasm_name": "keccak256_wasm"},
    {"label": "rsa",                "dir": "circuit-registry/rsa",          "name": "main_c",             "wasm_dir": "rsa",         "wasm_name": "rsa_wasm"},
]


def run_timed(cmd, cwd=None):
    start = time.perf_counter()
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    elapsed = (time.perf_counter() - start) * 1000
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    return elapsed


def benchmark(cmd, cwd=None):
    try:
        times = [run_timed(cmd, cwd=cwd) for _ in range(RUNS)]
        return sum(times) / len(times), min(times), max(times)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace").strip() if e.stderr else ""
        last_line = stderr.splitlines()[-1] if stderr else "(no output)"
        return None, None, last_line
    except FileNotFoundError:
        return None, None, f"not found: {cmd[0]}"


SCRIPT_DIR = Path(__file__).parent.resolve()

print(f"=== Witness Generation Benchmark ({RUNS} runs) ===\n")
print(f"{'Circuit':<22} {'Method':<10} {'avg':>10}  {'min':>10}  {'max':>10}")
print("-" * 68)

def fmt(label_col, method, avg, mn, mx):
    if avg is None:
        print(f"{label_col:<22} {method:<10} FAILED: {mx}")
    else:
        print(f"{label_col:<22} {method:<10} {avg:>9.2f}ms  {mn:>9.2f}ms  {mx:>9.2f}ms")


for circuit in CIRCUITS:
    label, d, name = circuit["label"], circuit["dir"], circuit["name"]
    input_json = str(Path(f"{d}/input.json").resolve())
    rust_bin = str(Path(f"{d}/{name}_rust/target/release/examples/witness").resolve())
    wasm_js = str((SCRIPT_DIR / "wasm-witnesses" / circuit["wasm_dir"] / "wasm_out" / f"{circuit['wasm_name']}.js").resolve())
    runner = str(SCRIPT_DIR / "run_wasm_witness.js")

    avg, mn, mx = benchmark([f"./{name}", "../input.json", "witness.wtns"], cwd=f"{d}/{name}_cpp")
    fmt(label, "C++", avg, mn, mx)

    avg, mn, mx = benchmark(["node", "generate_witness.js", f"{name}.wasm", "../input.json", "witness.wtns"], cwd=f"{d}/{name}_js")
    fmt("", "JS", avg, mn, mx)

    avg, mn, mx = benchmark([rust_bin, input_json])
    fmt("", "Rust", avg, mn, mx)

    avg, mn, mx = benchmark(["node", runner, wasm_js, input_json])
    fmt("", "Rust-WASM", avg, mn, mx)
    print()

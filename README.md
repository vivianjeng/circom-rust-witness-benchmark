# circom-rust-witness-benchmark

Benchmark witness generation time across four methods for circom circuits:

| Method | Description |
|---|---|
| **C++** | Native binary from circom `--c` output |
| **JS** | Node.js + WebAssembly from circom `--wasm` output |
| **Rust** | Native binary from circom `--rust` output |
| **Rust-WASM** | Rust witness compiled to `wasm32-unknown-unknown` via `wasm-bindgen`, called from Node.js |

## Circuits

| Circuit | Description |
|---|---|
| `multiplier2` | Simple 2-input multiplier |
| `keccak256_256_test` | Keccak-256 hash |
| `rsa` | RSA signature verification |

## Results

Benchmarked on Ubuntu (GitHub Actions), 5 runs each.

```
Circuit                Method            avg         min         max
--------------------------------------------------------------------
multiplier2            C++             1.48ms       1.32ms       1.93ms
                       JS             26.91ms      24.59ms      33.04ms
                       Rust            0.89ms       0.82ms       1.07ms
                       Rust-WASM      29.33ms      27.98ms      30.65ms

keccak256_256_test     C++            91.15ms      89.36ms      92.32ms
                       JS            337.47ms     332.32ms     343.68ms
                       Rust          334.34ms     330.58ms     344.80ms
                       Rust-WASM    1117.70ms    1053.61ms    1287.87ms

rsa                    C++           162.30ms     158.99ms     166.94ms
                       JS           3385.80ms    3377.92ms    3402.49ms
                       Rust          670.17ms     668.51ms     674.69ms
                       Rust-WASM    2066.52ms    1962.47ms    2151.58ms
```

## Repository Structure

```
.
├── benchmark.py               # Benchmark runner
├── witness_template.rs        # Template for native Rust witness binary
├── run_wasm_witness.js        # Node.js runner for Rust-WASM witnesses
├── wasm-witnesses/            # wasm-bindgen wrapper crates (one per circuit)
│   ├── Cargo.toml             # Workspace
│   ├── multiplier2/
│   │   ├── Cargo.toml         # cdylib, depends on circuit crate via path
│   │   └── src/lib.rs         # #[wasm_bindgen] generate_witness()
│   ├── keccak256/
│   └── rsa/
└── .github/workflows/ci.yml  # CI: compile circuits, build all methods, benchmark
```

The `circuit-registry/` directory is cloned at CI time from [zkmopro/circuit-registry](https://github.com/zkmopro/circuit-registry) and is not tracked in this repo.

## How It Works

### Rust-WASM

Each crate in `wasm-witnesses/` is a thin wrapper around the circom-generated Rust witness calculator:

```rust
#[wasm_bindgen]
pub fn generate_witness(input_json: &str) -> String {
    // parse JSON inputs, run witness calculator, return JSON witness array
}
```

Built with:
```sh
cargo build --release --target wasm32-unknown-unknown --manifest-path wasm-witnesses/Cargo.toml
wasm-bindgen wasm-witnesses/target/wasm32-unknown-unknown/release/<name>.wasm \
  --out-dir wasm-witnesses/<circuit>/wasm_out --target nodejs
```

### Running Locally

```sh
# Clone circuit-registry and compile circuits
git clone https://github.com/zkmopro/circuit-registry.git
# (follow CI steps for your platform)

# Build and run benchmark
python3 benchmark.py 5
```

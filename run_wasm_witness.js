#!/usr/bin/env node
// Usage: node run_wasm_witness.js <wasm_js_path> <input_json_path>
// Loads a wasm-bindgen --target nodejs module and calls generate_witness().

const [,, wasmJsPath, inputJsonPath] = process.argv;
if (!wasmJsPath || !inputJsonPath) {
    process.stderr.write('Usage: node run_wasm_witness.js <wasm_js_path> <input_json_path>\n');
    process.exit(1);
}

const { generate_witness } = require(require('path').resolve(wasmJsPath));
const inputJson = require('fs').readFileSync(inputJsonPath, 'utf8');
generate_witness(inputJson);

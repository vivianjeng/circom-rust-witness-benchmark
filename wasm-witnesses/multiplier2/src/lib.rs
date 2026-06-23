use malachite::integer::Integer;
use std::str::FromStr;
use wasm_bindgen::prelude::*;

fn parse_val(v: &serde_json::Value) -> Integer {
    match v {
        serde_json::Value::Number(n) => Integer::from_str(&n.to_string()).unwrap(),
        serde_json::Value::String(s) => Integer::from_str(s).unwrap(),
        _ => panic!("unsupported input value: {:?}", v),
    }
}

fn collect_inputs(
    key: &str,
    val: &serde_json::Value,
    out: &mut Vec<(String, usize, Integer)>,
    offset: &mut usize,
) {
    if let serde_json::Value::Array(arr) = val {
        for v in arr {
            collect_inputs(key, v, out, offset);
        }
    } else {
        out.push((key.to_string(), *offset, parse_val(val)));
        *offset += 1;
    }
}

#[wasm_bindgen]
pub fn generate_witness(input_json: &str) -> String {
    let json: serde_json::Value = serde_json::from_str(input_json).expect("invalid JSON");
    let mut inputs: Vec<(String, usize, Integer)> = Vec::new();
    for (key, val) in json.as_object().expect("input must be a JSON object") {
        let mut offset = 0usize;
        collect_inputs(key, val, &mut inputs, &mut offset);
    }
    let mut ctx = multiplier2::create_witness_calculator();
    for (name, idx, value) in inputs {
        ctx.set_input_signal(&name, idx, value);
    }
    let witness = ctx.get_witness_vec();
    let arr: Vec<String> = witness.iter().map(|v| v.to_string()).collect();
    serde_json::to_string(&arr).unwrap()
}

use std::str::FromStr;
use malachite::integer::Integer;
use CIRCUIT_CRATE::create_witness_calculator;

fn parse_val(v: &serde_json::Value) -> Integer {
    match v {
        serde_json::Value::Number(n) => Integer::from_str(&n.to_string()).unwrap(),
        serde_json::Value::String(s) => Integer::from_str(s).unwrap(),
        _ => panic!("unsupported value type: {:?}", v),
    }
}

// Recursively walk nested arrays, emitting (base_name, flat_index, value).
// set_input_signal(name, idx) places the value at sig_start + idx, where
// sig_start is looked up by base name in the circuit's hash map.
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

fn main() {
    let input_path = std::env::args().nth(1).unwrap_or_else(|| "../input.json".to_string());
    let json_str = std::fs::read_to_string(&input_path).expect("failed to read input file");
    let json: serde_json::Value = serde_json::from_str(&json_str).expect("failed to parse JSON");

    let mut inputs: Vec<(String, usize, Integer)> = Vec::new();
    for (key, val) in json.as_object().expect("input must be a JSON object") {
        let mut offset = 0usize;
        collect_inputs(key, val, &mut inputs, &mut offset);
    }

    let mut ctx = create_witness_calculator();
    for (name, idx, value) in inputs {
        ctx.set_input_signal(&name, idx, value);
    }
    let _ = ctx.get_witness_vec();
}

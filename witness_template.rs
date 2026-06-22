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

fn main() {
    let input_path = std::env::args().nth(1).unwrap_or_else(|| "../input.json".to_string());
    let json_str = std::fs::read_to_string(&input_path).expect("failed to read input file");
    let json: serde_json::Value = serde_json::from_str(&json_str).expect("failed to parse JSON");

    let mut ctx = create_witness_calculator();
    for (key, val) in json.as_object().expect("input must be a JSON object") {
        if let serde_json::Value::Array(arr) = val {
            for (i, v) in arr.iter().enumerate() {
                ctx.set_input(&format!("{}[{}]", key, i), parse_val(v));
            }
        } else {
            ctx.set_input(key, parse_val(val));
        }
    }
    let _ = ctx.get_witness_vec();
}

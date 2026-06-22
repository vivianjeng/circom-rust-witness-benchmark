use std::str::FromStr;
use malachite::integer::Integer;
use CIRCUIT_CRATE::create_witness_calculator;

fn flatten(prefix: &str, val: &serde_json::Value) -> Vec<(String, Integer)> {
    match val {
        serde_json::Value::Array(arr) => arr
            .iter()
            .enumerate()
            .flat_map(|(i, v)| flatten(&format!("{}[{}]", prefix, i), v))
            .collect(),
        serde_json::Value::Number(n) => vec![(prefix.to_string(), Integer::from_str(&n.to_string()).unwrap())],
        serde_json::Value::String(s) => vec![(prefix.to_string(), Integer::from_str(s).unwrap())],
        _ => panic!("unsupported value type: {:?}", val),
    }
}

fn main() {
    let input_path = std::env::args().nth(1).unwrap_or_else(|| "../input.json".to_string());
    let json_str = std::fs::read_to_string(&input_path).expect("failed to read input file");
    let json: serde_json::Value = serde_json::from_str(&json_str).expect("failed to parse JSON");

    let mut ctx = create_witness_calculator();
    for (key, val) in json.as_object().expect("input must be a JSON object") {
        for (signal, value) in flatten(key, val) {
            ctx.set_input(&signal, value);
        }
    }
    let _ = ctx.get_witness_vec();
}

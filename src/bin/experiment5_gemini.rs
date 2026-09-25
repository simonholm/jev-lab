use std::env;
use std::error::Error;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::PathBuf;
use std::time::{Duration, Instant};

use reqwest::blocking::Client;
use serde::Deserialize;
use serde_json::{Value, json};

const MODEL: &str = "google/gemini-2.5-flash-lite";
const ENDPOINT: &str = "https://openrouter.ai/api/v1/chat/completions";
const RUBRIC: &str = "Choose the category that best describes what this record itself documents, not an action or decision that can merely be inferred from it.\n\ndecision: explicitly records a choice, approval, rejection, or policy decision.\nimplementation: explicitly records work that was carried out or a change that was applied.\ntroubleshooting: primarily records diagnosis, investigation, debugging, or repair of a problem.\nobservation: primarily reports a fact, measurement, state, or result without documenting a decision or implementation.\ndiscussion: primarily records a proposal, suggestion, question, trade-off, or unresolved discussion.\nother: none of the above is the primary purpose.\n\nReturn category_confidence as a probability from 0.0 to 1.0 for the selected category.\n\nexplicit_decision: Does this record explicitly state that a decision, approval, rejection, or policy choice was made? Answer based only on what is explicitly documented. Do not count a decision merely implied by an implementation or other action.\n\ncompleted_change: Does this record explicitly state that a project change was actually completed or applied? A proposal, approval, plan, investigation, intended change, or description of past behavior does not count unless the record states that the change was carried out.\n\nretain_for_history: Would this record be worth retaining in a concise project history because it documents at least one of: an explicit decision, a completed project change, a significant problem and its resolution, a failed experiment that affected subsequent work, or a significant project result? Do not count transient status, routine command output, casual discussion, or mundane observations.\n\nmissing_required_context: Is important information missing from this record such that, by itself, a reader cannot identify what project event, change, problem, decision, or result the record refers to? Do not answer yes merely because additional background would be helpful.\n\nReturn each of the four judgments as a probability from 0.0 to 1.0. Return only the JSON object; no explanation, reasoning, summary, or prose.";

#[derive(Deserialize, serde::Serialize)]
struct Record {
    id: String,
    text: String,
}

fn response_format() -> Value {
    let probability = json!({"type": "number", "minimum": 0, "maximum": 1});
    json!({
        "type": "json_schema",
        "json_schema": {
            "name": "experiment5_judgments",
            "strict": true,
            "schema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["decision", "implementation", "troubleshooting", "observation", "discussion", "other"]},
                    "category_confidence": probability,
                    "explicit_decision": probability,
                    "completed_change": probability,
                    "retain_for_history": probability,
                    "missing_required_context": probability
                },
                "required": ["category", "category_confidence", "explicit_decision", "completed_change", "retain_for_history", "missing_required_context"],
                "additionalProperties": false
            }
        }
    })
}

fn validate(response: &Value) -> Result<(u64, u64, f64), Box<dyn Error>> {
    let content = response["choices"][0]["message"]["content"]
        .as_str()
        .ok_or("missing message content")?;
    let answer: Value = serde_json::from_str(content)?;
    let expected = response_format()["json_schema"]["schema"]["properties"]["category"]["enum"]
        .as_array()
        .ok_or("missing category enum")?
        .clone();
    if !expected.contains(&answer["category"])
        || answer.as_object().is_none_or(|fields| fields.len() != 6)
    {
        return Err("invalid category or answer object".into());
    }
    for field in [
        "category_confidence",
        "explicit_decision",
        "completed_change",
        "retain_for_history",
        "missing_required_context",
    ] {
        let value = answer[field].as_f64().ok_or(format!("missing {field}"))?;
        if !(0.0..=1.0).contains(&value) {
            return Err(format!("{field} outside 0..1").into());
        }
    }
    let input = response["usage"]["prompt_tokens"]
        .as_u64()
        .ok_or("missing input tokens")?;
    let output = response["usage"]["completion_tokens"]
        .as_u64()
        .ok_or("missing output tokens")?;
    let cost = response["usage"]["cost"]
        .as_f64()
        .ok_or("missing reported cost")?;
    Ok((input, output, cost))
}

fn run() -> Result<(), Box<dyn Error>> {
    let api_key = match env::var("OPENROUTER_API_KEY") {
        Ok(key) if !key.is_empty() => key,
        _ => return Err("OPENROUTER_API_KEY is missing; no requests were sent".into()),
    };
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let records = BufReader::new(File::open(root.join("experiment5-records.jsonl"))?);
    let output = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(root.join("experiment5-gemini-results.jsonl"))?;
    let mut output = BufWriter::new(output);
    let client = Client::builder().timeout(Duration::from_secs(60)).build()?;
    let started_run = Instant::now();
    let mut count = 0;
    let mut input_tokens = 0;
    let mut output_tokens = 0;
    let mut cost = 0.0;
    let mut total_latency = Duration::ZERO;

    for line in records.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let record: Record = serde_json::from_str(&line)?;
        let started = Instant::now();
        let result = client.post(ENDPOINT).bearer_auth(&api_key).json(&json!({
            "model": MODEL,
            "messages": [{"role": "system", "content": RUBRIC}, {"role": "user", "content": record.text}],
            "response_format": response_format(),
            "provider": {"require_parameters": true}
        })).send();
        let latency = started.elapsed();
        let response = match result {
            Ok(http) => {
                let status = http.status();
                let body = http.text()?;
                if !status.is_success() {
                    writeln!(
                        output,
                        "{}",
                        json!({"record": record, "latency_seconds": latency.as_secs_f64(), "http_status": status.as_u16(), "raw_body": body})
                    )?;
                    output.flush()?;
                    return Err(format!("{}: HTTP {status}", record.id).into());
                }
                serde_json::from_str::<Value>(&body)?
            }
            Err(error) => {
                writeln!(
                    output,
                    "{}",
                    json!({"record": record, "latency_seconds": latency.as_secs_f64(), "error": error.to_string()})
                )?;
                output.flush()?;
                return Err(error.into());
            }
        };
        writeln!(
            output,
            "{}",
            json!({"record": record, "latency_seconds": latency.as_secs_f64(), "response": response})
        )?;
        output.flush()?;
        let (input, generated, reported_cost) = validate(&response)?;
        input_tokens += input;
        output_tokens += generated;
        cost += reported_cost;
        total_latency += latency;
        count += 1;
        println!("{}: captured", record.id);
    }
    println!("Records: {count}");
    println!(
        "Input tokens: {input_tokens}; output tokens: {output_tokens}; reported cost: ${cost:.9}"
    );
    println!(
        "Runtime: {:.3} s; mean request latency: {:.3} s",
        started_run.elapsed().as_secs_f64(),
        total_latency.as_secs_f64() / count as f64
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}

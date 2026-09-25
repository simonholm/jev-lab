use std::env;
use std::error::Error;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::PathBuf;
use std::time::{Duration, Instant};

use reqwest::blocking::Client;
use serde::Deserialize;
use serde_json::{Value, json};

const MODEL: &str = "typesafe/jev-1.13";
const ENDPOINT: &str = "https://openrouter.ai/api/alpha/decisions";
const NOUL_QUESTIONS: [(&str, &str); 4] = [
    (
        "concrete_decision",
        "Does this record explicitly state that a decision, approval, rejection, or policy choice was made? Answer based only on what is explicitly documented. Do not count a decision merely implied by an implementation or other action.",
    ),
    (
        "completed_change",
        "Does this record explicitly state that a project change was actually completed or applied? A proposal, approval, plan, investigation, intended change, or description of past behavior does not count unless the record states that the change was carried out.",
    ),
    (
        "project_history",
        "Would this record be worth retaining in a concise project history because it documents at least one of: an explicit decision, a completed project change, a significant problem and its resolution, a failed experiment that affected subsequent work, or a significant project result? Do not count transient status, routine command output, casual discussion, or mundane observations.",
    ),
    (
        "needs_context",
        "Is important information missing from this record such that, by itself, a reader cannot identify what project event, change, problem, decision, or result the record refers to? Do not answer yes merely because additional background would be helpful.",
    ),
];

#[derive(Deserialize, serde::Serialize)]
struct Record {
    id: String,
    text: String,
}

struct ResponseFields {
    choice: String,
    confidence: String,
    tokens: u64,
    cost: f64,
}

fn questions() -> Value {
    let mut questions = json!({
        "category": {
            "type": "choice",
            "instructions": "Choose the category that best describes what this record itself documents, not an action or decision that can merely be inferred from it.\n\ndecision: explicitly records a choice, approval, rejection, or policy decision.\nimplementation: explicitly records work that was carried out or a change that was applied.\ntroubleshooting: primarily records diagnosis, investigation, debugging, or repair of a problem.\nobservation: primarily reports a fact, measurement, state, or result without documenting a decision or implementation.\ndiscussion: primarily records a proposal, suggestion, question, trade-off, or unresolved discussion.\nother: none of the above is the primary purpose.",
            "criteria": {
                "decision": "Explicitly records a choice, approval, rejection, or policy decision.",
                "implementation": "Explicitly records work that was carried out or a change that was applied.",
                "troubleshooting": "Primarily records diagnosis, investigation, debugging, or repair of a problem.",
                "observation": "Primarily reports a fact, measurement, state, or result without documenting a decision or implementation.",
                "discussion": "Primarily records a proposal, suggestion, question, trade-off, or unresolved discussion.",
                "other": "None of the above is the primary purpose."
            }
        }
    });
    for (name, instruction) in NOUL_QUESTIONS {
        questions[name] = json!({"type": "noul", "instructions": instruction});
    }
    questions
}

fn response_fields(response: &Value) -> Result<ResponseFields, Box<dyn Error>> {
    let category = &response["answers"]["category"];
    let choice = category["choice"]
        .as_str()
        .ok_or("missing category choice")?;
    if category["type"] != "choice" || questions()["category"]["criteria"].get(choice).is_none() {
        return Err("unexpected category answer".into());
    }
    if !category["probabilities"].is_object() {
        return Err("missing category probabilities".into());
    }
    for (name, _) in NOUL_QUESTIONS {
        let answer = &response["answers"][name];
        if answer["type"] != "noul" || !answer["noul"].is_number() {
            return Err(format!("unexpected {name} answer").into());
        }
    }
    let tokens = response["usage"]["input_tokens"]
        .as_u64()
        .ok_or("missing input token count")?;
    let cost = response["usage"]["cost"]
        .as_f64()
        .ok_or("missing reported cost")?;
    Ok(ResponseFields {
        choice: choice.to_string(),
        confidence: category
            .get("confidence")
            .map_or_else(|| "not returned".to_string(), Value::to_string),
        tokens,
        cost,
    })
}

fn run() -> Result<(), Box<dyn Error>> {
    let api_key = match env::var("OPENROUTER_API_KEY") {
        Ok(key) if !key.is_empty() => key,
        _ => {
            return Err(
                "OPENROUTER_API_KEY is missing from the environment; no requests were sent".into(),
            );
        }
    };
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let records = BufReader::new(File::open(root.join("experiment2-records.jsonl"))?);
    let mut output = BufWriter::new(File::create(root.join("experiment3-results.jsonl"))?);
    let client = Client::builder().timeout(Duration::from_secs(30)).build()?;
    let questions = questions();
    let mut count = 0;
    let mut input_tokens = 0;
    let mut cost = 0.0;
    let mut total_latency = Duration::ZERO;

    for line in records.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let record: Record = serde_json::from_str(&line)?;
        let started = Instant::now();
        let http_response = client
            .post(ENDPOINT)
            .bearer_auth(&api_key)
            .json(&json!({"model": MODEL, "state": record.text, "questions": questions}))
            .send()?;
        if !http_response.status().is_success() {
            return Err(format!(
                "{}: OpenRouter returned HTTP {}",
                record.id,
                http_response.status()
            )
            .into());
        }
        let response: Value = http_response.json()?;
        let latency = started.elapsed();
        let fields = response_fields(&response)?;

        writeln!(
            output,
            "{}",
            json!({"record": record, "latency_seconds": latency.as_secs_f64(), "response": response})
        )?;
        output.flush()?;
        println!("\n{}: {}", record.id, record.text);
        println!(
            "  category: {} (confidence: {})",
            fields.choice, fields.confidence
        );
        for (name, question) in NOUL_QUESTIONS {
            println!("  {question} {}", response["answers"][name]["noul"]);
        }
        input_tokens += fields.tokens;
        cost += fields.cost;
        total_latency += latency;
        count += 1;
    }

    println!("\nRecords: {count}");
    println!("Total input tokens: {input_tokens}");
    println!("Total reported cost: ${cost:.9}");
    println!(
        "Average latency per request: {:.3} s",
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

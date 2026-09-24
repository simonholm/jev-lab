"""Run one bounded Jev decision request per synthetic technical record."""

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MODEL = "typesafe/jev-1.13"
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
ROOT = Path(__file__).resolve().parent

NOUL_QUESTIONS = {
    "concrete_decision": "Does this record contain a concrete decision that was actually made?",
    "completed_change": "Does this record describe a completed change?",
    "project_history": "Does this record contain information useful for reconstructing project history?",
    "needs_context": "Does this record require surrounding context to understand what happened?",
}

QUESTIONS = {
    "category": {
        "type": "choice",
        "instructions": "What kind of record is this? Choose the best primary category for the record as written.",
        "criteria": {
            "decision": "An explicit choice or commitment among approaches, whether or not implemented.",
            "implementation": "A completed code, configuration, or documentation change.",
            "troubleshooting": "Investigation or resolution of a failure or unexpected behavior.",
            "observation": "A finding, measurement, or status report without a decision or change.",
            "discussion": "Open-ended consideration or proposal without a decision.",
            "other": "The record does not fit the other categories.",
        },
    },
    **{
        name: {"type": "noul", "instructions": question}
        for name, question in NOUL_QUESTIONS.items()
    },
}


def decide(text, api_key):
    body = json.dumps({"model": MODEL, "state": text, "questions": QUESTIONS}).encode()
    request = Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.perf_counter()
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    return result, time.perf_counter() - started


def check_response(result):
    answers = result["answers"]
    category = answers["category"]
    if category["type"] != "choice" or category["choice"] not in QUESTIONS["category"]["criteria"]:
        raise ValueError("unexpected category answer")
    if not isinstance(category["probabilities"], dict):
        raise ValueError("missing category probabilities")
    for name in NOUL_QUESTIONS:
        if answers[name]["type"] != "noul" or not isinstance(answers[name]["noul"], (int, float)):
            raise ValueError(f"unexpected {name} answer")
    usage = result["usage"]
    if not isinstance(usage["input_tokens"], int) or not isinstance(usage["cost"], (int, float)):
        raise ValueError("unexpected usage fields")


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is missing from the environment; no requests were sent.", file=sys.stderr)
        return 1

    records = [json.loads(line) for line in (ROOT / "records.jsonl").read_text().splitlines() if line.strip()]
    input_tokens = 0
    cost = 0.0
    total_latency = 0.0
    completed = 0
    with (ROOT / "results.jsonl").open("w") as output:
        for record in records:
            try:
                response, latency = decide(record["text"], api_key)
                check_response(response)
            except HTTPError as error:
                print(f"{record['id']}: OpenRouter returned HTTP {error.code}.", file=sys.stderr)
                return 1
            except (URLError, TimeoutError) as error:
                print(f"{record['id']}: request failed: {error.reason if isinstance(error, URLError) else 'timeout'}", file=sys.stderr)
                return 1
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                print(f"{record['id']}: unexpected API response: {error}", file=sys.stderr)
                return 1

            output.write(json.dumps({"record": record, "latency_seconds": latency, "response": response}) + "\n")
            output.flush()
            category = response["answers"]["category"]
            print(f"\n{record['id']}: {record['text']}")
            print(f"  category: {category['choice']} (confidence: {category.get('confidence', 'not returned')})")
            for name, question in NOUL_QUESTIONS.items():
                print(f"  {question} {response['answers'][name]['noul']}")
            input_tokens += response["usage"]["input_tokens"]
            cost += response["usage"]["cost"]
            total_latency += latency
            completed += 1

    print(f"\nRecords: {completed}")
    print(f"Total input tokens: {input_tokens}")
    print(f"Total reported cost: ${cost:.9f}")
    print(f"Average latency per request: {total_latency / completed:.3f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Run an executable Semgrep answer key, then ask Jev the same 20 exercises."""

import json
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from core.jev_poc import run
from core.semgrep_exam_cases import CASES


EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "semgrep_exam"
CHOICE_SEED = 20260918
LABELS = "ABCD"


def subset_label(labels):
    return ", ".join(labels) if labels else "None"


def prepare():
    version = subprocess.run(["semgrep", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    fixtures = EVIDENCE / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    rules, exercises, topics = [], {}, {}
    for index, (topic, formula, snippets) in enumerate(CASES, start=1):
        key = f"q{index:02d}"
        rule = {"id": key, "languages": ["python"], "severity": "WARNING", "message": "Match", **formula}
        rules.append({**rule, "paths": {"include": [f"**/{key}/*.py"]}})
        folder = fixtures / key
        folder.mkdir(exist_ok=True)
        for label, snippet in zip(LABELS, snippets, strict=True):
            compile(snippet, f"{key}/{label}.py", "exec")
            (folder / f"{label}.py").write_text(snippet + "\n")
        exercises[key] = {
            "rule_yaml": yaml.safe_dump({"rules": [rule]}, sort_keys=False),
            "snippets": dict(zip(LABELS, snippets, strict=True)),
        }
        topics[key] = topic
    config_path = EVIDENCE / "rules.yaml"
    config_path.write_text(yaml.safe_dump({"rules": rules}, sort_keys=False))
    command = ["semgrep", "scan", "--oss-only", "--metrics=off", "--disable-version-check",
               "--no-git-ignore", "--json", "--quiet", "--config", str(config_path), str(fixtures)]
    process = subprocess.run(command, capture_output=True, text=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    raw_path = EVIDENCE / f"semgrep_{stamp}.json"
    raw_path.write_text(process.stdout)
    (EVIDENCE / f"semgrep_{stamp}.stderr.txt").write_text(process.stderr)
    if process.returncode:
        raise RuntimeError(f"Semgrep failed ({process.returncode}); see {EVIDENCE}")
    result = json.loads(process.stdout)
    if result.get("errors"):
        raise ValueError(f"Semgrep reported errors: {result['errors']}")
    assert len(result["paths"]["scanned"]) == len(CASES) * len(LABELS)
    matched = {key: set() for key in exercises}
    for finding in result["results"]:
        path = Path(finding["path"])
        key = path.parent.name
        assert finding["check_id"].split(".")[-1] == key
        matched[key].add(path.stem)
    expected = {key: subset_label(sorted(labels)) for key, labels in matched.items()}
    choices = [subset_label([label for i, label in enumerate(LABELS) if mask & (1 << i)]) for mask in range(16)]
    rng = random.Random(CHOICE_SEED)
    questions = {}
    for key in exercises:
        correct = expected[key]
        options = [correct, *rng.sample([choice for choice in choices if choice != correct], 3)]
        rng.shuffle(options)
        questions[key] = {
            "type": "choice",
            "instructions": (
                f"For exercises.{key}, which snippets produce at least one finding under the given Semgrep rule? "
                "Select the complete set of matching snippet labels. Each snippet is scanned independently "
                "as a separate Python file using the rule shown, with default matching options. "
                "Comments and strings are part of the file. This asks about static matching, not runtime behavior."
            ),
            "criteria": {option: "No snippets match." if option == "None" else f"Exactly snippets {option} match." for option in options},
        }
    # The executable answer key stays in local evidence, outside Jev's message.
    key_path = EVIDENCE / f"answer_key_{stamp}.json"
    key_path.write_text(json.dumps({
        "semgrep_version": version, "command": command, "raw_output": str(raw_path),
        "expected": expected, "topics": topics, "timestamp": stamp,
    }, indent=2))
    message = json.dumps({
        "instructions": f"Semgrep CE {version} rule-reading exam. Treat all snippets as independent files. Report static findings, not whether the programs run successfully.",
        "exercises": exercises,
    })
    return message, questions, expected, topics, key_path


def main():
    message, questions, expected, topics, key_path = prepare()
    print(f"Verified {len(questions)} exercises against Semgrep: {key_path}")

    def evaluate(body):
        answers = body["answers"]
        if set(answers) != set(questions):
            raise ValueError("Returned question IDs differ from the exam.")
        results = []
        for key, answer in answers.items():
            if answer.get("choice") not in questions[key]["criteria"]:
                raise ValueError(f"Invalid answer for {key}")
            results.append({
                "question": key, "topic": topics[key], "response": answer["choice"],
                "expected": expected[key], "correct": answer["choice"] == expected[key],
                "confidence": answer["confidence"], "probabilities": answer["probabilities"],
                "amount_of_choices": len(questions[key]["criteria"]),
            })
        report = {
            "scenario": "semgrep_exam", "answer_key_file": str(key_path),
            "correct": sum(r["correct"] for r in results), "total": len(results), "results": results,
        }
        print(json.dumps(report, indent=2))
        return report

    return run(message, questions, evaluate=evaluate)


if __name__ == "__main__":
    raise SystemExit(main())

"""Ask 60 Noul questions in one request; keep reference labels local."""

import json
import random

from core.jev_poc import run
from core.primality import is_prime


SEEDS = {
    "Small (2–3 digits)": [41, 101, 211, 503, 887],
    "Medium (4–6 digits)": [1009, 10007, 99991, 100003, 900001],
    "Large (7–9 digits)": [1000001, 10000001, 50000001, 100000001, 900000001],
    "Very large (10–12 digits)": [1000000001, 10000000001, 50000000001, 100000000001, 900000000001],
    "Huge (15–18 digits)": [100000000000001, 1000000000000001, 10000000000000001, 100000000000000001, 900000000000000001],
}
SHUFFLE_SEED = 20260918
DECISION_THRESHOLD = 0.5
MESSAGE = "Determine whether each integer in the questions is a prime number."


def build_cases():
    cases = [
        {"scenario": "Basic (0–30)", "number": number}
        for number in (0, 1, 2, 3, 7, 9, 15, 17, 27, 29)
    ]
    for scenario, seeds in SEEDS.items():
        for seed in seeds:
            prime = seed
            while not is_prime(prime):
                prime += 2
            nearby = next((prime + gap for gap in (2, -2, 4, -4) if not is_prime(prime + gap)), None)
            if nearby is None:
                raise ValueError(f"No nearby composite found for {prime}")
            cases.extend([
                {"scenario": scenario, "number": prime, "paired_number": nearby},
                {"scenario": scenario, "number": nearby, "paired_number": prime},
            ])
    assert len(cases) == len({case["number"] for case in cases}) == 60
    for scenario in {case["scenario"] for case in cases}:
        group = [case for case in cases if case["scenario"] == scenario]
        assert len(group) == 10 and sum(is_prime(case["number"]) for case in group) == 5
    random.Random(SHUFFLE_SEED).shuffle(cases)
    return {f"q{index:02d}": case for index, case in enumerate(cases, start=1)}


CASES = build_cases()
QUESTIONS = {
    key: {"type": "noul", "instructions": f"Is {case['number']} a prime number?"}
    for key, case in CASES.items()
}


def evaluate(body):
    answers = body["answers"]
    if set(answers) != set(CASES):
        raise ValueError("Returned question IDs differ from the 60 requested IDs.")
    results = []
    for key, case in CASES.items():
        probability = answers[key].get("noul")
        if not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
            raise ValueError(f"Invalid Noul answer for {key}")
        expected = is_prime(case["number"])
        predicted = probability >= DECISION_THRESHOLD
        results.append({
            "question": key, **case, "expected": expected,
            "predicted": predicted, "noul": probability,
            "confidence": max(probability, 1 - probability),
            "correct": predicted == expected,
        })
    summary = []
    for scenario in ("Basic (0–30)", *SEEDS):
        group = [r for r in results if r["scenario"] == scenario]
        summary.append({
            "scenario": scenario, "correct": sum(r["correct"] for r in group),
            "total": len(group),
            "primes_correct": sum(r["correct"] and r["expected"] for r in group),
            "non_primes_correct": sum(r["correct"] and not r["expected"] for r in group),
        })
    report = {
        "scenario": "primality", "reference_method": "Deterministic Miller–Rabin for n < 2**64",
        "decision_threshold": DECISION_THRESHOLD,
        "correct": sum(r["correct"] for r in results), "total": len(results),
        "summary": summary, "results": results,
    }
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    raise SystemExit(run(MESSAGE, QUESTIONS, evaluate=evaluate))

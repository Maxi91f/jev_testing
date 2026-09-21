"""Compare Jev's letter counts with exact local counts."""

import json

from core.jev_poc import run

# Include words, isolated letters, repetitions and meaningless sequences.
# Uppercase R counts too; all other characters are ignored.
TEXTS = [
    "strawberry",
    "raspberry",
    "blueberry",
    "banana",
    "refrigerator",
    "error",
    "r",
    "x",
    "rr",
    "rrrr",
    "rrrrr",
    "rrrrrr",
    "rrrrrrrrrr",
    "rxrqr",
    "arbrcrdrer",
    "rxrxrxrxrxrxr",
    "qwxzpt",
    "RrRrRr",
]

MAX_EXACT_COUNT = 5
OVERFLOW = "more than 5"
CRITERIA = {
    str(count): f"The text contains exactly {count} occurrences of the letter r (case-insensitive)."
    for count in range(MAX_EXACT_COUNT + 1)
}
CRITERIA[OVERFLOW] = (
    f"The text contains more than {MAX_EXACT_COUNT} occurrences of the letter r (case-insensitive)."
)
QUESTIONS = {
    "r_count": {
        "type": "choice",
        "instructions": (
            "Count occurrences of the letter r in state.message only. "
            "Count both lowercase r and uppercase R. Count individual characters, "
            "not sounds or syllables. Choose the exact count, or the overflow "
            "category when the count exceeds its stated limit."
        ),
        "criteria": CRITERIA,
    },
}


def main():
    exit_code = 0
    results = []
    for text in TEXTS:
        # Ground truth stays local and is never included in the API request.
        count = text.lower().count("r")
        expected = str(count) if count <= MAX_EXACT_COUNT else OVERFLOW

        def evaluate(body):
            answer = body["answers"].get("r_count", {})
            report = {
                "text": text,
                "actual_count": count,
                "expected": expected,
                "predicted": answer.get("choice"),
                "confidence": answer.get("confidence"),
                "correct": answer.get("choice") == expected,
            }
            results.append(report)
            print(json.dumps(report, ensure_ascii=False))
            return report

        # One independent request per input, with the same choices and question.
        status = run(text, QUESTIONS, evaluate=evaluate)
        exit_code = max(exit_code, status)

    print("\nComparison:")
    for result in results:
        print(json.dumps(result, ensure_ascii=False))
    print(f"Correct: {sum(result['correct'] for result in results)}/{len(TEXTS)}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

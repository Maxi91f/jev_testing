"""Compare identical questions across five translations of one message."""

import json

from core.jev_poc import run

# Edit these constants and run: python3 scenarios/06_multilingual.py
# Each input expresses anger, requests a refund, and needs an answer today.
# These are draft translations, not independently validated references.
# Native-speaker review is needed before claiming exact semantic equivalence.
MESSAGES = {
    "Chinese": "我非常生气。我想要退款。我今天就需要一个答复。",
    "Spanish": "Estoy muy enojado. Quiero que me devuelvan el dinero. Necesito una respuesta hoy.",
    "English": "I am very angry. I want my money back. I need an answer today.",
    "Basque": "Oso haserre nago. Dirua itzultzea nahi dut. Gaur behar dut erantzuna.",
    "Guarani": "Chepochy eterei. Aipota oñeme’ẽ jey chéve che viru. Aikotevẽ peteĩ mbohovái ko árape.",
}

# Keep the questions, their language, and the option order identical in all calls.
# Only state.message changes. No language label or expected answer is sent.
QUESTIONS = {
    "anger": {
        "type": "score",
        "instructions": "How much anger does the message express?",
        # Score is an ordered scale, not a confidence percentage.
        "criteria": [
            "Neutral: expresses no anger or frustration.",
            "Annoyed: expresses mild anger or frustration.",
            "Very angry: explicitly expresses strong anger.",
        ],
    },
    "intent": {
        "type": "choice",
        "instructions": "What is the sender's main requested action?",
        # Choice keys are labels, not numeric levels.
        "criteria": {
            "refund": "Return the sender's money.",
            "replacement": "Replace a product with another one.",
            "information": "Provide information without a refund or replacement request.",
            "other": "An action not covered by the other options, or no request.",
        },
    },
    "urgent": {
        "type": "noul",
        "instructions": "Does the sender explicitly require an answer today?",
    },
}

# Reference interpretations stay local. A fractional anger score is not treated
# as an exact-match failure; this experiment compares the returned values.
REFERENCE = {"anger_level": 2, "intent": "refund", "urgent": True}


def main():
    exit_code = 0
    comparisons = []
    for language, message in MESSAGES.items():
        # The callback runs synchronously before the next language is processed.
        # The shared runner saves its report alongside the full API exchange.
        def evaluate(body):
            answers = body["answers"]
            if set(answers) != set(QUESTIONS):
                raise ValueError("Returned question IDs differ from the requested IDs.")
            report = {
                "scenario": "multilingual",
                "language": language,
                "translation_status": "draft, not independently validated",
                "reference": REFERENCE,
                "anger_score": answers["anger"].get("score"),
                "intent": answers["intent"].get("choice"),
                "intent_confidence": answers["intent"].get("confidence"),
                "urgency_noul": answers["urgent"].get("noul"),
            }
            comparisons.append(report)
            return report

        # One independent request per translation; no previous conversation.
        status = run(message, QUESTIONS, evaluate=evaluate)
        exit_code = max(exit_code, status)
        if status:
            comparisons.append({"language": language, "error": "See saved exchange"})

    print("\nComparison (anger: 0–2; intent confidence and urgency Noul: 0–1):")
    print("| Language | Anger score | Intent | Intent confidence | Urgency Noul |")
    print("|---|---:|---|---:|---:|")
    for result in comparisons:
        if "error" in result:
            print(f"| {result['language']} | ERROR | See saved exchange | — | — |")
        else:
            print(
                f"| {result['language']} | {result['anger_score']} | {result['intent']} "
                f"| {result['intent_confidence']} | {result['urgency_noul']} |"
            )
    print("Local reference interpretation: " + json.dumps(REFERENCE))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

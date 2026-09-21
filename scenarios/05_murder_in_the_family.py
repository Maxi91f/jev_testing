"""Run George J. Summers' Murder in the Family puzzle through Jev."""

# Source: Logic and Proof, section 2.5, exercise 1.
# https://avigad.github.io/logic_and_proof/propositional_logic.html#exercises
# Textbook copyright 2017 Jeremy Avigad, Robert Y. Lewis, Floris van Doorn.
# Upstream license and source capture: evidence/murder_in_the_family/.

from core.jev_poc import run

# Preserve the original wording; do not add hints or the expected solution.
MESSAGE = """Murder occurred one evening in the home of a father and mother and their son and daughter. One member of the family murdered another member, the third member witnessed the crime, and the fourth member was an accessory after the fact.

1. The accessory and the witness were of opposite sex.
2. The oldest member and the witness were of opposite sex.
3. The youngest member and the victim were of opposite sex.
4. The accessory was older than the victim.
5. The father was the oldest member.
6. The murderer was not the youngest member."""

QUESTIONS = {
    "murderer": {
        "type": "choice",
        "instructions": "Which of the four—father, mother, son, or daughter—was the murderer?",
        "criteria": {
            "father": "The father.",
            "mother": "The mother.",
            "son": "The son.",
            "daughter": "The daughter.",
        },
    },
}

# Reuse the same alternatives for all four people so only the subject changes.
ROLES = {
    "murderer": "The murderer.",
    "victim": "The victim.",
    "witness": "The witness to the crime.",
    "accessory": "The accessory after the fact.",
}
for person in QUESTIONS["murderer"]["criteria"]:
    QUESTIONS[f"{person}_role"] = {
        "type": "choice",
        "instructions": f"What was the {person}'s role in the crime?",
        "criteria": ROLES,
    }


def main():
    return run(MESSAGE, QUESTIONS)


if __name__ == "__main__":
    raise SystemExit(main())

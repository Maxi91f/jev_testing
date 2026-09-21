"""Ask Jev for all 16 cells of a unique, minimum-clue 4x4 Sudoku."""

import json

from core.jev_poc import run
from core.sudoku_search import DIGITS, UNITS, solutions

# Zero means blank. Exhaustive selection evidence: evidence/sudoku/search.json.
PUZZLE = [
    [1, 0, 3, 0],
    [0, 4, 0, 0],
    [0, 0, 0, 2],
    [0, 0, 0, 0],
]

RULES = (
    "Solve this 4x4 Sudoku. Zero denotes a blank cell. Keep all nonzero clues. "
    "Each row, each column, and each 2x2 block must contain the digits "
    + ", ".join(str(value) for value in sorted(DIGITS))
    + " exactly once. Rows are numbered from top to bottom and columns from "
    "left to right, starting at 1. The puzzle has exactly one solution."
)
MESSAGE = RULES + "\n\nGrid:\n" + "\n".join(
    " ".join(str(value) for value in row) for row in PUZZLE
)

# The local solution is never included in state, instructions or choices.
QUESTIONS = {
    f"r{row}c{column}": {
        "type": "choice",
        "instructions": (
            f"In the unique solution to the supplied Sudoku, what digit belongs "
            f"in row {row}, column {column}? Follow all rules in the supplied state."
        ),
        "criteria": {str(value): f"The cell contains {value}." for value in sorted(DIGITS)},
    }
    for row in range(1, 5)
    for column in range(1, 5)
}


def main():
    clues = [value for row in PUZZLE for value in row]
    matching = [board for board in solutions()
                if all(not clue or board[i] == clue for i, clue in enumerate(clues))]
    if len(matching) != 1:
        raise ValueError(f"Expected a unique solution; found {len(matching)}.")
    expected = matching[0]

    def evaluate(body):
        answers = body["answers"]
        predicted = []
        for key in QUESTIONS:
            choice = answers.get(key, {}).get("choice")
            predicted.append(int(choice) if choice in QUESTIONS[key]["criteria"] else None)
        correct = sum(actual == target for actual, target in zip(predicted, expected))
        units_valid = [set(predicted[i] for i in unit) == DIGITS for unit in UNITS]
        report = {
            "predicted_grid": [predicted[i:i + 4] for i in range(0, 16, 4)],
            "expected_grid": [list(expected[i:i + 4]) for i in range(0, 16, 4)],
            "correct_cells": correct,
            "correct_blank_cells": sum(predicted[i] == expected[i] for i, clue in enumerate(clues) if not clue),
            "preserved_clues": sum(predicted[i] == clue for i, clue in enumerate(clues) if clue),
            "valid_rows": sum(units_valid[:4]),
            "valid_columns": sum(units_valid[4:8]),
            "valid_blocks": sum(units_valid[8:]),
            "solved": correct == len(clues),
        }
        print("Sudoku evaluation:")
        print(json.dumps(report, indent=2))
        return report

    return run(MESSAGE, QUESTIONS, evaluate=evaluate)


if __name__ == "__main__":
    raise SystemExit(main())

"""Find a sparse unique 4x4 Sudoku with a long forced-move dependency chain."""

from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path

DIGITS = set(range(1, 5))
UNITS = (
    [tuple(r * 4 + c for c in range(4)) for r in range(4)]
    + [tuple(r * 4 + c for r in range(4)) for c in range(4)]
    + [tuple((r + dr) * 4 + c + dc for dr in range(2) for dc in range(2))
       for r in (0, 2) for c in (0, 2)]
)
PEERS = [set().union(*(set(unit) for unit in UNITS if i in unit)) - {i}
         for i in range(16)]


def solutions():
    boards = []
    def visit(board):
        if len(board) == 16:
            boards.append(tuple(board))
            return
        i = len(board)
        for value in sorted(DIGITS - {board[j] for j in PEERS[i] if j < i}):
            visit(board + [value])
    visit([])
    return boards


def difficulty(board):
    board = list(board)
    waves = []
    while 0 in board:
        candidates = {i: DIGITS - {board[j] for j in PEERS[i]}
                      for i, value in enumerate(board) if not value}
        forced = {i: next(iter(values)) for i, values in candidates.items()
                  if len(values) == 1}
        for unit in UNITS:
            for value in DIGITS - {board[i] for i in unit}:
                positions = [i for i in unit if value in candidates.get(i, set())]
                if len(positions) == 1:
                    forced[positions[0]] = value
        if not forced:
            return (True, len(waves), -len(waves[0]) if waves else 0), waves
        waves.append(sorted(forced.items()))
        for i, value in forced.items():
            board[i] = value
    return (False, len(waves), -len(waves[0])), waves


def main():
    boards = solutions()
    counts = {}
    best = None
    for clue_count in range(1, 5):
        unique_count = 0
        for positions in combinations(range(16), clue_count):
            groups = defaultdict(list)
            for board in boards:
                groups[tuple(board[i] for i in positions)].append(board)
            for values, matching in groups.items():
                if len(matching) != 1:
                    continue
                unique_count += 1
                puzzle = [0] * 16
                for i, value in zip(positions, values):
                    puzzle[i] = value
                rank, waves = difficulty(puzzle)
                if best is None or rank > best[0]:
                    best = (rank, puzzle, matching[0], waves)
        counts[clue_count] = unique_count
        if unique_count:
            break
    result = {
        'complete_boards': len(boards),
        'unique_puzzles_by_clue_count': counts,
        'difficulty_measure': 'Prefer puzzles not solved by naked/hidden singles; otherwise maximize synchronous singles rounds, then minimize initial forced cells.',
        'rank': best[0], 'puzzle': best[1], 'solution': best[2], 'forced_waves': best[3],
    }
    path = Path(__file__).resolve().parents[2] / 'evidence' / 'sudoku'
    path.mkdir(parents=True, exist_ok=True)
    (path / 'search.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

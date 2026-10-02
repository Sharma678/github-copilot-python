from __future__ import annotations

from collections.abc import Sequence

SIZE = 9
EMPTY = 0
Board = list[list[int]]
SearchState = tuple[Board, list[set[int]], list[set[int]], list[set[int]]]


def _prepare_state(board: Sequence[Sequence[int]]) -> SearchState | None:
    try:
        if len(board) != SIZE:
            return None
        working_board = [list(row) for row in board]
    except TypeError:
        return None

    if any(len(row) != SIZE for row in working_board):
        return None

    rows = [set() for _ in range(SIZE)]
    columns = [set() for _ in range(SIZE)]
    boxes = [set() for _ in range(SIZE)]

    for row in range(SIZE):
        for col in range(SIZE):
            value = working_board[row][col]
            if type(value) is not int or not EMPTY <= value <= SIZE:
                return None
            if value == EMPTY:
                continue

            box = (row // 3) * 3 + col // 3
            if value in rows[row] or value in columns[col] or value in boxes[box]:
                return None
            rows[row].add(value)
            columns[col].add(value)
            boxes[box].add(value)

    return working_board, rows, columns, boxes


def _search(
    board: Board,
    rows: list[set[int]],
    columns: list[set[int]],
    boxes: list[set[int]],
    limit: int,
) -> tuple[int, Board | None]:
    best_cell: tuple[int, int] | None = None
    best_candidates: set[int] | None = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue

            box = (row // 3) * 3 + col // 3
            candidates = set(range(1, SIZE + 1)) - rows[row] - columns[col] - boxes[box]
            if not candidates:
                return 0, None
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = row, col
                best_candidates = candidates
                if len(candidates) == 1:
                    break
        if best_candidates is not None and len(best_candidates) == 1:
            break

    if best_cell is None or best_candidates is None:
        return 1, [row[:] for row in board]

    row, col = best_cell
    box = (row // 3) * 3 + col // 3
    solution_count = 0
    first_solution = None

    for value in sorted(best_candidates):
        board[row][col] = value
        rows[row].add(value)
        columns[col].add(value)
        boxes[box].add(value)

        found, solution = _search(
            board,
            rows,
            columns,
            boxes,
            limit - solution_count,
        )
        if first_solution is None and solution is not None:
            first_solution = solution
        solution_count += found

        board[row][col] = EMPTY
        rows[row].remove(value)
        columns[col].remove(value)
        boxes[box].remove(value)

        if solution_count >= limit:
            break

    return solution_count, first_solution


def count_solutions(board: Sequence[Sequence[int]], limit: int = 2) -> int:
    """Count solutions up to ``limit``; invalid or unsolvable boards count as zero."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    state = _prepare_state(board)
    if state is None:
        return 0

    return _search(*state, limit)[0]


def solve(board: Sequence[Sequence[int]]) -> Board | None:
    """Return one solved copy of the board, or None if it has no solution."""
    state = _prepare_state(board)
    if state is None:
        return None

    return _search(*state, 1)[1]
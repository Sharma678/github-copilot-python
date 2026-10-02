import pytest

from difficulty import DIFFICULTY_CLUES
import sudoku_logic


def test_create_empty_board_has_expected_dimensions_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(value == sudoku_logic.EMPTY for row in board for value in row)


def test_deep_copy_is_independent():
    board = sudoku_logic.create_empty_board()

    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 1

    assert board[0][0] == sudoku_logic.EMPTY


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 4, 5)
    assert not sudoku_logic.is_safe(board, 4, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 4, 4, 5)


def test_generate_puzzle_returns_valid_solution_and_preserves_clues():
    clue_count = 35

    puzzle, solution = sudoku_logic.generate_puzzle(clue_count)

    expected_values = set(range(1, sudoku_logic.SIZE + 1))
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(set(row) == expected_values for row in solution)
    assert all(
        {solution[row][col] for row in range(sudoku_logic.SIZE)} == expected_values
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        {solution[row][col] for row in range(box_row, box_row + 3)
         for col in range(box_col, box_col + 3)} == expected_values
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )

    clues = 0
    for row in range(sudoku_logic.SIZE):
        assert len(puzzle[row]) == sudoku_logic.SIZE
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                clues += 1
                assert puzzle[row][col] == solution[row][col]

    assert clues == clue_count
    assert sudoku_logic.count_solutions(puzzle) == 1


@pytest.mark.parametrize("level, expected_clues", DIFFICULTY_CLUES.items())
def test_generate_puzzle_for_difficulty_returns_exact_clues_and_unique_solution(
    level, expected_clues
):
    puzzle, _ = sudoku_logic.generate_puzzle_for_difficulty(level)

    actual_clues = sum(
        value != sudoku_logic.EMPTY
        for row in puzzle
        for value in row
    )
    assert actual_clues == expected_clues
    assert sudoku_logic.count_solutions(puzzle) == 1


@pytest.mark.parametrize("level", ["Impossible", "", None])
def test_generate_puzzle_for_difficulty_rejects_invalid_levels(level):
    with pytest.raises(ValueError, match="Invalid difficulty"):
        sudoku_logic.generate_puzzle_for_difficulty(level)


def test_generate_puzzle_clues_api_remains_supported():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=45)

    actual_clues = sum(
        value != sudoku_logic.EMPTY
        for row in puzzle
        for value in row
    )
    assert actual_clues == 45
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
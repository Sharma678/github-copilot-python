import sudoku_logic
from sudoku_solver import count_solutions, solve


def make_solution():
    return [
        [((row * 3 + row // 3 + col) % sudoku_logic.SIZE) + 1
         for col in range(sudoku_logic.SIZE)]
        for row in range(sudoku_logic.SIZE)
    ]


def test_completed_valid_sudoku_has_one_solution():
    board = make_solution()

    assert count_solutions(board) == 1
    assert solve(board) == board


def test_invalid_board_has_no_solutions():
    board = make_solution()
    board[0][0] = board[0][1]

    assert count_solutions(board) == 0
    assert solve(board) is None


def test_multiple_solutions_are_detected_and_count_is_capped():
    board = sudoku_logic.create_empty_board()

    assert count_solutions(board) == 2
    assert count_solutions(board, limit=3) == 3


def test_solver_completes_a_partially_filled_board():
    solution = make_solution()
    puzzle = [row[:] for row in solution]
    puzzle[0][0] = sudoku_logic.EMPTY

    assert solve(puzzle) == solution
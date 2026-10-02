import copy
import random

from difficulty import clues_for_difficulty
from sudoku_solver import count_solutions

SIZE = 9
EMPTY = 0
Board = list[list[int]]


def deep_copy(board: Board) -> Board:
    return copy.deepcopy(board)


def create_empty_board() -> Board:
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board: Board) -> bool:
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board: Board, clues: int) -> bool:
    if not 17 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 17 and 81")

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    remaining_clues = SIZE * SIZE

    for row, col in cells:
        if remaining_clues <= clues:
            break

        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) == 1:
            remaining_clues -= 1
        else:
            board[row][col] = value

    return remaining_clues == clues


def generate_puzzle(clues: int = 35) -> tuple[Board, Board]:
    if not 17 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 17 and 81")

    while True:
        board = create_empty_board()
        if not fill_board(board):
            raise RuntimeError("Unable to generate a completed Sudoku board")
        solution = deep_copy(board)
        if remove_cells(board, clues):
            return deep_copy(board), solution


def generate_puzzle_for_difficulty(level: str) -> tuple[Board, Board]:
    """Generate a unique puzzle using the configured difficulty clue count."""
    return generate_puzzle(clues_for_difficulty(level))

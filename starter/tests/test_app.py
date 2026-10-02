import copy

import pytest

import app as app_module
import sudoku_logic


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.CURRENT.update({
        "puzzle": None,
        "solution": None,
        "hints_used": 0,
        "hinted_cells": set(),
    })
    with app_module.app.test_client() as test_client:
        yield test_client
    app_module.CURRENT.update({
        "puzzle": None,
        "solution": None,
        "hints_used": 0,
        "hinted_cells": set(),
    })


def make_solution():
    return [
        [((row * 3 + row // 3 + col) % sudoku_logic.SIZE) + 1
         for col in range(sudoku_logic.SIZE)]
        for row in range(sudoku_logic.SIZE)
    ]


def test_index_renders_game_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data
    assert b'id="hint"' in response.data
    assert b'id="hint-count"' in response.data


def test_new_game_defaults_to_medium_and_stores_solution(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = make_solution()
    requested_difficulties = []

    def generate_puzzle_for_difficulty(level):
        requested_difficulties.append(level)
        return puzzle, solution

    monkeypatch.setattr(
        app_module.sudoku_logic,
        "generate_puzzle_for_difficulty",
        generate_puzzle_for_difficulty,
    )

    response = client.get("/new")

    assert response.status_code == 200
    assert response.get_json() == {"puzzle": puzzle, "hints_used": 0}
    assert requested_difficulties == ["Medium"]
    assert app_module.CURRENT["puzzle"] == puzzle
    assert app_module.CURRENT["solution"] == solution
    assert app_module.CURRENT["hints_used"] == 0
    assert app_module.CURRENT["hinted_cells"] == set()


@pytest.mark.parametrize("difficulty", ["Easy", "Medium", "Hard"])
def test_new_game_accepts_difficulty(client, monkeypatch, difficulty):
    puzzle = sudoku_logic.create_empty_board()
    requested_difficulties = []

    def generate_puzzle_for_difficulty(level):
        requested_difficulties.append(level)
        return puzzle, make_solution()

    monkeypatch.setattr(
        app_module.sudoku_logic,
        "generate_puzzle_for_difficulty",
        generate_puzzle_for_difficulty,
    )

    response = client.get("/new", query_string={"difficulty": difficulty})

    assert response.status_code == 200
    assert response.get_json() == {"puzzle": puzzle, "hints_used": 0}
    assert requested_difficulties == [difficulty]


def test_new_game_returns_clear_error_for_invalid_difficulty(client):
    response = client.get("/new", query_string={"difficulty": "Expert"})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Invalid difficulty 'Expert'. Choose Easy, Medium, Hard."
    }


def test_check_returns_error_when_no_game_is_in_progress(client):
    response = client.post("/check", json={"board": make_solution()})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_check_returns_empty_incorrect_list_for_solution(client):
    solution = make_solution()
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": copy.deepcopy(solution)})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_check_does_not_mark_blank_cells_as_incorrect(client):
    solution = make_solution()
    board = copy.deepcopy(solution)
    board[0][0] = 0
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_check_returns_no_incorrect_cells_for_correct_partial_board(client):
    solution = make_solution()
    board = copy.deepcopy(solution)
    board[0][0] = 0
    board[1][1] = 0
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_check_reports_coordinates_of_incorrect_cells(client):
    solution = make_solution()
    board = copy.deepcopy(solution)
    board[0][0] = solution[0][1]
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [[0, 0]]}


def make_hint_game(empty_cells=((0, 0), (0, 1))):
    solution = make_solution()
    puzzle = copy.deepcopy(solution)
    for row, col in empty_cells:
        puzzle[row][col] = 0
    app_module.CURRENT.update({
        "puzzle": puzzle,
        "solution": solution,
        "hints_used": 0,
        "hinted_cells": set(),
    })
    return puzzle, solution


def test_hint_returns_correct_value_for_one_empty_cell(client):
    puzzle, solution = make_hint_game()

    response = client.post("/hint", json={"board": copy.deepcopy(puzzle)})

    assert response.status_code == 200
    assert response.get_json() == {
        "row": 0,
        "col": 0,
        "value": solution[0][0],
        "hints_used": 1,
    }
    assert app_module.CURRENT["hinted_cells"] == {(0, 0)}


def test_hint_does_not_reissue_a_previously_hinted_cell(client):
    puzzle, solution = make_hint_game()
    first_hint = client.post("/hint", json={"board": copy.deepcopy(puzzle)}).get_json()

    response = client.post("/hint", json={"board": copy.deepcopy(puzzle)})

    assert response.status_code == 200
    assert response.get_json() == {
        "row": 0,
        "col": 1,
        "value": solution[0][1],
        "hints_used": 2,
    }


def test_hint_does_not_overwrite_an_existing_user_entry(client):
    puzzle, solution = make_hint_game()
    board = copy.deepcopy(puzzle)
    board[0][0] = solution[0][0]

    response = client.post("/hint", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {
        "row": 0,
        "col": 1,
        "value": solution[0][1],
        "hints_used": 1,
    }
    assert board[0][0] == solution[0][0]


def test_hint_count_increments_for_each_hint(client):
    puzzle, _ = make_hint_game()
    first = client.post("/hint", json={"board": copy.deepcopy(puzzle)}).get_json()
    board = copy.deepcopy(puzzle)
    board[first["row"]][first["col"]] = first["value"]

    response = client.post("/hint", json={"board": board})

    assert response.get_json()["hints_used"] == 2
    assert app_module.CURRENT["hints_used"] == 2


def test_new_game_resets_hint_count(client, monkeypatch):
    puzzle, solution = make_hint_game()
    app_module.CURRENT["hints_used"] = 3
    app_module.CURRENT["hinted_cells"] = {(0, 0), (0, 1)}
    monkeypatch.setattr(
        app_module.sudoku_logic,
        "generate_puzzle_for_difficulty",
        lambda level: (puzzle, solution),
    )

    response = client.get("/new", query_string={"difficulty": "Hard"})

    assert response.status_code == 200
    assert response.get_json()["hints_used"] == 0
    assert app_module.CURRENT["hints_used"] == 0
    assert app_module.CURRENT["hinted_cells"] == set()


def test_hint_returns_clear_message_when_no_empty_cells_remain(client):
    _, solution = make_hint_game()

    response = client.post("/hint", json={"board": copy.deepcopy(solution)})

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "No empty cells remaining",
        "hints_used": 0,
    }
from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
    'hinted_cells': set()
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'Medium')
    try:
        puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    CURRENT['hinted_cells'] = set()
    return jsonify({'puzzle': puzzle, 'hints_used': CURRENT['hints_used']})

@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if (
        not isinstance(board, list)
        or len(board) != sudoku_logic.SIZE
        or any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE for row in board)
        or any(
            type(value) is not int or not 0 <= value <= sudoku_logic.SIZE
            for row in board
            for value in row
        )
    ):
        return jsonify({'error': 'Invalid board'}), 400

    hinted_cells = CURRENT['hinted_cells']
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            cell = (row, col)
            if (
                puzzle[row][col] == sudoku_logic.EMPTY
                and board[row][col] == sudoku_logic.EMPTY
                and cell not in hinted_cells
            ):
                hinted_cells.add(cell)
                CURRENT['hints_used'] += 1
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                    'hints_used': CURRENT['hints_used'],
                })

    return jsonify({
        'error': 'No empty cells remaining',
        'hints_used': CURRENT['hints_used'],
    }), 409

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != 0 and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)
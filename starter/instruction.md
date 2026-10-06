# Udacity GitHub Copilot Python Sudoku Project Instructions

## PROJECT CONTEXT

- This is a Flask-based Sudoku web application.
- Python is used for the backend and Sudoku logic.
- HTML, CSS, and JavaScript are used for the frontend.
- The application generates Sudoku puzzles with exactly one unique solution.
- Difficulty levels are Easy, Medium, and Hard.
- Easy has 45 clues.
- Medium has 35 clues.
- Hard has 28 clues.
- The project includes a Sudoku solver and bounded solution counter.
- The application has validation, hints, a timer, a Top 10 leaderboard using localStorage, and light/dark mode.

## CODE ORGANIZATION

- Keep backend logic modular and reusable.
- Keep Sudoku generation and solving separate from Flask routes.
- Keep frontend UI behavior in `main.js` and presentation in `styles.css`.
- Avoid unnecessary changes to unrelated files.
- Preserve existing public interfaces unless a requirement explicitly requires changing them.

## PYTHON STANDARDS

- Use modern Python syntax and type hints.
- Prefer clear, readable functions with single responsibilities.
- Use descriptive variable and function names.
- Add docstrings where they improve clarity.
- Handle invalid input explicitly.
- Avoid duplicated Sudoku-solving logic.
- Do not introduce unnecessary dependencies.

## FLASK STANDARDS

- Keep routes small and focused.
- Validate incoming request data.
- Return appropriate HTTP status codes for invalid requests.
- Preserve existing JSON response structures unless requirements require otherwise.

## FRONTEND STANDARDS

- Keep JavaScript modular and readable.
- Avoid changing working game behavior when adding UI features.
- Keep the interface responsive for desktop and mobile.
- Maintain light and dark mode support.
- Maintain keyboard accessibility and visible focus states.
- Do not use `innerHTML` for user-controlled leaderboard names.
- Store only appropriate client-side data in `localStorage`.

## SUDOKU REQUIREMENTS

- Every generated puzzle must have exactly one solution.
- Prefilled cells must remain locked.
- Difficulty must control the exact number of clues.
- Hints must fill only valid cells and lock the hinted cell.
- Check Solution must distinguish incorrect, incomplete, and solved states.
- Timer must start for a new puzzle and stop when the puzzle is successfully completed.
- A completed game should be recorded only once.
- Leaderboard must retain only the 10 fastest valid scores.

## TESTING

- Run the complete pytest suite after significant changes.
- Do not consider a change complete if existing tests fail.
- Add or update tests when backend behavior changes.
- Preserve existing tests unless the underlying requirement has intentionally changed.
- The standard test command from the starter directory is:

  ```powershell
  python -m pytest
  ```

## COPILOT WORKFLOW

- Before making broad changes, inspect the existing implementation.
- Make changes incrementally.
- Explain important design decisions.
- Prefer the smallest change that satisfies the requirement.
- Do not modify unrelated files.
- When a change could break existing behavior, run the tests before and after the change.
- If a suggested implementation is questionable, explain the trade-offs instead of blindly applying it.

## PROJECT SAFETY

- Never commit `.venv`, `__pycache__`, `.pytest_cache`, `*.pyc`, secrets, passwords, API keys, or other generated files.
- Keep generated and cache files out of Git.
- Do not introduce credentials into source code.

When working on this project, treat these instructions as the project's development guidelines and use them to keep Copilot's suggestions consistent, maintainable, testable, and aligned with the Udacity project requirements.

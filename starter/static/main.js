// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';
const LEADERBOARD_LIMIT = 10;
const THEME_STORAGE_KEY = 'sudokuTheme';
let puzzle = [];
let hintsUsed = 0;
window.hintsUsed = hintsUsed;
let timerIntervalId = null;
let timerStartedAt = null;
let elapsedTimeSeconds = 0;
window.elapsedTimeSeconds = elapsedTimeSeconds;
let currentGameDifficulty = null;
let completionPromptShown = false;
let completionRecorded = false;
let pendingCompletion = null;

function applyTheme(theme) {
  const darkMode = theme === 'dark';
  document.documentElement.dataset.theme = darkMode ? 'dark' : 'light';
  const button = document.getElementById('theme-toggle');
  button.setAttribute('aria-pressed', String(darkMode));
  button.setAttribute('aria-label', darkMode ? 'Switch to light mode' : 'Switch to dark mode');
  button.textContent = darkMode ? 'Dark mode: On' : 'Dark mode: Off';
}

function loadThemePreference() {
  try {
    return window.localStorage.getItem(THEME_STORAGE_KEY) === 'dark' ? 'dark' : 'light';
  } catch (error) {
    return 'light';
  }
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  } catch (error) {
    // Keep the selected theme active for this page even when storage is unavailable.
  }
}

function formatElapsedTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function renderTimer() {
  document.getElementById('game-timer').innerText = formatElapsedTime(elapsedTimeSeconds);
  window.elapsedTimeSeconds = elapsedTimeSeconds;
}

function validateLeaderboardEntry(entry) {
  if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return null;

  const name = typeof entry.name === 'string' ? entry.name.trim() : '';
  const validDifficulties = ['Easy', 'Medium', 'Hard'];
  if (
    !name
    || !Number.isSafeInteger(entry.timeSeconds)
    || entry.timeSeconds < 0
    || typeof entry.formattedTime !== 'string'
    || !validDifficulties.includes(entry.difficulty)
    || !Number.isSafeInteger(entry.hintsUsed)
    || entry.hintsUsed < 0
  ) {
    return null;
  }

  return {
    name: name.slice(0, 40),
    timeSeconds: entry.timeSeconds,
    formattedTime: entry.formattedTime,
    difficulty: entry.difficulty,
    hintsUsed: entry.hintsUsed,
  };
}

function sortAndCapLeaderboard(entries) {
  return entries
    .slice()
    .sort((first, second) => first.timeSeconds - second.timeSeconds)
    .slice(0, LEADERBOARD_LIMIT);
}

function loadLeaderboard() {
  try {
    const storedEntries = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!storedEntries) return [];

    const parsedEntries = JSON.parse(storedEntries);
    if (!Array.isArray(parsedEntries)) return [];
    return sortAndCapLeaderboard(parsedEntries.map(validateLeaderboardEntry).filter(Boolean));
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(entries) {
  try {
    window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(entries));
    return true;
  } catch (error) {
    return false;
  }
}

function renderLeaderboard(entries = loadLeaderboard()) {
  const tableBody = document.getElementById('leaderboard-entries');
  const emptyState = document.getElementById('leaderboard-empty');
  tableBody.replaceChildren();

  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    [index + 1, entry.name, entry.formattedTime, entry.difficulty, entry.hintsUsed]
      .forEach(value => {
        const cell = document.createElement('td');
        cell.textContent = String(value);
        row.appendChild(cell);
      });
    tableBody.appendChild(row);
  });

  emptyState.hidden = entries.length > 0;
}

function showCompletionNameForm() {
  if (completionPromptShown) return;

  completionPromptShown = true;
  pendingCompletion = {
    timeSeconds: elapsedTimeSeconds,
    formattedTime: formatElapsedTime(elapsedTimeSeconds),
    difficulty: currentGameDifficulty,
    hintsUsed,
  };
  const form = document.getElementById('leaderboard-name-form');
  form.reset();
  form.hidden = false;
  document.getElementById('leaderboard-message').textContent = 'Enter your name to submit your time.';
  document.getElementById('leaderboard-player-name').focus();
}

function recordCompletedGame(event) {
  event.preventDefault();
  if (completionRecorded || !pendingCompletion) return;

  const nameInput = document.getElementById('leaderboard-player-name');
  const name = nameInput.value.trim().slice(0, 40);
  const message = document.getElementById('leaderboard-message');
  if (!name) {
    message.textContent = 'Enter a name to submit your time.';
    nameInput.focus();
    return;
  }

  const entry = validateLeaderboardEntry({...pendingCompletion, name});
  if (!entry) {
    message.textContent = 'Unable to record this completion.';
    return;
  }

  const existingEntries = loadLeaderboard();
  const sortedEntries = sortAndCapLeaderboard(existingEntries);
  if (
    sortedEntries.length >= LEADERBOARD_LIMIT
    && entry.timeSeconds >= sortedEntries[sortedEntries.length - 1].timeSeconds
  ) {
    completionRecorded = true;
    pendingCompletion = null;
    document.getElementById('leaderboard-name-form').hidden = true;
    message.textContent = 'Your time did not make the Top 10.';
    return;
  }

  const updatedEntries = sortAndCapLeaderboard([...sortedEntries, entry]);
  if (!saveLeaderboard(updatedEntries)) {
    message.textContent = 'Leaderboard storage is unavailable. Your game is still complete.';
    return;
  }

  completionRecorded = true;
  pendingCompletion = null;
  document.getElementById('leaderboard-name-form').hidden = true;
  message.textContent = 'Your time was added to the leaderboard.';
  renderLeaderboard(updatedEntries);
}

function updateTimer() {
  if (timerStartedAt === null) return;
  elapsedTimeSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
  renderTimer();
}

function clearTimerInterval() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function resetTimer() {
  clearTimerInterval();
  timerStartedAt = null;
  elapsedTimeSeconds = 0;
  renderTimer();
}

function startTimer() {
  clearTimerInterval();
  timerStartedAt = Date.now();
  updateTimer();
  timerIntervalId = setInterval(updateTimer, 1000);
}

function stopTimer() {
  if (timerStartedAt !== null) updateTimer();
  clearTimerInterval();
  timerStartedAt = null;
}

function setHintsUsed(count) {
  hintsUsed = count;
  window.hintsUsed = count;
  document.getElementById('hint-count').innerText = count;
}

function updateHintButton() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const hasEmptyEditableCell = Array.from(inputs).some(input => !input.disabled && input.value === '');
  document.getElementById('hint').disabled = !hasEmptyEditableCell;
}

function getCurrentBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const value = inputs[row * SIZE + col].value;
      board[row][col] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.classList.add((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 0 ? 'box-even' : 'box-odd');
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateHintButton();
        validateBoard(true);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  updateHintButton();
}

async function newGame() {
  validationRequest++;
  resetTimer();
  completionPromptShown = false;
  completionRecorded = false;
  pendingCompletion = null;
  currentGameDifficulty = null;
  document.getElementById('leaderboard-name-form').hidden = true;
  document.getElementById('leaderboard-message').textContent = '';
  const hintButton = document.getElementById('hint');
  hintButton.disabled = true;
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok) {
    document.getElementById('message').innerText = data.error || 'Unable to start a new game.';
    updateHintButton();
    return;
  }
  renderPuzzle(data.puzzle);
  setHintsUsed(data.hints_used);
  currentGameDifficulty = difficulty;
  document.getElementById('message').innerText = '';
  startTimer();
}

let validationRequest = 0;

async function validateBoard(showStatus = false) {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = getCurrentBoard();
  const requestId = ++validationRequest;
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (requestId !== validationRequest) return;
  if (!res.ok || data.error) {
    msg.style.color = 'var(--status-error)';
    msg.innerText = data.error || 'Unable to check the puzzle.';
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    inputs[idx].classList.toggle('incorrect', incorrect.has(idx));
  }

  if (!showStatus) return;

  const hasEmptyCells = Array.from(inputs).some(input => input.value === '');
  if (incorrect.size > 0) {
    msg.style.color = 'var(--status-error)';
    msg.innerText = 'Some entries are incorrect.';
  } else if (hasEmptyCells) {
    msg.style.color = 'var(--status-warning)';
    msg.innerText = 'Puzzle incomplete. Fill in the remaining cells.';
  } else {
    msg.style.color = 'var(--status-success)';
    msg.innerText = 'Puzzle solved!';
    stopTimer();
    showCompletionNameForm();
  }
}

function checkSolution() {
  validateBoard(true);
}

async function requestHint() {
  const inputs = Array.from(document.getElementById('sudoku-board').getElementsByTagName('input'));
  const editableInputs = inputs.filter(input => !input.disabled);
  if (!editableInputs.some(input => input.value === '')) {
    document.getElementById('message').innerText = 'No empty cells remaining.';
    updateHintButton();
    return;
  }

  validationRequest++;
  const hintButton = document.getElementById('hint');
  const newGameButton = document.getElementById('new-game');
  hintButton.disabled = true;
  newGameButton.disabled = true;
  editableInputs.forEach(input => { input.disabled = true; });
  let hintApplied = false;

  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getCurrentBoard()})
    });
    const data = await res.json();
    const msg = document.getElementById('message');
    if (!res.ok || data.error) {
      msg.style.color = 'var(--status-error)';
      msg.innerText = data.error || 'Unable to get a hint.';
      return;
    }

    const cell = inputs[data.row * SIZE + data.col];
    if (!cell || cell.value !== '' || puzzle[data.row][data.col] !== 0) {
      msg.style.color = 'var(--status-error)';
      msg.innerText = 'Unable to apply the hint safely.';
      return;
    }
    cell.value = data.value;
    cell.disabled = true;
    cell.classList.add('hinted');
    cell.classList.remove('incorrect');
    setHintsUsed(data.hints_used);
    hintApplied = true;
  } catch (error) {
    const msg = document.getElementById('message');
    msg.style.color = 'var(--status-error)';
    msg.innerText = 'Unable to get a hint.';
  } finally {
    editableInputs.forEach(input => {
      if (!input.classList.contains('hinted')) input.disabled = false;
    });
    newGameButton.disabled = false;
    updateHintButton();
  }

  if (hintApplied) await validateBoard(true);
}

applyTheme(loadThemePreference());

// Wire buttons
window.addEventListener('load', () => {
  renderLeaderboard();
  document.getElementById('leaderboard-name-form').addEventListener('submit', recordCompletedGame);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  // initialize
  newGame();
});
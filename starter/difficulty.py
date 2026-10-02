DIFFICULTY_CLUES: dict[str, int] = {
    "Easy": 45,
    "Medium": 35,
    "Hard": 28,
}


def clues_for_difficulty(level: str) -> int:
    """Return the configured number of clues for a difficulty level."""
    if isinstance(level, str):
        normalized_level = level.strip().capitalize()
        if normalized_level in DIFFICULTY_CLUES:
            return DIFFICULTY_CLUES[normalized_level]

    choices = ", ".join(DIFFICULTY_CLUES)
    raise ValueError(f"Invalid difficulty {level!r}. Choose {choices}.")
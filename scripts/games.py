"""
Finished games page: loads and organizes games.json with in-process caching.
"""

import json
from pathlib import Path

# Games data cache
_GAMES_CACHE = None
_GAMES_BY_LETTER_CACHE = None


def load_games():
    """
    Loads games data from JSON file with caching. If file doesn't exist, returns empty list.
    Only caches successful non-empty loads to avoid poisoning cache with transient errors.
    """
    global _GAMES_CACHE

    if _GAMES_CACHE is not None:
        return _GAMES_CACHE

    try:
        # Get the parent directory of this script, then navigate to static/json
        json_path = Path(__file__).parent.parent / "static" / "json" / "games.json"
        with open(json_path, "r", encoding="utf-8") as f:
            games = json.load(f)["games"]
            # Only cache if we successfully loaded data
            if games:
                _GAMES_CACHE = games
            return games
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading games.json: {e}")
        return []


def get_games_dict():
    """
    Returns games organized by first letter for efficient template rendering.
    Uses caching to avoid repeated processing.
    Only caches when games are successfully loaded.
    """
    global _GAMES_BY_LETTER_CACHE

    if _GAMES_BY_LETTER_CACHE is not None:
        return _GAMES_BY_LETTER_CACHE

    games = load_games()

    # Don't cache empty results from transient errors
    if not games:
        return {}

    by_letter = {}
    for game in games:
        letter = game["title"][0].upper()
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(game)

    _GAMES_BY_LETTER_CACHE = by_letter
    return by_letter


def get_games_by_letter(letter):
    """
    Returns list of games that start with given letter.
    Uses cached pre-organized dictionary for efficiency.

    Args:
        letter: Single letter (case-insensitive) to filter games by.
                Multi-character input uses only the first character.

    Returns:
        List of games starting with the specified letter, or empty list.
    """
    if not letter:
        return []

    # Normalize: uppercase first character only
    normalized_letter = letter[0].upper()

    games_dict = get_games_dict()
    return games_dict.get(normalized_letter, [])

"""Text, Markdown, and JSON file parsing utilities."""

import json
from pathlib import Path
from typing import Any


def read_text_file(path: str | Path, *, max_chars: int | None = None) -> str:
    """Read a plain-text file and return its contents as a string.

    Handles Markdown, TXT, and any other UTF-8 encoded text file.

    Args:
        path: Path to the text file.
        max_chars: If set, truncate the returned content to at most this many
            characters.  The file is still read in full; truncation happens
            after reading.

    Returns:
        The file contents as a string, optionally truncated.

    Raises:
        FileNotFoundError: If *path* does not point to an existing file.
    """
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"File not found: {resolved}")

    text = resolved.read_text(encoding="utf-8")

    if max_chars is not None:
        text = text[:max_chars]

    return text


def parse_json_file(path: str | Path, *, json_path: str | None = None) -> Any:
    """Parse a JSON file and optionally extract a nested value by dot-notation path.

    Args:
        path: Path to the JSON file.
        json_path: Optional dot-separated key path (e.g. ``"departments"`` or
            ``"meta.version"``).  When provided, the parsed JSON is traversed
            key-by-key and only the targeted value is returned.

    Returns:
        The full parsed JSON object, or the value at *json_path* if specified.

    Raises:
        FileNotFoundError: If *path* does not point to an existing file.
        json.JSONDecodeError: If the file contains invalid JSON.
        KeyError: If any segment of *json_path* does not exist in the data.
    """
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"File not found: {resolved}")

    text = resolved.read_text(encoding="utf-8")
    data: Any = json.loads(text)

    if json_path is not None:
        for key in json_path.split("."):
            try:
                data = data[key]
            except (TypeError, KeyError):
                raise KeyError(f"Key not found: {key!r} (full path: {json_path!r})")

    return data

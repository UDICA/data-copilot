"""Query validation, path sandboxing, and result safety limits."""

import re
from pathlib import Path
from typing import Any


class QueryValidationError(Exception):
    """Raised when a SQL query fails safety validation."""


_WRITE_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|MERGE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def validate_sql_query(query: str, *, allow_writes: bool = False) -> bool:
    """Validate that a SQL query is safe to execute.

    Args:
        query: The SQL query string to validate.
        allow_writes: If True, skip write-operation checks.

    Returns:
        True if the query passes validation.

    Raises:
        QueryValidationError: If the query contains disallowed operations.
    """
    stripped = query.strip().rstrip(";")
    if not allow_writes and _WRITE_PATTERNS.search(stripped):
        raise QueryValidationError(
            "Query contains a write operation which is not allowed in read-only mode. "
            "Only SELECT, EXPLAIN, and WITH queries are permitted."
        )
    return True


def sanitize_path(path_str: str) -> Path:
    """Resolve a path string to an absolute path, removing traversal components.

    Args:
        path_str: A file path string, possibly containing '..' or relative segments.

    Returns:
        Resolved absolute Path.
    """
    return Path(path_str).resolve()


def is_within_allowed_paths(path_str: str, allowed_paths: list[str]) -> bool:
    """Check whether a resolved path falls within any of the allowed directories.

    Args:
        path_str: The file path to check.
        allowed_paths: List of allowed directory path strings.

    Returns:
        True if the path is inside at least one allowed directory.
    """
    resolved = sanitize_path(path_str)
    for allowed in allowed_paths:
        allowed_resolved = Path(allowed).resolve()
        if resolved == allowed_resolved or allowed_resolved in resolved.parents:
            return True
    return False


def truncate_result(
    rows: list[dict[str, Any]], *, max_rows: int = 1000
) -> tuple[list[dict[str, Any]], bool]:
    """Truncate a result set to the maximum allowed rows.

    Args:
        rows: List of row dictionaries.
        max_rows: Maximum number of rows to return.

    Returns:
        Tuple of (truncated rows, whether truncation occurred).
    """
    if len(rows) <= max_rows:
        return rows, False
    return rows[:max_rows], True

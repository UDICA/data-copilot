"""CSV and TSV file parsing with filtering and summary statistics."""

from pathlib import Path
from typing import Any

import pandas as pd


def parse_csv(
    path: str | Path,
    *,
    filters: dict[str, Any] | None = None,
    max_rows: int | None = None,
) -> pd.DataFrame:
    """Read a CSV or TSV file into a DataFrame with optional filtering.

    The separator is auto-detected based on file extension: ``.tsv`` and
    ``.tab`` files use a tab separator; all other extensions rely on the
    Python csv sniffer (``sep=None, engine="python"``).

    Args:
        path: Path to the CSV/TSV file.
        filters: Optional column=value equality filters.  Each key must be a
            column name present in the file and rows are kept only when the
            column value equals the filter value.
        max_rows: If set, return at most this many rows (applied after
            filtering via ``DataFrame.head``).

    Returns:
        A pandas DataFrame containing the (optionally filtered and truncated)
        data.

    Raises:
        FileNotFoundError: If *path* does not point to an existing file.
    """
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"File not found: {resolved}")

    suffix = resolved.suffix.lower()
    if suffix in (".tsv", ".tab"):
        df = pd.read_csv(resolved, sep="\t")
    else:
        df = pd.read_csv(resolved, sep=None, engine="python")

    if filters:
        for column, value in filters.items():
            df = df.loc[df[column] == value]

    if max_rows is not None:
        df = df.head(max_rows)

    return df


def get_csv_summary(path: str | Path) -> dict[str, Any]:
    """Return a structural summary of a CSV/TSV file.

    Args:
        path: Path to the CSV/TSV file.

    Returns:
        Dictionary with keys:
            - ``rows``: Total number of data rows.
            - ``columns``: Number of columns.
            - ``column_names``: List of column name strings.
            - ``column_types``: Mapping of column name to pandas dtype string.
            - ``sample``: First five rows as a list of dictionaries.

    Raises:
        FileNotFoundError: If *path* does not point to an existing file.
    """
    df = parse_csv(path)
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": df.head(5).to_dict(orient="records"),
    }

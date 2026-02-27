"""Excel workbook parsing with sheet selection and row limiting.

Wraps openpyxl / pandas to provide a simple interface for reading .xlsx files
into DataFrames, listing available sheets, and capping the number of rows
returned to keep LLM context windows manageable.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def list_sheets(path: Path) -> list[str]:
    """Return the ordered list of sheet names in an Excel workbook.

    Args:
        path: Filesystem path to an ``.xlsx`` file.

    Returns:
        Sheet names in the order they appear in the workbook.

    Raises:
        FileNotFoundError: If *path* does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")

    with pd.ExcelFile(path, engine="openpyxl") as xls:
        return xls.sheet_names


def parse_excel(
    path: Path,
    *,
    sheet_name: str | None = None,
    max_rows: int | None = None,
) -> pd.DataFrame:
    """Read a single sheet from an Excel workbook into a DataFrame.

    Args:
        path: Filesystem path to an ``.xlsx`` file.
        sheet_name: Name of the sheet to read.  When *None* the first sheet
            in the workbook is used.
        max_rows: Optional upper limit on the number of data rows returned
            (header row is not counted).  When *None* every row is returned.

    Returns:
        A :class:`~pandas.DataFrame` with the parsed sheet data.

    Raises:
        FileNotFoundError: If *path* does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")

    # Default to the first sheet (index 0) when no name is given.
    target = sheet_name if sheet_name is not None else 0

    df: pd.DataFrame = pd.read_excel(
        path,
        sheet_name=target,
        engine="openpyxl",
        nrows=max_rows,
    )
    return df

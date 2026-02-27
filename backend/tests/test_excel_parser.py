"""Tests for the Excel workbook parser."""

from pathlib import Path

import openpyxl
import pytest

from src.parsers.excel_parser import list_sheets, parse_excel


@pytest.fixture
def excel_path(tmp_path: Path) -> Path:
    """Create a minimal multi-sheet Excel workbook for testing."""
    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "Sales"
    ws.append(["product", "region", "revenue"])
    ws.append(["Widget", "North", 50000])
    ws.append(["Gadget", "South", 62000])
    ws.append(["Widget", "South", 48000])

    ws2 = wb.create_sheet("Targets")
    ws2.append(["region", "target"])
    ws2.append(["North", 100000])
    ws2.append(["South", 120000])

    path = tmp_path / "sample.xlsx"
    wb.save(path)
    return path


class TestListSheets:
    def test_lists_sheets(self, excel_path: Path) -> None:
        sheets = list_sheets(excel_path)
        assert sheets == ["Sales", "Targets"]


class TestParseExcel:
    def test_reads_default_sheet(self, excel_path: Path) -> None:
        df = parse_excel(excel_path)
        assert len(df) == 3
        assert "product" in df.columns

    def test_reads_named_sheet(self, excel_path: Path) -> None:
        df = parse_excel(excel_path, sheet_name="Targets")
        assert len(df) == 2
        assert "target" in df.columns


class TestErrors:
    def test_nonexistent_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope.xlsx"
        with pytest.raises(FileNotFoundError):
            list_sheets(missing)
        with pytest.raises(FileNotFoundError):
            parse_excel(missing)

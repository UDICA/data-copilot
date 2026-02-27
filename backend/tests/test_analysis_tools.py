"""Tests for the data analysis tools."""

import json

import pytest

from src.tools.analysis_tools import (
    cross_join_data,
    describe_data,
    export_to_csv,
    get_analysis_registry,
)


SAMPLE_DATA = json.dumps([
    {"name": "Alice", "region": "North", "revenue": 50000},
    {"name": "Bob", "region": "South", "revenue": 62000},
    {"name": "Carol", "region": "North", "revenue": 48000},
])

SAMPLE_LEFT = json.dumps([
    {"region": "North", "manager": "Dana"},
    {"region": "South", "manager": "Evan"},
])

SAMPLE_RIGHT = json.dumps([
    {"region": "North", "target": 100000},
    {"region": "South", "target": 120000},
])


class TestGetAnalysisRegistry:
    def test_returns_registry(self):
        registry = get_analysis_registry()
        tools = registry.list_tools()
        assert "describe_data" in tools
        assert "cross_join_data" in tools
        assert "export_to_csv" in tools


class TestDescribeData:
    @pytest.mark.asyncio
    async def test_numeric_statistics(self):
        result = await describe_data(SAMPLE_DATA)
        assert "Numeric Columns" in result
        # Standard describe() stats must be present.
        assert "mean" in result
        assert "count" in result

    @pytest.mark.asyncio
    async def test_categorical_statistics(self):
        result = await describe_data(SAMPLE_DATA)
        assert "Categorical Columns" in result
        # Region "North" appears twice.
        assert "North" in result

    @pytest.mark.asyncio
    async def test_source_attribution(self):
        result = await describe_data(SAMPLE_DATA)
        assert "[Source: describe_data" in result

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error(self):
        result = await describe_data("not valid json{{{")
        assert "[Error in describe_data]" in result
        assert "Invalid JSON" in result


class TestCrossJoinData:
    @pytest.mark.asyncio
    async def test_inner_join(self):
        result = await cross_join_data(SAMPLE_DATA, SAMPLE_RIGHT, "region")
        # All three original rows should match (North and South both exist).
        assert "Alice" in result
        assert "Bob" in result
        assert "Carol" in result
        # Target values from the right dataset should appear.
        assert "100000" in result
        assert "120000" in result

    @pytest.mark.asyncio
    async def test_source_attribution(self):
        result = await cross_join_data(SAMPLE_LEFT, SAMPLE_RIGHT, "region")
        assert "[Source: cross_join_data" in result

    @pytest.mark.asyncio
    async def test_missing_join_column(self):
        result = await cross_join_data(SAMPLE_LEFT, SAMPLE_RIGHT, "nonexistent")
        assert "[Error in cross_join_data]" in result
        assert "nonexistent" in result

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error(self):
        result = await cross_join_data("bad", SAMPLE_RIGHT, "region")
        assert "[Error in cross_join_data]" in result
        assert "Invalid JSON" in result


class TestExportToCsv:
    @pytest.mark.asyncio
    async def test_csv_output(self):
        result = await export_to_csv(SAMPLE_DATA)
        # Header row must include all column names.
        assert "name" in result
        assert "region" in result
        assert "revenue" in result
        # Data values must be present.
        assert "Alice" in result
        assert "62000" in result

    @pytest.mark.asyncio
    async def test_csv_is_comma_separated(self):
        result = await export_to_csv(SAMPLE_DATA)
        # The header line should be comma-separated.
        lines = result.strip().splitlines()
        csv_lines = [line for line in lines if "," in line]
        assert len(csv_lines) >= 4  # header + 3 data rows

    @pytest.mark.asyncio
    async def test_source_attribution(self):
        result = await export_to_csv(SAMPLE_DATA)
        assert "[Source: export_to_csv" in result

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error(self):
        result = await export_to_csv("{broken")
        assert "[Error in export_to_csv]" in result
        assert "Invalid JSON" in result

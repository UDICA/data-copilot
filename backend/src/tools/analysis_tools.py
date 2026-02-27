"""Data analysis tools — descriptive stats, cross-source joins, and data export."""

import json
import logging

import pandas as pd

from src.tools.registry import ToolRegistry, tool
from src.utils.formatting import format_as_markdown_table, format_error, format_tool_result

logger = logging.getLogger(__name__)

registry = ToolRegistry()


def get_analysis_registry() -> ToolRegistry:
    """Return the analysis tool registry.

    Returns:
        The module-level ToolRegistry containing all analysis tools.
    """
    return registry


@tool(
    registry,
    description="Generate descriptive statistics for a dataset. Input is a JSON array of records.",
)
async def describe_data(data_json: str) -> str:
    """Compute descriptive statistics for the provided dataset.

    Numeric columns get count, mean, std, min, quartiles, and max.
    Categorical (object) columns get value counts.

    Args:
        data_json: A JSON string containing an array of record objects.

    Returns:
        Formatted statistics text with source attribution, or an error string.
    """
    try:
        records = json.loads(data_json)
    except json.JSONDecodeError as exc:
        return format_error(f"Invalid JSON: {exc}", "describe_data")

    try:
        df = pd.DataFrame(records)

        sections: list[str] = []

        # Numeric columns — standard descriptive statistics.
        numeric_cols = df.select_dtypes(include="number")
        if not numeric_cols.empty:
            sections.append("## Numeric Columns\n")
            stats = numeric_cols.describe().round(2)
            sections.append(stats.to_string())

        # Categorical columns — value frequency counts.
        object_cols = df.select_dtypes(include="object")
        if not object_cols.empty:
            sections.append("\n## Categorical Columns\n")
            for col in object_cols.columns:
                counts = df[col].value_counts()
                sections.append(f"**{col}**")
                sections.append(counts.to_string())
                sections.append("")

        if not sections:
            return format_tool_result(
                "Dataset contains no numeric or categorical columns.",
                "describe_data",
                "in-memory dataset",
            )

        body = "\n".join(sections)
        return format_tool_result(body, "describe_data", "in-memory dataset")

    except Exception as exc:
        logger.exception("describe_data failed")
        return format_error(str(exc), "describe_data")


@tool(
    registry,
    description="Join two datasets on a shared column. Both inputs are JSON arrays of records.",
)
async def cross_join_data(left_json: str, right_json: str, join_column: str) -> str:
    """Merge two datasets using an inner join on a shared column.

    Args:
        left_json: JSON string containing the left dataset (array of records).
        right_json: JSON string containing the right dataset (array of records).
        join_column: The column name present in both datasets to join on.

    Returns:
        Merged result formatted as a markdown table with source attribution,
        or an error string.
    """
    try:
        left_records = json.loads(left_json)
        right_records = json.loads(right_json)
    except json.JSONDecodeError as exc:
        return format_error(f"Invalid JSON: {exc}", "cross_join_data")

    try:
        left_df = pd.DataFrame(left_records)
        right_df = pd.DataFrame(right_records)

        if join_column not in left_df.columns:
            return format_error(
                f"Column '{join_column}' not found in left dataset.",
                "cross_join_data",
            )
        if join_column not in right_df.columns:
            return format_error(
                f"Column '{join_column}' not found in right dataset.",
                "cross_join_data",
            )

        merged = pd.merge(left_df, right_df, on=join_column, how="inner")
        rows = merged.to_dict(orient="records")
        table = format_as_markdown_table(rows)
        return format_tool_result(table, "cross_join_data", "cross-source join")

    except Exception as exc:
        logger.exception("cross_join_data failed")
        return format_error(str(exc), "cross_join_data")


@tool(
    registry,
    description="Export data to CSV format. Input is a JSON array of records.",
)
async def export_to_csv(data_json: str) -> str:
    """Convert a dataset to CSV format.

    Args:
        data_json: A JSON string containing an array of record objects.

    Returns:
        CSV-formatted string of the data with source attribution,
        or an error string.
    """
    try:
        records = json.loads(data_json)
    except json.JSONDecodeError as exc:
        return format_error(f"Invalid JSON: {exc}", "export_to_csv")

    try:
        df = pd.DataFrame(records)
        csv_content = df.to_csv(index=False)
        return format_tool_result(csv_content, "export_to_csv", "CSV export")

    except Exception as exc:
        logger.exception("export_to_csv failed")
        return format_error(str(exc), "export_to_csv")

"""Tests for query validation and safety utilities."""

import pytest

from src.utils.safety import (
    QueryValidationError,
    is_within_allowed_paths,
    sanitize_path,
    truncate_result,
    validate_sql_query,
)


class TestValidateSqlQuery:
    def test_allows_select(self):
        assert validate_sql_query("SELECT * FROM users") is True

    def test_rejects_drop(self):
        with pytest.raises(QueryValidationError, match="write operation"):
            validate_sql_query("DROP TABLE users")

    def test_rejects_insert(self):
        with pytest.raises(QueryValidationError, match="write operation"):
            validate_sql_query("INSERT INTO users VALUES (1, 'a')")

    def test_rejects_update(self):
        with pytest.raises(QueryValidationError, match="write operation"):
            validate_sql_query("UPDATE users SET name='a'")

    def test_rejects_delete(self):
        with pytest.raises(QueryValidationError, match="write operation"):
            validate_sql_query("DELETE FROM users")

    def test_allows_explain(self):
        assert validate_sql_query("EXPLAIN SELECT * FROM users") is True

    def test_allows_with_cte(self):
        assert validate_sql_query("WITH cte AS (SELECT 1) SELECT * FROM cte") is True

    def test_allows_writes_when_enabled(self):
        assert validate_sql_query("INSERT INTO users VALUES (1)", allow_writes=True) is True


class TestSanitizePath:
    def test_resolves_traversal(self):
        result = sanitize_path("/data/../data/file.csv")
        assert ".." not in str(result)

    def test_returns_absolute(self):
        result = sanitize_path("/data/file.csv")
        assert result.is_absolute()


class TestIsWithinAllowedPaths:
    def test_allowed_path(self):
        assert is_within_allowed_paths("/data/files/report.csv", ["/data/files"]) is True

    def test_disallowed_path(self):
        assert is_within_allowed_paths("/etc/passwd", ["/data/files"]) is False

    def test_traversal_attack(self):
        assert is_within_allowed_paths("/data/files/../../etc/passwd", ["/data/files"]) is False


class TestTruncateResult:
    def test_within_limit(self):
        rows = [{"a": i} for i in range(5)]
        result, truncated = truncate_result(rows, max_rows=10)
        assert len(result) == 5
        assert truncated is False

    def test_exceeds_limit(self):
        rows = [{"a": i} for i in range(100)]
        result, truncated = truncate_result(rows, max_rows=10)
        assert len(result) == 10
        assert truncated is True

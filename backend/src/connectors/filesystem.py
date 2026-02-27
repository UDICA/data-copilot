"""Sandboxed file system access layer."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.safety import is_within_allowed_paths

logger = logging.getLogger(__name__)


class FilesystemConnector:
    """Provides sandboxed file system operations.

    All file access is restricted to directories listed in allowed_paths.
    Path traversal attempts are blocked before any I/O occurs.
    """

    def __init__(self, allowed_paths: list[str]) -> None:
        self._allowed_paths = allowed_paths

    def _check_access(self, path_str: str) -> Path:
        """Validate and resolve a path, ensuring it's within allowed directories.

        Args:
            path_str: The path to validate.

        Returns:
            Resolved Path object.

        Raises:
            PermissionError: If the path is outside allowed directories.
        """
        resolved = Path(path_str).resolve()
        if not is_within_allowed_paths(str(resolved), self._allowed_paths):
            raise PermissionError(
                f"Access denied: '{path_str}' is outside allowed directories"
            )
        return resolved

    def list_directory(self, path_str: str) -> list[dict[str, Any]]:
        """List contents of a directory.

        Args:
            path_str: Path to the directory.

        Returns:
            List of entry dicts with name, type, size_bytes, and extension.
        """
        path = self._check_access(path_str)
        entries = []
        for item in sorted(path.iterdir()):
            entry: dict[str, Any] = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size_bytes": item.stat().st_size if item.is_file() else None,
                "extension": item.suffix if item.is_file() else None,
            }
            entries.append(entry)
        return entries

    def read_file(self, path_str: str, *, max_size_mb: int = 50) -> str:
        """Read a file's text content.

        Args:
            path_str: Path to the file.
            max_size_mb: Maximum file size in megabytes.

        Returns:
            File content as string.

        Raises:
            PermissionError: If outside allowed directories.
            FileNotFoundError: If file doesn't exist.
            ValueError: If file exceeds size limit.
        """
        path = self._check_access(path_str)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path_str}")

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"File too large ({size_mb:.1f} MB, limit {max_size_mb} MB)")

        return path.read_text(encoding="utf-8")

    def get_file_info(self, path_str: str) -> dict[str, Any]:
        """Get metadata about a file.

        Args:
            path_str: Path to the file.

        Returns:
            Dict with name, size_bytes, extension, and modified timestamp.
        """
        path = self._check_access(path_str)
        stat = path.stat()
        return {
            "name": path.name,
            "size_bytes": stat.st_size,
            "extension": path.suffix,
            "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        }

    def search_files(
        self,
        directory: str,
        *,
        pattern: str = "*",
        recursive: bool = True,
    ) -> list[dict[str, Any]]:
        """Search for files matching a glob pattern.

        Args:
            directory: Directory to search in.
            pattern: Glob pattern (e.g., "*.csv", "report*").
            recursive: Whether to search subdirectories.

        Returns:
            List of matching file info dicts.
        """
        path = self._check_access(directory)
        glob_method = path.rglob if recursive else path.glob
        results = []
        for match in glob_method(pattern):
            if match.is_file():
                results.append({
                    "name": match.name,
                    "path": str(match),
                    "size_bytes": match.stat().st_size,
                    "extension": match.suffix,
                })
        return results

import argparse
from pathlib import Path
from typing import Iterator

IGNORED_DIRS: set[str] = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
IGNORED_FILE_NAMES: set[str] = {".gitignore", "uv.lock", "pyproject.toml"}
IGNORED_FILE_EXTENSIONS: set[str] = {".md", ".db", ".png"}


def parse_arguments() -> tuple[Path, str]:
    parser = argparse.ArgumentParser(
        description="Extract functions from a source code project into a SQLite database."
    )
    parser.add_argument("target_path", type=Path, help="Directory or file to analyze")
    parser.add_argument(
        "database_file", type=str, help="Path to the output SQLite database file"
    )

    args: argparse.Namespace = parser.parse_args()
    return args.target_path, args.database_file


def find_files(target_path: Path) -> Iterator[Path]:
    for dir_path, dir_names, file_names in target_path.walk():
        # In-place mutation is intentional: it tells walk() to skip
        # descending into these directories entirely
        dir_names[:] = [name for name in dir_names if name not in IGNORED_DIRS]
        for file_name in file_names:
            if file_name in IGNORED_FILE_NAMES:
                continue
            if Path(file_name).suffix in IGNORED_FILE_EXTENSIONS:
                continue
            yield dir_path / file_name

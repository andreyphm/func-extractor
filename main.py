import tree_sitter_python as tspython
import tree_sitter_c as tsc
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser, Node
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Iterator
from tqdm import tqdm
import sqlite3
import argparse


@dataclass
class LanguageInfo:
    name: str
    func_def: str
    parser: Parser
    target: str


@dataclass
class FunctionInfo:
    name: str
    code: str
    language: str
    file_path: str


LANGUAGES: list[LanguageInfo] = [
    LanguageInfo(
        name="python",
        func_def="function_definition",
        parser=Parser(Language(tspython.language())),
        target="name",
    ),
    LanguageInfo(
        name="c",
        func_def="function_definition",
        parser=Parser(Language(tsc.language())),
        target="declarator",
    ),
    LanguageInfo(
        name="java",
        func_def="method_declaration",
        parser=Parser(Language(tsjava.language())),
        target="name",
    ),
]

IGNORED_DIRS: set[str] = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}


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


def extract_func_name(node: Node, target: str) -> str:
    while node.type != "identifier":
        child: Node | None = node.child_by_field_name(target)
        if child is None:
            raise ValueError(
                f"Could not resolve function name: no '{target}' field on node of type '{node.type}'"
            )
        node = child
    return node.text.decode("utf-8")


def extract_functions(
    root_node: Node, func_def: str, target: str, language: str, file_path: str
) -> list[FunctionInfo]:
    func_list: list[FunctionInfo] = []
    stack: list[Node] = list(root_node.children)

    while stack:
        node = stack.pop()

        if node.type == func_def:
            try:
                func_name = extract_func_name(node, target)
                func_code = node.text.decode("utf-8")
                func_list.append(
                    FunctionInfo(
                        name=func_name,
                        code=func_code,
                        language=language,
                        file_path=file_path,
                    )
                )
            except ValueError as error:
                line = node.start_point[0] + 1
                tqdm.write(
                    f"Warning: failed to add function in {file_path}, line {line}: {error}"
                )

        stack.extend(node.children)

    return func_list


def find_files(target_path: Path) -> Iterator[Path]:
    for dir_path, dir_names, file_names in target_path.walk():
        dir_names[:] = [name for name in dir_names if name not in IGNORED_DIRS]
        for file_name in file_names:
            yield dir_path / file_name


def process_file(file_path: Path) -> list[FunctionInfo]:
    try:
        with open(file_path, "rb") as file:
            data: bytes = file.read()
    except OSError as error:
        tqdm.write(f"Warning: can't open file {file_path}: {error}")
        return []

    for current_language in LANGUAGES:
        try:
            tree = current_language.parser.parse(data)
        except Exception as error:
            tqdm.write(
                f"Warning: failed to parse {file_path} as {current_language.name}: {error}"
            )
            continue

        if tree.root_node.has_error:
            continue
        return extract_functions(
            tree.root_node,
            current_language.func_def,
            current_language.target,
            current_language.name,
            str(file_path),
        )
    tqdm.write(f"Warning: could not recognize the language of {file_path}")
    return []


def create_table(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS functions(
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            language TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
        """
    )


def insert_functions(con: sqlite3.Connection, func_list: list[FunctionInfo]) -> None:
    if not func_list:
        return
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO functions VALUES(:name, :code, :language, :file_path)",
        [asdict(func) for func in func_list],
    )


def main() -> None:
    target_path, database_file = parse_arguments()
    con = sqlite3.connect(database_file)
    create_table(con)

    if target_path.is_dir():
        files = list(find_files(target_path))
        for file_path in tqdm(files, total=len(files), desc="Processing files"):
            insert_functions(con, process_file(file_path))
    elif target_path.is_file():
        insert_functions(con, process_file(target_path))

    con.commit()
    con.close()
    tqdm.write("Program completed.")


if __name__ == "__main__":
    main()

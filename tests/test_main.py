import pytest
import sqlite3

from database import create_table, insert_functions
from input_processing import find_files
from extraction import FunctionInfo, extract_func_name, process_file


class DummyNode:
    def __init__(self, node_type: str, field=None):
        self.type = node_type
        self.field = field

    def child_by_field_name(self, name):
        return self.field


def test_direct_identifier():
    node = DummyNode("identifier")
    node.text = b"return_42"
    assert extract_func_name(node, "name") == "return_42"


def test_missing_field_raises_value_error():
    node = DummyNode("function_definition", field=None)
    with pytest.raises(ValueError):
        extract_func_name(node, "declarator")


def test_walks_through_nested_fields():
    identifier = DummyNode("identifier")
    identifier.text = b"return_42"

    declarator = DummyNode("function_declarator", field=identifier)
    func_def = DummyNode("function_definition", field=declarator)

    assert extract_func_name(func_def, "declarator") == "return_42"


def test_find_files_skips_ignored_dirs(tmp_path):
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "main.py").write_text("42")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("42")

    found_names = {path.name for path in find_files(tmp_path)}

    assert found_names == {"main.py"}


def test_process_file_missing_path_returns_empty(tmp_path):
    missing_path = tmp_path / "does_not_exist.py"

    functions = process_file(missing_path)

    assert functions == []


def test_process_file_unrecognized_language_returns_empty(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("At 20:31, Satoru Gojo arrived.")

    functions = process_file(file_path)

    assert functions == []


def test_create_table_and_insert_functions():
    con = sqlite3.connect(":memory:")
    create_table(con)

    functions = [
        FunctionInfo(
            name="correct",
            code="def correct(): pass",
            language="python",
            file_path="correct.py",
        ),
    ]
    insert_functions(con, functions)
    con.commit()

    rows = con.execute(
        "SELECT name, code, language, file_path FROM functions"
    ).fetchall()

    assert rows == [("correct", "def correct(): pass", "python", "correct.py")]


def test_insert_functions_empty_list_does_nothing():
    con = sqlite3.connect(":memory:")
    create_table(con)

    insert_functions(con, [])
    con.commit()

    count = con.execute("SELECT COUNT(*) FROM functions").fetchone()[0]

    assert count == 0

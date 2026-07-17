import tree_sitter_python as tspython
import tree_sitter_c as tsc
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from pathlib import Path
import sqlite3
import sys

language_info = []
language_info.append({"lang_name": "python", "func_def": "function_definition", "tree_sitter": tspython, "target": "name"})
language_info.append({"lang_name": "c",      "func_def": "function_definition", "tree_sitter": tsc,      "target": "declarator"})
language_info.append({"lang_name": "java",   "func_def": "method_declaration",  "tree_sitter": tsjava,   "target": "name"})


def parse_arguments():
    if len(sys.argv) != 3:
        print(f"Program exit with fail. Usage: uv run python {Path(sys.argv[0]).name} <target_path> <database_file>")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    database_file = sys.argv[2]
    return target_path, database_file


def seek_func_name(node, target):
    if node.type == "identifier":
        return node.text.decode("utf-8")
    return seek_func_name(node.child_by_field_name(target), target)


def seek_func(root_node, func_def, target, language, file_path):
    func_list = []
    for child in root_node.children:
        if child.type == func_def:
            func_name = seek_func_name(child, target)
            func_code = child.text.decode("utf-8")
            func_list.append({"name": func_name, "code": func_code, "language": language, "file_path": file_path})
        func_list += seek_func(child, func_def, target, language, file_path)
    return func_list


def process_file(file_path):
    with open(file_path, "rb") as file:
        data = file.read()

    for current_language in language_info:
        language = Language(current_language["tree_sitter"].language())
        parser = Parser(language)
        tree = parser.parse(data)
        if tree.root_node.has_error:
            continue
        return seek_func(tree.root_node, current_language["func_def"],
                         current_language["target"], current_language["lang_name"], str(file_path))
    return []


def list_to_db(func_list, database_file):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS functions(name, code, language, file_path)")
    cur.executemany("INSERT INTO functions VALUES(:name, :code, :language, :file_path)", func_list)
    con.commit()
    con.close()


def main():
    target_path, database_file = parse_arguments()
    func_list = []

    if target_path.is_dir():
        for file_path in target_path.rglob("*"):
            if not file_path.is_file():
                continue
            func_list += process_file(file_path)
    elif target_path.is_file():
        func_list += process_file(target_path)

    list_to_db(func_list, database_file)


if __name__ == "__main__":
    main()

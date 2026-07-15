import tree_sitter_python as tspython
import tree_sitter_c as tsc
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from pathlib import Path
import sqlite3

language_info = []
language_info.append({"lang_name": "python", "func_def": "function_definition", "tree_sitter": tspython, "target": "name"})
language_info.append({"lang_name": "c",      "func_def": "function_definition", "tree_sitter": tsc,      "target": "declarator"})
language_info.append({"lang_name": "java",   "func_def": "method_declaration",  "tree_sitter": tsjava,   "target": "name"})

def seek_func(root_node, func_list, func_def, target, language, file_path):
    for i in range(root_node.child_count):
        if (root_node.children[i].type == func_def):
            func_name = seek_func_name(root_node.children[i], target)
            func_code = root_node.children[i].text.decode("utf-8")
            func_list.append({"name": func_name, "code": func_code, "language": language, "file_path": file_path})
        seek_func(root_node.children[i], func_list, func_def, target, language, file_path)

def seek_func_name(node, target):
    if node.type == "identifier":
        return node.text.decode("utf-8")
    return seek_func_name(node.child_by_field_name(target), target)

def process_file(file_path):
    with open(file_path, "rb") as file:
        data = file.read()
    for current_language in language_info:
        language = Language(current_language["tree_sitter"].language())
        parser = Parser(language)
        tree = parser.parse(data)
        if tree.root_node.has_error:
            continue
        seek_func(tree.root_node, func_list, current_language["func_def"],
                  current_language["target"], current_language["lang_name"], str(file_path))
        break

def list_to_db(func_list):
    con = sqlite3.connect("functions.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS functions(name, code, language, file_path)")
    cur.executemany("INSERT INTO functions VALUES(:name, :code, :language, :file_path)", func_list)
    con.commit()
    con.close()

func_list = []
folder_path = Path(input())

if folder_path.is_dir():
    for file_path in Path(folder_path).rglob("*"):
        if not file_path.is_file():
            continue
        process_file(file_path)

if folder_path.is_file():
    process_file(folder_path)

list_to_db(func_list)

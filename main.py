import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def seek_func(root_node, func_list):
    for i in range(root_node.child_count):

        if (root_node.children[i].type == "function_definition"):
            func_name = root_node.children[i].child_by_field_name("name").text.decode("utf-8")
            func_code = root_node.children[i].text.decode("utf-8")

            func_list.append({
                "name": func_name,
                "code": func_code
            })

        seek_func(root_node.children[i], func_list)

py_language = Language(tspython.language())
parser = Parser(py_language)

with open("test_programs/test.py", "rb") as file:
    data = file.read()

tree = parser.parse(data)

func_list = []
seek_func(tree.root_node, func_list)

print(func_list)

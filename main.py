import tree_sitter_python as tspython
from tree_sitter import Language, Parser

py_language = Language(tspython.language())
parser = Parser(py_language)

tree = parser.parse(
       bytes(
       """
        def add(a,b):
            return a + b
       """,
       "utf8"
       ))

func_name = tree.root_node.children[0].children[1].text
print(func_name)

func_body = tree.root_node.children[0].text
print(func_body)

print(tree.root_node.type)
print(tree.root_node.children[0].type)
print(tree.root_node.children[0].children[0].type)
print(tree.root_node.children[0].children[1].type)
print(tree.root_node.children[0].children[2].type)
print(tree.root_node.children[0].children[3].type)
print(tree.root_node.children[0].children[4].type)
print(tree.root_node.children[0].children[4].children[0].type)

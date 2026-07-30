from dataclasses import dataclass
from pathlib import Path

from tqdm import tqdm
from tree_sitter import Node

from languages import arrange_languages


@dataclass
class FunctionInfo:
    name: str
    code: str
    language: str
    file_path: str


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


def process_file(file_path: Path) -> list[FunctionInfo]:
    try:
        with open(file_path, "rb") as file:
            data: bytes = file.read()
    except OSError as error:
        tqdm.write(f"Warning: can't open file {file_path}: {error}")
        return []

    for current_language in arrange_languages(file_path):
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

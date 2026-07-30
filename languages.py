from dataclasses import dataclass
from pathlib import Path

import tree_sitter_python as tspython
import tree_sitter_c as tsc
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser


@dataclass
class LanguageInfo:
    name: str
    func_def: str
    parser: Parser
    target: str


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

EXTENSION_HINTS: dict[str, str] = {
    ".py": "python",
    ".c": "c",
    ".java": "java",
}


def arrange_languages(file_path: Path) -> list[LanguageInfo]:
    hint: str | None = EXTENSION_HINTS.get(file_path.suffix)
    if hint is None:
        return LANGUAGES

    guessed: list[LanguageInfo] = [lang for lang in LANGUAGES if lang.name == hint]
    rest: list[LanguageInfo] = [lang for lang in LANGUAGES if lang.name != hint]
    return guessed + rest

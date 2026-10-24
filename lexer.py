
import re

TOKEN_SPECIFICATION = [
    ("NUMBER", r"\d+(?:\.\d+)?"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OPERATOR", r"==|!=|<=|>=|//|[()+*/%<>=-]"),
    ("COLON", r":"),
    ("COMMENT", r"\#.*"),
    ("WHITESPACE", r"[ \t]+"),
    ("MISMATCH", r"."),
]

KEYWORDS = {"if", "else", "while", "True", "False"}


def tokenize(source):
    tokens = []
    indentation_stack = [0]

    for line_number, line in enumerate(source.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent_text = line[:len(line) - len(line.lstrip(" \t"))]

        if "\t" in indent_text:
            raise ValueError(
                f"Line {line_number}: use spaces instead of tabs"
            )

        indent = len(indent_text)
        content = line[indent:]

        if indent > indentation_stack[-1]:
            indentation_stack.append(indent)
            tokens.append(("INDENT", indent))

        elif indent < indentation_stack[-1]:
            while indent < indentation_stack[-1]:
                indentation_stack.pop()
                tokens.append(("DEDENT", indent))

            if indent != indentation_stack[-1]:
                raise ValueError(
                    f"Line {line_number}: invalid indentation"
                )

        for match in re.finditer(
            r"\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|"
            r"==|!=|<=|>=|//|[()+*/%<>=:-]|\#.*|[ \t]+|.",
            content
        ):
            value = match.group()

            if value.startswith("#"):
                break

            if re.fullmatch(r"\d+(?:\.\d+)?", value):
                tokens.append(("NUMBER", value))

            elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                if value in KEYWORDS:
                    tokens.append(("KEYWORD", value))
                else:
                    tokens.append(("IDENTIFIER", value))

            elif value in {
                "+", "-", "*", "/", "//", "%", "=",
                "==", "!=", "<", ">", "<=", ">="
            }:
                tokens.append(("OPERATOR", value))

            elif value == ":":
                tokens.append(("COLON", value))

            elif value in ("(", ")"):
                tokens.append(("OPERATOR", value))

            elif value.isspace():
                continue

            else:
                raise ValueError(
                    f"Line {line_number}: unexpected character: {value}"
                )

        tokens.append(("NEWLINE", "\n"))

    while len(indentation_stack) > 1:
        indentation_stack.pop()
        tokens.append(("DEDENT", 0))

    tokens.append(("EOF", None))
    return tokens

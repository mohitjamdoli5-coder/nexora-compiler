
import re

TOKEN_SPECIFICATION = [
    ("NUMBER", r"\d+(\.\d+)?"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OPERATOR", r"==|!=|<=|>=|//|[+\-*/%<>=]"),
    ("COLON", r":"),
    ("MISMATCH", r"."),
]

KEYWORDS = {"if", "else", "while", "True", "False"}

def tokenize(source):
    tokens = []
    indentation_stack = [0]

    for line in source.splitlines():
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        content = line.lstrip(" ")

        if "\t" in line[:indent]:
            raise ValueError("Use spaces instead of tabs")

        if indent > indentation_stack[-1]:
            indentation_stack.append(indent)
            tokens.append(("INDENT", indent))
        elif indent < indentation_stack[-1]:
            while indent < indentation_stack[-1]:
                indentation_stack.pop()
                tokens.append(("DEDENT", indent))

            if indent != indentation_stack[-1]:
                raise ValueError("Invalid indentation")

        for match in re.finditer(
            r"\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|==|!=|<=|>=|//|[+\-*/%<>=:]|.",
            content
        ):
            value = match.group()

            if re.fullmatch(r"\d+(?:\.\d+)?", value):
                tokens.append(("NUMBER", value))
            elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                if value in KEYWORDS:
                    tokens.append(("KEYWORD", value))
                else:
                    tokens.append(("IDENTIFIER", value))
            elif value in {"+", "-", "*", "/", "//", "%", "=", "==", "!=", "<", ">", "<=", ">="}:
                tokens.append(("OPERATOR", value))
            elif value == ":":
                tokens.append(("COLON", value))
            elif value.isspace():
                continue
            else:
                raise ValueError(f"Unexpected character: {value}")

        tokens.append(("NEWLINE", "\\n"))

    while len(indentation_stack) > 1:
        indentation_stack.pop()
        tokens.append(("DEDENT", 0))

    tokens.append(("EOF", None))
    return tokens

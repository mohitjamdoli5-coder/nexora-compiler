
from lexer import tokenize


class Parser:
    def __init__(self, source):
        self.tokens = tokenize(source)
        self.position = 0

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return ("EOF", None)

    def advance(self):
        token = self.current()
        if self.position < len(self.tokens):
            self.position += 1
        return token

    def expect(self, kind, value=None):
        token = self.current()

        if token[0] != kind or (
            value is not None and token[1] != value
        ):
            raise SyntaxError(
                f"Expected {kind} {value}, got {token}"
            )

        return self.advance()

    def skip_newlines(self):
        while self.current()[0] == "NEWLINE":
            self.advance()

    def parse(self):
        statements = []

        while self.current()[0] != "EOF":
            if self.current()[0] in ("NEWLINE", "DEDENT"):
                self.advance()
                continue

            statements.append(self.statement())

        return statements

    def statement(self):
        token = self.current()

        if token == ("KEYWORD", "if"):
            return self.if_statement()

        if token == ("KEYWORD", "while"):
            return self.while_statement()

        return self.assignment()

    def parse_block(self):
        """Parse an indented block after a control statement."""
        self.expect("INDENT")
        statements = []

        while self.current()[0] not in ("DEDENT", "EOF"):
            if self.current()[0] == "NEWLINE":
                self.advance()
                continue

            statements.append(self.statement())

        self.expect("DEDENT")
        return statements

    def if_statement(self):
        self.expect("KEYWORD", "if")
        condition = self.expression()
        self.expect("COLON")
        self.expect("NEWLINE")

        then_body = self.parse_block()

        # Ignore blank lines between the if body and else.
        self.skip_newlines()

        else_body = []

        if self.current() == ("KEYWORD", "else"):
            self.advance()
            self.expect("COLON")
            self.expect("NEWLINE")
            else_body = self.parse_block()

        return ("if", condition, then_body, else_body)

    def while_statement(self):
        self.expect("KEYWORD", "while")
        condition = self.expression()
        self.expect("COLON")
        self.expect("NEWLINE")

        body = self.parse_block()

        return ("while", condition, body)

    def expression(self):
        return self.comparison()

    def comparison(self):
        left = self.addition()

        if (
            self.current()[0] == "OPERATOR"
            and self.current()[1] in (
                ">", "<", ">=", "<=", "==", "!="
            )
        ):
            operator = self.advance()[1]
            right = self.addition()
            left = ("binary", operator, left, right)

        return left

    def addition(self):
        left = self.term()

        while (
            self.current()[0] == "OPERATOR"
            and self.current()[1] in ("+", "-")
        ):
            operator = self.advance()[1]
            right = self.term()
            left = ("binary", operator, left, right)

        return left

    def term(self):
        left = self.factor()

        while (
            self.current()[0] == "OPERATOR"
            and self.current()[1] in ("*", "/", "//", "%")
        ):
            operator = self.advance()[1]
            right = self.factor()
            left = ("binary", operator, left, right)

        return left

    def factor(self):
        token = self.current()

        if token[0] == "NUMBER":
            self.advance()
            return ("number", token[1])

        if token == ("KEYWORD", "True"):
            self.advance()
            return ("boolean", True)

        if token == ("KEYWORD", "False"):
            self.advance()
            return ("boolean", False)

        if token[0] == "IDENTIFIER":
            self.advance()
            return ("variable", token[1])

        if token == ("OPERATOR", "("):
            self.advance()
            expression = self.expression()
            self.expect("OPERATOR", ")")
            return expression

        raise SyntaxError(f"Unexpected token: {token}")

    def assignment(self):
        name = self.expect("IDENTIFIER")[1]
        self.expect("OPERATOR", "=")
        expression = self.expression()
        self.expect("NEWLINE")

        return ("assign", name, expression)

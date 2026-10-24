
class Num:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"


class Var:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var({self.name})"


class BinOp:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left}, {self.operator}, {self.right})"


class Assign:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assign({self.name}, {self.value})"


class Block:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"

class If:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}, {self.body})"

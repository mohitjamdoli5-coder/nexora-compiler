
import ast
from ast_nodes import Num, Var, BinOp, Assign, Block, If, While


class ASTBuilder(ast.NodeVisitor):
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float, bool)):
            return Num(node.value)
        raise ValueError("Unsupported constant")

    def visit_Name(self, node):
        return Var(node.id)

    def visit_BinOp(self, node):
        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "//",
            ast.Mod: "%",
        }

        operator = operators.get(type(node.op))
        if operator is None:
            raise ValueError("Unsupported operator")

        return BinOp(
            self.visit(node.left),
            operator,
            self.visit(node.right)
        )

    def visit_Assign(self, node):
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise ValueError("Only simple assignments are supported")

        return Assign(
            node.targets[0].id,
            self.visit(node.value)
        )
    
    def visit_If(self, node):
        condition = self.visit(node.test)
        then_branch = self.visit(node.body[0]) if len(node.body) == 1 else Block(
            [self.visit(stmt) for stmt in node.body]
        )
        else_branch = None

        if node.orelse:
            else_branch = (
                self.visit(node.orelse[0])
                if len(node.orelse) == 1
                else Block([self.visit(stmt) for stmt in node.orelse])
            )

        return If(condition, then_branch, else_branch)

    def visit_Compare(self, node):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise ValueError("Only single comparisons are supported")

        operators = {
            ast.Lt: "<",
            ast.Gt: ">",
            ast.LtE: "<=",
            ast.GtE: ">=",
            ast.Eq: "==",
            ast.NotEq: "!=",
        }

        operator = operators.get(type(node.ops[0]))
        if operator is None:
            raise ValueError("Unsupported comparison")

        return BinOp(
            self.visit(node.left),
            operator,
            self.visit(node.comparators[0])
        )

    def visit_While(self, node):
        condition = self.visit(node.test)
        body = Block([self.visit(stmt) for stmt in node.body])
        return While(condition, body)

    

    def visit_Module(self, node):
        return Block([self.visit(stmt) for stmt in node.body])

    def generic_visit(self, node):
        raise ValueError(f"Unsupported syntax: {type(node).__name__}")


def parse_source(source):
    python_tree = ast.parse(source)
    return ASTBuilder().visit(python_tree)

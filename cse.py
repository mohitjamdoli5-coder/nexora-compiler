
from ast_nodes import Num, Var, BinOp, Assign, Block, If, While


def common_subexpression_elimination(tree):
    def optimize_expression(node, expressions):
        if isinstance(node, (Num, Var)):
            return node

        if isinstance(node, BinOp):
            left = optimize_expression(node.left, expressions)
            right = optimize_expression(node.right, expressions)

            if node.operator in ("+", "*", "==", "!="):
                if repr(left) > repr(right):
                    left, right = right, left

            key = repr(BinOp(left, node.operator, right))

            if key in expressions:
                return Var(expressions[key])

            return BinOp(left, node.operator, right)

        return node

    def optimize_statement(stmt, expressions):
        if isinstance(stmt, Block):
            return Block([
                optimize_statement(item, expressions)
                for item in stmt.statements
            ])

        if isinstance(stmt, Assign):
            value = optimize_expression(stmt.value, expressions)

            # Remove cached expressions that depend on a changed variable.
            for key in list(expressions):
                if stmt.name in key:
                    del expressions[key]

            if isinstance(value, BinOp):
                key = repr(value)
                if key in expressions:
                    value = Var(expressions[key])
                else:
                    expressions[key] = stmt.name

            return Assign(stmt.name, value)

        if isinstance(stmt, If):
            condition = optimize_expression(stmt.condition, expressions)

            then_expressions = expressions.copy()
            then_branch = optimize_statement(stmt.then_branch, then_expressions)

            else_expressions = expressions.copy()
            else_branch = (
                optimize_statement(stmt.else_branch, else_expressions)
                if stmt.else_branch is not None else None
            )

            # Avoid assuming expressions created in either branch are valid afterward.
            expressions.clear()

            return If(condition, then_branch, else_branch)

        if isinstance(stmt, While):
            condition = optimize_expression(stmt.condition, expressions)
            loop_expressions = expressions.copy()
            body = optimize_statement(stmt.body, loop_expressions)

            # Loop assignments can invalidate cached expressions.
            expressions.clear()

            return While(condition, body)

        return stmt

    return optimize_statement(tree, {})

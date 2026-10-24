
from ast_nodes import Num, Var, BinOp, Assign, Block, If, While


def fold_expression(node):
    if isinstance(node, (Num, Var)):
        return node

    if isinstance(node, BinOp):
        left = fold_expression(node.left)
        right = fold_expression(node.right)

        comparisons = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }

        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "//": lambda a, b: a // b,
            "%": lambda a, b: a % b,
        }

        if isinstance(left, Num) and isinstance(right, Num):
            try:
                if node.operator in comparisons:
                    return Num(comparisons[node.operator](left.value, right.value))

                if node.operator in operations:
                    result = operations[node.operator](left.value, right.value)
                    if isinstance(result, (int, float, bool)):
                        return Num(result)
            except (ZeroDivisionError, TypeError, ValueError, OverflowError):
                pass

        return BinOp(left, node.operator, right)

    return node


def constant_folding(node):
    if isinstance(node, Assign):
        return Assign(node.name, fold_expression(node.value))

    if isinstance(node, Block):
        return Block([constant_folding(s) for s in node.statements])

    if isinstance(node, If):
        return If(
            fold_expression(node.condition),
            constant_folding(node.then_branch),
            constant_folding(node.else_branch)
            if node.else_branch is not None else None
        )

    if isinstance(node, While):
        return While(
            fold_expression(node.condition),
            constant_folding(node.body)
        )

    return node


def constant_propagation(node):
    values = {}

    def propagate_expression(expr, env):
        if isinstance(expr, Num):
            return expr

        if isinstance(expr, Var):
            if expr.name in env:
                return Num(env[expr.name])
            return expr

        if isinstance(expr, BinOp):
            left = propagate_expression(expr.left, env)
            right = propagate_expression(expr.right, env)
            return fold_expression(BinOp(left, expr.operator, right))

        return expr

    def process(stmt, env):
        if isinstance(stmt, Block):
            return Block([process(s, env) for s in stmt.statements])

        if isinstance(stmt, Assign):
            expr = propagate_expression(stmt.value, env)
            if isinstance(expr, Num):
                env[stmt.name] = expr.value
            else:
                env.pop(stmt.name, None)
            return Assign(stmt.name, expr)

        if isinstance(stmt, If):
            condition = propagate_expression(stmt.condition, env)
            before = env.copy()

            then_env = before.copy()
            then_branch = process(stmt.then_branch, then_env)

            else_env = before.copy()
            else_branch = (
                process(stmt.else_branch, else_env)
                if stmt.else_branch is not None else None
            )

            env.clear()
            for name in then_env.keys() & else_env.keys():
                if then_env[name] == else_env[name]:
                    env[name] = then_env[name]

            return If(condition, then_branch, else_branch)

        if isinstance(stmt, While):
            condition = propagate_expression(stmt.condition, env)
            loop_env = env.copy()
            body = process(stmt.body, loop_env)

            assigned = set()

            def find_assignments(n):
                if isinstance(n, Assign):
                    assigned.add(n.name)
                elif isinstance(n, Block):
                    for s in n.statements:
                        find_assignments(s)
                elif isinstance(n, If):
                    find_assignments(n.then_branch)
                    if n.else_branch is not None:
                        find_assignments(n.else_branch)
                elif isinstance(n, While):
                    find_assignments(n.body)

            find_assignments(stmt.body)

            for name in assigned:
                env.pop(name, None)

            return While(condition, body)

        return stmt

    return process(node, values)


def _used_variables(node):
    if isinstance(node, Var):
        return {node.name}

    if isinstance(node, Num):
        return set()

    if isinstance(node, BinOp):
        return _used_variables(node.left) | _used_variables(node.right)

    if isinstance(node, Assign):
        return _used_variables(node.value)

    if isinstance(node, Block):
        used = set()
        for stmt in node.statements:
            used.update(_used_variables(stmt))
        return used

    if isinstance(node, If):
        used = _used_variables(node.condition)
        used.update(_used_variables(node.then_branch))
        if node.else_branch is not None:
            used.update(_used_variables(node.else_branch))
        return used

    if isinstance(node, While):
        return _used_variables(node.condition) | _used_variables(node.body)

    return set()


def dead_code_elimination(node):
    if isinstance(node, Block):
        statements = []

        for stmt in node.statements:
            optimized = dead_code_elimination(stmt)
            if optimized is None:
                continue
            if isinstance(optimized, Block):
                statements.extend(optimized.statements)
            else:
                statements.append(optimized)

        last_assignment = {}
        for index, stmt in enumerate(statements):
            if isinstance(stmt, Assign):
                last_assignment[stmt.name] = index

        result = []
        for index, stmt in enumerate(statements):
            if isinstance(stmt, Assign) and last_assignment[stmt.name] != index:
                continue
            result.append(stmt)

        return Block(result)

    if isinstance(node, If):
        condition = fold_expression(node.condition)

        if isinstance(condition, Num) and isinstance(condition.value, bool):
            if condition.value:
                return dead_code_elimination(node.then_branch)
            if node.else_branch is not None:
                return dead_code_elimination(node.else_branch)
            return None

        then_branch = dead_code_elimination(node.then_branch)
        else_branch = (
            dead_code_elimination(node.else_branch)
            if node.else_branch is not None else None
        )

        return If(condition, then_branch, else_branch)

    if isinstance(node, While):
        condition = fold_expression(node.condition)

        if isinstance(condition, Num) and condition.value is False:
            return None

        return While(condition, dead_code_elimination(node.body))

    if isinstance(node, Assign):
        return Assign(node.name, fold_expression(node.value))

    return node

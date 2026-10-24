
from ast_nodes import Num, Var, BinOp, Assign, Block, If, While

def loop_invariant_code_motion(tree):
    if not isinstance(tree, Block):
        return tree

    optimized_statements = []

    for statement in tree.statements:

        if isinstance(statement, While):
            if isinstance(statement.condition, Num) and isinstance(statement.condition.value, bool):
                optimized_statements.append(statement)
                continue
            
        if not isinstance(statement, While):
            optimized_statements.append(statement)
            continue

        if not isinstance(statement.body, Block):
            optimized_statements.append(statement)
            continue

        loop_variables = set()

        for item in statement.body.statements:
            if isinstance(item, Assign):
                loop_variables.add(item.name)

        invariant_statements = []
        remaining_statements = []

        for item in statement.body.statements:
            if not isinstance(item, Assign) or not isinstance(item.value, BinOp):
                remaining_statements.append(item)
                continue

            expression = item.value
            variables = set()

            if isinstance(expression.left, Var):
                variables.add(expression.left.name)

            if isinstance(expression.right, Var):
                variables.add(expression.right.name)

            if variables.isdisjoint(loop_variables):
                invariant_statements.append(item)
            else:
                remaining_statements.append(item)

        optimized_statements.extend(invariant_statements)

        optimized_statements.append(
            While(statement.condition, Block(remaining_statements))
        )

    return Block(optimized_statements)

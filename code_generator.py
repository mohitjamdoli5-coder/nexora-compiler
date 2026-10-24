
from ast_nodes import Num, Var, BinOp, Assign, Block, If, While

def generate_expression(node):
    if isinstance(node, Num):
        if isinstance(node.value, bool):
            return str(node.value)
        return str(node.value)

    if isinstance(node, Var):
        return node.name

    if isinstance(node, BinOp):
        return (
            f"({generate_expression(node.left)} "
            f"{node.operator} "
            f"{generate_expression(node.right)})"
        )

    raise ValueError(f"Unsupported expression: {type(node).__name__}")


def generate_code(node, indent=0):
    prefix = "    " * indent

    if isinstance(node, Block):
        lines = []
        for stmt in node.statements:
            result = generate_code(stmt, indent)
            if result:
                lines.append(result)
        return "\n".join(lines)

    if isinstance(node, Assign):
        return f"{prefix}{node.name} = {generate_expression(node.value)}"

    if isinstance(node, If):
        condition = generate_expression(node.condition)
        then_code = generate_code(node.then_branch, indent + 1)

        if not then_code:
            then_code = "    " * (indent + 1) + "pass"

        result = f"{prefix}if {condition}:\n{then_code}"

        if node.else_branch is not None:
            else_code = generate_code(node.else_branch, indent + 1)
            if not else_code:
                else_code = "    " * (indent + 1) + "pass"
            result += f"\n{prefix}else:\n{else_code}"

        return result

    if isinstance(node, While):
        condition = generate_expression(node.condition)
        body_code = generate_code(node.body, indent + 1)

        if not body_code:
            body_code = "    " * (indent + 1) + "pass"

        return f"{prefix}while {condition}:\n{body_code}"

    raise ValueError(f"Unsupported statement: {type(node).__name__}")


from ast_nodes import Num, Var, BinOp, Assign, Block, If, While


def convert_node(node):
    kind = node[0]

    if kind == "number":
        value = node[1]
        if "." in value:
            value = float(value)
        else:
            value = int(value)
        return Num(value)
    
    if kind == "boolean":
        return Num(node[1])


    if kind == "variable":
        return Var(node[1])

    if kind == "binary":
        return BinOp(
            convert_node(node[2]),
            node[1],
            convert_node(node[3])
        )

    if kind == "assign":
        return Assign(node[1], convert_node(node[2]))

    if kind == "if":
        condition = convert_node(node[1])
        then_branch = Block([convert_node(s) for s in node[2]])

        else_branch = None
        if len(node) > 3 and node[3]:
            else_branch = Block([convert_node(s) for s in node[3]])

        return If(condition, then_branch, else_branch)

    if kind == "while":
        condition = convert_node(node[1])
        body = Block([convert_node(s) for s in node[2]])
        return While(condition, body)

    raise ValueError(f"Unsupported AST node: {node}")


def convert_program(parsed_tree):
    return Block([convert_node(node) for node in parsed_tree])

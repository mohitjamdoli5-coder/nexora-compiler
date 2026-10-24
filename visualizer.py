
import os
import shutil
import subprocess

from ast_nodes import Num, Var, BinOp, Assign, Block, If, While

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_graphviz_dot():
    """
    Find Graphviz executable on Windows or Linux.
    Works locally and on Render when Graphviz is installed.
    """
    dot_path = shutil.which("dot")

    if dot_path:
        return dot_path

    # Fallback for Windows installations.
    windows_paths = [
        r"C:\Program Files\Graphviz\bin\dot.exe",
        r"C:\Program Files (x86)\Graphviz\bin\dot.exe",
    ]

    for path in windows_paths:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(
        "Graphviz 'dot' executable not found. "
        "Install Graphviz and ensure its bin directory is in PATH."
    )


def visualize_ast(tree, filename="ast_tree.dot", image_filename=None):
    if image_filename is None:
        image_filename = os.path.join(BASE_DIR, "ast_tree.png")

    if not os.path.isabs(filename):
        filename = os.path.join(BASE_DIR, filename)

    if not os.path.isabs(image_filename):
        image_filename = os.path.join(BASE_DIR, image_filename)

    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    os.makedirs(
        os.path.dirname(os.path.abspath(image_filename)),
        exist_ok=True
    )

    lines = [
        "digraph AST {",
        '    graph [bgcolor="white"];',
        '    node [shape=box, style="rounded,filled", fillcolor="#E0EAFF", color="#64748B", fontname="Arial"];',
        '    edge [color="#64748B"];'
    ]

    counter = [0]

    def add_node(label):
        node_id = f"node{counter[0]}"
        counter[0] += 1

        safe_label = (
            str(label)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )

        lines.append(f'    {node_id} [label="{safe_label}"];')
        return node_id

    def add_edge(parent, child):
        lines.append(f"    {parent} -> {child};")

    def visit(node, parent=None):
        if isinstance(node, Num):
            current = add_node(f"Num: {node.value}")
        elif isinstance(node, Var):
            current = add_node(f"Var: {node.name}")
        elif isinstance(node, BinOp):
            current = add_node(f"Operator: {node.operator}")
        elif isinstance(node, Assign):
            current = add_node(f"Assign: {node.name}")
        elif isinstance(node, Block):
            current = add_node("Block")
        elif isinstance(node, If):
            current = add_node("If")
        elif isinstance(node, While):
            current = add_node("While")
        else:
            current = add_node(type(node).__name__)

        if parent is not None:
            add_edge(parent, current)

        if isinstance(node, BinOp):
            visit(node.left, current)
            visit(node.right, current)

        elif isinstance(node, Assign):
            visit(node.value, current)

        elif isinstance(node, Block):
            for statement in node.statements:
                visit(statement, current)

        elif isinstance(node, If):
            visit(node.condition, current)
            visit(node.then_branch, current)

            if node.else_branch is not None:
                visit(node.else_branch, current)

        elif isinstance(node, While):
            visit(node.condition, current)
            visit(node.body, current)

    visit(tree)
    lines.append("}")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    dot_executable = find_graphviz_dot()

    subprocess.run(
        [
            dot_executable,
            "-Tpng",
            filename,
            "-o",
            image_filename
        ],
        check=True,
        capture_output=True,
        text=True
    )

    print(f"AST DOT file created: {filename}")
    print(f"AST image created: {image_filename}")

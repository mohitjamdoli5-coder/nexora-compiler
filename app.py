
from flask import Flask, render_template, request, jsonify, send_file
from parser import Parser
from ast_adapter import convert_program
from pass_manager import PassManager
from code_generator import generate_code
from visualizer import visualize_ast
from ast_nodes import Block, Assign, Num, If, While
from symbol_table import SymbolTable
from copy import deepcopy
import os
import re
import traceback

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def normalize_source(source):
    """Normalize Python-style input and simple C-style control blocks."""
    lines = [
        line.rstrip()
        for line in source.splitlines()
        if line.strip() and line.strip() != "END"
    ]

    # Keep Python-style indentation unchanged.
    if not any("{" in line or "}" in line for line in lines):
        return "\n".join(lines)

    result = []
    indent = 0

    for raw in lines:
        line = raw.strip()
        line = re.sub(r";\s*$", "", line)

        # Handle a closing brace followed by else.
        if re.match(r"^\}\s*else\b", line):
            indent = max(0, indent - 1)
            result.append("    " * indent + "else:")
            indent += 1
            continue

        # Handle a standalone closing brace.
        if line == "}":
            indent = max(0, indent - 1)
            continue

        # Handle else blocks.
        if re.match(r"^else\s*\{?\s*$", line):
            result.append("    " * indent + "else:")
            indent += 1
            continue

        # Handle if/while blocks written with braces.
        match = re.match(
            r"^(if|while)\s*\((.*)\)\s*\{?\s*$",
            line
        )

        if match:
            keyword, condition = match.groups()
            result.append(
                "    " * indent
                + f"{keyword} {condition.strip()}:"
            )
            indent += 1
            continue

        # Ignore standalone opening braces.
        if line == "{":
            continue

        result.append("    " * indent + line)

    return "\n".join(result)


def build_symbol_table(tree):
    table = SymbolTable()
    rows = []

    def collect(node):
        if isinstance(node, Block):
            for statement in node.statements:
                collect(statement)

        elif isinstance(node, Assign):
            value = None
            data_type = "Expression"

            if isinstance(node.value, Num):
                value = node.value.value
                data_type = type(value).__name__

            table.define(node.name, value, data_type)

            rows.append({
                "name": node.name,
                "value": (
                    str(value)
                    if value is not None
                    else "Expression"
                ),
                "type": data_type
            })

        elif isinstance(node, If):
            collect(node.then_branch)
            if node.else_branch is not None:
                collect(node.else_branch)

        elif isinstance(node, While):
            collect(node.body)

    collect(tree)
    return rows


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/optimize", methods=["POST"])
def optimize():
    try:
        data = request.get_json(silent=True) or {}
        source_code = data.get("code", "")

        if not source_code.strip():
            return jsonify({
                "error": "Please enter some source code."
            }), 400

        normalized_code = normalize_source(source_code)

        app.logger.info(
            "Normalized source:\n%s",
            normalized_code
        )

        parsed_tree = Parser(normalized_code).parse()
        tree = convert_program(parsed_tree)
        original_tree = deepcopy(tree)

        before_dot = os.path.join(BASE_DIR, "ast_before.dot")
        before_png = os.path.join(BASE_DIR, "ast_before.png")
        after_dot = os.path.join(BASE_DIR, "ast_after.dot")
        after_png = os.path.join(BASE_DIR, "ast_after.png")

        visualize_ast(
            original_tree,
            before_dot,
            before_png
        )

        optimized_tree = PassManager().run(tree)

        visualize_ast(
            optimized_tree,
            after_dot,
            after_png
        )

        return jsonify({
            "normalized_code": normalized_code,
            "optimized_code": generate_code(optimized_tree),
            "ast_image": "/ast-after-image",
            "ast_before_image": "/ast-before-image",
            "ast_after_image": "/ast-after-image",
            "symbol_table": build_symbol_table(optimized_tree)
        })

    except Exception as error:
        app.logger.error(
            "NEXORA ERROR:\n%s",
            traceback.format_exc()
        )

        return jsonify({
            "error": str(error),
            "error_type": type(error).__name__
        }), 400


@app.route("/ast-image")
@app.route("/ast-after-image")
def ast_after_image():
    path = os.path.join(BASE_DIR, "ast_after.png")

    if not os.path.exists(path):
        return jsonify({
            "error": "AST after optimization has not been generated."
        }), 404

    return send_file(path, mimetype="image/png")


@app.route("/ast-before-image")
def ast_before_image():
    path = os.path.join(BASE_DIR, "ast_before.png")

    if not os.path.exists(path):
        return jsonify({
            "error": "AST before optimization has not been generated."
        }), 404

    return send_file(path, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

from visualizer import visualize_ast
from lexer_parser import parse_source
from pass_manager import PassManager
from code_generator import generate_code
from symbol_table import SymbolTable
from ast_nodes import Block, Assign, Num


def build_symbol_table(tree):
    table = SymbolTable()

    if isinstance(tree, Block):
        for statement in tree.statements:
            if isinstance(statement, Assign):
                value = statement.value.value if isinstance(statement.value, Num) else None

                data_type = None
                if isinstance(statement.value, Num):
                    data_type = type(statement.value.value).__name__

                table.define(statement.name, value, data_type)

    return table


def main():
    print("=" * 45)
    print("       ASTOpt - Compiler Optimizer")
    print("=" * 45)

    source_code = """
x = 3 + 4 * 2
y = x + 1
if False:
    z = 9
"""

    print("\nOriginal Code:")
    print(source_code)

    try:
        tree = parse_source(source_code)
        optimized_tree = PassManager().run(tree)
        visualize_ast(optimized_tree)
        print("\nOptimized Code:")
        print(generate_code(optimized_tree))

        symbol_table = build_symbol_table(optimized_tree)
        symbol_table.display()

    except Exception as error:
        print("Error:", error)


if __name__ == "__main__":
    main()

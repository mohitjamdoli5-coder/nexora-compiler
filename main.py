
from parser import Parser
from ast_adapter import convert_program
from visualizer import visualize_ast
from pass_manager import PassManager
from code_generator import generate_code
from symbol_table import SymbolTable
from ast_nodes import Block, Assign, Num


def read_source_code():
    print("\nEnter your code below.")
    print("Type END on a new line when finished.\n")

    lines = []

    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip() == "END":
            break

        lines.append(line)

    return "\n".join(lines)


def build_symbol_table(tree):
    table = SymbolTable()

    def collect_statements(node):
        if isinstance(node, Block):
            for statement in node.statements:
                collect_statements(statement)

        elif isinstance(node, Assign):
            value = (
                statement_value(node.value)
            )

            data_type = (
                type(value).__name__
                if value is not None
                else None
            )

            table.define(node.name, value, data_type)

    def statement_value(node):
        if isinstance(node, Num):
            return node.value
        return None

    collect_statements(tree)
    return table


def main():
    print("=" * 45)
    print("       ASTOpt - Compiler Optimizer")
    print("=" * 45)

    source_code = read_source_code()

    if not source_code.strip():
        print("\nNo code entered.")
        return

    print("\nOriginal Code:")
    print(source_code)

    try:
        parsed_tree = Parser(source_code).parse()
        tree = convert_program(parsed_tree)

        print("\nParsing successful!")

        optimized_tree = PassManager().run(tree)

        visualize_ast(optimized_tree)

        print("\nOptimized Code:")
        print(generate_code(optimized_tree))

        print("\nSymbol Table:")
        symbol_table = build_symbol_table(optimized_tree)
        symbol_table.display()

    except Exception as error:
        print(f"\nCompilation Error: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()


import time
from lexer_parser import parse_source
from pass_manager import PassManager
from code_generator import generate_code


def benchmark(source_code):
    start_time = time.perf_counter()
    tree = parse_source(source_code)
    parse_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    optimized_tree = PassManager().run(tree)
    optimization_time = time.perf_counter() - start_time

    original_code = source_code
    optimized_code = generate_code(optimized_tree)

    print("\nBenchmark Results")
    print("-" * 45)
    print(f"Parsing time:      {parse_time:.8f} seconds")
    print(f"Optimization time: {optimization_time:.8f} seconds")
    print(f"Original lines:    {len(original_code.splitlines())}")
    print(f"Optimized lines:   {len(optimized_code.splitlines())}")

    return {
        "parse_time": parse_time,
        "optimization_time": optimization_time,
        "original_lines": len(original_code.splitlines()),
        "optimized_lines": len(optimized_code.splitlines()),
    }


if __name__ == "__main__":
    program = """
x = 3 + 4 * 2
y = x + 1
z = 10 * 20
"""

    benchmark(program)

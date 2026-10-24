
from parser import Parser
from ast_adapter import convert_program

source = """x = 10 + 5
if x >= 10:
    y = 1
else:
    y = 2
"""

parsed_tree = Parser(source).parse()
custom_tree = convert_program(parsed_tree)

print(custom_tree)
print("Adapter conversion successful!")

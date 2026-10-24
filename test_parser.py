
from parser import Parser

source = """x = 10
if x >= 10:
    y = x + 1
    z = y * 2
w = 5
"""

parser = Parser(source)
tree = parser.parse()

print("Parsing successful!")
print(tree)


from lexer import tokenize

source = """x = 10
if x >= 10:
    y = x + 1
    z = y * 2
w = 5
"""

for token in tokenize(source):
    print(token)

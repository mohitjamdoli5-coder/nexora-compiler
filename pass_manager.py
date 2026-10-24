
from optimizations import (
    constant_folding,
    constant_propagation,
    dead_code_elimination,
)
from loop_motion import loop_invariant_code_motion
from cse import common_subexpression_elimination


class PassManager:
    def __init__(self):
        self.passes = [
            constant_folding,
            constant_propagation,
            constant_folding,
            common_subexpression_elimination,
            loop_invariant_code_motion,
            dead_code_elimination,
        ]

    def run(self, tree):
        for optimization_pass in self.passes:
            tree = optimization_pass(tree)
        return tree

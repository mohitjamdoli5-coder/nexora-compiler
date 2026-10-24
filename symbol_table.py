
class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def define(self, name, value=None, data_type=None):
        self.symbols[name] = {
            "value": value,
            "data_type": data_type
        }

    def lookup(self, name):
        return self.symbols.get(name)

    def update(self, name, value):
        if name in self.symbols:
            self.symbols[name]["value"] = value
            return True
        return False

    def exists(self, name):
        return name in self.symbols

    def display(self):
        if not self.symbols:
            print("Symbol table is empty.")
            return

        print("\nSymbol Table")
        print("-" * 45)
        print(f"{'Variable':<15}{'Value':<15}{'Data Type':<15}")
        print("-" * 45)

        for name, details in self.symbols.items():
            print(
                f"{name:<15}"
                f"{str(details['value']):<15}"
                f"{str(details['data_type']):<15}"
            )

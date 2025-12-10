# DSL/dsl/ast_nodes.py

class Series:
    """
    Represents a dataframe series reference, e.g. df['close'].
    """
    def __init__(self, value):
        self.type = "series"
        self.value = value

    def to_dict(self):
        return {
            "type": "series",
            "value": self.value
        }


class Number:
    """
    Represents a numeric literal such as 1000000 or 30.
    FIX #2: prevents numbers from being misinterpreted as df['1000000'].
    """
    def __init__(self, value):
        self.type = "number"
        self.value = float(value)

    def to_dict(self):
        return {
            "type": "number",
            "value": self.value
        }


class Indicator:
    """
    Represents SMA(close,20) or RSI(close,14).
    """
    def __init__(self, text):
        self.type = "indicator"
        name, rest = text.split("(", 1)
        self.name = name.lower()
        params = rest.rstrip(")").split(",")
        self.params = [p.strip() for p in params]

    def to_dict(self):
        return {
            "type": "indicator",
            "name": self.name,
            "params": self.params
        }


class BinaryOp:
    """
    Represents comparison operations: >, <, <=, >=
    """
    def __init__(self, left, op, right):
        self.type = "binary_op"
        self.left = left
        self.op = op
        self.right = right

    def to_dict(self):
        return {
            "type": "binary_op",
            "left": self.left.to_dict(),
            "op": self.op,
            "right": self.right.to_dict()
        }


class CrossOp:
    """
    Represents: crosses above / crosses below
    """
    def __init__(self, left, direction, right):
        self.type = "cross"
        self.dir = direction
        self.left = left
        self.right = right

    def to_dict(self):
        return {
            "type": "cross",
            "dir": self.dir,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }

from lark import Lark, Transformer
from pathlib import Path
from .ast_nodes import Series, Indicator, BinaryOp, CrossOp, Number

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"
grammar = GRAMMAR_PATH.read_text()

dsl_parser = Lark(grammar, start="start", parser="lalr")

class DSLTransformer(Transformer):

    def start(self, items):
        return items

    def entry_section(self, items):
        return ("entry", items[0])

    def exit_section(self, items):
        return ("exit", items[0])

    def comparison(self, items):
        left, op, right = items
        return BinaryOp(left, op.value, right)

    def and_op(self, items):
        return {"type": "and", "left": items[0], "right": items[1]}

    def or_op(self, items):
        return {"type": "or", "left": items[0], "right": items[1]}

    def cross_above(self, items):
        return CrossOp(items[0], "above", items[1])

    def cross_below(self, items):
        return CrossOp(items[0], "below", items[1])

    def indicator(self, items):
        return Indicator(str(items[0]))

    def ident(self, items):
        return Series(str(items[0]))

    def number(self, items):
        return Number(items[0])   # ✔ FIXED: numbers are literal values

    def yest_high(self, items):
        return Series("yesterday_high")


def parse_dsl(text: str):
    tree = dsl_parser.parse(text)
    ast_items = DSLTransformer().transform(tree)
    final = {"entry": [], "exit": []}
    for section, rule in ast_items:
        final[section].append(
            rule.to_dict() if hasattr(rule, "to_dict") else rule
        )
    return final

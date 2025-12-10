"""
End-to-End demo script for NL -> DSL -> AST -> Code -> Execution -> Backtest
Save as: DSL/demo/run_demo.py
Run from project root:
    python DSL/demo/run_demo.py
"""

# -------------------------------------------------------
# FIX 1: Ensure DSL/ is in Python path
# -------------------------------------------------------
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -------------------------------------------------------
# Imports
# -------------------------------------------------------
import json
import textwrap
import pandas as pd
import numpy as np

from nlp.nl_to_json import nl_to_json
from dsl.parser import parse_dsl
from generator.codegen import generate_strategy_code, sma, rsi
from backtest.simulator import run_backtest

# -------------------------------------------------------
# FIX 2: Convert AST objects to JSON-safe dicts
# -------------------------------------------------------
def ast_to_jsonable(node):
    """Recursively convert AST objects into JSON-serializable dictionaries."""
    # Convert dict
    if isinstance(node, dict):
        return {k: ast_to_jsonable(v) for k, v in node.items()}
    # Convert list
    if isinstance(node, list):
        return [ast_to_jsonable(x) for x in node]
    # Convert AST node object via .to_dict()
    if hasattr(node, "to_dict"):
        return ast_to_jsonable(node.to_dict())
    # Primitive values
    return node


# -------------------------------------------------------
# Convert JSON (from NL) into DSL string
# -------------------------------------------------------
def nl_json_to_dsl(nl_json: dict) -> str:
    """Convert NL->JSON structured output into a DSL string."""
    def clause_list(kind):
        parts = []
        for it in nl_json.get(kind, []):
            left = it["left"]
            op = it["operator"]
            right = it["right"]
            parts.append(f"{left} {op} {right}")
        return " AND ".join(parts)

    entry = clause_list("entry")
    exit_ = clause_list("exit")

    return f"ENTRY: {entry if entry else 'True'}\nEXIT: {exit_ if exit_ else 'False'}"


# -------------------------------------------------------
# Generate sample OHLCV data
# -------------------------------------------------------
def sample_data(n=120, seed=42):
    rng = pd.date_range("2023-01-01", periods=n, freq="D")
    np.random.seed(seed)
    noise = np.random.normal(loc=0.1, scale=1.0, size=n)
    price = 100 + np.cumsum(noise)

    df = pd.DataFrame({
        "open":  price + np.random.normal(0, 0.3, size=n),
        "high":  price + np.random.uniform(0, 1.0, size=n),
        "low":   price - np.random.uniform(0, 1.0, size=n),
        "close": price,
        "volume": np.random.randint(800000, 1500000, size=n)
    }, index=rng)

    return df


# -------------------------------------------------------
# MAIN DEMO PIPELINE
# -------------------------------------------------------
def run_demo(nl_input: str, df: pd.DataFrame):
    print("\n" + "="*80)
    print("NATURAL LANGUAGE INPUT:")
    print(nl_input)
    print("="*80 + "\n")

    # ---------------- PHASE 1: NL -> JSON ----------------
    nl_json = nl_to_json(nl_input)
    print("NL -> JSON (structured):")
    print(json.dumps(nl_json, indent=2))
    print()

    # ---------------- PHASE 2: JSON -> DSL ----------------
    dsl_text = nl_json_to_dsl(nl_json)
    print("Generated DSL:")
    print(dsl_text)
    print()

    # ---------------- PHASE 3: DSL -> AST ----------------
    ast = parse_dsl(dsl_text)
    print("Parsed AST (dict):")
    print(json.dumps(ast_to_jsonable(ast), indent=2))
    print()

    # ---------------- PHASE 4: AST -> Python Code ----------------
    code_str = generate_strategy_code(ast, df_name="df")
    print("Generated Python code:")
    print(code_str)
    print()

    # Execute generated code
    namespace = {"pd": pd, "sma": sma, "rsi": rsi}
    exec(code_str, namespace)
    evaluate_signals = namespace["evaluate_signals"]

    # ---------------- PHASE 5: Generate Signals + Backtest ----------------
    signals = evaluate_signals(df)

    print("Signals (head):")
    print(signals.head())
    print()

    trades, metrics, equity_curve = run_backtest(df, signals)

    print("Trades:")
    for t in trades:
        print(t)
    print()

    print("Backtest Metrics:")
    print(json.dumps(metrics, indent=2))
    print()

    print("Equity Curve (tail):")
    print(equity_curve.tail())
    print("\n" + "="*80 + "\n")

    return {
        "nl_json": nl_json,
        "dsl_text": dsl_text,
        "ast": ast_to_jsonable(ast),
        "code_str": code_str,
        "signals": signals,
        "trades": trades,
        "metrics": metrics,
        "equity_curve": equity_curve,
    }


# -------------------------------------------------------
# Example Usage
# -------------------------------------------------------
if __name__ == "__main__":
    nl_input = (
        "Buy when the close price is above the 20-day moving average and volume is above 1 million. "
        "Exit when RSI(14) is below 30."
    )

    df = sample_data(n=200, seed=0)
    run_demo(nl_input, df)

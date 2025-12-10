import pandas as pd

##############################################
# INDICATOR IMPLEMENTATIONS
##############################################

def sma(series: pd.Series, n: int):
    """Simple Moving Average"""
    return series.rolling(int(n)).mean()

def rsi(series: pd.Series, n: int):
    """Relative Strength Index"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(n).mean()
    avg_loss = loss.rolling(n).mean()
    
    # Prevent division by zero
    avg_loss = avg_loss.replace(0, 1e-9)
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


##############################################
# AST → PYTHON EXPRESSION HELPERS
##############################################

def _resolve_operand(node, df_name="df"):

    if hasattr(node, "to_dict"):
        node = node.to_dict()

    if node["type"] == "series":
        val = node["value"]
        if val == "yesterday_high":
            return f"{df_name}['high'].shift(1)"
        return f"{df_name}['{val}']"

    if node["type"] == "indicator":
        name = node["name"]
        series = node["params"][0]
        period = node["params"][1]
        if name == "sma":
            return f"sma({df_name}['{series}'], {period})"
        if name == "rsi":
            return f"rsi({df_name}['{series}'], {period})"

    # NEW ---------------------
    if node["type"] == "number":
        return str(node["value"])

    return str(node)



def __expr_from_ast(node, df_name="df"):
    """Turn an AST node into executable Python expression."""

    # Convert object → dict
    if hasattr(node, "to_dict"):
        node = node.to_dict()

    t = node["type"]

    # Comparison operators
    if t == "binary_op":
        left = _resolve_operand(node["left"], df_name)
        right = _resolve_operand(node["right"], df_name)
        return f"({left} {node['op']} {right})"

    # Cross events
    if t == "cross":
        left = _resolve_operand(node["left"], df_name)
        right = _resolve_operand(node["right"], df_name)

        if node["dir"] == "above":
            return (
                f"(({left} > {right}) & "
                f"({left}.shift(1) <= {right}.shift(1)))"
            )
        if node["dir"] == "below":
            return (
                f"(({left} < {right}) & "
                f"({left}.shift(1) >= {right}.shift(1)))"
            )

    # Boolean AND
    if t == "and":
        left = __expr_from_ast(node["left"], df_name)
        right = __expr_from_ast(node["right"], df_name)
        return f"({left} & {right})"

    # Boolean OR
    if t == "or":
        left = __expr_from_ast(node["left"], df_name)
        right = __expr_from_ast(node["right"], df_name)
        return f"({left} | {right})"

    raise ValueError(f"Unknown AST node type: {t}")



##############################################
# MAIN FUNCTION: AST → STRATEGY CODE
##############################################

def generate_strategy_code(ast: dict, df_name="df"):
    """
    Takes an AST dictionary and returns a Python function definition
    that evaluates entry/exit signals on a pandas DataFrame.

    Output is a Python function as a string:
        def evaluate_signals(df):
            signals = ...
            return signals
    """
    
    entry_parts = []
    exit_parts = []
    
    # Convert AST nodes to Python expressions
    for node in ast.get("entry", []):
        entry_parts.append(__expr_from_ast(node, df_name))
    
    for node in ast.get("exit", []):
        exit_parts.append(__expr_from_ast(node, df_name))
    
    # If no rules, default to always False
    entry_expr = (
        " & ".join(entry_parts)
        if entry_parts
        else f"pd.Series(False, index={df_name}.index)"
    )
    exit_expr = (
        " | ".join(exit_parts)
        if exit_parts
        else f"pd.Series(False, index={df_name}.index)"
    )
    
    # Python function template
    func_code = f"""
def evaluate_signals({df_name}):
    signals = pd.DataFrame(index={df_name}.index)
    signals['entry'] = {entry_expr}
    signals['exit'] = {exit_expr}
    return signals
"""
    
    return func_code

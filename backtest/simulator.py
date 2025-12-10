# Phase 5 — backtest/simulator.py
import pandas as pd
from typing import List, Dict, Any, Tuple

def run_backtest(df: pd.DataFrame,
                 signals: pd.DataFrame,
                 price_field: str = "close",
                 capital: float = 1.0) -> Tuple[List[Dict[str, Any]], Dict[str, Any], pd.Series]:
    """
    Run a simple backtest.

    Args:
        df: OHLCV DataFrame indexed by datetime, must contain `price_field`.
        signals: DataFrame with boolean columns 'entry' and 'exit' aligned to df.index.
        price_field: column name to use as execution price (default 'close').
        capital: starting capital (normalized, default 1.0)

    Returns:
        trades: list of trades (dicts with entry/exit details)
        metrics: dict with total_return_pct, max_drawdown_pct, num_trades, win_rate, avg_return_pct
        equity_curve: pd.Series of equity over time (index = df.index)
    """
    if "entry" not in signals.columns or "exit" not in signals.columns:
        raise ValueError("signals DataFrame must contain 'entry' and 'exit' boolean columns")

    # ensure alignment
    signals = signals.reindex(df.index).fillna(False)
    
    position = None  # dict storing entry info while in a trade
    trades: List[Dict[str, Any]] = []
    equity = capital
    equity_curve: List[float] = []
    peak = equity

    # iterate rows in order
    for i, idx in enumerate(df.index):
        price = float(df.iloc[i][price_field])
        is_entry = bool(signals.iloc[i]["entry"])
        is_exit = bool(signals.iloc[i]["exit"])

        # Enter
        if position is None and is_entry:
            position = {
                "entry_date": idx,
                "entry_price": price,
            }

        # Exit
        if position is not None and is_exit:
            position["exit_date"] = idx
            position["exit_price"] = price
            position["return_pct"] = (position["exit_price"] / position["entry_price"] - 1.0) * 100.0
            # apply return multiplicatively to equity
            equity = equity * (1.0 + (position["return_pct"] / 100.0))
            trades.append(position)
            position = None

        equity_curve.append(equity)
        peak = max(peak, equity)

    # If still in position at the end, close at last price (optionally you could keep open)
    if position is not None:
        last_price = float(df.iloc[-1][price_field])
        position["exit_date"] = df.index[-1]
        position["exit_price"] = last_price
        position["return_pct"] = (position["exit_price"] / position["entry_price"] - 1.0) * 100.0
        equity = equity * (1.0 + (position["return_pct"] / 100.0))
        trades.append(position)
        equity_curve[-1] = equity
        position = None

    # Metrics
    total_return_pct = (equity - capital) / capital * 100.0
    ec = pd.Series(equity_curve, index=df.index[:len(equity_curve)])
    roll_max = ec.cummax()
    drawdown = (ec - roll_max) / roll_max
    max_drawdown_pct = drawdown.min() * 100.0

    num_trades = len(trades)
    wins = [t for t in trades if t.get("return_pct", 0) > 0]
    win_rate = (len(wins) / num_trades * 100.0) if num_trades > 0 else 0.0
    avg_return_pct = (sum(t.get("return_pct", 0.0) for t in trades) / num_trades) if num_trades > 0 else 0.0

    metrics = {
        "total_return_pct": total_return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "num_trades": num_trades,
        "win_rate_pct": win_rate,
        "avg_trade_return_pct": avg_return_pct
    }

    return trades, metrics, ec


# -------------------------
# Quick demo (run as a cell)
# -------------------------
if __name__ == "__main__":
    # Generate a small synthetic dataset
    import numpy as np
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    np.random.seed(1)
    price = 100 + np.cumsum(np.random.normal(0.5, 1.5, size=len(dates)))
    df = pd.DataFrame({
        "open": price + np.random.normal(0, 0.5, size=len(dates)),
        "high": price + np.random.uniform(0, 1.5, size=len(dates)),
        "low": price - np.random.uniform(0, 1.5, size=len(dates)),
        "close": price,
        "volume": (np.random.poisson(1_000_000, size=len(dates))).astype(int)
    }, index=dates)

    # Very simple signal: enter when price increases > 0.8 vs previous day, exit when decreases < -0.2
    signals = pd.DataFrame(index=df.index)
    signals["entry"] = (df["close"].diff() > 0.8).fillna(False)
    signals["exit"] = (df["close"].diff() < -0.2).fillna(False)

    trades, metrics, equity_curve = run_backtest(df, signals)
    print("Trades:")
    for t in trades:
        print(t)
    print("\nMetrics:")
    print(metrics)
    print("\nEquity head:")
    print(equity_curve.head())

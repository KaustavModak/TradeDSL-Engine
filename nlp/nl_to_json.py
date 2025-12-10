import re
from typing import Dict, Any

print(">>> USING nl_to_json.py FROM:", __file__)

# -----------------------------
# Helper: parse volumes ('1M', '1 million', '500k')
# -----------------------------
def parse_volume(text: str):
    m = re.search(r'(\d+(?:\.\d+)?)\s*(m|M|million|k|K|thousand)?', text)
    if not m:
        return None

    num = float(m.group(1))
    unit = (m.group(2) or "").lower()

    if unit in ("m", "million"):
        return int(num * 1_000_000)
    if unit in ("k", "thousand"):
        return int(num * 1_000)

    return int(num)


# -----------------------------
# FIXED normalize_indicator
# -----------------------------
def normalize_indicator(text: str):
    # CORRECT: capture "20-day moving average"
    m = re.search(r"(\d+)\s*-\s*day\s+moving\s+average", text, re.I)
    if m:
        return f"sma(close,{m.group(1)})"

    # Match RSI(14)
    m = re.search(r"rsi\s*\(?\s*(\d+)\s*\)?", text, re.I)
    if m:
        return f"rsi(close,{m.group(1)})"

    return None


# -----------------------------
# FIXED extract_comparisons
# -----------------------------
def extract_comparisons(text: str):
    print(">>> DEBUG extract text:", text)
    comps = []

    # FIXED robust SMA detection
    m = re.search(r"close.*above.*?(\d+)\s*-\s*day\s+moving\s+average", text, re.I)
    if m:
        period = m.group(1)
        comps.append(("close", ">", f"sma(close,{period})"))

    # Volume above 1M
    m = re.search(r"volume.*above\s+([^\.,;]+)", text, re.I)
    if m:
        vol = parse_volume(m.group(1))
        if vol:
            comps.append(("volume", ">", vol))

    # Crosses above yesterday high
    m = re.search(r"(close|price).*cross(?:es)?\s+above\s+yesterday'?s high", text, re.I)
    if m:
        comps.append(("close", "crosses_above", "yesterday_high"))

    # RSI(14) below 30
    m = re.search(r"rsi\s*\(?\s*(\d+)\s*\)?.*below\s*(\d+)", text, re.I)
    if m:
        rsi_len = m.group(1)
        threshold = float(m.group(2))
        comps.append((f"rsi(close,{rsi_len})", "<", threshold))

    return comps 



# -----------------------------
# MAIN FUNCTION — NL → JSON
# -----------------------------
def nl_to_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    sentences = re.split(r"[.\n]", text)

    entry_rules = []
    exit_rules = []

    for s in sentences:
        sl = s.lower().strip()
        if not sl:
            continue

        # Entry keywords
        if any(k in sl for k in ["buy", "enter", "trigger entry"]):
            entry_rules += extract_comparisons(s)

        # Exit keywords
        elif any(k in sl for k in ["exit", "sell", "close position"]):
            exit_rules += extract_comparisons(s)

        else:
            # fallback logic
            if "rsi" in sl:
                exit_rules += extract_comparisons(s)
            else:
                entry_rules += extract_comparisons(s)

    def conv(lst):
        return [{"left": L, "operator": O, "right": R} for (L, O, R) in lst]

    return {
        "entry": conv(entry_rules),
        "exit": conv(exit_rules)
    }

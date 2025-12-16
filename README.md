# Natural Language Trading Strategy Engine

This project converts **natural language trading rules** into a fully executable **backtesting engine**.  
It follows a compiler-style pipeline:

**Natural Language → JSON → DSL → AST → Python Code → Backtest Results**

This project is built exactly according to the specifications of the assignment PDF.

---

#  Features

### ✔ Convert English trading rules into structured JSON  
Input example:

> “Buy when the close price is above the 20-day moving average and volume is above 1 million.  
> Exit when RSI(14) is below 30.”

Output JSON:

```json
{
  "entry": [
    {"left": "close", "operator": ">", "right": "sma(close,20)"},
    {"left": "volume", "operator": ">", "right": 1000000}
  ],
  "exit": [
    {"left": "rsi(close,14)", "operator": "<", "right": 30}
  ]
}
```
### Human-readable DSL representation
ENTRY: close > sma(close,20) AND volume > 1000000.

EXIT: rsi(close,14) < 30

### DSL → AST (Abstract Syntax Tree)

The DSL is parsed using a Lark-based grammar, producing structured AST nodes:

- Series nodes

- Indicator nodes

- Comparison nodes

- Logical operators (AND/OR)

- Cross events

### AST → Python code generation

### Fully functional backtest engine

The system produces:

- Detailed list of trades

- Total return

- Max drawdown

- Win rate

- Average trade return

- Equity curve

## Project Structure
```bash
DSL/
│
├── nlp/
│   └── nl_to_json.py           # Phase 1: Natural Language → JSON
│
├── dsl/
│   ├── grammar.lark            # Phase 2: DSL grammar
│   ├── parser.py               # Phase 3: DSL → AST
│   └── ast_nodes.py            # AST node classes
│
├── generator/
│   └── codegen.py              # Phase 4: AST → Python code
│
├── backtest/
│   └── simulator.py            # Phase 5: Backtest engine
│
└── demo/
    └── run_demo.py             # Phase 6: End-to-end pipeline demo
```
## Installation

Install dependencies:
```bash
pip install pandas numpy lark-parser
```
## Running the Demo

Execute the full pipeline:
```bash
python DSL/demo/run_demo.py
```

Example output includes:

- Input NL text

- JSON rules

- DSL

- AST

- Generated Python code

- Backtest results

# ⭐ **DSL Grammar Specification (Short Document)**

## 1. Introduction

This document describes the **Domain Specific Language (DSL)** used to define trading strategies in a structured and machine-readable format.
The DSL is designed to be simple, readable, and easy to convert into executable Python code.

A strategy in this DSL contains two main sections:

* `ENTRY:` — conditions that trigger a buy
* `EXIT:` — conditions that trigger a sell

Each rule supports indicators, comparisons, numbers, logical operators, and cross events.

---

## 2. DSL Structure

A DSL strategy consists of:

```
ENTRY: <entry_expression>
EXIT: <exit_expression>
```

Each `<expression>` can include:

* Comparisons
* Indicators
* Logical operators (`AND`, `OR`)
* Cross events (`CROSSES ABOVE`, `CROSSES BELOW`)
* Special identifiers like `yesterday_high`

---

## 3. Grammar Overview (Informal)

```
<strategy>   ::= <entry_section> <exit_section>

<entry_section> ::= "ENTRY:" <expr>
<exit_section>  ::= "EXIT:" <expr>

<expr> ::= <expr> "AND" <expr>
         | <expr> "OR"  <expr>
         | <comparison>
         | <cross>

<comparison> ::= <value> <operator> <value>

<operator> ::= ">" | "<" | ">=" | "<="

<cross> ::= <value> "CROSSES ABOVE" <value>
          | <value> "CROSSES BELOW" <value>

<value> ::= <identifier>
          | <number>
          | <indicator>

<indicator> ::= IDENT "(" <params> ")"
<params> ::= <value> ("," <value>)*
```

This grammar is implemented using **Lark**, a Python parsing library.

---

## 4. Allowed Components

### **4.1 Identifiers**

Represent columns in the input DataFrame:

```
close
open
high
low
volume
yesterday_high
```

### **4.2 Numbers**

```
100
1000000
20
14
30
```

### **4.3 Indicators**

Supported indicators:

```
sma(close,20)
rsi(close,14)
```

More can be added easily in future.

### **4.4 Comparison Operators**

```
>
<
>=
<=
```

### **4.5 Logical Operators**

```
AND
OR
```

### **4.6 Cross Events**

```
close CROSSES ABOVE sma(close,20)
rsi(close,14) CROSSES BELOW 30
```

---

## 5. Examples

### **Example 1 — Simple Moving Average Strategy**

```
ENTRY: close > sma(close,20)
EXIT: close < sma(close,20)
```

### **Example 2 — Multiple Conditions**

```
ENTRY: close > sma(close,20) AND volume > 1000000
EXIT: rsi(close,14) < 30
```

### **Example 3 — Cross Event**

```
ENTRY: close CROSSES ABOVE sma(close,50)
EXIT: close CROSSES BELOW sma(close,50)
```

### **Example 4 — OR Logic**

```
ENTRY: rsi(close,14) < 30 OR close < sma(close,200)
EXIT: rsi(close,14) > 70
```

---

## 6. How the DSL is Used

1. The DSL text is parsed using the Lark grammar.
2. A **parse tree** is produced.
3. The **AST transformer** converts the parse tree into AST node classes.
4. The AST is then transformed into executable Python code.

Example flow:

```
DSL → AST → Python condition → evaluate_signals() → backtest
```

---

## 7. Design Goals

* **Readable**: Easy for users to write and understand.
* **Consistent**: Every strategy follows the same structure.
* **Safe**: Users cannot execute arbitrary Python code.
* **Extensible**: New indicators or operators can be added easily.

---

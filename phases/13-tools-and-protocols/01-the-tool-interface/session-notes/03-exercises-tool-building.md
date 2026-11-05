# Exercises 1–3 — Building the Stock Tool, Breaking the Validator, Firing the Gate

All work in `code/exercises.py`. Exercises 1–3 verified by live output.

## Exercise 1 — `get_stock_price(ticker)`

Three edits in loop-consumption order: executor → registry → router.

**The data-honesty decision.** First version returned `fake.get(ticker)` with no default → `price: None` for unknown tickers. A silent default is harmless-ish for weather (`20`) but indefensible for a price — a fabricated plausible-looking number is dangerous wrong. Final shape: explicit error result the model can report:

```python
def tool_get_stock_price(args: dict) -> dict:
    fake = {"AAPL": 369, "TSLA": 125}
    ticker = args["ticker"]
    currency = args.get("currency", "usd")
    if ticker not in fake:
        return {"ticker": ticker, "error": "unknown ticker"}
    return {"ticker": ticker, "price": fake[ticker], "currency": currency}
```

Purity is about side effects; data honesty is a separate axis.

**The glued-string bug.** Adjacent Python strings concatenate with no separator — dropping the trailing space made the registry print `by ticker.Do not use`. The description is read by the model; glued sentences are exactly what `outputs/skill-tool-interface-reviewer.md` audits.

**The lowercase trap.** `fake_decide` runs `msg = user_msg.lower()`; tickers are uppercase. The phrase-match + `.upper()` workaround works for all-caps tickers but fails for `BRK.B` (`\w+` can't match the dot), and `.title()` before `.upper()` was dead code. Pattern: **extraction of case-significant data must read the raw message before `.lower()`.**

**Schema** mirrored `get_weather`: required `ticker`, optional enum `currency: ["usd", "eur"]`.

## Exercise 2 — break the validator, decide reject-or-ignore

Probes live in their **own route branches** (`broken add 7`, `sneaky stock price of AAPL`) — the first attempt mutated the legitimate stock route instead, permanently contaminating every happy-path demo. Process lesson: probes never share routes with real queries.

```console
$ python3 code/exercises.py
USER : broken add 7
TURN 1 DECIDE : call add id=call_eb1fa3b9
           args = {"a": 7.0}
           VALIDATION ERRORS : ["missing required field 'b'"]
USER : sneaky stock price of AAPL
           VALIDATION ERRORS : ["unknown field 'mode' not in schema"]
```

The original validator produced zero errors for probe B — it only iterates `schema["properties"]`.

**Verdict: reject.** First argument was "prompt injections" — right conclusion, imprecise layer. Prompt injection is untrusted *text steering the model's decisions* (a decide-step threat). The unknown-field leak is a **trust-boundary failure**: `tool.executor(call["arguments"])` hands the entire args dict to the executor, and undeclared keys cross unvalidated — the executor may pass the dict onward (SQL, shell, HTTP body). Two arguments for reject: hallucination semantics (`"mod"` is plausibly a typo for `mode` — ignore means the call *succeeds while doing the wrong thing*, the worst failure class), and fail-fast auditability (a rejected call is logged and retried; an ignored field vanishes without a trace).

**Enforcement**, three lines in the validator's object branch:

```python
known = set(schema.get("properties", {}))
for key in value:
    if key not in known:
        errors.append(f"unknown field '{key}' not in schema")
```

Nuance: real JSON Schema spells this `additionalProperties: false`; some hosts deliberately allow unknown fields for forward compatibility. The difference from the harness: production hosts make the choice **visible and deliberate, never silent**.

## Exercise 3 — classify, flag, watch the gate fire

`place_trade(ticker, shares, action)` scaffolded with `consequential=True` — the description's negative constraint (`"Do not use for price lookups…"`) disambiguates it from adjacent tool `get_stock_price`.

```console
$ python3 code/exercises.py
USER : buy 10 shares of AAPL
TURN 1 DECIDE : call place_trade id=call_71e4d0ad
           args = {"ticker": "AAPL", "shares": 10.0, "action": "buy"}
           GATE : tool is consequential, would confirm
TURN 1 EXECUTE: place_trade -> {"status": "filled", "action": "buy",
                                "ticker": "AAPL", "shares": 10.0}
```

- Registry classifies all five: four `[pure]`, one `[consequential]`; the gate fires **only** for `place_trade` — the flag is the mechanical enforcement point.
- Gate position: `DECIDE → validate → GATE → EXECUTE`. In a real host, that line is where the loop *pauses* for user confirmation — Rule of Two enforcement happens exactly there.
- `shares: 10.0` — the minimal validator subset only knows `number`; production tightens to `"type": "integer"`.
# Registry, Validator, and the Loop in Code

Source: `phases/13-tools-and-protocols/01-the-tool-interface/code/main.py` (stdlib, no LLM). Exercises live in `code/exercises.py`.

## The `Tool` record is the describe step

```python
@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    executor: Callable[[dict], Any]
    consequential: bool = False
```

- `name` — stable, machine-readable (`add`, not "math helper")
- `description` — written for the *model*: "Use when… Do not use for…" — negative constraints stop misuse
- `input_schema` — JSON Schema contract the validator enforces
- `executor` — ordinary Python; `consequential` flags side-effecting tools (gate hook)

## Validator: minimal JSON Schema subset, ~20 stdlib lines

```python
def validate(schema, value):
    errors = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(value, dict):
            return [f"expected object, got {type(value).__name__}"]
        for field in schema.get("required", []):
            if field not in value:
                errors.append(f"missing required field '{field}'")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errors.extend(validate(sub, value[key]))
        return errors
    if t == "number" and not isinstance(value, (int, float)): ...
    if t == "string" and not isinstance(value, str): ...
    if "enum" in schema and value not in schema["enum"]: ...
```

Key behaviors verified by hand trace:

- `"required": []` (get_time) → `{}` passes cleanly; the default (`args.get("timezone", "UTC")`) lives **inside the executor**. Host checks the schema contract, executor owns defaults.
- `units: "kelvin"` against `enum: ["celsius", "fahrenheit"]` → `value 'kelvin' not in enum [...]` — and **the executor never runs** (`run_loop` returns on non-empty errors before `tool.executor`).
- Watch spelling: a typo in the enum list makes *every* legit value fail.

## The loop: `run_loop` choreography

Observed live for every query: `DECIDE → EXECUTE → OBSERVE` on turn 1, then final answer on turn 2 once the tool output is in history. The haiku query shows the third path — answer directly without calling anything.

Ordering inside the call loop, which is the security posture of step three:

1. `tools_by_name.get(call["name"])` → `None` means the model hallucinated a tool name; host refuses
2. `validate(...)` — reject before execute, every time
3. `if tool.consequential` — gate line (would confirm with user)
4. `tool.executor(call["arguments"])` — timed with `perf_counter`
5. result appended with `role: "tool"`, `id: call["id"]` — **result correlation in code**

## MAX_TURNS circuit breaker

`MAX_TURNS = 5` defends against a **runaway loop**: a model that keeps emitting calls forever (re-calling `get_weather` because it disliked the answer, ping-ponging two tools). The model has no built-in sense of "enough" — termination is *host* policy. Production bounds: Claude Code 20, OpenAI Assistants 10, Cursor 25. Without it: the "agent spent $400 in API calls overnight" post-mortem.

## Why the history check must come first in `fake_decide`

```python
if last.get("role") == "tool":
    return {"content": f"Final answer built from tool output: ..."}
```

After a tool result lands, the next decision must be driven by the **newest context**, not by re-parsing the original user message. If keyword routing ran first, the router would match "please add 7 and 35" again and re-emit the same call — the tool result sits unread while the loop re-executes until the breaker kills it. Rule: **observe consumes the result before decide can look at anything else.**
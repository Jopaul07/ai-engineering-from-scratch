# The Tool Interface — Session Notes

## Contents

| File | Topic | One-line takeaway |
|---|---|---|
| `01-four-step-loop-and-ownership.md` | The describe → decide → execute → observe invariant | Host does all the plumbing, model does exactly one thing — decide; the call `id` correlates results to in-flight requests, it is not a registry key. |
| `02-registry-validator-and-loop-code.md` | `Tool` dataclass, validator subset, `run_loop`, `MAX_TURNS` | Validate before execute, every time; observe consumes the tool result before decide re-parses the user message. |
| `03-exercises-tool-building.md` | Exercises 1–3: stock tool, validator probes, consequential gate | Never fabricate a number the executor doesn't know; probes get their own routes; the gate line is where a real host pauses for confirmation. |
| `04-claude-desktop-and-tool-choice.md` | Exercises 4–5: MCP loop in Claude Desktop, `tool_choice` | The model never sees server topology — the host dispatches; tool poisoning travels through *describe*, and `tool_choice` overrides decide's judgment. |

## Session facts

- Date: 2026-11-03
- Lesson: Phase 13 · 01 — The Tool Interface (lesson 8 of 13 on the Software Engineering Fundamentals path)
- Warm-up recall: 2/2 (carried over from Phase 0 · 12 — data leakage suspected at 99% accuracy, NaN root cause via logging activations/inspecting exploding values)
- Quiz score: 3/3 — no `quiz.json` ships with this lesson (repo gap worth flagging upstream), so the check was built from lesson material
- Quiz verdicts: pure/consequential classification correct but only half the reasoning (re-run safety + gate location); JSON failure modes and native-function-calling advantages all correct; MCP ownership slip recurred (observe is host work)
- Exercises: all five completed; 1–3 verified by live output in `code/exercises.py`, 4 rendered as Mermaid + filled provider table, 5 identified (`tool_choice`)
- Learner decisions: fixed flagged issues personally from tutor-provided fix descriptions; requested scaffolding for Exercise 3 and the Mermaid rendering for Exercise 4; asked to be pointed at the Exercise 5 answer after two full-correction sessions

## Stumbles worth re-reading

- **Ownership slip (recurring)**: first said host owns decide and model owns observe; recurred on the MCP question ("decision and observation handled by model via MCP client"). Corrected twice. Watch this in Phase 13 · 06 — observe is always host work.
- **`id` misread as registry key**: thought the call id makes tool selection efficient. It correlates results to in-flight calls (parallel, out-of-order); `name` does selection.
- **Answered the wrong question**: on the circuit breaker, gave the JSON-failure-modes/recovery answer — correct content, different question. Check which question is on the table.
- **Hijacked happy path in Exercise 2**: injected `mode: turbo` into the legitimate stock route instead of adding a dedicated probe branch. Probes live in their own routes.
- **Injection layer imprecision**: argued unknown-field rejection via "prompt injections." Sharpened to trust-boundary failure (entire args dict crosses to the executor unvalidated) vs prompt injection (untrusted text steering decide). Tool poisoning travels through descriptions, not arguments.
- **Glued string concat bug**: adjacent Python strings concatenate with no separator — dropped the trailing space and the model-facing description read `ticker.Do not use`.
- **Model routes MCP calls (wrong)**: Claude Desktop owns the `name → server` mapping; the model never sees server topology.
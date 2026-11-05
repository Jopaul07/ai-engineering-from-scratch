# Debugging and Profiling — Session Notes

## Contents

| File | Topic | One-line takeaway |
|---|---|---|
| `01-silent-failures-and-inspection.md` | The three-level pyramid + `debug_print` | AI bugs are silent; one helper function catches shape, dtype, device, and NaN in a single line. |
| `02-conditional-breakpoints-and-logging.md` | `breakpoint()`, logging, VS Code debugger | Stop only when something looks wrong; severity levels are a runtime filter, not a code edit. |
| `03-performance-and-memory.md` | `Timer`, `cProfile`, `line_profiler`, `tracemalloc`, GPU OOM | Data loading usually starves the GPU; fix `num_workers > 0` before touching hardware. |
| `04-bugs-and-tensorboard.md` | Shape, NaN, leakage, wrong device + histograms | Data leakage is caught by a one-line set intersection; TensorBoard histograms show vanishing vs exploding gradients. |
| `05-pdb-crossentropy-and-linear-layers.md` | Exercise 5 follow-up: pdb from zero, CE loss shapes, Linear internals | `outputs [16,2]` vs `labels [16]` is correct — CE indexes, doesn't compare; PyTorch stores weights `(out, in)` with rows as neurons. |

## Session facts

- Date: 2026-10-28
- Lesson: Phase 0 · 12 — Debugging & Profiling
- Warm-up recall: 2/2 (carried over from Phase 0 · 11 — `chmod +x` for execute permission, `du -h --max-depth=1` for disk hogs)
- Quiz score: 3/3
- Exercises: all five worked in follow-up sessions (debug_tools.py NaN injection via custom module, cProfile finding `slow_data_augment` at 85% of loop time, tracemalloc 4-snapshot diff proving line 5 freed pre-snapshot, TensorBoard overfit run with val loss rising since epoch 15, pdb drill on exercise5_pdb.py)
- Learner decisions: requested confirmation before `uv pip install tensorboard`; asked for a step-by-step pdb walkthrough (zero prior debugger experience)

## Stumbles worth re-reading

- Confirmed the fix for "data loading = 60% of step time" is `num_workers > 0` (a code fix), not a faster GPU — but initially framed it as "reducing data loading time" rather than recognizing the GPU was idle/starved.
- Asked how `add_histogram` actually works rather than treating it as a black box — the binning + stacked-across-steps mental model was what made vanishing/exploding gradients legible.
- Sharpened the phrase "upstream/downstream" — in gradient flow (loss → layer1 → layer5), layer 1 is *downstream* of layer 5, so say "furthest from the loss" instead of relying on layer numbers.
- Exercise 5 follow-ups (see `05-pdb-crossentropy-and-linear-layers.md`): pdb scope lesson (`p x.shape` → NameError because `x` lives in `main()`, not the paused frame); read `[32, 8]` as "32 features, 8 neurons" before correcting to rows=neurons; correctly recognized their textbook `x @ W` training as convention A vs PyTorch's `(out, in)`; initially expected the 10-classes/2-labels case to crash — it didn't (labels 0/1 are valid indexes), while the reverse case does (`IndexError: Target 3 is out of bounds`).

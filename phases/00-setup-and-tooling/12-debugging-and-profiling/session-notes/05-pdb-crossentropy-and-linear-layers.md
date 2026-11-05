# Exercise 5 Follow-up: pdb, CrossEntropyLoss Shapes, and Linear-Layer Internals

## The problem

Exercise 5 opened a longer conversation: how a debugger actually works, why `outputs` is `[16, 2]`
while `labels` is `[16]` yet the loss computes, and what the weight matrix of `nn.Linear(8, 32)`
really represents. This note records that discussion and the live-verified answers.

## pdb from zero — the mental model

A debugger runs your program but can **pause it at a chosen line** (a breakpoint) while it is alive
mid-execution. `pdb` is Python's built-in debugger; `breakpoint()` is the statement that says
"pause here". Exercise 5 places it deliberately in the gap between `loss.backward()` and
`optimizer.step()` — the exact window where gradients are live and the most bugs live.

```python
loss.backward()   # computes gradients, stores them in .grad
breakpoint()      # <- PAUSE HERE, gradients are live
optimizer.step()  # only runs after you type 'c'
```

Running it with uv (uses the project `.venv` automatically):

```bash
uv run python -m pdb phases/00-setup-and-tooling/12-debugging-and-profiling/code/exercise5_pdb.py
```

Essential pdb commands:

| Command | Does |
|---|---|
| `c` | continue until the next `breakpoint()` |
| `p <expr>` | print any expression's value |
| `l` / `ll` | list source around the current line |
| `n` / `s` | next line / step into functions |
| `w` | show the call stack |
| `q` | quit the run |

## The scope lesson (live-verified stumble)

Pausing inside `train_step()` and typing `p x.shape` produced
`*** NameError: name 'x' is not defined` — because `x` lives in `main()`, a different frame.
A debugger shows **the frame you are standing in**. `p inputs.shape`, `p inputs.device` and
`p model[0].weight.grad` all worked because those are `train_step()`'s locals.

## CrossEntropyLoss: `[16, 2]` vs `[16]` is correct, not a bug

```text
outputs: [16, 2]  -> per sample, one score per class (logits)
labels:  [16]     -> per sample, ONE number: the index of the correct class
```

`labels` is an index, not a score. Mechanism per sample: softmax the 2 logits, pick the
probability at the label's index, take `-log(...)`; the loss averages over the batch.
Example: logits `[0.2, 1.5]`, label `1` → probs `[0.31, 0.69]` → loss `-log(0.69) ≈ 0.37`.

Two live-verified follow-ups that came out of this:

| Variant | Result | Why |
|---|---|---|
| last layer `Linear(32, 10)`, labels 0–1 | no crash, loss ≈ 1.99 | labels 0/1 are valid indexes; classes 2–9 are dead weight. Baseline loss of a fresh K-class model is `ln(K)` (ln(10) ≈ 2.30, ln(2) ≈ 0.69 — the exercise started near 0.73) |
| last layer `Linear(32, 2)`, labels 0–9 | **crash** | `IndexError: Target 3 is out of bounds.` — label 3 indexes column 3 of a row that only has 2 columns |

**The rule**: CrossEntropyLoss never compares shapes — it *indexes*. The only hard constraint is
`0 <= label < out_features`. Whether the task is sensible (last layer size == label range == same
classification task) is something PyTorch cannot check for you.

## What a neuron is, and the weight matrix

One neuron of `nn.Linear(8, 32)`: `z = w·x + b` — it owns 8 weights + 1 bias and produces one
scalar. The layer is 32 such neurons sharing the same 8 inputs. Stacking their weight vectors as
rows gives exactly the stored `0.weight (32, 8)`; the whole layer collapses to `Z = XW^T + b`.

Live verification (manual math vs PyTorch, seed 0):

```console
$ uv run python  # layer = nn.Linear(8, 32); x = torch.randn(16, 8)
PyTorch layer(x) shape:       (16, 32)
Manual  x @ W.T + b shape:    (16, 32)
Max difference between them: 2.384185791015625e-07
Neuron 7 via row dot product: 0.052902594208717346
Neuron 7 via z_torch[0, 7]:   0.05290259048342705
```

Neuron 7 = **row 7** of the weight matrix dotted with the sample, plus `b[7]` — matching
`z_torch[0, 7]` exactly.

## The two storage conventions (both correct)

| Convention | Storage | Forward | Used by |
|---|---|---|---|
| A: `x @ W` | `(in, out)` — columns are neurons | no transpose | textbooks, from-scratch numpy |
| B: PyTorch | `(out, in)` — **rows are neurons** | `x @ W.T` | `nn.Linear` |

They are transposes of each other; being fluent at translating is the skill. The sanity rule:
`nn.Linear(in, out) → weight (out, in), bias (out,)` — the bias shape always pins down which axis
is the neurons.

Stumble from the session: the learner initially read `[32, 8]` as "32 features, 8 neurons" and
then correctly recognized their own `x @ W` training as convention A. Correction to remember:
in PyTorch storage, each **row** is one neuron with 8 weights (one per input feature).

## The interface contract and the chaining rule

`nn.Linear(8, 32)` means: **expects input with 8 features, returns output with 32 features**.
Constructor args describe the data flow, not the matrix orientation. Batch dims pass through
untouched; only the last dim changes.

Chaining rule, live-verified by breaking it:

```console
$ model = nn.Sequential(nn.Linear(8, 32), nn.ReLU(), nn.Linear(64, 2))
$ model(x)   # x: (16, 8)
RuntimeError: mat1 and mat2 shapes cannot be multiplied (16x32 and 64x2)
```

The error names the failing matmul: `mat1 = 16x32` (data arriving) vs `mat2 = 64x2`
(the layer's stored weight transposed); inner dims must cancel. It fails at **forward time**,
not at construction — PyTorch cannot know the data flow until execution.

## Parameter audit (each number derivable)

| Name | Shape | Count | Derivation |
|---|---|---|---|
| `0.weight` | (32, 8) | 256 | 32 outputs × 8 inputs |
| `0.bias` | (32,) | 32 | one bias per neuron |
| `2.weight` | (2, 32) | 64 | 2 outputs × 32 inputs |
| `2.bias` | (2,) | 2 | one per neuron |
| Total | | **354** | `(8·32+32) + (32·2+2)` |

Formula per Linear layer: `(in × out) + out` (the `+out` is the bias). No index `1.weight`
exists because `nn.ReLU()` at index 1 has no parameters. Every `.grad` has the same shape as its
parameter; before `backward()` it is `None`, not zero. One-liner for real models:
`sum(p.numel() for p in model.parameters())`.

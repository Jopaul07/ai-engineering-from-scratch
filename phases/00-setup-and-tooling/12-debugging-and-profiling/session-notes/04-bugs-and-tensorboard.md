# The Four Classic AI Bugs and TensorBoard Histograms

## Bug: NaN loss — symptom vs source

NaN means something exploded. Common causes: learning rate too high, division by zero in a custom loss, `log(0)`, or exploding gradients in RNNs.

```python
def detect_nan(model, loss, step):
    if torch.isnan(loss):
        print(f"NaN loss at step {step}")
        for name, param in model.named_parameters():
            if param.grad is not None:
                if torch.isnan(param.grad).any():
                    print(f"  NaN gradient in {name}")
                if torch.isinf(param.grad).any():
                    print(f"  Inf gradient in {name}")
```

Once you *know* loss is NaN, this walks the parameters and tells you exactly which layer's gradient went bad. Options like switching optimizers or restarting with a different seed are "guess and restart" moves that treat the symptom, not the cause.

## Bug: data leakage — 99% accuracy is a bug

A model scoring 99% on the test set sounds great. It's a bug. The confirmation is a **set intersection**:

```python
def check_data_leakage(train_set, test_set, id_column="id"):
    train_ids = set(train_set[id_column].tolist())
    test_ids = set(test_set[id_column].tolist())
    overlap = train_ids & test_ids
    if overlap:
        print(f"DATA LEAKAGE: {len(overlap)} samples in both train and test")
        return True
    return False
```

One line catches the disaster. Also watch for **temporal leakage**: using future data to predict the past. Sort by timestamp before splitting.

**Caveat worth remembering**: an `id` column only catches *identity* leakage. Two rows can have different IDs but be near-duplicates (same image cropped twice, same patient appearing twice) — real pipelines also need temporal splits and fuzzy-match checks. For a first-line test, ID intersection catches the most common disaster.

## TensorBoard — watching training over time

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/experiment_1")

for step in range(num_steps):
    loss = train_step(model, batch)

    writer.add_scalar("loss/train", loss.item(), step)
    writer.add_scalar("lr", optimizer.param_groups[0]["lr"], step)

    if step % 100 == 0:
        for name, param in model.named_parameters():
            writer.add_histogram(f"weights/{name}", param, step)
            if param.grad is not None:
                writer.add_histogram(f"grads/{name}", param.grad, step)

writer.close()
```

Launch with `tensorboard --logdir=runs`.

### Reading the scalars

| Signal | Diagnosis |
|---|---|
| Loss not decreasing | LR too low, or architecture issue |
| Loss oscillating wildly | LR too high |
| Train loss ↓, val loss ↑ | Overfitting |
| Loss goes to NaN | Numerical instability |

### Reading the histograms — what `add_histogram` actually does

A weight tensor like `fc1.weight` of shape `[256, 128]` is 32,768 individual numbers; a scalar loss tells you nothing about them. The histogram answers: **at step N, what is the distribution of these values?**

Mechanically it's just binning:

```python
# simplified — what add_histogram does under the hood:
counts, bin_edges = np.histogram(fc1.weight.detach().cpu().numpy(), bins=30)
# -> "at step 5000, 400 values in [-0.02, -0.01), 610 in [-0.01, 0.0), ..."
```

TensorBoard then stacks these distributions across steps — a scrolling 3D view where each slice is "the distribution of this layer's weights at step N." The story is in how the shape *moves*.

| Pattern | Meaning |
|---|---|
| Gradients pile up in the bin at exactly 0, weights barely change | **Vanishing gradients** — signal died before reaching this layer |
| Gradient histogram spreads ever wider / spikes to huge magnitudes | **Exploding gradients** — needs clipping |
| Weights march steadily away from init, gradients healthy and symmetric around 0 | **Healthy training** |
| A layer's histogram freezes after step ~200 while later layers keep moving | **Dead layer** (dead ReLUs, or a broken skip connection) |
| Gradients become asymmetrically lopsided | One-sided signal flow, often a masking or padding bug |

### The "upstream vs downstream" trap

In the forward pass, data flows input → layer1 → layer5 → output. But **gradients flow backward** — loss → layer5 → layer1. So layer 1 is *downstream* of layer 5 in gradient flow, even though it's upstream in data flow.

If layer 1's gradient histogram collapses while layer 5's looks fine, the signal died *between the loss and layer 1*. In team conversations, say "furthest from the loss" or "nearest to the loss" — that's unambiguous regardless of layer numbering.

### Vanishing vs exploding — different fixes

**Gradient clipping caps the *max* norm — it can only shrink gradients, so it's useless for vanishing gradients.** It's an exploding-gradient tool only.

| Problem | Fixes |
|---|---|
| Vanishing gradients | Residual/skip connections; ReLU/GELU instead of sigmoid/tanh (sigmoid's derivative maxes at 0.25 — multiply a few and the gradient vanishes); BatchNorm/LayerNorm; He/Xavier init; LSTM/GRU gates for RNNs |
| Exploding gradients | Gradient clipping; lower learning rate |

Two habits that make histograms usable:

1. **Compare early layers vs late layers.** Vanishing gradients show up *first* in layers furthest from the loss. If layer 1's gradient histogram is collapsing while layer 10's looks fine, you've localized the problem.
2. **Log every ~100 steps, not every step.** Histograms are expensive to compute and store; every step just adds noise and slows the run.

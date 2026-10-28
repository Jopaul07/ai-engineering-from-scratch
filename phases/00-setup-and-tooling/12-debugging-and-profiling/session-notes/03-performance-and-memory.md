# Performance and Memory Profiling

## Timing sections — know where time goes first

The simplest profiling tool is a context-manager timer:

```python
import time

class Timer:
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start
        print(f"[{self.name}] {elapsed:.4f}s")

with Timer("data loading"):
    batch = next(dataloader_iter)

with Timer("forward pass"):
    outputs = model(batch)

with Timer("backward pass"):
    loss.backward()
```

**Why `perf_counter` and not `time.time`**: `time.time()` can jump when the system clock syncs (NTP adjust). `perf_counter()` is monotonic — it only ever moves forward — so durations are always real.

## The classic finding: data loading dominates

Session-verified example split:

```text
[data loading] 0.4200s
[forward pass] 0.0800s
[backward pass] 0.1500s
```

Data loading is 60%+ of the step time. **The fix is `num_workers > 0` in your DataLoader, not a faster GPU.** This is a *code* fix, not a hardware fix — the GPU is starving at 60% idle waiting for batches, and buying a faster GPU makes the starvation *more* expensive. Parallel workers prefetch the next batch while the GPU crunches the current one.

## cProfile first, then line_profiler

Manual timers are for the three phases you already know. When you *don't* know where time goes:

```bash
python -m cProfile -s cumtime train.py
```

Reports total calls, self-time, and **cumulative time** (which includes callees), so the top rows show the big branches of the call tree.

For line-by-line resolution, `line_profiler`:

```python
@profile
def train_step(model, data, target):
    output = model(data)
    loss = F.cross_entropy(output, target)
    loss.backward()
    return loss
```

```bash
kernprof -l -v train.py
```

The workflow: **cProfile first** to find the hot function, then **line_profiler** on that one function to find the hot line. Don't start with line-level profiling — on a 200-line script it's noise.

## CPU memory — `tracemalloc` (stdlib, always available)

```python
import tracemalloc

tracemalloc.start()

model = build_model()
data = load_dataset()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)
```

The snapshot reports allocations grouped by source line — the top line is your memory hog.

## GPU memory and the OOM ladder

```python
print(torch.cuda.memory_allocated() / 1e9)  # actually in use
print(torch.cuda.memory_reserved() / 1e9)   # cached by the allocator
```

When you hit OOM, the fix order (cheapest first, most invasive last):

| Order | Fix | Cost |
|---|---|---|
| 1 | Reduce batch size | One-line change; always first |
| 2 | `torch.cuda.empty_cache()` | Free |
| 3 | `del tensor` + `empty_cache()` for large intermediates | Small code change |
| 4 | Mixed precision (`torch.cuda.amp`) | Big win, halves memory |
| 5 | Gradient checkpointing | Last resort — trades recompute for memory, costs ~30% extra time |

Session-confirmed: batch size first (cheapest, one line), gradient checkpointing last (recompute tax), and the middle order is `empty_cache` (free) before mixed precision (the big win before paying the checkpointing tax).

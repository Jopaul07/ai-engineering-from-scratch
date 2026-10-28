# Conditional Breakpoints, Logging, and the Interactive Debugger

## Conditional `breakpoint()` — stop only when something looks wrong

An unconditional breakpoint in a 10,000-step training run means pressing `c` 10,000 times. Condition it on failure signals instead:

```python
def training_step(model, batch, criterion, optimizer):
    inputs, labels = batch
    outputs = model(inputs)
    loss = criterion(outputs, labels)

    if loss.item() > 100 or torch.isnan(loss):
        breakpoint()

    loss.backward()
    optimizer.step()
```

Once dropped into the debugger, useful commands:

| Command | Purpose |
|---|---|
| `p outputs.shape` | check shapes |
| `p loss.item()` | see the loss value |
| `p torch.isnan(outputs).sum()` | count NaNs |
| `p model.fc1.weight.grad` | check gradients |
| `c` / `q` | continue / quit |

## Where was the NaN born?

The NaN in the loss is a *symptom*, not the source. At step 2000 with `loss = NaN`, inspect in order:

1. `p torch.isnan(outputs).sum()` — did the NaN appear in the **forward pass**? (division by zero, `log(0)` in a custom loss)
2. `p model.fc1.weight.grad` — were the **gradients** already NaN/Inf from the *previous* step? (exploding gradients poisoning the update)
3. `p inputs.min()` — did a zero or negative value sneak into the batch that a `log()` or division chokes on?

If outputs are clean but grads are NaN, the explosion happened *upstream in time* — a gradient-clipping problem. If outputs are NaN, it's a forward-pass numerical bug.

## Logging over print — severity levels are a runtime filter

Prints are for the moment of debugging. **Logging** is for when the run fails at 3 AM and the terminal output scrolled off screen:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Starting training: lr=%.4f, batch_size=%d", lr, batch_size)
logger.warning("Loss spike detected: %.4f at step %d", loss.item(), step)
logger.error("NaN loss at step %d, stopping", step)
```

**Stumble from this session**: when asked how to see *only* spikes in a long run, the first instinct was "comment out the `logger.info` line." That works but is blunt — you lose the info trail and must remember to un-comment. The cleaner move is to change the *threshold*:

```python
logging.basicConfig(level=logging.WARNING, ...)
```

`INFO` messages are silently swallowed, `WARNING` and above pass through — no code edits, and you can flip it back with one word. Severity levels are a runtime filter, not a code change.

## VS Code debugger (the interactive version)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Training",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

The key flag is `"justMyCode": false` — without it, you cannot step *into* library code like PyTorch's `cross_entropy` or a DataLoader worker. Gutter breakpoints, the Variables pane, and the Debug Console (arbitrary Python expressions mid-execution) are faster than pdb for stepping through preprocessing pipelines.

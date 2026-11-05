# Silent Failures and Tensor Inspection

## The problem

A web app crashes with a stack trace. A misconfigured training loop runs for 8 hours, burns $200 in GPU time, and produces a model that predicts the mean of every input — *without ever raising an error*. The culprit was a tensor on the wrong device, a forgotten `.detach()`, or labels leaking into features.

## The three-level pyramid

```text
Level 3 — Training dynamics: loss curves, gradient norms, activations
Level 2 — Tensor operations: shapes, dtypes, devices, NaN/Inf values
Level 1 — Standard Python: breakpoints, logging, profiling, memory
```

Most people jump straight to Level 3 (staring at TensorBoard). But **80% of AI bugs live at Levels 1 and 2** — so that's where inspection effort goes first.

## One helper that catches three bug patterns

```python
def debug_print(name, tensor):
    print(f"{name}: shape={tensor.shape}, dtype={tensor.dtype}, "
          f"device={tensor.device}, "
          f"min={tensor.min().item():.4f}, max={tensor.max().item():.4f}, "
          f"mean={tensor.mean().item():.4f}, "
          f"has_nan={tensor.isnan().any().item()}")
```

One call prints everything a debugger makes you inspect one-at-a-time. Call it after every suspicious operation; remove prints once the bug is found.

`has_nan=True` is the field that catches silent NaN early — a model whose loss went NaN at step 2000 but wasn't noticed until the curve was checked hours later would have been caught instantly with this one boolean.

## Why shape mismatch is the most frequent bug

A tensor has shape `[batch, features]` when the model expects `[batch, channels, height, width]`. Catch it *before* training by registering a **forward hook** on every module and recording the shape transformation:

```python
def check_shapes(model, sample_input):
    print(f"Input: {sample_input.shape}")
    hooks = []

    def make_hook(name):
        def hook(module, inp, out):
            in_shape = inp[0].shape if isinstance(inp, tuple) else inp.shape
            out_shape = out.shape if hasattr(out, "shape") else type(out)
            print(f"  {name}: {in_shape} -> {out_shape}")
        return hook

    for name, module in model.named_modules():
        hooks.append(module.register_forward_hook(make_hook(name)))

    with torch.no_grad():
        model(sample_input)

    for h in hooks:
        h.remove()
```

Run once with a sample batch to print the entire shape map (`fc1: [32, 784] -> [32, 128]`). Note `h.remove()` — hooks are persistent, so without removal they keep firing and slow training down.

## Wrong device: silent slowness

Tensors on different devices cause runtime errors — but sometimes a tensor silently stays on CPU while everything else is on GPU, and training just runs *slowly* instead of erroring.

```python
def check_devices(model, *tensors):
    model_device = next(model.parameters()).device
    print(f"Model device: {model_device}")
    for i, t in enumerate(tensors):
        if t.device != model_device:
            print(f"  WARNING: tensor {i} on {t.device}, model on {model_device}")
```

`next(model.parameters()).device` is the standard idiom for asking "where does the model live?"

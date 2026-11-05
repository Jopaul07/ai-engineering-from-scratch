# Redirects, Streams, and the Three Wires

> Why `2>&1` works, why its position matters, and what `&` actually means.

## The model: three numbered wires

Every process is born with three open file descriptors (fds):

| fd | Name | Direction |
|----|------|-----------|
| 0 | stdin | input coming in |
| 1 | stdout | normal output going out |
| 2 | stderr | error messages going out |

By default both 1 and 2 lead to your screen. An fd is just a wire with a number — nothing mystical.

## The redirect symbols

| Symbol | Meaning |
|--------|---------|
| `> file` | re-plug wire 1 into a file (overwrite) |
| `>> file` | re-plug wire 1 into a file (append) |
| `2> file` | re-plug wire 2 into a file |
| `2>&1` | re-plug wire 2 into *whatever socket wire 1 currently uses* |
| `\|` | wire one command's stdout into the next command's stdin |

**The `&` in `2>&1` means "the next token is an fd number, not a filename."** Without it, `2>1` creates a junk file literally named `1`. Verified live in session:

```console
$ python3 -c "print('ERR', file=sys.stderr)" 2>1
$ ls        # → a file named '1' now exists, containing the error
```

## Order matters — the proven bug

The shell processes redirects **left to right**:

```bash
python train.py > output.log 2>&1   # correct: stdout→file first, then stderr follows
python train.py 2>&1 > output.log   # broken: stderr follows stdout's ORIGINAL target (screen)
```

Live demo output from the session — the broken order leaks errors to the screen:

```console
--- correct order, file contains:
ERR: CUDA out of memory
OUT: epoch 1 loss 0.5201

--- wrong order, file contains:
OUT: epoch 1 loss 0.5201        # ERR went to the screen instead
```

This is the "where did my errors go?" mystery at 2am. The mnemonic: `2>&1` means "point wire 2 where wire 1 points **right now**."

## The three meanings of `&` — disambiguated

| Syntax | Meaning |
|--------|---------|
| `2>&1` | "next is an fd number" (redirect context) |
| `sleep 1 &` | run in background (end of command) |
| `cmd1 && cmd2` | run cmd2 only if cmd1 succeeded |

## Practical takeaway

The one command you'll type for every training run:

```bash
python train.py > train.log 2>&1
```

Both normal output and errors captured in one file, in the correct order.

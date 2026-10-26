# Background Jobs and tmux

> Why closing a terminal kills your training, and the three escape hatches ranked.

## The problem: SIGHUP

When a terminal closes, the shell sends **SIGHUP** to its child processes — and they die by default. Your 12-hour training run, gone because you closed a laptop.

The session proved the ancestry live: `launchd → Ghostty → login → zsh → opencode → zsh` — every link in that chain dies together on hangup. `htop` (F5, tree view) shows this same tree visually on your own machine.

## The three escape hatches

| Method | Survives terminal close? | Can reattach and see live output? |
|--------|--------------------------|-----------------------------------|
| `command &` | No | No |
| `nohup command &` | Yes | No — check the log file |
| `tmux` | Yes | **Yes** — plus multiple panes |

Rule of thumb: anything longer than a few minutes → tmux.

```bash
nohup python train.py > train.log 2>&1 &   # the nohup form
tmux new -s train                          # the tmux form
```

## tmux: the complete working vocabulary

One prefix key (`Ctrl+B`) plus a letter:

| Keys | Effect |
|------|--------|
| `tmux new -s train` | new named session |
| `Ctrl+B` then `"` | split pane horizontally |
| `Ctrl+B` then `%` | split pane vertically |
| `Ctrl+B` then arrows | move between panes |
| `Ctrl+B` then `d` | **detach** — session keeps running |
| `tmux attach -t train` | reattach |
| `tmux ls` | list sessions |
| `tmux kill-session -t train` | kill everything in the session at once |

## What the session actually verified (Exercise 1)

Three panes: `htop`, `watch -n1 date`, a Python ticker. After `Ctrl+B d`:

```console
$ tmux ls
practice: 1 windows (created Sat Oct 24 19:53:30 2026)
```

— confirmed **from an independent shell**, proving the session lives outside any one terminal. Reattach brought all three panes back exactly as left, ticker still ticking.

## The mental model

tmux's *server process* owns your programs; terminals are disposable viewers. Detaching kills the viewer, not the session. The session lives on the **remote machine** when you SSH — so it does not matter which laptop you reattach from tomorrow.

## The canonical AI workflow

Pane 1: `python train.py` · Pane 2: `watch -n1 nvidia-smi` · Pane 3: `tail -f logs/train.log | grep --line-buffered loss` — then detach and go home. The repo's `shell_aliases.sh` automates this exact layout with `trainenv`.

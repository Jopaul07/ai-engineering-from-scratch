# Pipelines in Practice

> Composing `grep`, `awk`, `wc`, and friends into one-line data tools.

## The core idea

A pipeline is one dataflow, not several commands. Each program reads stdin and writes stdout; `|` wires them together. Tools that know nothing about each other compose freely.

```bash
grep "loss:" train.log | awk '{print $NF}' > losses.txt
#      └─ filter            └─ extract      └─ write to file
```

- **pipe `|`** — stdout of one command → stdin of the *next command*
- **redirect `>`** — stdout → a *file*
- They chain freely: pipes between tools, redirect at the end.

## The worked example (built live in session)

Generated a 100-epoch fake log, then:

```console
$ for i in $(seq 1 100); do echo "epoch $i loss: $(echo "scale=4; 1/$i" | bc)"; sleep 0.1; done > fake_train.log
$ grep loss fake_train.log | awk '{print $NF}' > losses.txt
$ wc -l losses.txt
     100 losses.txt
$ head -3 losses.txt
1.0000
.5000
.3333
```

Key details worth remembering:

- **`$NF`** in awk = the *last* field of the line (NF = number of fields; `$NF` indexes it).
- **`$(...)`** is command substitution — run a command, use its output as text.
- The loss values decreased because `1/i` is monotonic — a well-behaved training run.

## Debugging a pipeline: test stages separately

If the final output looks wrong, do not stare at the whole pipeline. Break it:

```bash
grep loss fake_train.log | head -3        # does stage 1 emit what you expect?
grep loss fake_train.log | awk '{print $NF}' | head -3   # now add stage 2
```

Same instinct as `tail -5 fake_train.log` before filtering: **inspect the format first**, then trust the filter.

## The self-matching grep trap

```bash
ps aux | grep python        # matches your own grep process too
ps aux | grep -v grep | grep -i python   # drop it, then filter
```

`grep -v` inverts the match. You will use this exact idiom forever.

## Patterns that recur in AI work

```bash
cat train.log | grep "loss" | wc -l                       # count occurrences
tail -f train.log | grep --line-buffered "ERROR"          # live error watch
grep "final_accuracy" results/*.log | sort -t= -k2 -n -r  # rank experiments
find . -name "*.pt" | xargs du -h | sort -rh | head -20   # biggest checkpoints
```

`--line-buffered` matters: grep normally buffers output in blocks, which makes live `tail -f` watches feel broken.

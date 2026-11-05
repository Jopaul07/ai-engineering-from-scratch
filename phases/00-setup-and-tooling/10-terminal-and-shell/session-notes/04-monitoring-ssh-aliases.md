# Monitoring, SSH, and Process-Local State

> Watching your machine, reaching remote boxes, and why `source` beats `bash` for config.

## Monitoring: two different questions

*"Is my GPU busy?"* and *"what's eating my RAM/disk?"* are different tools:

| Tool | Answers | Notes |
|------|---------|-------|
| `htop` | CPU/RAM per process | `F6` sort by memory → find leaks; `F9` kill; `F5` tree view |
| `nvidia-smi` | GPU util, VRAM, temperature | one-shot snapshot |
| `watch -n1 nvidia-smi` | same, every second | the classic tmux pane-2 command |
| `df -h` / `du -sh *` | disk free / folder sizes | datasets fill disks fast — the session saw `200Gi free of 460Gi` |

macOS note: `htop` and `watch` are not preinstalled; `brew install htop watch` (done in session).

## SSH: the system-level model

Client and server halves, four handshake steps: connect → server proves itself (checked against `known_hosts`) → you prove yourself by signing a challenge with your **private key** (the key never crosses the wire) → server checks your public key against `authorized_keys`.

What lives in `~/.ssh`:

| File | Role | Why permissions matter |
|------|------|------------------------|
| `id_ed25519` | private key | ssh **refuses** world-readable private keys |
| `id_ed25519.pub` | public half | freely copyable to servers |
| `known_hosts` | trusted server fingerprints | change = possible man-in-the-middle warning |
| `config` | nickname database (client-side only) | `chmod 600` |
| `agent/` | `ssh-agent` socket — keys held in memory | type passphrase once per boot |

Debugging tools: `ssh -G <alias>` prints the fully resolved config without connecting (config files fail silently — a two-space indent typo and your block is ignored); `ssh -v` narrates every handshake decision; `ssh-keygen -R <ip>` forgets a dead cloud box.

## The config alias (Exercise 4, done and verified)

```text
Host gpu
    HostName localhost
    User jopauljnelluvely
    IdentityFile ~/.ssh/id_ed25519
```

Verified: `ssh -G gpu` resolved `hostname localhost`, `user jopauljnelluvely`, `identityfile ~/.ssh/id_ed25519`.

Why it matters: every SSH tool accepts the alias — `ssh gpu`, `scp results.csv gpu:~/`, `rsync -avz ./data/ gpu:~/data/`, `ssh -L 8888:localhost:8888 gpu`. One config block, no memorized IPs.

**Port forwarding:** `-L local_port:localhost:remote_port` — left of the colon is *your laptop's* port; the right side is the destination *as seen from the remote box*. A service that only listens remotely (Jupyter 8888, TensorBoard 6006) appears in your local browser.

## `source` vs `bash` — the sneakiest lesson of the session

```console
$ bash shell_aliases.sh   # exit 0, feels successful... then: gpu not found
$ source shell_aliases.sh # gpu is an alias for nvidia-smi ...
```

`bash script.sh` spawns a **child process**: it defines all 40 aliases in its own memory, exits, and the memory evaporates. `source` executes the file **inside your current shell** — no process boundary, definitions stick.

Generalization: nothing crosses a process boundary — not signals to parents (SIGHUP cascades *down*), not definitions to parents. And non-interactive shells (`zsh -c ...`) do not even read `~/.zshrc` at startup; only interactive shells do.

**Trust ritual before appending anything to `~/.zshrc`** (it runs in every future shell):

```bash
zsh -n script.sh                  # syntax check, no execution
zsh -c "source script.sh && type ta"   # trial-load in a disposable child
cp ~/.zshrc ~/.zshrc.bak-$(date +%m%d) # backup, then append with >>
```

The child-shell trial load *is* the earlier `bash` mistake, deliberately weaponized as a sandbox.

## Aliases vs functions

- `alias ta='tmux attach -t'` — fixed text, no arguments.
- `killtrain() { ... }` — a function takes `$1`, so you choose the pattern.
- Rule: no arguments → alias; needs arguments → function.
- Safety note from the alias file: `killtraining` uses `pkill -f "python.*train"`, which matches any command line containing that pattern — including unrelated scripts with "train" in the name.

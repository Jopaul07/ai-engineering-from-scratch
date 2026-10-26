# Terminal & Shell — Session Notes (Index)

> Exported live-tutoring session for Phase 0, Lesson 10. Four topic files + this index.

## Contents

| File | Topic | Core takeaway |
|------|-------|---------------|
| [01-redirects-and-streams.md](01-redirects-and-streams.md) | fd, `>`, `2>&1`, `&`, ordering bugs | Every process has 3 numbered wires; redirects re-plug them left to right |
| [02-pipelines-in-practice.md](02-pipelines-in-practice.md) | `grep`/`awk`/`wc`, log processing | Pipes wire stdout to stdin; test each stage separately |
| [03-background-and-tmux.md](03-background-and-tmux.md) | SIGHUP, `&`, `nohup`, tmux | tmux owns your processes; the terminal is just a viewer |
| [04-monitoring-ssh-aliases.md](04-monitoring-ssh-aliases.md) | htop, SSH config, port forwarding, `source` vs `bash` | Config is client-side; aliases live in process memory |

## Session facts

- Quiz: 3/3 post-questions correct (2026-10-26)
- All 4 lesson exercises completed and verified live, including tmux detach/reattach confirmed from an independent shell
- Learner declined the live Remote Login (sshd) test for security reasons — sound call; the skill was the deliverable
- Two stumbles, both resolved by live demos: `2>&1` ordering, and the two meanings of `&`

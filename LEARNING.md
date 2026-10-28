# My AI Engineering Path
<!-- Managed by the ai-engineering-from-scratch learning skills.
     Repo: https://github.com/rohitg00/ai-engineering-from-scratch -->

## Mission

Complete the Software Engineering Fundamentals path. Practical end goal not yet recorded.

## Placement

- Date: 2026-10-22
- Score: self-selected
- Entry point: Phase 0: Setup & Tooling
- Pace: not yet recorded

## Path

| Phase | Name | Status | Est. hours |
|---|---|---|---|
| 0 | Setup & Tooling | Do | 16 |
| 1 | Math Foundations | Skip | 23 |
| 2 | ML Fundamentals | Skip | 26 |
| 3 | Deep Learning Core | Skip | 15 |
| 4 | Computer Vision | Skip | 27 |
| 5 | NLP — Foundations to Advanced | Skip | 30 |
| 6 | Speech & Audio | Skip | 18 |
| 7 | Transformers Deep Dive | Skip | 14 |
| 8 | Generative AI | Skip | 14 |
| 9 | Reinforcement Learning | Skip | 13 |
| 10 | LLMs from Scratch | Skip | 26 |
| 11 | LLM Engineering | Skip | 19 |
| 12 | Multimodal AI | Skip | 65 |
| 13 | Tools & Protocols | Do | 76 |
| 14 | Agent Engineering | Do | 55 |
| 15 | Autonomous Systems | Skip | 20 |
| 16 | Multi-Agent & Swarms | Skip | 28 |
| 17 | Infrastructure & Production | Do | 34 |
| 18 | Ethics, Safety & Alignment | Skip | 31 |
| 19 | Capstone Projects | Skip | 620 |

## Focused path

Software Engineering Fundamentals (`learning-paths/software-engineering-fundamentals.json`):

| # | Lesson | Status |
|---|---|---|
| 1 | Phase 0 · 01 — Dev Environment | Complete (learner-reported) |
| 2 | Phase 0 · 02 — Git & Collaboration | Complete (learner-reported) |
| 3 | Phase 0 · 06 — Python Environments | Complete (learner-reported) |
| 4 | Phase 0 · 07 — Docker for AI | Complete (learner-reported) |
| 5 | Phase 0 · 09 — Data Management | Complete |
| 6 | Phase 0 · 10 — Terminal & Shell | Complete |
| 7 | Phase 0 · 12 — Debugging & Profiling | Complete |
| 8 | Phase 13 · 01 — The Tool Interface | Pending |
| 9 | Phase 13 · 05 — Tool Schema Design | Pending |
| 10 | Phase 14 · 38 — Verification Gates | Pending |
| 11 | Phase 17 · 20 — Shadow, Canary, Progressive | Pending |
| 12 | Phase 17 · 25 — Security, Secrets & Audit | Pending |
| 13 | Phase 17 · 23 — SRE for AI | Pending |

## Progress log

| Date | Lesson | Quiz | Note |
|------|--------|------|------|
| 2026-10-22 | Phase 0 · 01 — Dev Environment | — | Learner-reported complete. |
| 2026-10-22 | Phase 0 · 02 — Git & Collaboration | — | Learner-reported complete. |
| 2026-10-22 | Phase 0 · 06 — Python Environments | — | Learner-reported complete. |
| 2026-10-22 | Phase 0 · 07 — Docker for AI | — | Learner-reported complete. |
| 2026-10-22 | Phase 0 · 09 — Data Management | 3/3 | Solid on streaming (knew IterableDataset has no len()). Ran all code live via root .venv; needed `uv pip install --python .venv/bin/python datasets`. |
| 2026-10-24 | Phase 0 · 10 — Terminal & Shell | 3/3 | Stumbled on fd/redirect semantics (`2>&1`) at first — live wrong-order demo made it click. Mixed up the two meanings of `&`; proved both with `2>1` junk-file demo. |
| 2026-10-26 | Phase 0 · 10 — Terminal & Shell exercises | — | All 4 done: tmux 3-pane detach/reattach verified live via `tmux ls`; aliases appended to ~/.zshrc after zsh -n + child-shell trial-load; 100-epoch grep/awk pipeline solo (100 lines, decreasing); ~/.ssh/config written + verified via `ssh -G gpu`. Learner declined live Remote Login test for security reasons — correct call. Key insight gained: `bash script.sh` vs `source` (child process vs same-process state). |
| 2026-10-26 | Phase 0 · 11 — Linux for AI | 5/5 | Exercises done locally (tmux detach/reattach, df/du cache audit, htop mem sort). Quiz clean on first pass: ~ home, sudo, chmod +x, du/sort for disk hogs, macOS vs GNU sed -i gotcha. |
| 2026-10-28 | Phase 0 · 12 — Debugging & Profiling | 3/3 | Strong instincts: picked data-leakage + set-intersection confirm unprompted; knew clipping is for exploding not vanishing. Sharpened: gradient flows loss→layer1, so "furthest from the loss" is the unambiguous phrasing. logging level-toggle over commenting out. |

## Review queue

Empty for now.

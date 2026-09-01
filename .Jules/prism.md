## 2023-10-27 - Suppressing Unhelpful Stderr
**Learning:** In bash scripts, utility commands that are expected to fail gracefully (like checking for an active WM process, e.g. `i3-msg restart` when `i3` isn't running) often spew unhandled "command not found" or "connection refused" errors to stderr. This breaks the console UX and causes user alarm even if the script successfully ignores the error (`|| true`).
**Action:** When executing background commands or soft-failure utilities, explicitly redirect stderr to `/dev/null` (`>/dev/null 2>&1`) to preserve a clean terminal interface.

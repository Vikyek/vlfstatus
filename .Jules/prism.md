## 2023-10-27 - Suppressing Unhelpful Stderr
**Learning:** In bash scripts, utility commands that are expected to fail gracefully (like checking for an active WM process, e.g. `i3-msg restart` when `i3` isn't running) often spew unhandled "command not found" or "connection refused" errors to stderr. This breaks the console UX and causes user alarm even if the script successfully ignores the error (`|| true`).
**Action:** When executing background commands or soft-failure utilities, explicitly redirect stderr to `/dev/null` (`>/dev/null 2>&1`) to preserve a clean terminal interface.

## 2026-09-02 - Bash ANSI color pattern
**Learning:** `install.sh` has a reusable Bash script ANSI escape pattern that respects the `NO_COLOR` environment variable and `isatty()` (`[ -t 1 ]`).
**Action:** Use this standard pattern to enforce `NO_COLOR` compliant console output in Bash scripts in this repository.

## 2026-10-24 - Handling Missing Dependencies
**Learning:** Raw stack traces from `ImportError` exceptions cause console clutter and confuse users who might not understand the difference between an unhandled code bug and an expected missing environment requirement.
**Action:** When a tool relies on standard but optional external python dependencies (e.g. `fontforge`), wrap the initial import in a `try/except` block, suppress the raw traceback, and use standard error formatting (routed to `stderr`) to instruct the user on how to install the dependency.

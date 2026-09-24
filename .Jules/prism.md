## 2023-10-27 - Suppressing Unhelpful Stderr
**Learning:** In bash scripts, utility commands that are expected to fail gracefully (like checking for an active WM process, e.g. `i3-msg restart` when `i3` isn't running) often spew unhandled "command not found" or "connection refused" errors to stderr. This breaks the console UX and causes user alarm even if the script successfully ignores the error (`|| true`).
**Action:** When executing background commands or soft-failure utilities, explicitly redirect stderr to `/dev/null` (`>/dev/null 2>&1`) to preserve a clean terminal interface.

## 2026-09-02 - Bash ANSI color pattern
**Learning:** `install.sh` has a reusable Bash script ANSI escape pattern that respects the `NO_COLOR` environment variable and `isatty()` (`[ -t 1 ]`).
**Action:** Use this standard pattern to enforce `NO_COLOR` compliant console output in Bash scripts in this repository.

## 2026-10-24 - Handling Missing Dependencies
**Learning:** Raw stack traces from `ImportError` exceptions cause console clutter and confuse users who might not understand the difference between an unhandled code bug and an expected missing environment requirement.
**Action:** When a tool relies on standard but optional external python dependencies (e.g. `fontforge`), wrap the initial import in a `try/except` block, suppress the raw traceback, and use standard error formatting (routed to `stderr`) to instruct the user on how to install the dependency.

## 2025-02-12 - Python ANSI color pattern
**Learning:** Python scripts emitting ANSI escape codes to `sys.stderr` should verify that `os.environ.get("NO_COLOR")` is empty and `sys.stderr.isatty()` is true, otherwise raw ANSI characters can break CI environments and redirect output readability.
**Action:** Use conditional assignment (e.g., `C_ERROR = '\033[1;31m' if not os.environ.get("NO_COLOR") and sys.stderr.isatty() else ''`) to enforce compliant Python console output formatting.

## 2024-11-09 - Reusable setup script formatting pattern
**Learning:** Found a reusable output formatting pattern for bash setup scripts using indented semantic symbols and dimmed step headers to dramatically improve readability and visual hierarchy, without requiring external dependencies like `tqdm` or `gum`.
**Action:** Always prefer this lightweight `step()` + indented `info/success/warn` structure for bash scripts to increase scannability without breaking POSIX compatibility.
## 2025-02-12 - Appending line-clear sequence for carriage-returns
**Learning:** When using a carriage-return (`\r`) to create an in-place terminal progress counter, if the loop contains other logs or if subsequent messages are shorter, the trailing characters from previous outputs will remain and garble the terminal output.
**Action:** Always append an ANSI line-clear escape sequence (e.g., `\033[K`) when outputting `\r` updates to ensure clean rendering.

## 2026-09-13 - Immediate Error Command Context
**Learning:** When bash scripts fail and rely on a global `ERR` trap to catch exceptions, simply printing the line number of the failure (e.g. `$LINENO`) forces the developer to manually open the source file to figure out what went wrong. This breaks immediate console feedback.
**Action:** Use the `$BASH_COMMAND` built-in variable inside global bash `ERR` traps to instantly print the exact command that failed directly to the console.

## 2025-01-01 - Prevent Nested Step Formatting
**Learning:** Calling primary section header functions (like `step()` with `---` separators) consecutively or nested causes jagged, double-spaced output and breaks the visual hierarchy.
**Action:** Avoid nesting separator functions. Use a single primary section header and fall back to indented list items (e.g., `info()`) for sub-tasks to maintain a clean visual hierarchy.

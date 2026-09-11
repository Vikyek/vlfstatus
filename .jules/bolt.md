## 2025-02-12 - JSON Parsing Bottleneck in Bash Status Bar
**Learning:** Parsing JSON sequentially with 9 separate `grep` processes in a tight `while true; do ... sleep 1` bash loop consumes significant CPU and blocks rendering updates.
**Action:** Always cache parsing logic by checking file modification time (`stat -c %Y`) when extracting data from polling background daemons. This drops extraction time from ~45ms to <5ms per tick.
## 2025-02-12 - Replacing subshells with builtins in bash tight loop
**Learning:** Calling standard external commands (like `date`, `cat`) within a high-frequency loop (e.g., `while true; do ... sleep 1`) forks a new process each time. These fork/exec calls are significantly more expensive than running pure bash built-ins (e.g., `printf` and `read`).
**Action:** Replace `$(date +"...")` with `printf -v VAR "%(...)T" -1`, replace `$(date +%s)` with `$EPOCHSECONDS`, and replace `$(cat file)` with `read -r VAR < file`. This saves ~15-20ms of execution time per loop iteration and reduces system CPU usage without compromising readability.

## 2024-05-18 - [Batching subprocess calls inside loops]
**Learning:** In bash scripts with high-frequency loops (like `vlfstatus`), iterative variable updates that rely on subprocess calls (e.g., `TOTAL=$(awk ...)`) scale poorly when inside nested loops over dynamic collections (like multiple accounts), due to the fork/exec overhead multiplying (O(N) subprocesses).
**Action:** Always batch math or text processing by building expression strings inside the loop and evaluating them once via a single subprocess call outside the loop, significantly reducing CPU usage and latency.
## 2025-02-12 - Batching external command evaluation in bash high-frequency loops
**Learning:** When evaluating external commands (like `awk` for floating-point math) inside a tight bash loop, calling the command on each iteration spawns multiple subshells per second, resulting in significant overhead and high CPU usage due to fork/exec calls.
**Action:** Optimize performance by iteratively building expression strings within the loop and executing a single, batched evaluation command outside the loop.
## 2023-10-25 - Reducing fork/exec overhead with native regex in bash loops
**Learning:** External pipeline tools like `grep`, `sed`, `awk`, and `head` inside high-frequency bash loops (e.g., `vlfstatus`) cause significant CPU usage and performance degradation due to multiple subshell fork/exec operations per tick. Replace external pipelines with CLI-native formatting flags (e.g., `nmcli -t -f`) and bash's built-in regular expression matching (`[[ "$VAR" =~ regex ]]`).
**Action:** Replace external text parsing pipelines with CLI-native formatting flags and bash built-ins to eliminate redundant subprocess execution.

## 2025-02-12 - Decoupling slow-changing state calculations from high-frequency bash loops
**Learning:** Even when state updates are correctly gated by file modification checks, subsequent calculations based on that state (like calling `awk` to average floating-point arrays) can accidentally remain outside the check block, causing them to execute on every single tick of a high-frequency loop and wasting CPU.
**Action:** Always verify that calculations dependent on slow-changing state are nested inside the condition block or cached when the state updates, completely eliminating redundant subshells from the fast path.
## 2025-02-12 - Pruning dead subshell assignments in bash loops
**Learning:** Leaving unused or immediately-overridden variables that evaluate external commands (like `awk`) in high-frequency bash loops results in hidden fork/exec CPU overhead on every tick, and may spam `stderr` with syntax errors.
**Action:** Explicitly prune dead code and redundant subshell evaluations in tight loops to minimize subprocesses.
## 2025-05-18 - Avoid subshell overhead by checking sysfs before invoking external binaries
**Learning:** In high-frequency bash loops, invoking external commands (like `nmcli`) unconditionally causes expensive fork/exec overhead (approx. 66ms per 100 iterations) even when the state hasn't changed.
**Action:** Before executing slow networking or system state commands, read from kernel `/sys/class` (e.g., `/sys/class/net/wlp8s0/operstate`) using bash built-in `read` which executes almost instantaneously (~2ms per 100 iterations), bypassing external binary execution completely when the device is down or idle.
## 2025-02-12 - Rate limiting and eliminating subshells in high-frequency loops
**Learning:** Checking process statuses (like `pgrep` or `systemctl`) or using command substitution (`$(...)`) to format text in high-frequency bash loops (e.g. `while true; do ... sleep 1`) introduces hidden CPU overhead due to frequent fork/execs.
**Action:** Use a TICK counter to rate-limit expensive external commands (e.g. `if (( TICK % 5 == 0 )); then`), and use `printf -v VARIABLE_NAME` instead of command substitution to update string output inside tight loops.

## 2024-05-18 - Eliminating stat fork/exec with bash built-in file tests
**Learning:** Using `stat -c %Y file` to check file modification times inside a high-frequency loop introduces significant CPU overhead due to fork/execing a subshell and an external command on every tick.
**Action:** Replace `stat` checks with bash's built-in file test operator `-nt` (newer than) against a marker file (e.g., `[[ data_file -nt marker_file ]] && touch marker_file`). This completely bypasses subprocess execution, dramatically improving efficiency in tight loops.

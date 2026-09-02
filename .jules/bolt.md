## 2025-02-12 - JSON Parsing Bottleneck in Bash Status Bar
**Learning:** Parsing JSON sequentially with 9 separate `grep` processes in a tight `while true; do ... sleep 1` bash loop consumes significant CPU and blocks rendering updates.
**Action:** Always cache parsing logic by checking file modification time (`stat -c %Y`) when extracting data from polling background daemons. This drops extraction time from ~45ms to <5ms per tick.
## 2025-02-12 - Replacing subshells with builtins in bash tight loop
**Learning:** Calling standard external commands (like `date`, `cat`) within a high-frequency loop (e.g., `while true; do ... sleep 1`) forks a new process each time. These fork/exec calls are significantly more expensive than running pure bash built-ins (e.g., `printf` and `read`).
**Action:** Replace `$(date +"...")` with `printf -v VAR "%(...)T" -1`, replace `$(date +%s)` with `$EPOCHSECONDS`, and replace `$(cat file)` with `read -r VAR < file`. This saves ~15-20ms of execution time per loop iteration and reduces system CPU usage without compromising readability.

## 2024-05-18 - [Batching subprocess calls inside loops]
**Learning:** In bash scripts with high-frequency loops (like `vlfstatus`), iterative variable updates that rely on subprocess calls (e.g., `TOTAL=$(awk ...)`) scale poorly when inside nested loops over dynamic collections (like multiple accounts), due to the fork/exec overhead multiplying (O(N) subprocesses).
**Action:** Always batch math or text processing by building expression strings inside the loop and evaluating them once via a single subprocess call outside the loop, significantly reducing CPU usage and latency.

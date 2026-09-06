## 2025-02-12 - JSON Parsing Bottleneck in Bash Status Bar
**Learning:** Parsing JSON sequentially with 9 separate `grep` processes in a tight `while true; do ... sleep 1` bash loop consumes significant CPU and blocks rendering updates.
**Action:** Always cache parsing logic by checking file modification time (`stat -c %Y`) when extracting data from polling background daemons. This drops extraction time from ~45ms to <5ms per tick.
## 2025-02-12 - Replacing subshells with builtins in bash tight loop
**Learning:** Calling standard external commands (like `date`, `cat`) within a high-frequency loop (e.g., `while true; do ... sleep 1`) forks a new process each time. These fork/exec calls are significantly more expensive than running pure bash built-ins (e.g., `printf` and `read`).
**Action:** Replace `$(date +"...")` with `printf -v VAR "%(...)T" -1`, replace `$(date +%s)` with `$EPOCHSECONDS`, and replace `$(cat file)` with `read -r VAR < file`. This saves ~15-20ms of execution time per loop iteration and reduces system CPU usage without compromising readability.
## 2025-02-12 - Batching external command evaluation in bash high-frequency loops
**Learning:** When evaluating external commands (like `awk` for floating-point math) inside a tight bash loop, calling the command on each iteration spawns multiple subshells per second, resulting in significant overhead and high CPU usage due to fork/exec calls.
**Action:** Optimize performance by iteratively building expression strings within the loop and executing a single, batched evaluation command outside the loop.
## 2023-10-25 - Reducing fork/exec overhead with native regex in bash loops
**Learning:** External pipeline tools like `grep`, `sed`, `awk`, and `head` inside high-frequency bash loops (e.g., `vlfstatus`) cause significant CPU usage and performance degradation due to multiple subshell fork/exec operations per tick.
**Action:** Replace external text parsing pipelines with CLI-native formatting flags (e.g., `nmcli -t -f`) and bash's built-in regular expression matching (`[[ "$VAR" =~ regex ]]`).

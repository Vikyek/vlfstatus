## 2025-02-12 - JSON Parsing Bottleneck in Bash Status Bar
**Learning:** Parsing JSON sequentially with 9 separate `grep` processes in a tight `while true; do ... sleep 1` bash loop consumes significant CPU and blocks rendering updates.
**Action:** Always cache parsing logic by checking file modification time (`stat -c %Y`) when extracting data from polling background daemons. This drops extraction time from ~45ms to <5ms per tick.

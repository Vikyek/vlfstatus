## 2024-05-18 - Prevent JSON & Pango Injection in Status Bar
**Vulnerability:** The Wi-Fi connection name (SSID) retrieved from `nmcli` was inserted directly into the JSON and Pango markup output without any sanitization. A malicious SSID containing characters like `<`, `>`, `&`, `"`, or `\` could cause JSON parsing errors or Pango markup injection, potentially crashing the status bar or leading to XSS-like behaviors.
**Learning:** In bash scripts generating structured output (JSON, HTML, Pango) from external untrusted input (like Wi-Fi SSIDs), input must be rigorously sanitized. When using bash parameter expansion for replacement, one must be careful with bash 5.2+'s `patsub_replacement` option, where unescaped `&` in the replacement string acts as a backreference. Disabling it with `shopt -u patsub_replacement 2>/dev/null || true` ensures cross-version compatibility for replacements like `&amp;`.
**Prevention:** Always escape special characters (e.g., `\`, `"`, `&`, `<`, `>`) in external strings before interpolating them into JSON or markup formats. Ensure escaping is robust across different shell configurations.

## 2025-02-14 - Replace insecure os.system call
**Vulnerability:** A script `patch_font.py` used `os.system("fc-cache -f")` to refresh the font cache.
**Learning:** Using `os.system` executes commands in a shell environment, which leaves the script vulnerable to shell injection if any user input or variables are ever introduced, and relies on the shell's behavior which is generally insecure.
**Prevention:** Always use `subprocess.run` with a list of arguments (e.g., `["fc-cache", "-f"]`) to execute external commands directly without spawning a shell.

## 2026-09-02 - Removed Hardcoded Google Client Secret
**Vulnerability:** A hardcoded Google API `client_secret` was present in `fetch_quota.py`. Hardcoded credentials can easily be leaked if the repository becomes public or is accessed by unauthorized users, granting them unauthorized access to the Google API using the application's identity.
**Learning:** Hardcoding sensitive information such as API keys and secrets directly in the source code exposes them to significant security risks, especially in scripts distributed or committed to version control.
**Prevention:** Always load sensitive credentials from secure sources such as environment variables (e.g., `os.environ.get`), secure configuration files, or secret management services instead of hardcoding them in the codebase.

## 2026-09-03 - Strip Control Characters from External Input
**Vulnerability:** Untrusted external input (such as Wi-Fi SSIDs from `nmcli`) was inserted into JSON strings without stripping control characters. While standard special characters like `<` and `"` were escaped, literal control characters like newlines (`\n`), carriage returns (`\r`), or ANSI escape codes (`\e`) can break the JSON parser in the window manager (e.g. i3bar or swaybar), causing a Denial of Service.
**Learning:** JSON specifications require control characters to be escaped. Failing to handle them allows attackers to crash downstream consumers of the JSON payload.
**Prevention:** Always strip or escape control characters (e.g., using `VAR="${VAR//[[:cntrl:]]/}"`) when inserting untrusted input into structured formats like JSON.

## 2026-09-05 - Prevent Stack Trace Leakage on Missing Dependencies
**Vulnerability:** The script `fetch_quota.py` imported external dependencies (`secretstorage`) directly at the top level. If the module was missing, the application crashed, exposing internal stack traces to the user/logs.
**Learning:** Raw tracebacks leak internal application structure, file paths, and execution context. When a script runs as a background daemon (like `fetch_quota.py`), unhandled exceptions can also pollute system logs unnecessarily. Failing securely means abstracting away implementation details from the failure state.
**Prevention:** Wrap unreliable or external dependency imports in `try/except ImportError` blocks. Suppress raw tracebacks and instead route clear, styled instructional messages to standard error (`sys.stderr`), then exit securely.

## 2026-09-06 - Enforce Strict File Permissions on Credential Files
**Vulnerability:** The script `fetch_quota.py` loaded Google API client secrets from local configuration files (`~/.gemini/config/.vault_credentials.env` and `~/.config/vlfstatus/credentials.env`) without verifying their file permissions. If these files were world-readable or group-readable (e.g., `chmod 644`), sensitive credentials could be exposed to unauthorized users on the same system.
**Learning:** When storing and reading sensitive information in local files, it's crucial to enforce strict file permissions to ensure that only the owner has read access.
**Prevention:** Before opening files containing credentials or sensitive data, use `os.stat` to verify that the file's permissions are properly restricted (e.g., `st.st_mode & 0o077` should be `0` for `chmod 600`). Reject or skip reading the file if permissions are insecure, and provide clear instructional error messages.

## 2026-09-04 - Prevent Untrusted Search Path Vulnerabilities
**Vulnerability:** External system calls using `subprocess.run` (like calling `agy` or `fc-cache`) relied on the system's `PATH` variable to locate the executable by only providing the executable's name instead of the absolute path. If an attacker has poisoned the `PATH` variable to point to a malicious executable, `subprocess.run()` will execute it.
**Learning:** Depending entirely on the `PATH` environment variable in Python scripts that invoke subprocesses can be a vector for privilege escalation or malicious code execution. Using `shutil.which()` is NOT a fix because it uses the exact same `PATH` resolution mechanism and will resolve to the malicious path.
**Prevention:** Always verify and supply the absolute path when calling external executables (e.g. `/usr/bin/fc-cache`), or explicitly sanitize the `PATH` passed to `env` in `subprocess.run()` to a trusted subset like `/usr/local/bin:/usr/bin:/bin` if you don't know the absolute path dynamically.

## 2026-09-08 - Prevent Command Injection via Uninitialized Variables in Subshells
**Vulnerability:** A script `vlfstatus` executed `awk` with uninitialized variables inside a subshell using `$()`. Because these variables were not explicitly initialized or sanitized within the script, their values could be controlled via the environment when the script was launched. If an attacker provided an environment variable with a payload like `system("malicious_command")`, it would be injected into the `awk` command and executed (CWE-78).
**Learning:** Command injection (CWE-78) can occur when uninitialized variables are passed into subshells or external commands, as bash will inherit these variables from the environment. This makes scripts vulnerable to Remote Code Execution (RCE) or Local Privilege Escalation (LPE) if invoked with a manipulated environment.
**Prevention:** Always explicitly initialize and sanitize variables before using them in commands or subshells. Prune dead code and redundant subshell executions. Avoid using `eval` or directly substituting variables into command strings if they are dynamically evaluated by an interpreter like `awk`.

## 2026-09-09 - Prevent Command Injection via awk string interpolation
**Vulnerability:** A script `vlfstatus` dynamically built mathematical expressions from parsed JSON string values into bash variables (`TOTAL_G_EXPR` and `TOTAL_C_EXPR`) and directly interpolated these variables into `awk` program strings (e.g., `awk "BEGIN {val=($TOTAL_G_EXPR)...}"`). Because the `TOTAL_G_EXPR` variable could contain untrusted data originating from JSON parsing or environment injections, an attacker could supply an `awk` payload (like `0) system("malicious_command"); (0`) that would execute arbitrary commands when `awk` ran.
**Learning:** Command Injection (CWE-78) can occur when bash variables containing untrusted input are directly interpolated into the command strings of other interpreters like `awk`, `sed`, or `perl`. The external interpreter evaluates the injected string as code.
**Prevention:** Always pass dynamic data to external interpreters like `awk` using safe mechanisms such as the `-v` flag (e.g., `awk -v expr="$MY_VAR" 'BEGIN { ... }'`), treating the input strictly as data rather than executable code. Do not use bash double quotes to interpolate variables directly into `awk` command strings.

## 2026-09-10 - Prevent Local Privilege Escalation (LPE) via Root Execution
**Vulnerability:** Bash scripts like `vlfstatus` and `install.sh` sourced user-writable configuration files (e.g., `~/.cache/bar_colors.sh` or `~/.config/vlfstatus/config`) without explicitly checking if the script was executed with elevated privileges (e.g., `sudo`). An attacker could manipulate these configuration files, and if the script was inadvertently run as root, arbitrary commands within those configurations would be executed with elevated privileges, resulting in Local Privilege Escalation (LPE).
**Learning:** Scripts that process untrusted or user-modifiable inputs should not run as root unless strictly necessary. The principle of least privilege should be strictly enforced at the entry point of scripts.
**Prevention:** Always include a check for the Effective User ID (`$EUID`) at the beginning of user-level scripts (`if [ "$EUID" -eq 0 ]; then exit 1; fi`) to prevent accidental or malicious execution with root privileges.

## 2026-09-18 - Prevent Arbitrary Variable Overwrites in Config Parsing (CWE-473)
**Vulnerability:** While mitigating arbitrary code execution from sourced configurations, the `vlfstatus` bash script implemented a safe parsing loop (`while IFS='=' read -r key val`). However, it used a highly generic regular expression (`^[a-zA-Z_][a-zA-Z0-9_]*$`) to validate keys before passing them to `printf -v`. An attacker could add entries like `PATH=/malicious/path` or `FETCH_QUOTA_PATH=/malicious/script.py` to `~/.config/vlfstatus/config`, successfully overwriting internal script state and hijacking execution flows (CWE-473).
**Learning:** Even safe variable assignment techniques (`printf -v`) can lead to vulnerabilities if the accepted key names are not strictly constrained. Generically allowing any valid bash variable name exposes the entire script's internal logic and environment variables to manipulation by an untrusted configuration file.
**Prevention:** To prevent arbitrary variable overwrites, never use generic bash variable regexes when loading configurations. Always validate keys against a strict, explicit allowlist regular expression (e.g., `^(COLOR_[a-zA-Z0-9_]+|MULTI_ACCOUNT_MODE)$`) before assignment.

## 2026-09-16 - Prevent Arbitrary Code Execution via Sourced Configuration Files
**Vulnerability:** The bash script `vlfstatus` loaded user configuration and color caches (`~/.config/vlfstatus/config` and `~/.cache/bar_colors.sh`) using the `source` command. Since `source` evaluates file contents as bash commands in the current shell, any malicious code injected into these files (e.g. by another application or downloaded script) would be executed with the user's privileges, leading to arbitrary code execution.
**Learning:** Sourcing untrusted or externally modifiable configuration files in bash scripts is a dangerous pattern because it does not distinguish between variable assignments and executable commands.
**Prevention:** Instead of `source`, read configuration files safely using a `while read` loop, validate keys against a strict regex (e.g., `^[a-zA-Z_][a-zA-Z0-9_]*$`), sanitize values by stripping quotes, and assign them using `printf -v "$key" "%s" "$val"` to prevent any code evaluation.

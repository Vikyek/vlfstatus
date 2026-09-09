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

## 2026-10-27 - Remove Dead Code with Uninitialized Variables in Subshells
**Vulnerability:** In `vlfstatus`, the command `read -r TOTAL_G TOTAL_C <<< $(awk "BEGIN {print $AWK_G_EXPR, $AWK_C_EXPR}")` was used, but `$AWK_G_EXPR` and `$AWK_C_EXPR` were uninitialized in the script. Because they were uninitialized, an attacker could hijack them via environment variables. The `awk` payload evaluates the injected string, which allows an attacker to execute arbitrary commands (Command Injection / CWE-78), leading to Remote Code Execution.
**Learning:** Uninitialized variables inside subshells, particularly when passed to evaluative commands like `awk`, create severe vulnerabilities as they can be easily manipulated via the environment.
**Prevention:** Always explicitly initialize or sanitize variables before using them in subshells or passing them to external commands. Additionally, aggressively prune dead code and redundant subshell executions, as they not only increase CPU overhead but can also act as hidden attack vectors.

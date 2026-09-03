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

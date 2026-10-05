import json
import urllib.request
import urllib.parse
import urllib.error
import time
import os
import sys
import tempfile
import hashlib
import subprocess
import shutil
from datetime import datetime

# Styling setup respecting NO_COLOR
if not os.environ.get("NO_COLOR") and sys.stdout.isatty():
    C_INFO = '\033[1;34m'
    C_SUCCESS = '\033[1;32m'
    C_ERROR = '\033[1;31m'
    C_BOLD = '\033[1m'
    C_DIM = '\033[2m'
    C_RESET = '\033[0m'
    C_CLEAR = '\033[K'
else:
    C_INFO = ''
    C_SUCCESS = ''
    C_ERROR = ''
    C_BOLD = ''
    C_DIM = ''
    C_RESET = ''
    C_CLEAR = ''

if not os.environ.get("NO_COLOR") and sys.stderr.isatty():
    C_ERROR_ERR = '\033[1;31m'
    C_SUCCESS_ERR = '\033[1;32m'
    C_BOLD_ERR = '\033[1m'
    C_DIM_ERR = '\033[2m'
    C_RESET_ERR = '\033[0m'
    C_CLEAR_ERR = '\033[K'
else:
    C_ERROR_ERR = ''
    C_SUCCESS_ERR = ''
    C_BOLD_ERR = ''
    C_DIM_ERR = ''
    C_RESET_ERR = ''
    C_CLEAR_ERR = ''

# SECURITY: Prevent leaking stack traces when dependencies are missing.
try:
    import secretstorage
except ImportError:
    print(file=sys.stderr)
    print(f"  {C_ERROR_ERR}✖ ERROR:{C_RESET_ERR} Missing required dependency: secretstorage", file=sys.stderr)
    print(f"    {C_DIM_ERR}↳ Please install it (e.g., pip install secretstorage){C_RESET_ERR}", file=sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)

def get_credential(key_name):
    val = os.environ.get(key_name)
    if val:
        return val
    
    env_paths = [
        os.path.expanduser("~/.gemini/config/.vault_credentials.env"),
        os.path.expanduser("~/.config/vlfstatus/credentials.env")
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            # SECURITY: Enforce strict file permissions on credential files
            try:
                st = os.stat(env_path)
                if st.st_mode & 0o077:
                    print(file=sys.stderr)
                    print(f"  {C_ERROR_ERR}✖ ERROR:{C_RESET_ERR} Insecure permissions on {C_BOLD_ERR}{env_path}{C_RESET_ERR}", file=sys.stderr)
                    print(f"    {C_DIM_ERR}↳ File must not be readable by group/others. Run 'chmod 600 {env_path}'{C_RESET_ERR}", file=sys.stderr)
                    print(file=sys.stderr)
                    continue
            except Exception:
                pass

            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f"{key_name}="):
                            found_val = line.split("=", 1)[1].strip("\"'")
                            if found_val:
                                return found_val
            except Exception:
                pass
    return None

def get_client_secret():
    return get_credential("GOOGLE_CLIENT_SECRET")

def get_client_id():
    return get_credential("GOOGLE_CLIENT_ID")

def refresh_token(ref_token):
    url = "https://oauth2.googleapis.com/token"
    client_id = get_client_id()
    if not client_id:
        raise ValueError("Missing GOOGLE_CLIENT_ID in environment or vault credentials")

    client_secret = get_client_secret()
    if not client_secret:
        raise ValueError("Missing GOOGLE_CLIENT_SECRET in environment or vault credentials")

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": ref_token,
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"], int(res.get("expires_in", 3600))

def fetch_quota_from_agy_cli():
    try:
        # Sanitize environment PATH to prevent untrusted execution
        safe_env = os.environ.copy()
        trusted_paths = [os.path.expanduser("~/.local/bin"), "/usr/local/bin", "/usr/bin", "/bin"]
        safe_env["PATH"] = os.pathsep.join(trusted_paths)
        agy_path = shutil.which("agy", path=safe_env["PATH"])
        if not agy_path:
            return None
        res = subprocess.run(
            ["agy", "-p", "/quota", "--output-format", "json"],
            executable=agy_path,
            capture_output=True,
            text=True,
            timeout=20,
            env=safe_env
        )
        if res.returncode != 0 or not res.stdout.strip():
            return None

        data = json.loads(res.stdout)
        usage_data = data.get("command", {}).get("data", {})
        groups = usage_data.get("groups", [])
        if not groups:
            return None

        acc_output = {}
        for group in groups:
            disp_name = group.get("name", "")
            prefix = "gemini" if "Gemini" in disp_name else "claude"
            for bucket in group.get("buckets", []):
                window = bucket.get("window", "")
                suffix = "5h" if window == "5h" else "weekly"
                rem_frac = bucket.get("remaining_fraction", 0.0)
                rem_pct = round(rem_frac * 100, 1)

                reset_time = bucket.get("reset_time", "")
                reset_epoch = 0
                if reset_time:
                    try:
                        rt = datetime.fromisoformat(reset_time.replace("Z", "+00:00"))
                        reset_epoch = int(rt.timestamp())
                    except Exception:
                        pass

                acc_output[f"{prefix}_{suffix}"] = f"{rem_pct}%"
                acc_output[f"{prefix}_{suffix}_reset_epoch"] = reset_epoch

        for prefix in ("gemini", "claude"):
            if f"{prefix}_5h" not in acc_output and f"{prefix}_weekly" in acc_output:
                acc_output[f"{prefix}_5h"] = acc_output[f"{prefix}_weekly"]
                acc_output[f"{prefix}_5h_reset_epoch"] = acc_output.get(f"{prefix}_weekly_reset_epoch", 0)
            if f"{prefix}_weekly" not in acc_output and f"{prefix}_5h" in acc_output:
                acc_output[f"{prefix}_weekly"] = acc_output[f"{prefix}_5h"]
                acc_output[f"{prefix}_weekly_reset_epoch"] = acc_output.get(f"{prefix}_5h_reset_epoch", 0)

        return acc_output
    except Exception:
        return None

def write_output_json(out_path, data):
    dir_name = os.path.dirname(out_path)
    os.makedirs(dir_name, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=dir_name, text=True)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, out_path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    cache_dir = os.path.expanduser("~/.cache/token-conso")
    out_path = os.path.expanduser("~/.cache/agy_quota.json")
    
    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            if sys.stdout.isatty():
                now = datetime.now().strftime("%H:%M:%S")
                sys.stdout.write(f"\r{C_DIM}  [{now}] Quota daemon active | Cycles: {cycle_count}{C_RESET}{C_CLEAR}")
                sys.stdout.flush()

            try:
                current_data = {}
                if os.path.exists(out_path):
                    try:
                        with open(out_path, "r") as f:
                            current_data = json.load(f)
                    except Exception:
                        pass

                # 1. Primary: fetch via agy CLI
                acc_output = fetch_quota_from_agy_cli()
                if acc_output:
                    output = {"accounts": [acc_output], "last_updated_epoch": int(time.time())}
                    write_output_json(out_path, output)
                else:
                    # Keep existing data alive if fetch failed temporarily
                    if current_data:
                        current_data["last_updated_epoch"] = int(time.time())
                        write_output_json(out_path, current_data)
            except Exception:
                pass

            time.sleep(30)
    except KeyboardInterrupt:
        print(file=sys.stderr)
        print(f"  {C_DIM_ERR}↳ Quota daemon stopped cleanly by user.{C_RESET_ERR}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # SECURITY: Prevent raw stack traces from leaking to the console on SIGINT
        print(file=sys.stderr)
        print(f"  {C_SUCCESS_ERR}✔{C_RESET_ERR} {C_DIM_ERR}Quota daemon gracefully terminated.{C_RESET_ERR}{C_CLEAR_ERR}", file=sys.stderr)
        sys.exit(0)

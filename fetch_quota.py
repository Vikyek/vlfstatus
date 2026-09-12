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
from datetime import datetime

# Styling setup respecting NO_COLOR
if not os.environ.get("NO_COLOR") and sys.stderr.isatty():
    C_ERROR = '\033[1;31m'
    C_DIM = '\033[2m'
    C_RESET = '\033[0m'
    C_CLEAR = '\033[K'
else:
    C_ERROR = ''
    C_DIM = ''
    C_RESET = ''
    C_CLEAR = ''

# SECURITY: Prevent leaking stack traces when dependencies are missing.
try:
    import secretstorage
except ImportError:
    print(file=sys.stderr)
    print(f"{C_ERROR}[✖ ERROR]{C_RESET} Missing required dependency: secretstorage", file=sys.stderr)
    print(f"    {C_DIM}↳ Please install it (e.g., pip install secretstorage){C_RESET}", file=sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)

def get_client_secret():
    secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if secret:
        return secret
    
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
                    print(f"{C_ERROR}[✖ ERROR]{C_RESET} Insecure permissions on {env_path}", file=sys.stderr)
                    print(f"    {C_DIM}↳ File must not be readable by group/others. Run 'chmod 600 {env_path}'{C_RESET}", file=sys.stderr)
                    print(file=sys.stderr)
                    continue
            except Exception:
                pass

            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GOOGLE_CLIENT_SECRET="):
                            val = line.split("=", 1)[1].strip("\"'")
                            if val:
                                return val
            except Exception:
                pass
    return None

def refresh_token(ref_token):
    url = "https://oauth2.googleapis.com/token"
    client_id = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"

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
        safe_env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
        res = subprocess.run(
            ["agy", "-p", "/quota", "--output-format", "json"],
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

if __name__ == "__main__":
    main()

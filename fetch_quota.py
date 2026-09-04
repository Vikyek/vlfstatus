import secretstorage
import json
import urllib.request
import urllib.parse
import urllib.error
import time
import os
import tempfile
import hashlib
from datetime import datetime

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

def get_account_items():
    items = []
    seen_tokens = set()
    try:
        path = os.path.expanduser("~/.config/opencode/antigravity-accounts.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                for acc in data.get("accounts", []):
                    rf = acc.get("refreshToken")
                    pid = acc.get("projectId")
                    em = acc.get("email")
                    if rf and rf not in seen_tokens:
                        seen_tokens.add(rf)
                        items.append({"refreshToken": rf, "projectId": pid, "email": em})
    except Exception:
        pass

    try:
        connection = secretstorage.dbus_init()
        collections = list(secretstorage.get_all_collections(connection))
        for collection in collections:
            for item in collection.get_all_items():
                attrs = item.get_attributes()
                if attrs.get('service') == 'gemini' and attrs.get('username') == 'antigravity':
                    secret_data = json.loads(item.get_secret().decode('utf-8', errors='ignore'))
                    rf = secret_data.get("token", {}).get("refresh_token")
                    pid = secret_data.get("projectId") or secret_data.get("project_id")
                    em = secret_data.get("email")
                    if rf and rf not in seen_tokens:
                        seen_tokens.add(rf)
                        items.append({"refreshToken": rf, "projectId": pid, "email": em})
    except Exception:
        pass
    return items

def get_ref_tokens():
    return [item["refreshToken"] for item in get_account_items()]

def load_cached_token(cache_path):
    if not os.path.exists(cache_path):
        return None, 0
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
            expiry = data.get("expiry_seconds", 0)
            if expiry > time.time() + 60:
                return data.get("access_token"), expiry
    except Exception:
        pass
    return None, 0

def save_cached_token(cache_path, token, expires_in):
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        data = {
            "access_token": token,
            "expiry_seconds": int(time.time() + expires_in)
        }
        with open(os.open(cache_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def fetch_quota_summary(token, project_id=None):
    url = "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary"
    data = json.dumps({"project": project_id}).encode("utf-8") if project_id else b"{}"
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "antigravity"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

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
    
    while True:
        current_data = {}
        if os.path.exists(out_path):
            try:
                with open(out_path, "r") as f:
                    current_data = json.load(f)
            except Exception:
                pass

        try:
            acc_items = get_account_items()
            if not acc_items:
                raise Exception("No accounts available")
            
            output = {"accounts": []}
            seen_emails = set()

            for idx, acc_info in enumerate(acc_items):
                ref_token = acc_info["refreshToken"]
                project_id = acc_info.get("projectId")

                token_hash = hashlib.sha256(ref_token.encode('utf-8')).hexdigest()[:16]
                cache_path = os.path.join(cache_dir, f"antigravity-auth-{token_hash}.json")

                try:
                    token, expiry = load_cached_token(cache_path)
                    if not token:
                        token, expires_in = refresh_token(ref_token)
                        save_cached_token(cache_path, token, expires_in)

                    email = acc_info.get("email")
                    if not email:
                        try:
                            u_req = urllib.request.Request(
                                "https://www.googleapis.com/oauth2/v1/userinfo",
                                headers={"Authorization": f"Bearer {token}"}
                            )
                            with urllib.request.urlopen(u_req, timeout=5) as u_resp:
                                u_info = json.loads(u_resp.read().decode("utf-8"))
                                email = u_info.get("email")
                        except Exception:
                            pass

                    if email:
                        if email in seen_emails:
                            continue
                        seen_emails.add(email)

                    try:
                        summary = fetch_quota_summary(token, project_id=project_id)
                    except urllib.error.HTTPError as e:
                        if e.code == 403 and not project_id:
                            summary = fetch_quota_summary(token, project_id="aicode-consumers")
                        else:
                            raise
                    
                    acc_output = {"email": email} if email else {}
                    for group in summary.get("groups", []):
                        disp_name = group.get("displayName", "")
                        prefix = "gemini" if "Gemini" in disp_name else "claude"
                        for bucket in group.get("buckets", []):
                            window = bucket.get("window", "")
                            suffix = "5h" if window == "5h" else "weekly"
                            rem_frac = bucket.get("remainingFraction", 0.0)
                            rem_pct = round(rem_frac * 100, 1)

                            reset_time = bucket.get("resetTime", "")
                            reset_epoch = 0
                            if reset_time:
                                try:
                                    rt = datetime.fromisoformat(reset_time.replace("Z", "+00:00"))
                                    reset_epoch = int(rt.timestamp())
                                except Exception:
                                    pass

                            acc_output[f"{prefix}_{suffix}"] = f"{rem_pct}%"
                            acc_output[f"{prefix}_{suffix}_reset_epoch"] = reset_epoch
                    
                    output["accounts"].append(acc_output)
                except Exception as e:
                    pass # Skip failing tokens
            
            output["last_updated_epoch"] = int(time.time())
            write_output_json(out_path, output)
            
        except Exception:
            if current_data:
                current_data["last_updated_epoch"] = int(time.time())
                write_output_json(out_path, current_data)
            else:
                write_output_json(out_path, {"last_updated_epoch": int(time.time())})
            
        time.sleep(60)

if __name__ == "__main__":
    main()

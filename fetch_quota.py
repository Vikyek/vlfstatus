import secretstorage
import json
import urllib.request
import urllib.parse
import urllib.error
import time
import os
import tempfile

def refresh_token(ref_token):
    url = "https://oauth2.googleapis.com/token"
    client_id = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"

    # SECURITY: Do not hardcode secrets
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not client_secret:
        raise ValueError("Missing GOOGLE_CLIENT_SECRET environment variable")

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

def get_ref_tokens():
    tokens = []
    try:
        path = os.path.expanduser("~/.config/opencode/antigravity-accounts.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                accounts = data.get("accounts", [])
                for acc in accounts:
                    ref_token = acc.get("refreshToken")
                    if ref_token and ref_token not in tokens:
                        tokens.append(ref_token)
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
                    ref_token = secret_data.get("token", {}).get("refresh_token")
                    if ref_token and ref_token not in tokens:
                        tokens.append(ref_token)
    except Exception:
        pass
    return tokens

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

def fetch_quota_summary(token):
    url = "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary"
    req = urllib.request.Request(
        url,
        data=b"{}",
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
    import hashlib
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
            ref_tokens = get_ref_tokens()
            if not ref_tokens:
                raise Exception("No refresh tokens available")
            
            output = {"accounts": []}

            for idx, ref_token in enumerate(ref_tokens):
                # Use a hash of the refresh token to create a unique cache path
                token_hash = hashlib.sha256(ref_token.encode('utf-8')).hexdigest()[:16]
                cache_path = os.path.join(cache_dir, f"antigravity-auth-{token_hash}.json")

                try:
                    token, expiry = load_cached_token(cache_path)
                    if not token:
                        token, expires_in = refresh_token(ref_token)
                        save_cached_token(cache_path, token, expires_in)

                    summary = fetch_quota_summary(token)
                    
                    acc_output = {}
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
                                from datetime import datetime
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

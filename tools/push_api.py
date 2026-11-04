"""Push the project files to GitHub using the Git Data API (works when github.com HTTPS is blocked).

Usage: GH_TOKEN=... python -I tools/push_api.py OWNER REPO [BRANCH]
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
FILES = [
    ".gitignore",
    "README.md",
    "中国传统纹样资料汇编.md",
    "images/CREDITS.md",
    "images/met_images.json",
    "tools/extract.py",
    "tools/fetch_met.py",
    "tools/link_sources.py",
]


def request(method, path, data=None, token=None):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        API + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "motif-sourcebook",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"{method} {path} -> {exc.code}: {detail}") from exc


def main(owner, repo, branch="main"):
    token = os.environ["GH_TOKEN"]
    base = f"/repos/{owner}/{repo}"

    for root, _dirs, names in os.walk("images"):
        for name in sorted(names):
            if name.lower().endswith((".jpg", ".jpeg", ".png")):
                FILES.append(f"{root.replace(os.sep, '/')}/{name}")

    parent = None
    try:
        ref = request("GET", f"{base}/git/ref/heads/{branch}", token=token)
        parent = ref["object"]["sha"]
        print(f"parent commit: {parent}")
    except SystemExit as exc:
        if "-> 404:" not in str(exc) and "-> 409:" not in str(exc):
            raise
        print("no existing branch; creating initial commit")

    blobs = []
    for path in FILES:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("ascii")
        blob = request(
            "POST",
            f"{base}/git/blobs",
            {"content": content, "encoding": "base64"},
            token,
        )
        blobs.append({"path": path.replace(os.sep, "/"), "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print(f"blob {path}")

    tree = request("POST", f"{base}/git/trees", {"tree": blobs}, token)

    commit_data = {
        "message": "Add Chinese traditional motifs sourcebook with English glossary and source links",
        "tree": tree["sha"],
    }
    if parent:
        commit_data["parents"] = [parent]
    commit = request("POST", f"{base}/git/commits", commit_data, token)
    print(f"commit: {commit['sha']}")

    if parent:
        request("PATCH", f"{base}/git/refs/heads/{branch}", {"sha": commit["sha"], "force": True}, token)
    else:
        request("POST", f"{base}/git/refs", {"ref": f"refs/heads/{branch}", "sha": commit["sha"]}, token)
    print(f"updated refs/heads/{branch}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "main")

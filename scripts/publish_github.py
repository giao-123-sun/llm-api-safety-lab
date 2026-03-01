from __future__ import annotations

from pathlib import Path
import base64
import os
import re
import subprocess
import requests


def _run(cmd: list[str], cwd: str | None = None) -> None:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr}")


def _extract_token(path: str = "config/github_key.txt") -> str:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})", text)
    if not match:
        raise RuntimeError("No GitHub token found in config/github_key.txt")
    return match.group(1)


def _github_user(token: str) -> str:
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    r = requests.get("https://api.github.com/user", headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["login"]


def _ensure_repo(token: str, owner: str, repo: str) -> str:
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    get_r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=30)
    if get_r.status_code == 404:
        payload = {"name": repo, "private": False, "description": "Closed-loop LLM API safety research lab"}
        post_r = requests.post("https://api.github.com/user/repos", headers=headers, json=payload, timeout=30)
        post_r.raise_for_status()
    elif not get_r.ok:
        get_r.raise_for_status()
    return f"https://github.com/{owner}/{repo}"


def _enable_pages(token: str, owner: str, repo: str) -> str | None:
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    payload = {"source": {"branch": "main", "path": "/docs"}}
    r = requests.post(f"https://api.github.com/repos/{owner}/{repo}/pages", headers=headers, json=payload, timeout=30)
    if r.status_code in (201, 204, 409):
        return f"https://{owner}.github.io/{repo}/"
    return None


def _push_repo(owner: str, repo: str, token: str) -> None:
    if not Path(".git").exists():
        _run(["git", "init"])
    _run(["git", "add", "."])
    # Commit may fail if no changes; keep non-fatal.
    proc = subprocess.run(["git", "commit", "-m", "feat: add closed-loop llm api safety pipeline"], capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr)
    _run(["git", "branch", "-M", "main"])
    remote_url_public = f"https://github.com/{owner}/{repo}.git"
    remote_url_auth = f"https://{owner}:{token}@github.com/{owner}/{repo}.git"
    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True, text=True)
    _run(["git", "remote", "add", "origin", remote_url_auth])
    _run(["git", "push", "-u", "origin", "main", "--force"])
    _run(["git", "remote", "set-url", "origin", remote_url_public])


def main() -> None:
    token = _extract_token()
    owner = _github_user(token)
    repo = os.environ.get("LAB_REPO_NAME", "llm-api-safety-lab")
    repo_url = _ensure_repo(token, owner, repo)
    _push_repo(owner, repo, token)
    pages_url = _enable_pages(token, owner, repo)
    print(f"Repo URL: {repo_url}")
    if pages_url:
        print(f"Project URL: {pages_url}")
    else:
        print("Project URL: GitHub Pages enable request not confirmed. Use repo URL for now.")


if __name__ == "__main__":
    main()


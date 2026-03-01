from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class OpenRouterConfig:
    baseurl: str
    default_model: str
    api_key: str
    referer: str | None = None
    app_title: str | None = None
    proxy_url: str | None = None


def _parse_loose_kv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().strip('"').strip("'")] = value.strip().strip('"').strip("'")
    return values


def load_openrouter_config(path: str | Path = "config/key.txt") -> OpenRouterConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"OpenRouter config not found: {p}")
    values = _parse_loose_kv(p.read_text(encoding="utf-8", errors="replace"))
    baseurl = values.get("baseurl", "").rstrip("/")
    model = values.get("model_name", "")
    api_key = values.get("api_key", "")
    referer = values.get("HTTP-Referer")
    app_title = values.get("X-Title")
    proxy_url = values.get("proxy_url") or values.get("proxy")
    if not proxy_url:
        import os

        proxy_url = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if not baseurl or not model or not api_key:
        raise ValueError("config/key.txt must contain baseurl, model_name, api_key")
    return OpenRouterConfig(
        baseurl=baseurl,
        default_model=model,
        api_key=api_key,
        referer=referer or None,
        app_title=app_title or None,
        proxy_url=proxy_url or None,
    )


def load_github_token(path: str | Path = "config/github_key.txt") -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})", text)
    return match.group(1) if match else None

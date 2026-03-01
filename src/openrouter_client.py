from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config_loader import OpenRouterConfig


@dataclass
class ChatResult:
    text: str
    raw: dict


class OpenRouterClient:
    def __init__(self, config: OpenRouterConfig, timeout_s: int = 60) -> None:
        self._cfg = config
        self._timeout_s = timeout_s
        self._session = requests.Session()
        self._session.trust_env = False
        retry = Retry(
            total=4,
            connect=4,
            read=4,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._cfg.api_key}",
            "Content-Type": "application/json",
        }
        if self._cfg.referer:
            headers["HTTP-Referer"] = self._cfg.referer
        if self._cfg.app_title:
            headers["X-Title"] = self._cfg.app_title
        return headers

    def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: dict | None = None,
    ) -> ChatResult:
        payload = {
            "model": model or self._cfg.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        resp = self._session.post(
            f"{self._cfg.baseurl}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=self._timeout_s,
        )
        resp.raise_for_status()
        data = resp.json()
        text = self._extract_text(data)
        return ChatResult(text=text, raw=data)

    def generate_image(
        self,
        prompt: str,
        output_path: str | Path,
        model: str = "google/gemini-3.1-flash-image-preview",
    ) -> Path:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["text", "image"],
            "temperature": 0.4,
            "max_tokens": 800,
        }
        resp = self._session.post(
            f"{self._cfg.baseurl}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=self._timeout_s,
        )
        resp.raise_for_status()
        data = resp.json()
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        image_bytes = self._extract_image_bytes(data)
        out.write_bytes(image_bytes)
        return out

    @staticmethod
    def _extract_text(data: dict) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "\n".join(x for x in parts if x)
        return ""

    @staticmethod
    def _extract_image_bytes(data: dict) -> bytes:
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("No choices in image response")
        message = choices[0].get("message", {})
        images = message.get("images")
        if isinstance(images, list):
            for img in images:
                image_url = img.get("image_url", {})
                url = image_url.get("url", "")
                if url.startswith("data:image"):
                    return OpenRouterClient._decode_data_url(url)
                if url.startswith("http"):
                    dl = OpenRouterClient._sessionless_get(url)
                    dl.raise_for_status()
                    return dl.content
        content = message.get("content", [])
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "image":
                    url = item.get("image_url", "")
                    if isinstance(url, dict):
                        url = url.get("url", "")
                    if isinstance(url, str) and url.startswith("data:image"):
                        return OpenRouterClient._decode_data_url(url)
        raise ValueError("No image payload found")

    @staticmethod
    def _decode_data_url(url: str) -> bytes:
        try:
            payload = url.split(",", 1)[1]
            return base64.b64decode(payload)
        except Exception as exc:
            raise ValueError("Invalid data URL for image") from exc

    @staticmethod
    def _sessionless_get(url: str) -> requests.Response:
        # Download generated assets without inheriting host proxy settings.
        sess = requests.Session()
        sess.trust_env = False
        return sess.get(url, timeout=60)

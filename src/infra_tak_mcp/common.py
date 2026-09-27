from __future__ import annotations

import json
import os
from urllib.parse import urljoin

import httpx


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def cfg() -> dict[str, str]:
    return {
        "mtx": env("MTX_API", "http://127.0.0.1:9898"),
        "tak": env("TAK_MARTI", "https://127.0.0.1:8446"),
        "tak_user": env("TAK_USER"),
        "tak_pass": env("TAK_PASS"),
        "console": env("INFRATAK_URL", "https://127.0.0.1:5001"),
        "console_user": env("INFRATAK_USER"),
        "console_pass": env("INFRATAK_PASS"),
        "nodered": env("NODERED_URL", "http://127.0.0.1:1880"),
        "nodered_user": env("NODERED_USER"),
        "nodered_pass": env("NODERED_PASS"),
        "stream_host": env("STREAM_HOST", "stream.example.com"),
        "stream_proto": env("STREAM_PROTO", "rtsp"),
        "stream_port": env("STREAM_PORT", "8554"),
        "allow_docker": env("ALLOW_DOCKER", "1"),
    }


def verify() -> bool:
    return env("TLS_VERIFY", "0") not in {"0", "false", "no"}


def client() -> httpx.Client:
    return httpx.Client(timeout=30.0, verify=verify(), follow_redirects=True)


def fmt(r: httpx.Response) -> str:
    try:
        body = json.dumps(r.json(), indent=2)
    except Exception:
        body = r.text[:8000]
    return f"HTTP {r.status_code}\n{body}"


def console_login(http: httpx.Client, c: dict[str, str]) -> None:
    if not c["console_user"]:
        return
    base = c["console"].rstrip("/")
    payload = {"username": c["console_user"], "password": c["console_pass"]}
    for path, kwargs in (
        ("/login", {"data": payload}),
        ("/login", {"json": payload}),
        ("/api/login", {"json": payload}),
    ):
        try:
            r = http.post(urljoin(base + "/", path.lstrip("/")), **kwargs)
            if r.status_code < 400:
                return
        except Exception:
            continue


def auth_pair(user: str, password: str):
    return (user, password) if user else None

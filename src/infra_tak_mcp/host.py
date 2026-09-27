from __future__ import annotations

import json
import subprocess
from typing import Any
from urllib.parse import urljoin

from infra_tak_mcp import catalog
from infra_tak_mcp.common import auth_pair, cfg, client, fmt


def register(mcp) -> None:
    @mcp.tool()
    def stack_health() -> str:
        """Probe MediaMTX, Node-RED Admin, TAK Marti, and infra-TAK console."""
        c = cfg()
        out: dict[str, Any] = {
            "config": {k: v for k, v in c.items() if "pass" not in k},
            "marketplace_keys": list(catalog.MODULES),
        }
        probes = (
            ("mediamtx_info", urljoin(c["mtx"].rstrip("/") + "/", "v3/info")),
            ("nodered_settings", urljoin(c["nodered"].rstrip("/") + "/", "settings")),
            ("tak_marti", urljoin(c["tak"].rstrip("/") + "/", "Marti/api/version")),
            ("infratak", c["console"]),
        )
        with client() as http:
            for name, url in probes:
                try:
                    r = http.get(url)
                    out[name] = {"url": url, "status": r.status_code, "ok": r.is_success}
                except Exception as exc:
                    out[name] = {"url": url, "error": str(exc)}
        return json.dumps(out, indent=2)

    @mcp.tool()
    def mediamtx_paths() -> str:
        """List MediaMTX paths. infra-TAK binds the control API on :9898."""
        c = cfg()
        with client() as http:
            last = ""
            for path in ("v3/paths/list", "v2/paths/list"):
                url = urljoin(c["mtx"].rstrip("/") + "/", path)
                try:
                    r = http.get(url)
                    last = f"{url} -> {r.status_code}\n{fmt(r)}"
                    if r.is_success:
                        return last
                except Exception as exc:
                    last = f"{url} -> {exc}"
            return last or "MediaMTX API unreachable"

    @mcp.tool()
    def mediamtx_info() -> str:
        """MediaMTX server info."""
        c = cfg()
        with client() as http:
            for path in ("v3/info", "v2/info"):
                url = urljoin(c["mtx"].rstrip("/") + "/", path)
                try:
                    r = http.get(url)
                    if r.is_success:
                        return fmt(r)
                except Exception as exc:
                    return str(exc)
            return "MediaMTX info endpoint not found"

    @mcp.tool()
    def docker_ps() -> str:
        """List Docker containers (ALLOW_DOCKER=1)."""
        if cfg()["allow_docker"] not in {"1", "true", "yes"}:
            return "Docker disabled. Set ALLOW_DOCKER=1."
        try:
            p = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"],
                capture_output=True, text=True, timeout=15,
            )
        except FileNotFoundError:
            return "docker binary not found. Run this MCP on the TAK host."
        return p.stdout or p.stderr or "(no containers)"

    @mcp.tool()
    def docker_logs(name: str, tail: int = 80) -> str:
        """Tail logs for a Docker container."""
        if cfg()["allow_docker"] not in {"1", "true", "yes"}:
            return "Docker disabled. Set ALLOW_DOCKER=1."
        tail = max(1, min(int(tail), 400))
        p = subprocess.run(
            ["docker", "logs", "--tail", str(tail), name],
            capture_output=True, text=True, timeout=20,
        )
        text = (p.stdout or "") + (p.stderr or "")
        return text[-20000:] if text else f"no logs / exit {p.returncode}"

    @mcp.tool()
    def tak_list_videos() -> str:
        """List TAK Server Video Manager feeds."""
        c = cfg()
        url = urljoin(c["tak"].rstrip("/") + "/", "Marti/api/video")
        with client() as http:
            r = http.get(url, auth=auth_pair(c["tak_user"], c["tak_pass"]))
            return fmt(r)

    @mcp.tool()
    def tak_publish_video(path: str, alias: str = "") -> str:
        """Register a MediaMTX path on TAK Video Manager with decomposed fields."""
        c = cfg()
        path = path.lstrip("/")
        alias = alias or path
        uid = "VIDEO-" + "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in path)
        proto, host, port = c["stream_proto"], c["stream_host"], int(c["stream_port"])
        body = {
            "videoConnections": [{
                "uuid": uid, "active": True, "alias": alias,
                "feeds": [{
                    "uuid": uid + "-feed", "active": True, "alias": alias,
                    "protocol": proto, "address": host, "port": port,
                    "path": "/" + path,
                    "url": f"{proto}://{host}:{port}/{path}",
                    "networkTimeout": "5000", "bufferTime": "500",
                    "rtspReliable": "1", "type": "VIDEO",
                }],
            }]
        }
        url = urljoin(c["tak"].rstrip("/") + "/", "Marti/api/video")
        with client() as http:
            r = http.post(url, json=body, auth=auth_pair(c["tak_user"], c["tak_pass"]))
            return f"POST {url}\n{fmt(r)}"

    @mcp.tool()
    def advertise_ready_streams() -> str:
        """POST every ready MediaMTX path into TAK Video Manager."""
        raw = mediamtx_paths()
        posted = []
        try:
            data = json.loads(raw.split("\n", 1)[-1].replace("HTTP 200\n", "", 1))
            items = data.get("items") or data.get("paths") or []
        except Exception:
            return "could not parse MediaMTX paths:\n" + raw
        if not items:
            return "no ready paths\n" + raw
        for it in items:
            if isinstance(it, dict) and it.get("ready") and it.get("name"):
                posted.append({"path": it["name"], "result": tak_publish_video(it["name"])})
        return json.dumps(posted, indent=2)

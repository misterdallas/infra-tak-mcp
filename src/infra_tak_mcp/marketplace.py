from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

from infra_tak_mcp import catalog
from infra_tak_mcp.common import auth_pair, cfg, client, console_login, fmt


def register(mcp) -> None:
    @mcp.tool()
    def marketplace_list() -> str:
        """Catalog of infra-TAK marketplace module keys this MCP knows how to drive."""
        return json.dumps({"modules": catalog.known()}, indent=2)

    @mcp.tool()
    def marketplace_call(
        module: str,
        action: str,
        body_json: str = "",
        confirm: bool = False,
    ) -> str:
        """Call /api/<module>/<action> on the infra-TAK console.

        action: status | log | logs | version | update-status | start | stop |
        restart | deploy | uninstall | raw
        raw body_json: {"method":"GET","path":"deployment-config","json":{}}
        confirm=true required for deploy, uninstall, start, stop, restart.
        """
        c = cfg()
        key = catalog.normalize(module)
        base = catalog.api_base(key)
        action = (action or "status").lower().strip()
        destructive = action in {
            "deploy", "uninstall", "control-start", "control-stop",
            "control-restart", "start", "stop", "restart",
        }
        if destructive and not confirm:
            return json.dumps({"error": "confirm=true required", "module": key, "action": action})

        extra: dict[str, Any] = {}
        if body_json.strip():
            try:
                extra = json.loads(body_json)
            except json.JSONDecodeError as exc:
                return f"body_json is not valid JSON: {exc}"

        method, path, payload = "GET", "", None
        if action in {"status", "detect"}:
            path = "log"
        elif action in {"log", "logs", "version", "update-status"}:
            path = "log" if action == "log" else action
        elif action in {"start", "control-start"}:
            method, path, payload = "POST", "control", {"action": "start"}
        elif action in {"stop", "control-stop"}:
            method, path, payload = "POST", "control", {"action": "stop"}
        elif action in {"restart", "control-restart"}:
            method, path, payload = "POST", "control", {"action": "restart"}
        elif action == "deploy":
            method, path, payload = "POST", "deploy", extra or {}
        elif action == "uninstall":
            method, path, payload = "POST", "uninstall", extra or {}
            if "password" not in payload and c["console_pass"]:
                payload["password"] = c["console_pass"]
        elif action == "raw":
            method = str(extra.get("method", "GET")).upper()
            path = str(extra.get("path", "")).lstrip("/")
            payload = extra.get("json") if method != "GET" else None
        else:
            return f"unknown action {action}"

        url = urljoin(c["console"].rstrip("/") + "/", f"{base.strip('/')}/{path}".lstrip("/"))
        with client() as http:
            console_login(http, c)
            auth = auth_pair(c["console_user"], c["console_pass"])
            try:
                r = http.get(url, auth=auth) if method == "GET" else http.request(method, url, json=payload, auth=auth)
            except Exception as exc:
                return f"{method} {url} failed: {exc}"
            return f"{method} {url}\n{fmt(r)}"

    @mcp.tool()
    def marketplace_deploy(module: str, params_json: str = "{}", confirm: bool = False) -> str:
        """Start a marketplace deploy job. Poll marketplace_call(module, 'log')."""
        return marketplace_call(module, "deploy", params_json, confirm=confirm)

    @mcp.tool()
    def marketplace_control(module: str, action: str, confirm: bool = False) -> str:
        """Start, stop, or restart a marketplace module."""
        action = action.lower().strip()
        if action not in {"start", "stop", "restart"}:
            return "action must be start, stop, or restart"
        return marketplace_call(module, action, confirm=confirm)

    @mcp.tool()
    def marketplace_uninstall(module: str, admin_password: str = "", confirm: bool = False) -> str:
        """Uninstall a marketplace module. Requires confirm=true."""
        body = {"password": admin_password} if admin_password else {}
        return marketplace_call(module, "uninstall", json.dumps(body), confirm=confirm)

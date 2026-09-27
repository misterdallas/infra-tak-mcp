from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

from infra_tak_mcp.common import auth_pair, cfg, client, fmt


def _nr(http, c: dict[str, str], method: str, path: str, **kw):
    url = urljoin(c["nodered"].rstrip("/") + "/", path.lstrip("/"))
    return http.request(method, url, auth=auth_pair(c["nodered_user"], c["nodered_pass"]), **kw)


def register(mcp) -> None:
    @mcp.tool()
    def nodered_info() -> str:
        """Node-RED settings, diagnostics, and palette from the loopback Admin API."""
        c = cfg()
        with client() as http:
            chunks = []
            for path in ("settings", "diagnostics", "nodes"):
                try:
                    r = _nr(http, c, "GET", path)
                    chunks.append(f"## GET /{path}\n{fmt(r)}")
                except Exception as exc:
                    chunks.append(f"## GET /{path}\n{exc}")
            return "\n\n".join(chunks)

    @mcp.tool()
    def nodered_list_flows() -> str:
        """GET /flows from Node-RED Admin API on 127.0.0.1:1880."""
        c = cfg()
        with client() as http:
            try:
                r = _nr(http, c, "GET", "flows")
            except Exception as exc:
                return f"Node-RED unreachable at {c['nodered']}: {exc}"
            return fmt(r)

    @mcp.tool()
    def nodered_deploy_flows(flows_json: str, confirm: bool = False) -> str:
        """POST /flows and replace the running Node-RED document. confirm=true required."""
        if not confirm:
            return "confirm=true required — this replaces the running Node-RED flows"
        try:
            doc = json.loads(flows_json)
        except json.JSONDecodeError as exc:
            return f"flows_json is not valid JSON: {exc}"
        c = cfg()
        with client() as http:
            r = _nr(http, c, "POST", "flows", json=doc, headers={"Node-RED-Deployment-Type": "full"})
            return fmt(r)

    @mcp.tool()
    def nodered_add_flow(flow_json: str, confirm: bool = False) -> str:
        """Append nodes to the current flows and redeploy. confirm=true required."""
        if not confirm:
            return "confirm=true required"
        try:
            incoming = json.loads(flow_json)
        except json.JSONDecodeError as exc:
            return f"flow_json is not valid JSON: {exc}"
        c = cfg()
        with client() as http:
            cur = _nr(http, c, "GET", "flows")
            if cur.status_code >= 400:
                return f"cannot read current flows\n{fmt(cur)}"
            existing = cur.json()
            if isinstance(existing, dict) and "flows" in existing:
                nodes, wrap = list(existing["flows"]), True
            elif isinstance(existing, list):
                nodes, wrap = list(existing), False
            else:
                return f"unexpected flows shape\n{fmt(cur)}"
            add = incoming["flows"] if isinstance(incoming, dict) and "flows" in incoming else incoming
            if not isinstance(add, list):
                add = [add]
            nodes.extend(add)
            payload: Any = {"flows": nodes} if wrap else nodes
            r = _nr(http, c, "POST", "flows", json=payload, headers={"Node-RED-Deployment-Type": "full"})
            return fmt(r)

    @mcp.tool()
    def nodered_install_node(package: str, confirm: bool = False) -> str:
        """Install a palette package such as node-red-contrib-tak."""
        if not confirm:
            return "confirm=true required"
        c = cfg()
        with client() as http:
            r = _nr(http, c, "POST", "nodes", json={"module": package})
            return fmt(r)

    @mcp.tool()
    def nodered_inject(node_id: str) -> str:
        """Trigger an inject node by id."""
        c = cfg()
        with client() as http:
            r = _nr(http, c, "POST", f"inject/{node_id}")
            return fmt(r)

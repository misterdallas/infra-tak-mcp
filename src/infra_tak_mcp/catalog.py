"""Known infra-TAK marketplace keys and API conventions.

Core services live in app.py; add-on tiles live under modules/*.py.
API base is /api/<key>/ unless a module froze api_base.
"""

from __future__ import annotations

MODULES: dict[str, dict] = {
    "takserver": {
        "name": "TAK Server",
        "conflicts": [],
        "notes": "Client port 8089. Admin 8443 cert / 8446 password.",
    },
    "federationhub": {
        "name": "Federation Hub",
        "conflicts": [],
        "notes": "Optional TAK federation.",
    },
    "authentik": {
        "name": "Authentik",
        "conflicts": [],
        "notes": "SSO at tak.<domain>.",
    },
    "takportal": {
        "name": "TAK Portal",
        "conflicts": [],
        "notes": "User and cert enrollment.",
    },
    "caddy": {
        "name": "Caddy SSL",
        "conflicts": [],
        "notes": "Reverse proxy + Let's Encrypt.",
    },
    "cloudtak": {
        "name": "CloudTAK",
        "conflicts": [],
        "notes": "Browser TAK. MinIO store image may 401 on old Quay tags.",
    },
    "mediamtx": {
        "name": "MediaMTX",
        "conflicts": ["tvr"],
        "notes": "Control API 127.0.0.1:9898. Conflicts with TAK Video Restreamer.",
    },
    "tvr": {
        "name": "TAK Video Restreamer",
        "api_base": "/api/tak-video-restreamer",
        "conflicts": ["mediamtx"],
        "notes": "Shares streaming ports with MediaMTX.",
    },
    "nodered": {
        "name": "Node-RED",
        "conflicts": [],
        "notes": "Editor behind Authentik. Admin API on 127.0.0.1:1880.",
    },
    "emailrelay": {
        "name": "Email Relay",
        "conflicts": [],
        "notes": "Outbound SMTP.",
    },
    "guarddog": {
        "name": "Guard Dog",
        "conflicts": [],
        "notes": "Health monitor and auto-recovery.",
    },
    "cesium": {
        "name": "Cesium 3D Tiles",
        "conflicts": [],
        "notes": "",
    },
    "webodm": {
        "name": "WebODM",
        "conflicts": [],
        "notes": "",
    },
    "netbird": {
        "name": "NetBird",
        "conflicts": [],
        "notes": "Mesh VPN. Overlaps Tailscale TUN/CGNAT.",
    },
    "eudassist": {
        "name": "EUD Remote Assist",
        "conflicts": [],
        "notes": "",
    },
    "atlas": {
        "name": "ATLAS MDM",
        "conflicts": [],
        "notes": "Android MDM for ATAK tablets.",
    },
    "simulator": {
        "name": "TAK Simulator",
        "conflicts": [],
        "notes": "Scripted CoT load / demos.",
    },
    "clientfeed": {
        "name": "TAK Client Feed",
        "conflicts": [],
        "notes": "Publish connected clients as a map feed.",
    },
}

ALIASES = {
    "tak-video-restreamer": "tvr",
    "video-restreamer": "tvr",
    "node-red": "nodered",
    "node_red": "nodered",
    "media-mtx": "mediamtx",
    "mtx": "mediamtx",
    "tak-server": "takserver",
    "tak_server": "takserver",
    "fedhub": "federationhub",
    "federation-hub": "federationhub",
    "mdm": "atlas",
    "atlas-mdm": "atlas",
    "email-relay": "emailrelay",
    "guard-dog": "guarddog",
    "client-feed": "clientfeed",
}


def normalize(key: str) -> str:
    k = (key or "").strip().lower()
    return ALIASES.get(k, k)


def api_base(key: str) -> str:
    key = normalize(key)
    meta = MODULES.get(key, {})
    return meta.get("api_base") or f"/api/{key}"


def known() -> list[dict]:
    rows = []
    for key, meta in MODULES.items():
        rows.append(
            {
                "key": key,
                "name": meta["name"],
                "api_base": api_base(key),
                "conflicts": meta.get("conflicts") or [],
                "notes": meta.get("notes") or "",
            }
        )
    return rows

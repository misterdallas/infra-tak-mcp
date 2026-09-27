"""MCP server for an infra-TAK host."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from infra_tak_mcp import host, marketplace, nodered
from infra_tak_mcp.common import env

mcp = FastMCP(
    "infra-tak",
    instructions=(
        "Operate a full infra-TAK marketplace on the local host. "
        "Use marketplace_list then marketplace_call for any tile. "
        "Node-RED flows go through nodered_* tools on 127.0.0.1:1880. "
        "MediaMTX control API is 127.0.0.1:9898. "
        "Destructive module actions require confirm=true."
    ),
)

marketplace.register(mcp)
nodered.register(mcp)
host.register(mcp)


def main() -> None:
    transport = env("MCP_TRANSPORT", "stdio")
    if transport in {"http", "streamable-http", "sse"}:
        mcp.run(
            transport="streamable-http",
            host=env("MCP_HOST", "127.0.0.1"),
            port=int(env("MCP_PORT", "8765")),
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()

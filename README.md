# infra-tak-mcp

MCP server that drives an [infra-TAK](https://github.com/takwerx/infra-TAK) host from Cursor, Claude Desktop, Claude Code, or any MCP client.

It runs **on the Ubuntu TAK box** (or over SSH stdio) and talks to loopback APIs:

- infra-TAK console marketplace (`/api/<module>/...`)
- Node-RED Admin API (`http://127.0.0.1:1880`)
- MediaMTX control API (`http://127.0.0.1:9898`)
- TAK Server Marti video (`/Marti/api/video`)
- Docker

This is not an official takwerx product.

## Tools

### Marketplace

`marketplace_list`, `marketplace_call`, `marketplace_deploy`, `marketplace_control`, `marketplace_uninstall`

Known keys: `takserver`, `federationhub`, `authentik`, `takportal`, `caddy`, `cloudtak`, `mediamtx`, `tvr`, `nodered`, `emailrelay`, `guarddog`, `cesium`, `webodm`, `netbird`, `eudassist`, `atlas`, `simulator`, `clientfeed`.

`marketplace_call(..., action="raw")` hits extra module routes. Deploy / uninstall / start / stop / restart require `confirm=true`.

### Node-RED

`nodered_info`, `nodered_list_flows`, `nodered_add_flow`, `nodered_deploy_flows`, `nodered_install_node`, `nodered_inject`

Use the loopback Admin API. The public `https://nodered.<domain>` URL is Authentik, not the Admin API.

### Video / host

`stack_health`, `mediamtx_paths`, `mediamtx_info`, `tak_list_videos`, `tak_publish_video`, `advertise_ready_streams`, `docker_ps`, `docker_logs`.

## Install on the TAK host

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git
sudo git clone https://github.com/misterdallas/infra-tak-mcp.git /opt/infra-tak-mcp
cd /opt/infra-tak-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
nano .env
```

## MCP client (stdio over SSH)

```json
{
  "mcpServers": {
    "infra-tak": {
      "command": "ssh",
      "args": [
        "YOUR_USER@YOUR_TAK_HOST",
        "cd /opt/infra-tak-mcp && . .venv/bin/activate && set -a && . ./.env && set +a && python -m infra_tak_mcp.server"
      ]
    }
  }
}
```

Do not publish `:8765` or MediaMTX `:9898` on a public interface.

## License

MIT

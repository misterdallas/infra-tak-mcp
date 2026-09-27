# infra-tak-mcp

MCP server that drives an [infra-TAK](https://github.com/takwerx/infra-TAK) host from **Grok Build**, Cursor, Claude Desktop, or any MCP client.

Run it **on the Ubuntu TAK box**. Clients on a laptop speak **stdio over SSH**. Do not publish the MCP HTTP port or the MediaMTX control API.

This is not an official takwerx product.

## What it talks to

| Target | Where |
|---|---|
| infra-TAK marketplace | console `/api/<module>/...` |
| Node-RED Admin API | `http://127.0.0.1:1880` (not the public Authentik URL) |
| MediaMTX control API | `http://127.0.0.1:9898` (not 9997) |
| TAK Marti video | `/Marti/api/video` |
| Docker | local `docker` CLI |

## Install on the TAK host (Ubuntu 22.04)

`/opt` is root-owned. After a `sudo git clone`, chown the tree to your login user. Use a venv. **Do not** `pip install -e .` — Ubuntu 22.04 system pip has no PEP 660 editable hook.

Pin **MCP 1.x**. This server uses the FastMCP 1.x API. `mcp` 2.x breaks the Grok Build handshake.

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git
sudo git clone https://github.com/misterdallas/infra-tak-mcp.git /opt/infra-tak-mcp
sudo chown -R "$USER:$USER" /opt/infra-tak-mcp
cd /opt/infra-tak-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip setuptools wheel
pip install . -c constraints.txt
cp -n .env.example .env
nano .env
python -c "import mcp; print(mcp.__version__)"   # must be 1.x
```

One-shot:

```bash
curl -fsSL https://raw.githubusercontent.com/misterdallas/infra-tak-mcp/main/install.sh | sudo bash
```

## Grok Build (laptop)

Passwordless SSH first:

```bash
ssh-copy-id USER@TAK_HOST
ssh USER@TAK_HOST 'echo ok'
```

```bash
grok mcp add infra-tak -- ssh USER@TAK_HOST 'cd /opt/infra-tak-mcp && . .venv/bin/activate && set -a && . ./.env && set +a && python -m infra_tak_mcp.server'
grok mcp list
grok mcp doctor infra-tak
```

Or copy `mcp.grok.example.toml` into `~/.grok/config.toml`.

Do **not** add this server as a public custom connector on grok.com. That requires a reachable HTTPS URL and would expose marketplace deploy/stop.

## Cursor / Claude Desktop

See `mcp.cursor.example.json`.

## Tools

Marketplace: `marketplace_list`, `marketplace_call`, `marketplace_deploy`, `marketplace_control`, `marketplace_uninstall`

Keys: `takserver`, `federationhub`, `authentik`, `takportal`, `caddy`, `cloudtak`, `mediamtx`, `tvr`, `nodered`, `emailrelay`, `guarddog`, `cesium`, `webodm`, `netbird`, `eudassist`, `atlas`, `simulator`, `clientfeed`.

`action="raw"` hits extra module routes. Deploy / uninstall / start / stop / restart require `confirm=true`.

Node-RED: `nodered_info`, `nodered_list_flows`, `nodered_add_flow`, `nodered_deploy_flows`, `nodered_install_node`, `nodered_inject`

Host: `stack_health`, `mediamtx_paths`, `mediamtx_info`, `tak_list_videos`, `tak_publish_video`, `advertise_ready_streams`, `docker_ps`, `docker_logs`

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Permission denied: '.../.venv'` or `cp: cannot create '.env'` | `sudo chown -R "$USER:$USER" /opt/infra-tak-mcp` |
| `build_editable` / PEP 660 error | Use `pip install .` inside the venv, never `-e` |
| `Defaulting to user installation` | The venv is not active, or you used system pip |
| Grok Build handshake fails / doctor dies after connect | Host pulled `mcp` 2.x. `pip install --force-reinstall 'mcp[cli]>=1.9.0,<2'` |
| MediaMTX curl refused | Use `127.0.0.1:9898` on the TAK host, not 9997 and not the laptop |
| Node-RED tools 401/empty | Hit loopback `:1880`, not `https://nodered.<domain>` |

## License

MIT

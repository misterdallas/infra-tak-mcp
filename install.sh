#!/bin/bash
set -euo pipefail
DEST=${DEST:-/opt/infra-tak-mcp}
OWNER=${SUDO_USER:-$USER}

if [[ $EUID -ne 0 ]]; then
  echo "Run: sudo bash install.sh"
  exit 1
fi

apt-get update -y
apt-get install -y python3 python3-venv python3-pip git

if [[ ! -d $DEST/.git ]]; then
  git clone https://github.com/misterdallas/infra-tak-mcp.git "$DEST"
else
  git -C "$DEST" pull --ff-only || true
fi

chown -R "$OWNER:$OWNER" "$DEST"
su -s /bin/bash "$OWNER" -c "
  cd '$DEST'
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -U pip setuptools wheel
  pip install .
  test -f .env || cp .env.example .env
"

chmod 600 "$DEST/.env" || true
echo
echo "Installed for $OWNER in $DEST"
echo "Edit $DEST/.env then:"
echo "  cd $DEST && . .venv/bin/activate && python -m infra_tak_mcp.server"

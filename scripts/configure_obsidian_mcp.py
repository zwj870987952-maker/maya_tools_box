"""Configure the local Obsidian MCP plugin and Codex for this project vault.

Run only after the plugin release files have been placed in .obsidian/plugins/.
The generated token and Codex config stay local and are ignored by Git.
"""
from __future__ import annotations

import json
import secrets
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBSIDIAN = ROOT / ".obsidian"
PLUGIN = OBSIDIAN / "plugins" / "obsidian-local-rest-api"
CODEX_CONFIG = ROOT / ".codex" / "config.toml"
MCP_URL = "http://127.0.0.1:27123/mcp/"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    manifest = PLUGIN / "manifest.json"
    if not manifest.is_file() or not (PLUGIN / "main.js").is_file():
        raise SystemExit("Obsidian Local REST API plugin files are missing.")
    plugin_id = json.loads(manifest.read_text(encoding="utf-8"))["id"]
    if plugin_id != "obsidian-local-rest-api":
        raise SystemExit("Unexpected Obsidian plugin ID: " + plugin_id)

    enabled_path = OBSIDIAN / "community-plugins.json"
    enabled = json.loads(enabled_path.read_text(encoding="utf-8")) if enabled_path.exists() else []
    if not isinstance(enabled, list):
        raise SystemExit("Invalid community-plugins.json")
    if plugin_id not in enabled:
        enabled.append(plugin_id)
    write_json(enabled_path, enabled)

    settings_path = PLUGIN / "data.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
    if not isinstance(settings, dict):
        raise SystemExit("Invalid Obsidian plugin settings")
    token = settings.get("apiKey")
    if not isinstance(token, str) or not token:
        token = secrets.token_hex(32)
    settings.update({
        "apiKey": token,
        "port": 27124,
        "insecurePort": 27123,
        "enableInsecureServer": True,
        "enableSecureServer": False,
        "bindingHost": "127.0.0.1",
        "enableSignedUrls": False,
    })
    write_json(settings_path, settings)

    CODEX_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    section = (
        "[mcp_servers.obsidian]\n"
        + 'url = "{}"\n'.format(MCP_URL)
        + 'http_headers = {{ Authorization = "Bearer {}" }}\n'.format(token)
        + "startup_timeout_sec = 20\n"
        + "tool_timeout_sec = 45\n"
    )
    if CODEX_CONFIG.exists():
        old = CODEX_CONFIG.read_text(encoding="utf-8")
        if "[mcp_servers.obsidian]" not in old:
            CODEX_CONFIG.write_text(old.rstrip() + "\n\n" + section, encoding="utf-8")
        elif section not in old:
            raise SystemExit("Existing Obsidian MCP config differs; edit it manually to avoid overwriting other settings.")
    else:
        CODEX_CONFIG.write_text(section, encoding="utf-8")
    print("Obsidian MCP plugin and project Codex config prepared.")
    print("MCP URL: " + MCP_URL)


if __name__ == "__main__":
    main()

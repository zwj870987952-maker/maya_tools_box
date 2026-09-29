"""Verify the local Obsidian MCP service without displaying the API key."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".obsidian/plugins/obsidian-local-rest-api/data.json"
URL = "http://127.0.0.1:27123/mcp/"
PROTOCOL = "2025-11-25"


def request(payload, key, session=None):
    headers = {
        "Authorization": "Bearer " + key,
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": PROTOCOL,
    }
    if session:
        headers["Mcp-Session-Id"] = session
    data = json.dumps(payload).encode("utf-8")
    with urlopen(Request(URL, data=data, headers=headers), timeout=10) as response:
        body = response.read().decode("utf-8")
        session = response.headers.get("Mcp-Session-Id") or session
    event = next((line[6:] for line in body.splitlines() if line.startswith("data: ")), None)
    return (json.loads(event) if event else None), session


def main():
    if not SETTINGS.is_file():
        raise SystemExit("Missing plugin settings. Run scripts/setup_obsidian_vault.ps1 first.")
    key = json.loads(SETTINGS.read_text(encoding="utf-8")).get("apiKey")
    if not key:
        raise SystemExit("Missing Obsidian API key. Run scripts/setup_obsidian_vault.ps1 first.")
    try:
        init, session = request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": "maya-tools-box-check", "version": "1.0"},
            },
        }, key)
        if not session or not init or "result" not in init:
            raise ValueError("MCP initialization failed")
        request({"jsonrpc": "2.0", "method": "notifications/initialized"}, key, session)
        listed, _ = request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, key, session)
        tools = listed["result"]["tools"]
        if "vault_read" not in {tool["name"] for tool in tools}:
            raise ValueError("vault_read is unavailable")
        read, _ = request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "vault_read", "arguments": {"path": "knowledge/00-首页.md"}},
        }, key, session)
        result = read["result"]
        if result.get("isError"):
            raise ValueError("vault_read returned an error")
        note = json.loads(next(item["text"] for item in result["content"] if item["type"] == "text"))
        if "# Maya Tools Box 知识库" not in note["content"]:
            raise ValueError("MCP read the wrong vault or homepage")
    except (HTTPError, URLError, OSError, KeyError, StopIteration, ValueError) as exc:
        raise SystemExit("Obsidian MCP check failed: {}".format(exc))
    print("Obsidian MCP connected: {} tools; knowledge homepage readable.".format(len(tools)))


if __name__ == "__main__":
    main()

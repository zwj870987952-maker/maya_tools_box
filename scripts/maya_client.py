"""Helper client to invoke Python in live Maya instance via DCC MCP Gateway REST API."""
import json
import re
import sys
import urllib.error
import urllib.request

GATEWAY_URL = "http://127.0.0.1:9765"


def get_execute_python_slug():
    req = urllib.request.Request(
        f"{GATEWAY_URL}/v1/search",
        data=json.dumps({"query": "execute_python"}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode("utf-8")
        try:
            data = json.loads(content)
            hits = data.get("hits", [])
            if hits:
                return hits[0]["tool_slug"]
        except Exception:
            pass
        match = re.search(r"tool_slug:\s*([^\s]+)", content)
        if match:
            return match.group(1).strip()
        match = re.search(r'"tool_slug":\s*"([^"]+)"', content)
        if match:
            return match.group(1).strip()
        raise RuntimeError(f"Could not parse tool slug from search response: {content}")


def execute_python_in_maya(code: str) -> dict:
    slug = get_execute_python_slug()
    payload = {
        "tool_slug": slug,
        "arguments": {"code": code}
    }
    req = urllib.request.Request(
        f"{GATEWAY_URL}/v1/call",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read().decode("utf-8")
            try:
                return json.loads(content)
            except Exception:
                return {"raw": content}
    except urllib.error.HTTPError as error:
        err_body = error.read().decode("utf-8", errors="replace")
        return {"http_code": error.code, "error_body": err_body}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        code_file = sys.argv[1]
        with open(code_file, "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    result = execute_python_in_maya(code)
    print(json.dumps(result, ensure_ascii=False, indent=2))

from __future__ import annotations

import argparse
import json
import sys
import urllib.request


RPC = "http://127.0.0.1:23119/better-bibtex/json-rpc"


def search(query: str) -> list[dict]:
    payload = json.dumps(
        {"jsonrpc": "2.0", "method": "item.search", "params": [query], "id": 1}
    ).encode()
    request = urllib.request.Request(
        RPC, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
        request, timeout=15
    ) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result.get("result", [])


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Probe the Better BibTeX JSON-RPC API.")
    parser.add_argument("query", help="A real citation key or title fragment")
    args = parser.parse_args()
    try:
        matches = search(args.query)
    except Exception as exc:
        raise SystemExit(f"Better BibTeX probe failed: {exc}") from exc
    if not matches:
        raise SystemExit(f"Better BibTeX probe found no item for: {args.query}")
    print(json.dumps({"connected": True, "query": args.query, "matches": matches}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

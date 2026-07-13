from __future__ import annotations

import argparse
import json
import sys
import urllib.request


RPC = "http://127.0.0.1:23119/better-bibtex/json-rpc"


def search(query: str) -> list[dict]:
    payload = json.dumps({"jsonrpc": "2.0", "method": "item.search", "params": [query], "id": 1}).encode()
    request = urllib.request.Request(RPC, data=payload, headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=15) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result.get("result", [])


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Test Better BibTeX JSON-RPC and optionally search the Zotero library.")
    parser.add_argument("query", nargs="?", help="Citation key, title, author/year phrase, or other search text")
    args = parser.parse_args()
    try:
        results = search(args.query or "__better_bibtex_connection_test__")
    except Exception as exc:
        raise SystemExit(f"Better BibTeX connection failed: {exc}") from exc
    print(json.dumps({"connected": True, "query": args.query, "matches": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

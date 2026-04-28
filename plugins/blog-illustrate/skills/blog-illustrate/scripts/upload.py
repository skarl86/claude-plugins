#!/usr/bin/env python3
"""
Upload PNG (or other image) to blog MCP via raw HTTP.

base64 인코딩 결과를 conversation 컨텍스트에 노출시키지 않으려고 별도 프로세스로 격리.
한 번에 여러 장을 처리하려면 --batch 모드 사용 (JSON 파일에 [{file,name,alt}, ...]).

설정:
  - blog MCP URL과 API token은 환경변수로 받음:
      BLOG_MCP_URL    (예: https://your-blog.vercel.app/mcp)
      BLOG_MCP_TOKEN  (예: blg_live_...)
  - 또는 .mcp.json 의 blog 항목에서 자동 추출 시도 (CWD 기준)

사용:
  # 한 장 업로드
  python3 upload.py --file path/to/img.png --name post-001-diagram.png --alt "설명"

  # 여러 장 batch
  python3 upload.py --batch jobs.json
  # jobs.json 형식:
  # [
  #   {"file": "img1.png", "name": "post-001-a.png", "alt": "..."},
  #   {"file": "img2.png", "name": "post-001-b.png", "alt": "..."}
  # ]

출력: JSON. 각 항목 {name, url} 또는 {name, error}.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.request
from pathlib import Path


def load_mcp_config() -> tuple[str, str]:
    """ENV 우선, 없으면 .mcp.json 의 blog 항목에서 추출."""
    url = os.environ.get("BLOG_MCP_URL")
    token = os.environ.get("BLOG_MCP_TOKEN")
    if url and token:
        return url, token

    # walk upward looking for .mcp.json
    cur = Path.cwd().resolve()
    for parent in [cur, *cur.parents]:
        cfg_path = parent / ".mcp.json"
        if not cfg_path.exists():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
            blog = cfg.get("mcpServers", {}).get("blog", {})
            url = url or blog.get("url")
            auth = blog.get("headers", {}).get("Authorization", "")
            if auth.startswith("Bearer "):
                token = token or auth.removeprefix("Bearer ")
            if url and token:
                return url, token
        except (json.JSONDecodeError, OSError):
            continue
    raise RuntimeError(
        "blog MCP URL/token not found. Set BLOG_MCP_URL + BLOG_MCP_TOKEN, "
        "or run from a workspace containing .mcp.json with a 'blog' entry."
    )


def call_tool(url: str, token: str, name: str, args: dict, request_id: int) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": name, "arguments": args},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
    # SSE-style 응답도 처리
    if body.startswith("event:") or "\ndata: " in body:
        for line in body.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])
    return json.loads(body)


def upload_one(url: str, token: str, file_path: str, filename: str, alt: str, rid: int) -> dict:
    src = Path(file_path)
    if not src.exists():
        return {"name": filename, "error": f"file not found: {file_path}"}
    mime, _ = mimetypes.guess_type(src.name)
    mime = mime or "image/png"
    raw = src.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    size_mb = len(raw) / (1024 * 1024)
    print(f"  uploading {filename} ({size_mb:.2f} MB, {mime})", file=sys.stderr)
    try:
        resp = call_tool(url, token, "upload_media", {
            "filename": filename,
            "content_base64": b64,
            "mime": mime,
            "alt": alt,
        }, rid)
    except Exception as e:
        return {"name": filename, "error": str(e)}

    public_url = None
    if "result" in resp:
        sc = resp["result"].get("structuredContent") or {}
        public_url = sc.get("url")
        if not public_url:
            for item in resp["result"].get("content", []):
                if item.get("type") == "text":
                    try:
                        public_url = json.loads(item["text"]).get("url")
                    except json.JSONDecodeError:
                        public_url = item["text"]
        if resp["result"].get("isError"):
            return {"name": filename, "error": public_url or "upload failed"}
    return {"name": filename, "url": public_url}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", help="single file to upload")
    ap.add_argument("--name", help="upload filename")
    ap.add_argument("--alt", default="", help="alt text")
    ap.add_argument("--batch", help="JSON file with list of {file, name, alt}")
    args = ap.parse_args()

    url, token = load_mcp_config()

    jobs: list[tuple[str, str, str]] = []
    if args.batch:
        for j in json.loads(Path(args.batch).read_text()):
            jobs.append((j["file"], j.get("name") or Path(j["file"]).name, j.get("alt", "")))
    elif args.file:
        jobs.append((args.file, args.name or Path(args.file).name, args.alt))
    else:
        ap.error("specify --file or --batch")

    results = [upload_one(url, token, f, n, a, i + 1) for i, (f, n, a) in enumerate(jobs)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all("url" in r for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

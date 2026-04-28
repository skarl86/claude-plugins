#!/usr/bin/env bash
# Local HTTP server helper for blog-illustrate.
#
# Playwright는 file:// 프로토콜을 차단하므로 HTML 템플릿을 http://127.0.0.1:8765/ 로 띄워야 한다.
# 이 스크립트는 작업 디렉토리(인자로 받음)에서 backgound python http.server 를 시작한다.
#
# 사용:
#   bash scripts/serve.sh /path/to/work-dir [port]
#   # → http://127.0.0.1:<port>/  에서 디렉토리 내용 서비스
#
# 종료:
#   lsof -i :8765 | awk 'NR>1{print $2}' | xargs kill
#
# 주의:
# - cwd가 곧 server root. _common.css 같은 sibling 파일이 함께 있어야 함.
# - 같은 포트로 두 번 띄우면 두 번째 프로세스는 실패. 먼저 lsof로 확인 권장.

set -euo pipefail

WORK="${1:?usage: serve.sh <dir> [port]}"
PORT="${2:-8765}"

if [[ ! -d "$WORK" ]]; then
  echo "ERROR: directory not found: $WORK" >&2
  exit 2
fi

if lsof -i :"$PORT" >/dev/null 2>&1; then
  echo "WARN: port $PORT already in use. Reusing." >&2
  echo "  → tear down with: lsof -i :$PORT | awk 'NR>1{print \$2}' | xargs kill" >&2
  exit 0
fi

cd "$WORK"
nohup python3 -m http.server "$PORT" >/dev/null 2>&1 &
disown
sleep 1

if curl -sIf "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
  echo "Server up: http://127.0.0.1:$PORT/  (root: $WORK)"
else
  echo "ERROR: server failed to start on :$PORT" >&2
  exit 3
fi

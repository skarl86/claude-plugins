# blog-illustrate

블로그 글에 어울리는 일러스트레이션을 한 번의 워크플로우로 만든다 — HTML/CSS 템플릿으로 디자인 → Playwright로 PNG 렌더 → blog MCP로 업로드 → 본문에 image reference 삽입.

스크린샷 원본이 없거나 회사 내부 식별자가 섞여 있어 그대로 못 쓰는 경우, 모든 값을 의사값으로 일반화한 깔끔한 다이어그램을 일관된 톤으로 만들어 준다.

## When to use

- text-only draft를 검토하면서 "여기에 그림이 들어가면 좋을지" 판단이 필요할 때
- 폴더 구조 / 의사결정 트리 / before-after 비교 / 다층 방어 같은 컨셉을 시각화하고 싶을 때
- 기존 게시글에 일러스트를 추가/교체할 때
- 원본 스크린샷에 PII나 내부 경로가 노출되어 그대로 못 쓰는 상황

## How it triggers

이런 표현을 만나면 자동 트리거:

- "블로그 글에 그림 좀 넣어줘"
- "mockup 만들어줘"
- "다이어그램 추가해줘"
- "시각화 해줘"
- "이 부분 일러스트로"

## Workflow (6 steps)

1. **Identify** — draft 읽고 시각화 후보 위치 추출 (보통 3~5곳)
2. **Confirm** — 사용자에게 후보 표 제시, OK 받기
3. **Design** — 5종 시작 템플릿 중 선택해 콘텐츠 채움
4. **Render** — local HTTP 서버 + Playwright headless로 PNG 추출
5. **Upload** — `scripts/upload.py`로 blog MCP에 업로드, public URL 회수
6. **Insert** — `update_post`로 본문에 image reference 삽입

자세한 가이드는 `SKILL.md` 참조.

## Templates

| 템플릿 | 용도 |
|---|---|
| `terminal-single.html` | 단일 터미널 패널 (명령 + 폴더 트리 등) |
| `terminal-dual.html` | 좌우 두 터미널 (모니터링 setup, before/after) |
| `decision-tree.html` | 게이트 → 분기 → 결과 노드 (의사결정 흐름) |
| `comparison-cards.html` | 두 컬럼 카드 (without/with 비교) |
| `mapping-diagram.html` | 좌측 ↔ 우측 매핑 (folder → DB row 등) |
| `layered-defense.html` | 위→아래 layer 적층 (다층 방어) |

## Design tone

Dracula-inspired dark theme + macOS terminal chrome. 한 시리즈 안에서 글마다 같은 톤 유지.

색 토큰·타이포·viewport 사이즈 가이드는 `references/style-guide.md` 참조.

## Setup

### 1. Playwright MCP

스킬은 Playwright MCP 도구로 PNG를 렌더링한다 (`mcp__plugin_playwright_playwright__browser_*`). 공식 Playwright MCP 플러그인이 활성화되어 있어야 함.

### 2. blog MCP

`scripts/upload.py`가 blog MCP의 `upload_media` tool을 raw HTTP로 호출한다. 두 가지 방식 중 하나로 자격증명 제공:

**환경변수**:
```bash
export BLOG_MCP_URL="https://your-blog.example.com/mcp"
export BLOG_MCP_TOKEN="blg_live_xxxxx"
```

**.mcp.json 자동 추출** (workspace 안에서 호출 시):
```jsonc
{
  "mcpServers": {
    "blog": {
      "type": "http",
      "url": "https://your-blog.example.com/mcp",
      "headers": { "Authorization": "Bearer blg_live_xxxxx" }
    }
  }
}
```

블로그 측은 `upload_media`, `update_post` 같은 tool을 노출해야 함. 본 스킬은 특정 블로그 구현에 종속되지 않도록 raw HTTP로 호출.

### 3. Python deps

`scripts/upload.py`는 표준 라이브러리만 사용 — 추가 설치 불필요.

## Example invocation

```
/blog-illustrate post id <uuid> 에 다이어그램 3장 추가
/blog-illustrate 이 draft 검토 (markdown 첨부)
/blog-illustrate 이중 안전장치 부분 시각화
```

스킬은 매 단계에서 사용자 확인을 한 번 거치므로 (후보 식별 → 샘플 1장 → 일괄), "전부 알아서 진행" 모드를 원하면 명시 필요.

## Sample output

| 종류 | 예시 |
|---|---|
| terminal-dual | 좌측에 스킬 실행 / 우측에 모니터링 화면 — Stage 진행률, 자동 수집된 개선점 박스 |
| decision-tree | 게이트 → "audit 결과는?" → 0건 / N건+커버됨 / N건+커버못함 3분기 |
| comparison-cards | "without skill (반나절)" vs "within skill (한두 시간)" 두 카드 |
| mapping-diagram | 좌측 폴더 트리 → 우측 DB 테이블 (각 .md → row tag) |
| layered-defense | 위험 시나리오 → LAYER 1~4 차단 → "안전 ✓" |

## Pitfalls captured

- **file:// 차단**: Playwright는 `file:///` URL 거부. 반드시 local HTTP 서버 경유 (`scripts/serve.sh`).
- **server cwd**: `python3 -m http.server`는 cwd를 root로 함. HTML 파일이 있는 디렉토리에서 시작해야 `_common.css` 가 로드됨.
- **viewport vs content height**: viewport height가 content보다 크면 fullPage screenshot에 빈 영역 포함. height를 content에 맞춰 조정 (1~2회 시행착오 OK).
- **nested grid+flex 폭 안 늘어남**: grid column 안의 flex item에서 width가 의도대로 안 늘어나면 `align-self: stretch; width: 100% !important; max-width: none !important` 강제.
- **base64 컨텍스트 부담**: 이미지 base64 직접 conversation에 띄우지 말고 항상 Python script로 격리해서 MCP 호출.
- **PII / 내부 식별자**: 모든 값 의사값으로. 실제 사건 식별자·실제 함수명·실제 파일 경로·내부 워크트리 이름 노출 금지.

## License

MIT

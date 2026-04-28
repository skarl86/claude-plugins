---
name: blog-illustrate
description: |
  블로그 글에 어울리는 일러스트레이션(다이어그램·터미널 mockup·비교 카드·의사결정 트리 등)을
  HTML/CSS로 디자인 → Playwright로 PNG 렌더링 → blog MCP로 업로드 → 본문에 image
  reference 삽입까지 처리하는 스킬. 모든 값은 의사값/일반화로 — 회사 내부 식별자 노출 금지.

  다음 상황에서 적극적으로 사용:
  - "블로그 글에 그림 좀 넣어줘", "mockup 만들어줘", "다이어그램 추가", "시각화 해줘"
  - text-only draft를 검토하면서 어디에 그림이 들어가면 좋을지 후보 식별이 필요할 때
  - 기존 게시글에 일러스트를 추가/교체할 때
  - 스크린샷 원본은 없지만 "이런 장면을 시각화하고 싶다" 는 의도가 있을 때
argument-hint: "<블로그 글 markdown 또는 post id> + (선택) 추가 지시"
trigger:
  - "블로그.*그림"
  - "mockup"
  - "다이어그램.*추가"
  - "시각화"
  - "일러스트"
---

<Purpose>
블로그 글에 들어갈 일러스트레이션을 일관된 스타일로 생성한다. 한 글에 보통 3~5장.

원칙:
- 텍스트로 길게 설명하기 어려운 구조(매핑·트리·다층 방어 등)만 시각화. 이미 잘 흐르는 산문은 건드리지 않는다.
- 모든 값은 의사값/일반화. 회사 내부 식별자(주문번호·실제 함수명·workspace 경로 등) 노출 금지.
- 톤 통일: dark terminal aesthetic + macOS 윈도우 chrome (Dracula-inspired 색감). 한 시리즈 안에서 글마다 같은 톤 유지.
</Purpose>

<Use_When>
- 사용자가 글 draft를 보여주며 "그림 검토" / "그림 추가" 요청
- 본 스킬이 만든 기존 일러스트의 톤·내용 조정
- 다른 스킬/사람이 만든 글에 일러스트 추가
</Use_When>

<Workflow>
6단계로 진행. 각 단계 끝에 사용자 확인 1회 권장 (한꺼번에 5장 만들어 놓고 다 틀리면 비용 큼).

## 1. Identify — 후보 식별

draft를 읽으면서 시각화 후보 위치를 추출한다. 보통 한 글에 3~5곳.

**그림이 의미 있는 신호**:
- 텍스트로 폴더 구조나 매핑을 길게 설명하는 부분
- 표가 아니라 트리/흐름인 분기 로직
- 여러 옵션·시나리오를 비교하는 표 (시각적 대비가 더 강함)
- "이중 안전장치", "다층 방어", "before vs after" 같은 layered/대비 컨셉
- 단계 진행 (timeline, lifecycle)

**그림이 필요 없는 곳** (Skip):
- 도입부 (텍스트 흐름이 더 자연스러움)
- 단순 bullet list (그림으로 바꿔도 정보량 동일)
- 이미 다른 시각 자료가 가까이 있는 섹션
- 한두 줄짜리 짧은 인용/제스처

## 2. Confirm — 사용자에게 후보 표 제시

후보 식별 결과를 다음 형식의 표로 보여주고 OK 받는다:

| # | 위치 (섹션/문장 인용) | 그림 형태 | 가치 |
|---|---|---|---|
| A | "설계 결정 1 ... DB row" | 좌↔우 매핑 다이어그램 | ⭐⭐⭐ |

가치는 ⭐~⭐⭐⭐로 표기. 사용자가 "A·B만" / "전부" / 개별 선택할 수 있게.

## 3. Design — 템플릿 선택 + 콘텐츠 채움

`templates/` 의 5종 시작 템플릿 중 하나를 선택해 복사 후 콘텐츠만 바꾼다.

| 템플릿 | 용도 |
|---|---|
| `terminal-single.html` | 단일 터미널 패널 (스킬 호출 + 폴더 트리, 명령 출력 등) |
| `terminal-dual.html` | 좌우 두 터미널 (모니터링 setup, before/after 등) |
| `decision-tree.html` | 게이트 → 분기 → 결과 노드 (의사결정 흐름) |
| `comparison-cards.html` | 두 컬럼 카드 (without/with 비교) |
| `mapping-diagram.html` | 좌측 ↔ 우측 매핑 (예: 폴더 → DB row) |
| `layered-defense.html` | 위에서 아래로 layer 적층 (다층 방어) |

모든 템플릿은 `_common.css` import. 색상 토큰·타입 시스템은 거기에 정의.
새 형태가 필요하면 `_common.css`의 토큰을 그대로 쓰면서 새 HTML 작성.

## 4. Render — local HTTP 서버 + Playwright

```bash
# work 디렉토리로 templates를 복사 후 서버 기동
WORK=/tmp/illustrate-$(date +%s)
mkdir -p "$WORK"
cp -r .claude/skills/blog-illustrate/templates/* "$WORK/"
cd "$WORK" && nohup python3 -m http.server 8765 >/dev/null 2>&1 & disown
```

**중요**: Playwright는 `file://` 프로토콜 차단. 반드시 `http://127.0.0.1:8765/` 경유.

```
mcp__plugin_playwright_playwright__browser_resize(width=<W>, height=<H>)
mcp__plugin_playwright_playwright__browser_navigate(url="http://127.0.0.1:8765/<file>.html")
mcp__plugin_playwright_playwright__browser_take_screenshot(filename="<name>.png", fullPage=true, type="png")
```

viewport size 가이드:
- 콘텐츠 높이에 맞게 조정 (너무 크면 fullPage 결과에 빈 영역). 이상적 height = 콘텐츠 + 상하 padding ~80px
- 가로: 단일 카드 880~920, 2분할 1240~1320, 3분할 1100~1140

## 5. Upload — blog MCP

`scripts/upload.py` 사용:
```bash
python3 .claude/skills/blog-illustrate/scripts/upload.py \
  --file <png-path> --name <slug>.png --alt "<설명>"
# 출력: 업로드된 public URL
```

여러 장은 한 Python 프로세스로 처리해 base64를 conversation에 노출시키지 않는다. 자세한 호출 패턴은 스크립트 상단 주석 참조.

## 6. Insert — 본문에 image reference

`mcp__blog__update_post` 호출. body_md 안에 `![alt](url)` 형식으로 자연스러운 위치에 삽입.

이미지 위에/아래 한두 문장은 그림과 본문을 잇는 brige 역할. 그냥 이미지만 던지지 말고 "위 도식이 ~을 보여준다" 식의 한 줄 추가.
</Workflow>

<Identification_Examples>
실제 사례 (참고용 — 그대로 복붙 금지, 매번 글에 맞게 식별):

| 글 유형 | 후보 위치 |
|---|---|
| "스킬을 어떻게 만들었나" 류 | 폴더 구조 / 의사결정 트리 / 안전장치 도식 |
| "검증·회귀 테스트" 류 | setup 다이어그램 / before-after 비교 / 결과 표 |
| "아키텍처 결정" 류 | before-after 시스템도 / 데이터 흐름 / 트레이드오프 표 |
| "라이브러리 사용법" 류 | API 호출 시퀀스 / 객체 관계도 |
</Identification_Examples>

<Style_Guide>
자세한 토큰: `references/style-guide.md`

핵심:
- 배경: 다크 카드 `#1e1e2e`, 페이지 `linear-gradient(135deg, #f5f7fa 0%, #e8ecf4 100%)`
- 폰트: 본문 `'SF Pro Text'`, 코드 `'SF Mono'` / `'JetBrains Mono'`
- 색 (Dracula-inspired):
  - 폴더 `#8be9fd` (cyan, bold)
  - 명령 `#f1fa8c` (yellow)
  - 주석 `#6272a4` (italic gray)
  - OK `#50fa7b` (green)
  - warn `#ffb86c` (orange)
  - bad `#ff5555` (red)
  - keyword `#bd93f9` (purple, bold)
  - arrow `#ff79c6` (pink, bold)
- 카드: `border-radius: 12px`, `box-shadow: 0 14px 36px -10px rgba(20,30,60,0.22)`
- macOS terminal chrome: traffic-light dots (red/yellow/green), title bar에 path 표시
</Style_Guide>

<Pitfalls>
- **file:// 차단**: Playwright는 `file:///` URL 거부. 반드시 local HTTP 서버 경유.
- **server cwd**: `python3 -m http.server`는 cwd를 root로 함. HTML 파일이 있는 디렉토리에서 시작해야 `_common.css` 가 로드됨.
- **viewport vs content height**: viewport height가 content보다 크면 fullPage screenshot에 빈 영역 포함. height를 content에 가깝게 조정 (시행착오 1~2회 OK).
- **nested grid+flex 폭 안 늘어남**: grid column 안의 flex item에서 width가 의도대로 안 늘어나면 `align-self: stretch; width: 100% !important; max-width: none !important` 강제.
- **base64 컨텍스트 부담**: 이미지 base64는 한 장에 1.5MB 단위. 직접 conversation에 띄우지 말고 항상 Python script로 격리해서 MCP 호출.
- **PNG 원본 그대로**: 1~1.5MB 정도면 그대로 업로드 (10MB 제한 안에 들어옴). 압축으로 픽셀 손실보다 원본 가독성 우선.
- **PII / 내부 식별자**: 모든 값 의사값으로. 실제 사건 주문번호·실제 함수명·실제 파일 경로·내부 워크트리 이름 노출 금지. 일반화된 placeholder로 대체.
- **MCP tool prefix**: blog MCP를 raw HTTP로 호출할 땐 tool name에 `mcp__blog__` prefix 금지 (서버는 raw `upload_media` 만 인식).
- **fullPage screenshot**: 항상 `fullPage=true`로. 안 그러면 viewport 높이로 잘림.
</Pitfalls>

<Confirmation_Pattern>
대규모 작업이라 사용자 확인 단계를 두 번 둠:

1. **후보 식별 직후** — 후보 표 보여주고 OK / 추가 / 제거
2. **샘플 1장 렌더 직후** — 톤·내용 OK 받기. 여기서 어긋나면 나머지 4장 만들기 전에 수정. 한꺼번에 5장 만들고 다 다시 만드는 비용 절감.

3장 다 OK 후에야 일괄 업로드 + 본문 갱신 진행.

**예외**: 사용자가 "그냥 알아서 쭉 진행해"라고 명시한 경우만 확인 단계 생략.
</Confirmation_Pattern>

<Tool_Usage>
- **Bash**: 디렉토리 생성, http 서버 기동, scripts 실행
- **Write**: HTML 템플릿 채우기
- **Read**: 기존 글 본문, 템플릿 구조 확인
- **mcp__plugin_playwright_playwright__***: 렌더링 (navigate, resize, take_screenshot, close)
- **mcp__blog__update_post**: 본문에 이미지 reference 삽입
- **scripts/upload.py**: blog MCP에 PNG 업로드 (HTTP 직접 호출, base64 컨텍스트 회피)
</Tool_Usage>

<Examples>
호출 형태:
> "이 draft에 그림 들어가면 좋을 위치 검토해줘. 톤은 기존 글들과 통일."
> "post id `<uuid>` 에 다이어그램 3장 추가해줘"
> "이중 안전장치 부분 시각화"

응답 패턴:
1. draft 읽음 (Read 또는 mcp__blog__get_post)
2. 후보 3~5곳 표로 제시 → 사용자 OK
3. 톤 샘플 1장 렌더링 → 사용자 OK
4. 나머지 일괄 렌더링·업로드
5. 본문 갱신 + 캡션 한 줄 추가
</Examples>

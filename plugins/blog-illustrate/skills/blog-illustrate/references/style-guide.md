# blog-illustrate 스타일 가이드

블로그 일러스트의 시각 일관성을 위한 색·타이포·카드 토큰. SKILL.md에서 한 차례 요약하고, 자세한 결정 근거는 여기에.

## 디자인 톤

**Dracula-inspired dark theme + macOS terminal chrome.**

- 다크 카드 위에 코드/터미널을 자연스럽게 표현
- 페이지 배경은 부드러운 light gradient — 카드가 떠 보이도록
- 모든 카드는 macOS 윈도우 chrome (traffic-light dots) — 친숙하고 "터미널 같은" 분위기
- 색은 의미 있는 곳에만 — over-color 금지

## 색 토큰 (`_common.css`)

| Token | Hex | 용도 |
|---|---|---|
| `.prompt`  | `#50fa7b` (green, bold)   | shell prompt `$` |
| `.cmd`     | `#f1fa8c` (yellow)        | command / subcommand |
| `.comment` | `#6272a4` (italic gray)   | inline comment, secondary annotation |
| `.folder`  | `#8be9fd` (cyan, bold)    | directory name |
| `.file`    | `#e8e8f0` (off-white)     | file name (default text) |
| `.tree`    | `#5a637a` (gray)          | tree branch chars `├──`, `└──`, `│` |
| `.arrow`   | `#ff79c6` (pink, bold)    | directional indicator `→`, `▷` |
| `.ok`      | `#50fa7b` (green, bold)   | success / PASS / completed |
| `.warn`    | `#ffb86c` (orange)        | warning / partial / improvement |
| `.bad`     | `#ff5555` (red)           | error / FAIL / blocked |
| `.dim`     | `#6272a4` (gray)          | secondary text, metadata |
| `.kw`      | `#bd93f9` (purple, bold)  | keyword, tool name |
| `.str`     | `#f1fa8c` (yellow)        | string literal |
| `.spark`   | `#ff79c6` (pink, bold)    | highlight bullet `▶`, `✨` |

**원칙**:
- 한 화면에 6색 이하. 너무 많으면 시선이 흩어짐.
- "강조"는 색 + 굵기 둘 중 하나만. 둘 다 쓰면 노이즈.
- 빨강은 진짜 위험·실패에만. UNCOVERED, REJECT, DANGER 등.
- 녹색은 결과에만. 진행 중에는 노랑(warn) 또는 시안.

## 타이포

- **본문 (한국어 포함)**: `'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif`
- **코드/터미널**: `'SF Mono', 'JetBrains Mono', Menlo, monospace`
- **사이즈**: 본문 13px, 코드 12.5~13px, 라벨/메타 11~12px, 헤딩 13~16px
- **lineheight**: 1.55~1.7 (한국어가 영어보다 살짝 더 필요)

## 카드 / 컨테이너

```css
border-radius: 12px;
box-shadow: 0 14px 36px -10px rgba(20,30,60,0.22), 0 2px 6px rgba(0,0,0,0.06);
border: 1px solid rgba(0,0,0,0.05);
```

**왜 그림자 두 겹**: 부드러운 큰 그림자 + 작은 contact shadow. 시각적으로 카드가 페이지에 닿아 있는 느낌.

## 페이지 배경

```css
background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf4 100%);
padding: 40px 30px;
```

블로그 본문에 임베드되면 페이지 배경은 잘리고 카드만 보임. 그래도 padding은 있어야 카드 그림자가 잘리지 않음.

## 윈도우 chrome (terminal 카드)

```html
<div class="titlebar">
  <div class="dot r"></div>
  <div class="dot y"></div>
  <div class="dot g"></div>
  <span class="title">컨텍스트: 경로/모드 <span class="badge">상태</span></span>
</div>
```

- traffic-light dot 색은 macOS 표준 (red `#ff5f57`, yellow `#febc2e`, green `#28c840`)
- title 텍스트는 흐린 회색 (시선 안 끌게)
- badge로 상태 표시 (warn = working, ok = monitoring/success)

## viewport 사이즈 가이드

| 레이아웃 | 가로 | 세로 |
|---|---|---|
| 단일 카드 (terminal-single) | 880~920 | 콘텐츠 + 80px |
| 좌우 두 패널 (terminal-dual, comparison-cards, mapping-diagram) | 1240~1320 | 콘텐츠 + 80px |
| 3분할 (decision-tree) | 1100~1140 | 600~700 |
| layered (defense, timeline) | 880~920 | 600~800 |

**원칙**: 가로는 콘텐츠가 넘치지 않게. 세로는 콘텐츠 + 상하 padding 정도. fullPage screenshot 시 빈 공간 최소화.

## 콘텐츠 작성 원칙

- **모든 값은 의사값**. `<incident_id>`, `example-folder`, `2026-04-22_some-slug` 같은 generic 값 사용.
- **숫자는 적게**. "3건", "60%" 같은 결정적 숫자는 효과적이지만, 너무 많으면 mockup이 데이터로 보임.
- **한국어 + 영어 섞어 쓰기**. 코드 토큰(`Stage 2`, `findings.md`, `audit.md`)은 영어로, 설명은 한국어로.
- **"...은", "...는" 토씨 생략**. 모노스페이스 표시에서 토씨 정렬이 어려워서 비주얼이 깨짐.

## 자주 만나는 함정

- **nested grid + flex 폭 안 늘어남**: grid 자식인 flex item에 width:100% 안 먹을 때 → `align-self: stretch; width: 100% !important; max-width: none !important`
- **viewport 너무 큼 → 빈 공간**: viewport height를 콘텐츠에 가깝게. 1~2회 시행착오 OK.
- **fullPage 잊기**: `fullPage=true` 안 주면 viewport height로 잘림.
- **한국어 줄바꿈**: 긴 한국어 문장은 자연스러운 위치에서 `<br>` 또는 자유로운 줄바꿈 (`white-space: pre-wrap`).
- **인라인 style vs 외부 CSS**: 새 mockup 만들 때 `_common.css`로 안 떨어지는 일회성 스타일은 `<style>` 블록 내에. 재사용 가능하면 `_common.css`로 promote.

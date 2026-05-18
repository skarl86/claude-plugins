# 다이어그램 패턴 — 코드블록을 SVG/HTML 박스로

마크다운에서 `<pre>` 코드블록(ASCII art, 트리, 흐름도)은 슬라이드에서 깨지기 쉽다. 한글 폰트와 모노스페이스가 섞이면 박스 정렬이 어긋나고, 폰트 mismatch로 글자가 잘린다. 그래서 이 스킬은 코드블록을 **그대로 두지 말고** 다음 패턴 중 하나로 변환한다.

## 변환 결정표

| 마크다운 모양 | 권장 변환 |
|---|---|
| 가로 흐름 `A → B → C` | [D1. 박스 + 화살표 행](#d1-박스--화살표-행) |
| 분기/루프 흐름 (실패 시 돌아가기 등) | [D2. SVG 흐름도](#d2-svg-흐름도) |
| 디렉토리 트리 (`├─ /`) | [D3. 카드 그리드](#d3-카드-그리드) |
| 명령어 목록 (`$ cmd ...`) | [D4. codebox](#d4-codebox) |
| YAML/JSON 짧은 예시 | [D4. codebox](#d4-codebox) (단, 5줄 이내) |

원칙은 단순하다: **글자 정렬에 의존하는 표현은 모두 박스/SVG로 변환한다.**

---

## D1. 박스 + 화살표 행

가장 자주 쓰는 패턴. 마크다운에 `A → B → C` 또는 `[A] → [B] → [C]` 형태가 있으면 이걸로.

```html
<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; align-items: center; margin: 16px 0;">
  <div class="flow-node">CS 신고</div>
  <div class="arrow">→</div>
  <div class="flow-node accent">debugger</div>
  <div class="arrow">→</div>
  <div class="flow-node accent2">validate</div>
  <div class="arrow">→</div>
  <div class="flow-node good">PR · merge</div>
</div>
```

`.flow-node`는 `accent`/`accent2`/`good` modifier로 의미 컬러링. `grid-template-columns: repeat(N, 1fr)` N은 박스+화살표 합친 셀 수.

---

## D2. SVG 흐름도

루프·분기·점선이 필요한 흐름은 inline SVG. 가장 단단하다.

### 필수 marker 정의

```svg
<defs>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto">
    <path d="M0,0 L12,6 L0,12 z" fill="#0284c7"/>
  </marker>
  <marker id="arrowGreen" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto">
    <path d="M0,0 L12,6 L0,12 z" fill="#047857"/>
  </marker>
  <marker id="arrowRed" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto">
    <path d="M0,0 L12,6 L0,12 z" fill="#b91c1c"/>
  </marker>
</defs>
```

- `refX=11, markerWidth=12`이면 marker 머리가 path 끝점에 거의 닿게 위치한다
- `orient="auto"`: path 방향 따라 머리도 회전
- 3색 marker는 의미별로 분리

### 박스 (rect + text)

```svg
<rect x="40" y="40" width="280" height="100" rx="14" fill="#f8fafc" stroke="#0284c7" stroke-width="2"/>
<text x="180" y="80" text-anchor="middle" font-size="24" font-weight="700" fill="#0f172a">① 단계</text>
<text x="180" y="112" text-anchor="middle" font-size="20" fill="#64748b">서브타이틀</text>
```

검증·게이트 박스는 amber 톤:
```svg
<rect ... fill="#fef3c7" stroke="#b45309" stroke-width="2.5"/>
<text ... fill="#b45309">검증</text>
```

완료/성공 박스는 emerald 톤:
```svg
<rect ... fill="#d1fae5" stroke="#047857" stroke-width="2.5"/>
<text ... fill="#047857">완료</text>
```

### 직진 화살표 (실선, 파랑)

```svg
<line x1="320" y1="90" x2="375" y2="90" stroke="#0284c7" stroke-width="2.5" marker-end="url(#arrow)"/>
```

### Dogleg 화살표 (꺾인 흐름)

`V` (수직)와 `H` (수평) path가 가독성이 좋다. Q (Bezier)보다 디버그 쉬움.

```svg
<!-- ③ 통과 → ④ 박스로: 아래로 내려갔다가 왼쪽으로 -->
<path d="M 860 140 V 215 H 520 V 255" fill="none" stroke="#0284c7" stroke-width="2.5" marker-end="url(#arrow)"/>
```

### 실패 회귀 (점선, 빨강)

```svg
<path d="M 860 40 V -10 H 520 V 38" fill="none" stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="6,5" marker-end="url(#arrowRed)"/>
<text x="690" y="-18" text-anchor="middle" font-size="20" fill="#b91c1c" font-weight="600">실패 시 ②로</text>
```

**중요**: 같은 시작·끝 박스를 가진 정상 화살표와 회귀 화살표는 *경로가 겹치지 않게* 분리한다. 한쪽은 박스 위쪽 우회 (음수 y), 다른 쪽은 박스 아래쪽 우회 (큰 y). viewBox를 음수로 시작(`viewBox="0 -40 1700 700"`)하면 박스 위쪽 공간을 확보할 수 있다.

### ViewBox 가이드

| 흐름 | 권장 viewBox |
|---|---|
| 한 줄 가로 흐름 | `0 0 1700 200` |
| 2단 흐름 (Phase 2개) | `0 0 1700 380` |
| 3단 흐름 + 위/아래 회귀 | `0 -40 1700 700` |

SVG 컨테이너:
```html
<div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 20px 0;">
  <svg viewBox="..." xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: auto;">
    ...
  </svg>
</div>
```

`width: 100%; height: auto`로 슬라이드 폭에 맞추되 비율은 viewBox 그대로.

---

## D3. 카드 그리드 (디렉토리 트리 대체)

마크다운에 디렉토리 트리가 있으면 `<pre>` 그대로 옮기지 말고 카드 그리드로.

```html
<div class="grid-3">
  <div class="card">
    <h4>📂 루트</h4>
    <p style="font-size: 22px;"><code>AGENTS.md</code> · 공통 규칙<br/><code>CLAUDE.md</code> · 보안 가이드</p>
  </div>
  <div class="card">
    <h4>📂 .claude/skills/ <span class="accent">16개</span></h4>
    <p style="font-size: 22px;"><code>assemble-team</code> · <code>probe-*</code> · ...</p>
  </div>
  ...
</div>
```

폴더 이모지 `📂`로 시각 단서를 준다. 카드 안 본문 font-size는 22px가 보기 좋다.

---

## D4. codebox

짧은 명령어 목록이나 5줄 이내 YAML/JSON. 일반 `<pre>` 대신 `.codebox` 클래스를 쓰면 라이트 테마 톤과 어울린다.

```html
<div class="codebox">
cxdm env upload &lt;svc&gt; &lt;env&gt;
cxdm workflows create
cxdm services list
</div>
```

YAML/JSON 예시는 키 색상을 강조하기 위해 `<span class="kk">key</span>` 같은 마크업을 끼워도 좋다 (`.codebox .kk { color: var(--accent-2); }`를 CSS에 추가하면).

`<pre>` 태그는 가급적 쓰지 않는다 — 1080px 안에서 폭 조절이 까다롭다. 코드가 길면 두 칸으로 쪼개거나, 핵심만 인용한다.

---

## 안티 패턴 — 하지 말 것

- ❌ 마크다운 `pre` 블록을 그대로 `<pre>`로 옮기기 (한글 환경에서 글자 잘림)
- ❌ ASCII 화살표 (`→`, `↓`, `─`)를 그대로 `<pre>`에 두기 (정렬 깨짐)
- ❌ 디렉토리 트리(`├─ /`)를 `<pre>`로 (이모지/한글 폭 mismatch)
- ❌ 정상 흐름과 회귀 흐름이 같은 path를 지나가게 그리기 (어디로 가는 화살표인지 헷갈림)
- ❌ SVG marker `refX` 누락 — 화살표 머리가 path 끝에서 떨어져 보임

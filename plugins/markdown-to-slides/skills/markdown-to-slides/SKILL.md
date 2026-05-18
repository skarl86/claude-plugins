---
name: markdown-to-slides
description: |
  마크다운 문서를 1920×1080 발표용 슬라이드 HTML과 슬라이드별 PNG 이미지로 변환하는 스킬.
  사용자가 정리해둔 글을 그대로 프레젠테이션 자료로 뽑아낼 때 사용한다 — Keynote/PowerPoint
  같은 외부 도구 없이 마크다운 한 파일에서 슬라이드 HTML + 이미지 패키지가 나온다.

  다음 상황에서 이 스킬을 적극적으로 사용:
  - "이 문서/마크다운/글을 PPT로 만들어줘", "발표 자료로 변환해줘", "슬라이드 이미지로 뽑아줘"
  - "프레젠테이션 자료 만들어줘" / "딕(deck) 만들어줘" / "슬라이드 데크"
  - 사용자가 마크다운 경로를 던지며 발표·공유·세미나·온보딩 자료를 요청
  - "각 슬라이드를 이미지로 저장해줘" (HTML만 있는 상태에서 캡처 요청)

  사용자가 PPT라는 단어를 쓰더라도 .pptx 파일을 만드는 게 아니라
  HTML + PNG 이미지로 뽑는다(이게 회의실 빔/공유에 더 안정적). 이 점은 처음에 한 번 명시.

  활용 시 산출물:
  - <input-stem>-slides/index.html — 모든 슬라이드 단일 HTML
  - <input-stem>-slides/slide-01.png ~ slide-NN.png — Retina(@2x) PNG, 3840×2160
---

# markdown-to-slides

마크다운 한 파일을 받아서 같은 디렉토리에 `<stem>-slides/` 폴더를 만들고, 그 안에 슬라이드 HTML과 슬라이드별 PNG 이미지를 떨어뜨리는 스킬이다. 회의실 빔에서 잘 보이는 라이트 테마 1종으로 출력한다.

## 입력 / 출력 한눈에

| 항목 | 내용 |
|---|---|
| 입력 | 마크다운 파일 경로 1개 (사용자가 지정) |
| 산출 디렉토리 | `<dir>/<stem>-slides/` (기본). 사용자가 다른 경로 지정 가능 |
| HTML | `index.html` — 모든 슬라이드가 세로로 쌓인 단일 파일 |
| 이미지 | `slide-01.png` ~ `slide-NN.png` — 3840×2160, 8-bit RGB |
| 의존성 | Node.js + `playwright` (chromium). 로컬에 없으면 임시로 설치 |

## 작업 흐름 (단계별로 따라간다)

### 1. 마크다운 읽고 슬라이드 단위로 분할

- **1순위 분할자**: `---` 수평선. 사용자가 의도적으로 슬라이드 경계를 박은 경우다.
- **보조 분할자**: `---`가 너무 적어 슬라이드당 분량이 너무 큰 경우(대략 600자/슬라이드 초과), `## ` 헤딩 단위로 한 번 더 쪼개도 된다.
- 첫 단락(타이틀 + 부제 + 작성자 메타)은 별도의 *타이틀 슬라이드*로 분리한다.

분할이 끝나면 슬라이드별로 다음을 결정한다.

- **타이틀**: `##` 헤딩이 있으면 그것을 쓰고, 없으면 첫 문장
- **레이아웃 힌트**: 표가 있나, 카드 그리드가 어울리나, 인용구가 메인인가, 코드/다이어그램이 있나
- **번호**: 1~N. 우상단 indicator(`NN / NN`)와 footer에 표기

### 2. 슬라이드 HTML 생성

`assets/template.html`을 기반으로 본문을 합쳐 단일 HTML 파일을 만든다. 각 슬라이드는 다음 골격을 따른다.

```html
<section class="slide" data-slide="01">
  <div class="num">01 / 28</div>
  <div class="tag">섹션 라벨</div>
  <h2>슬라이드 제목</h2>
  <!-- 본문 -->
  <div class="footer"><span>좌측 라벨</span><span>1 / 28</span></div>
</section>
```

핵심 규칙:

1. **`data-slide` 속성**은 2자리 zero-pad (`"01"`, `"02"`, … `"28"`). 캡처 스크립트가 이 값으로 슬라이드를 식별한다.
2. **페이지 번호는 3곳을 동기화해야 한다** — 같은 슬라이드 안에 `data-slide="04"`, `.num`의 "04 / 28", `.footer` 마지막 `<span>4 / 28</span>` 또는 `<span>4</span>` 세 군데. **HTML을 다 생성한 뒤 자동으로 동기화하는 게 가장 안전하다**: 슬라이드별로 `data-slide` 하나만 정확히 박고, `.num`과 footer의 페이지 번호는 작성 시점에 일관되게 채우거나, 짧은 sed/스크립트로 일괄 치환한다. 슬라이드 중간에 한 장을 삽입·삭제할 때 이 3곳을 모두 손봐야 한다는 점을 기억한다.
3. **컨테이너 크기는 정확히 1920×1080.** 화면 비율을 깨면 PPT/공유 화면에서 잘린다.
4. **본문이 짧은 슬라이드는 빈 영역을 두지 않는다.** 마크다운 한 섹션이 너무 짧으면 카드 그리드(`.grid-3`/`.grid-4`), 통계 대시보드(`.stat`), 또는 시각 강조 인용(`blockquote`)으로 시각 밸런스를 채운다. 빈 슬라이드는 발표에서 어색하다 — 차라리 다음 슬라이드와 합치거나 본문을 풍부하게 채운다.
5. **라이트 테마 고정.** 회의실 조명에서도 잘 보이는 흰 배경 + slate/sky/amber 팔레트. 색상 의미:
   - sky-700(`#0284c7`) = primary accent / 통과·정상 흐름
   - amber-700(`#b45309`) = warning / 사용자 검증 / 주의
   - emerald-700(`#047857`) = good / 완료 / 프로그래밍 검증
   - red-700(`#b91c1c`) = bad / 실패 회귀
6. **코드블록을 다이어그램으로 적극 대체.** 마크다운에 ASCII art(`┌─┐` `→` 등)나 디렉토리 트리, 흐름도가 있으면 `<pre>` 그대로 두지 말고 SVG 또는 카드 그리드/박스로 변환한다. `<pre>`는 한글 환경에서 깨지기 쉽고 폰트 mismatch로 인한 글자 잘림이 흔하다. `references/diagram-patterns.md` 참고.
7. **마크다운 표 → `<table>`**. 행이 8행 이상이면 `font-size: 22~24px`, `padding: 10~12px`로 압축. 안 그러면 footer와 겹친다.
8. **footer 영역 침범 금지.** `.footer`는 `position: absolute; bottom: 36px`. 본문이 footer를 넘으면 자르거나 분할한다.

레이아웃 패턴 카탈로그는 `references/layout-patterns.md`에 있다. 슬라이드 성격에 맞는 패턴을 골라 쓴다.

### 3. 의존성 확보

```bash
cd <output-dir>
# 한 번만: node + playwright
npm init -y >/dev/null
npm pkg set type=module >/dev/null
npm i playwright
npx playwright install chromium
```

이미 설치돼 있으면 skip. 같은 머신에서 한 번이라도 이 스킬을 돌렸으면 chromium은 `~/Library/Caches/ms-playwright`(macOS) 또는 `~/.cache/ms-playwright`(Linux)에 캐싱돼 있어서 재다운로드는 없다.

**기존 `node_modules`를 재사용하려면** 산출 디렉토리에 새로 깔지 말고, 기존 디렉토리에서 스크립트를 실행한다:

```bash
# 예: $CLAUDE_JOB_DIR/build에 이미 playwright가 깔려 있는 경우
cd $CLAUDE_JOB_DIR/build
node /path/to/scripts/screenshot.mjs <html-path> <output-dir>
```

스크립트는 절대 경로를 받기 때문에 *실행 디렉토리는 자유*다. 산출물 폴더에 굳이 `node_modules`를 또 깔지 않아도 된다.

### 4. 슬라이드별 PNG 캡처

`scripts/screenshot.mjs`를 산출 디렉토리에 복사하거나 직접 호출한다.

```bash
node scripts/screenshot.mjs <html-path> <output-dir> <total-slides>
```

스크립트가 하는 일:

- chromium headless 실행, viewport 1920×1080, `deviceScaleFactor: 2`
- HTML 로드 → `networkidle` 대기 + 폰트 안정화용 800ms 추가
- `.slide[data-slide="NN"]` 셀렉터로 각 슬라이드 요소만 캡처
- `slide-NN.png` 저장 (3840×2160 PNG)

### 5. 결과 보고

사용자에게 산출물 경로 + 슬라이드 수를 한 줄로 보고하고, 디자인 점검이 필요한 슬라이드 2~3장을 `Read`로 보여주면서 시각 검수를 받는다. 사용자가 특정 슬라이드에 피드백을 주면 *해당 슬라이드만* HTML 수정 후 캡처 스크립트를 다시 한 번 돌린다(전체 N장 재캡처도 1분 안쪽).

## 자주 마주치는 문제와 대응

| 증상 | 원인 | 대응 |
|---|---|---|
| 마지막 행이 footer와 겹침 | 표 행이 많거나 카드 padding 큼 | 표 `font-size`/`padding` 축소, blockquote → 일반 `<p>`로 변경 |
| 코드블록 글자 잘림 | `<pre>` 폭이 1720px 초과 | 줄바꿈, 또는 SVG/카드 다이어그램으로 대체 |
| 한글 폰트가 다르게 렌더 | 시스템에 폰트 없음 | `font-family`에 `Apple SD Gothic Neo`, `Pretendard`, `Noto Sans KR` 순서로 폴백 |
| PNG가 흐릿함 | `deviceScaleFactor` 누락 | 스크립트에서 반드시 2 이상 |
| 슬라이드 번호 불일치 | renumber 누락 | `data-slide` ↔ `.num` ↔ footer 페이지 번호 3곳 모두 일치해야 함 |
| 화살표 머리가 안 보임 | SVG marker `refX`/`orient` 누락 | `references/diagram-patterns.md`의 marker 정의 그대로 사용 |

## 톤·문체에 대한 가이드 (선택)

이 스킬 자체는 톤을 강제하지 않는다. 사용자가 마크다운에 쓴 톤을 그대로 살린다. 단, 사용자가 명시적으로 톤 변환을 요청하지 않은 한 *원본 마크다운의 문체를 임의로 바꾸지 않는다.*

발표용으로 좋은 톤 가이드를 사용자가 원할 때만 제안:
- "정답 제시" 톤 → "경험 공유" 톤으로 전환 ("~해야 한다" → "~해보니 좋더라구요")
- 다른 사람을 평가하는 표현 → 본인 경험 1인칭으로 (예: "어떤 동료는 ..." → "저는 ...")

## 참고 파일

- `assets/template.html` — 빈 슬라이드 데크 부트스트랩 (CSS 통합)
- `scripts/screenshot.mjs` — playwright 캡처 스크립트
- `references/layout-patterns.md` — 슬라이드 레이아웃 패턴 카탈로그 (타이틀, 2단 그리드, 4카드, 표 중심, SVG 다이어그램, 통계 대시보드 등)
- `references/diagram-patterns.md` — ASCII/코드블록을 SVG·HTML 박스로 바꾸는 패턴

## 작업 시작 체크리스트

- [ ] 사용자가 준 마크다운 경로가 실재하는지 `Read`로 확인
- [ ] 산출 디렉토리 결정 (기본: `<같은 디렉토리>/<stem>-slides/`)
- [ ] 슬라이드 분할안 정리 (몇 장 나올지 사용자에게 미리 공유)
- [ ] HTML 작성 → playwright 설치 확인 → 캡처 → 검수
- [ ] PPT라는 단어를 사용자가 쓰더라도 .pptx가 아닌 HTML+PNG라는 점을 한 번 명시

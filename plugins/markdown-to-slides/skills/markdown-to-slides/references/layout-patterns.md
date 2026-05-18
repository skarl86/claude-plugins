# 슬라이드 레이아웃 패턴 카탈로그

각 슬라이드의 본문 성격에 따라 어울리는 패턴이 다르다. 마크다운 슬라이드를 HTML로 옮길 때, 본문에 어떤 요소가 있는지 보고 다음 패턴 중 하나를 골라 쓴다.

## 목차
- [P1. 타이틀](#p1-타이틀)
- [P2. 빅 인용 (one-liner)](#p2-빅-인용-one-liner)
- [P3. 2단 grid (대비/Before·After)](#p3-2단-grid-대비beforeafter)
- [P4. 4카드 grid (필수 요소 4개)](#p4-4카드-grid-필수-요소-4개)
- [P5. 표 중심 (매트릭스·인벤토리)](#p5-표-중심-매트릭스인벤토리)
- [P6. SVG/박스 다이어그램](#p6-svg박스-다이어그램)
- [P7. 통계 대시보드 (정리 슬라이드)](#p7-통계-대시보드-정리-슬라이드)
- [P8. 체크리스트](#p8-체크리스트)
- [P9. 단계 행 (numbered list)](#p9-단계-행-numbered-list)

---

## P1. 타이틀

데크 첫 슬라이드 또는 챕터 구분.

```html
<section class="slide vcenter" data-slide="01">
  <div class="num">01 / NN</div>
  <div style="margin: auto 0;">
    <div class="tag">섹션 라벨</div>
    <h1 class="title">
      <span class="accent">강조 단어</span><br/>
      메인 타이틀 2-3줄
    </h1>
    <p class="lead dim">부제 한 줄</p>
  </div>
  <div class="footer"><span>왼쪽 메타</span><span>오른쪽 메타</span></div>
</section>
```

언제: 데크 첫 장 / 새 챕터 시작 / "안녕하세요" 타입 인사

---

## P2. 빅 인용 (one-liner)

핵심 메시지 하나만 크게.

```html
<section class="slide vcenter" data-slide="NN">
  <div class="num">NN / NN</div>
  <div class="tag">정리</div>
  <div style="margin: auto 0;">
    <blockquote style="font-size: 48px; line-height: 1.4; font-weight: 700; padding: 16px 0;">
      <span class="dim" style="font-weight: 600;">A가 아니라,</span><br/>
      <span class="accent" style="font-weight: 800;">B</span>가 핵심이었어요.
    </blockquote>
  </div>
</section>
```

언제: 마크다운에서 `> ...` 인용만 있고 본문이 짧은 슬라이드, 결론·정리 슬라이드

---

## P3. 2단 grid (대비/Before·After)

좌우 두 영역 비교.

```html
<div class="grid-2">
  <div class="card bad">
    <h4>Before</h4>
    <p>... 문제 ...</p>
  </div>
  <div class="card good">
    <h4>After</h4>
    <p>... 개선 ...</p>
  </div>
</div>
```

`.card`는 `accent`/`warn`/`good`/`bad` modifier로 컬러 의미 전달. Before/After가 아닌 일반 두 항목은 `.card.accent` 두 개 또는 modifier 없는 두 개.

언제: 마크다운에 "Before/After" 또는 "두 가지" 짝지음이 있을 때

---

## P4. 4카드 grid (필수 요소 4개)

```html
<div class="grid-4">
  <div class="card accent"><h4>1. 컨벤션</h4><p>설명</p></div>
  <div class="card accent"><h4>2. 도메인 규칙</h4><p>설명</p></div>
  <div class="card accent"><h4>3. 진행 단계</h4><p>설명</p></div>
  <div class="card accent"><h4>4. 완료 기준</h4><p>설명</p></div>
</div>
```

3개·5개라면 `.grid-3` 또는 그리드 + 마지막 행 중앙 정렬.

언제: "필요한 4가지", "구성 요소", 짧은 항목들이 병렬일 때

---

## P5. 표 중심 (매트릭스·인벤토리)

마크다운 표 그대로 옮기되, 행 수에 따라 크기 조정.

| 행 수 | font-size | padding |
|---|---|---|
| ~6행 | 30px | 16px 20px |
| 7~8행 | 26px | 14px 18px |
| 9~10행 | 24px | 12px 16px |
| 10행 초과 | 22px | 10px 14px |

```html
<table style="font-size: 24px;">
  <thead><tr>
    <th style="width: 22%; padding: 12px 16px;">단계</th>
    <th style="padding: 12px 16px;">적용 하네스</th>
    <th style="padding: 12px 16px;">역할</th>
  </tr></thead>
  <tbody>
    <tr><td style="padding: 12px 16px;"><b>1. 문제 인식</b></td><td style="padding: 12px 16px;">...</td><td style="padding: 12px 16px;">...</td></tr>
    ...
  </tbody>
</table>
```

타이틀과 표 사이 부제(`<p class="dim">`)는 짧게. blockquote는 가급적 빼고 일반 p로.

언제: 마크다운에 표가 메인 콘텐츠

---

## P6. SVG/박스 다이어그램

ASCII art나 흐름도가 마크다운에 있으면 **반드시** SVG/HTML 박스로 변환한다. `references/diagram-patterns.md` 참고.

가벼운 가로 흐름은 `.flow-node` + `.arrow`로:

```html
<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; align-items: center;">
  <div class="flow-node">CS 신고</div>
  <div class="arrow">→</div>
  <div class="flow-node accent">처리기</div>
  <div class="arrow">→</div>
  <div class="flow-node good">완료</div>
</div>
```

복잡한 흐름(루프, 분기, 점선)은 inline SVG로.

언제: 마크다운 `pre` 블록에 ASCII art가 있거나, 흐름·관계도가 본문 핵심일 때

---

## P7. 통계 대시보드 (정리 슬라이드)

```html
<div style="display:flex; gap: 40px; margin-top: 40px; justify-content: space-between;">
  <div class="stat"><div class="stat-val">11</div><div class="stat-label">AGENTS.md</div></div>
  <div class="stat"><div class="stat-val">16</div><div class="stat-label">스킬</div></div>
  <div class="stat"><div class="stat-val">3</div><div class="stat-label">디버거 에이전트</div></div>
</div>
```

언제: 데크 후반 "정리/지표" 슬라이드, 인벤토리 요약

---

## P8. 체크리스트

```html
<ul>
  <li>☐ 항목 1</li>
  <li>☐ 항목 2</li>
  <li>☐ 항목 3</li>
</ul>
```

이미 끝난 항목은 `☑`. 8~10항목 권장. 그 이상이면 2열 그리드로.

언제: 마크다운에 `- [ ]` 체크리스트가 있을 때 (그대로 옮긴다)

---

## P9. 단계 행 (numbered list)

7~10단계 같은 시퀀스를 한 슬라이드에 보일 때, 표보다 행 카드가 시각적으로 좋다.

```html
<div style="background: var(--bg-2); border-radius: 16px; border: 1px solid var(--line); padding: 8px 32px;">
  <div style="display: grid; grid-template-columns: 80px 1fr 120px; gap: 20px; align-items: center; padding: 14px 18px; border-bottom: 1px solid var(--line);">
    <div style="width: 60px; height: 60px; border-radius: 50%; background: var(--accent); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 30px;">1</div>
    <div style="font-size: 26px;">문제 인식</div>
    <div class="dim" style="text-align: right; font-size: 22px;">(사용자 입력)</div>
  </div>
  ...
</div>
```

step 번호 박스 배경은 `accent`/`warn`/`good`으로 의미 컬러링.

언제: 마크다운에 번호 매긴 표나 시퀀스가 있을 때

---

## 슬라이드 길이가 안 맞을 때

본문이 1080px 안에 들어가지 않으면:

1. 슬라이드를 2장으로 쪼갠다 (`## 8.6 구현` → `8.6a 공통 규칙` / `8.6b cxdm CLI`)
2. 본문 크기 축소: `<p>` 30 → 26, `<li>` 30 → 24
3. blockquote → 일반 p (blockquote는 padding이 크다)
4. 카드 padding 24px → 16px
5. 표가 원인이면 [P5](#p5-표-중심-매트릭스인벤토리) 가이드 적용

반대로 너무 비어 보이면 stat·카드 그리드를 추가해 시각 밸런스를 맞춘다.

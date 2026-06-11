---
name: goalify
description: Converts any rough task prompt into a fully working /goal condition statement for Claude Code's /goal feature (run-until-done autonomous mode). Use this whenever the user mentions /goal or goal mode in any language, asks to convert/optimize/write a prompt for /goal, or wants Claude to keep working until something is done — e.g. "/goal 프롬프트 만들어줘", "이거 goal로 바꿔줘", "끝날 때까지 알아서 돌아가게 해줘", "make this a goal condition", "write a /goal for fixing these tests". Even if the user pastes a vague task and merely hints at autonomous completion, use this skill to produce the /goal statement.
---

# Goalify — /goal 프롬프트 변환기

사용자의 거친(rough) 프롬프트를 Claude Code `/goal` 기능에서 **확실히 동작하는** 조건문으로 변환한다.

## 왜 변환이 필요한가 (핵심 전제)

`/goal <조건문>`은 조건이 충족될 때까지 Claude가 자동으로 턴을 반복하는 기능이다. 매 턴이 끝나면 **별도의 작은 평가 모델(기본 Haiku)이 대화 transcript만 읽고** yes/no를 판정한다. 평가자는 도구를 실행하거나 파일을 읽을 수 없다.

이 제약에서 모든 규칙이 나온다:

1. 조건은 **측정 가능**해야 한다 — "코드를 개선한다"는 판정 불가, "`npm test`가 exit 0"은 판정 가능.
2. 조건에 **검증 방법이 명시**되어야 한다 — Claude가 그 명령을 실행해서 결과를 transcript에 남겨야 평가자가 볼 수 있다.
3. **바운드가 있어야 한다** — 조건이 영원히 충족되지 않으면 무한정 돌기 때문에 "or stop after N turns" 같은 탈출 조항이 필요하다.
4. 최대 4,000자, 세션당 활성 goal은 1개.

## 변환 워크플로

### 1단계 — 의도 추출

사용자의 원본 프롬프트에서 "끝났다"의 정의를 찾는다. 명시돼 있지 않으면 작업 종류로부터 추론한다:

| 작업 종류 | 기본 종료 상태 |
|---|---|
| 버그 수정 | 재현 케이스가 통과 + 기존 테스트 전부 통과 |
| 기능 구현 | 새 기능 테스트 작성·통과 + 빌드 성공 |
| 마이그레이션/리팩토링 | 전체 컴파일 + 전체 테스트 통과 + 대상 패턴 0건 (grep으로 확인) |
| 린트/타입 에러 제거 | 해당 명령 exit 0, 에러 카운트 0 |
| 백로그/이슈 소진 | 남은 항목 수 0 |

의도가 진짜 애매하고 사용자가 대화 중이면 **핵심 질문 1개만** 묻는다. 사용자가 없거나 백그라운드 맥락이면 합리적 기본값을 고르고 출력의 "가정" 항목에 표기한다.

### 2단계 — 검증 명령을 실제로 확인

현재 디렉토리가 프로젝트라면 `package.json`의 scripts, `Makefile`, `pyproject.toml`, CI 설정(.github/workflows) 등을 읽어 **실제 존재하는 명령**으로 check를 작성한다. 없는 명령을 지어내면 Claude가 실행에 실패하고 goal이 영원히 끝나지 않으므로, 이 단계는 생략하지 않는다.

프로젝트 맥락이 전혀 없으면(사용자가 프롬프트 텍스트만 준 경우) 생태계 표준 명령을 쓰되 출력의 "확인 필요" 항목에 명시한다.

### 3단계 — 조건문 조립

네 요소를 이 어순으로 배치한다 (한 줄, 사용자의 언어로 작성하되 명령어는 그대로):

```
<측정 가능한 종료 상태>, verified by <정확한 명령>이 <기대 결과(exit 0 / 출력 0건 등)>;
constraints: <실행 중 지켜야 할 제약>; or stop after <N> turns
```

- **종료 상태**: 테스트 결과, exit code, 파일 수, grep 매치 0건, 큐 비움 같은 객관적 사실.
- **검증**: Claude가 매 턴 실행해 증거를 남길 수 있는 구체적 명령. 2개 이상이면 and로 연결.
- **제약**: 부작용 방지 조항. 예: "다른 테스트 파일은 수정하지 않는다", "기존 public API 시그니처 유지", "테스트를 skip 처리하지 않는다". 특히 **테스트 무력화 금지 조항**은 거의 항상 넣을 가치가 있다 — 평가자는 테스트가 통과한 *방법*을 따지지 않기 때문이다.
- **바운드**: 작업 규모에 맞는 턴 수. 단일 버그 ~10턴, 모듈 마이그레이션 ~20턴, 대규모 백로그 ~30턴. 사용자가 지정하면 그 값.

### 4단계 — 자가 검증 체크리스트

출력 전에 조건문을 평가자의 눈으로 다시 읽는다:

- [ ] transcript에 남은 증거만으로 yes/no 판정이 가능한가? ("DB가 최적화됨" 같은 숨은 상태 의존 금지)
- [ ] 검증 명령이 실제로 존재하는가 (또는 "확인 필요"로 표기했는가)?
- [ ] "더 좋게", "깔끔하게", "최적화" 같은 판정 불가 단어가 남아 있지 않은가?
- [ ] 바운드 조항이 있는가?
- [ ] 4,000자 이하인가?
- [ ] 제약이 goal 달성의 편법(테스트 삭제, skip, 하드코딩)을 막는가?

### 5단계 — 출력

정확히 이 구조로 출력한다. 첫 코드블록은 사용자가 그대로 복사-붙여넣기할 수 있어야 한다:

````markdown
```
/goal <변환된 조건문 한 줄>
```

| 항목 | 내용 |
|---|---|
| 종료 상태 | ... |
| 검증 방법 | ... (어떤 파일에서 이 명령을 확인했는지) |
| 제약 | ... |
| 바운드 | N턴 — 근거 |
| 가정 / 확인 필요 | ... (없으면 "없음") |
````

## 안티패턴 → 교정

| 원본 (동작 안 함) | 교정 (동작함) |
|---|---|
| 코드를 더 깔끔하게 만들어줘 | `src/` 안의 모든 함수가 50줄 이하이고 `npm run lint`가 exit 0, verified by `npm run lint && awk` 길이 검사 스크립트 출력 0건; constraints: 동작 변경 금지, `npm test` 계속 통과; or stop after 15 turns |
| 버그 다 고쳐줘 | `npm test`의 실패 테스트가 0개, verified by `npm test` exit 0; constraints: 테스트를 삭제하거나 skip 처리하지 않는다; or stop after 15 turns |
| 성능 최적화해줘 | `npm run bench`의 p95가 200ms 이하, verified by 벤치 출력 transcript 기록; constraints: 기존 테스트 전부 통과 유지; or stop after 20 turns |
| 문서 업데이트해줘 | `docs/`의 모든 공개 함수가 README 표에 등재, verified by 공개 export 목록과 README 표의 diff가 0건; or stop after 10 turns |

## /goal이 부적합한 경우 — 정직하게 말하기

다음 경우엔 변환을 강행하지 말고, 이유와 대안을 제시한다:

- **본질적으로 주관적인 목표** ("UI 예쁘게", "글 잘 다듬어줘"): 측정 가능한 proxy(예: Lighthouse 점수, 글자 수 범위)가 합의 가능하면 그걸로 변환을 제안하고, 아니면 일반 대화형 작업이나 plan mode를 권한다.
- **여러 독립 목표가 섞인 프롬프트**: goal은 세션당 1개다. 목표별로 분할해 순차 실행할 `/goal` 시퀀스를 모두 작성해주고, 하나씩 실행하라고 안내한다.
- **시간 간격 기반 반복** ("5분마다 확인해줘"): `/goal`이 아니라 `/loop`의 영역이다.

## 예시

**입력**: "auth 모듈 테스트가 자꾸 깨지는데 끝날 때까지 알아서 고쳐줘"

**출력**:

```
/goal test/auth 디렉토리의 모든 테스트가 통과한다, verified by `npm test -- test/auth`가 exit 0이고 실패 0건이 transcript에 기록됨; constraints: test/auth 외의 테스트 파일을 수정하지 않고, 테스트를 skip하거나 삭제하지 않는다; or stop after 12 turns
```

**입력**: "이 레포 타입스크립트 strict 모드로 바꾸는 작업, goal로 돌리고 싶어"

**출력**:

```
/goal tsconfig.json에 "strict": true가 설정된 상태에서 `npx tsc --noEmit`이 exit 0이고 `npm test`가 exit 0이다, verified by 두 명령의 실행 결과가 transcript에 기록됨; constraints: @ts-ignore나 any 캐스팅으로 에러를 숨기지 않는다(새로 추가된 @ts-ignore 0건을 grep으로 확인), 기존 테스트를 수정하지 않는다; or stop after 25 turns
```

## 참고 자료

`/goal`의 전체 공식 스펙(평가 메커니즘, resume 동작, 비대화형 실행, 요구 버전)이 필요하면 [references/goal-spec.md](references/goal-spec.md)를 읽는다.

# Claude Code `/goal` 공식 스펙 요약

출처: https://code.claude.com/docs/en/goal (2026-06 기준)

## 개요

`/goal <condition>`은 완료 조건을 설정하고, 조건이 충족될 때까지 Claude Code가 여러 턴에 걸쳐 자율적으로 계속 작업하게 한다. 매 턴이 끝나면 별도의 평가 모델이 조건 충족 여부를 판정하고, 미충족이면 자동으로 다음 턴을 시작한다. 충족되면 goal이 자동 해제된다.

- 요구 버전: Claude Code **v2.1.139+** (2026-05-12 릴리스)
- 활성 중 표시: `◎ /goal active` 인디케이터 (경과 시간, 턴 수, 토큰 사용량)

## 입력 형식

```
/goal <자연어 조건문>
```

- 최대 **4,000자** 자유 텍스트
- 세션당 **1개** — 다시 실행하면 기존 goal을 교체
- 설정 즉시 해당 조건을 지시문으로 첫 턴이 시작됨
- `/goal` (무인자) — 현재 상태 확인
- `/goal clear` — 해제 (별칭: stop, off, reset, none, cancel)

## 평가 메커니즘 (가장 중요)

- 매 턴 종료 후 **별도의 작은 모델(기본 Haiku)** 이 조건문 + 대화 transcript를 받아 yes/no + 짧은 사유를 반환
- "no"면 그 사유가 다음 턴의 가이드로 Claude에게 전달되고 자동으로 새 턴 시작
- "yes"면 goal 해제 + transcript에 achieved 기록
- **평가자는 도구를 호출하거나 파일을 읽지 못한다** — Claude가 대화에 드러낸 것만 판정
  - 동작: "test/auth 테스트 전부 통과" — Claude가 테스트를 돌리고 결과가 transcript에 남음
  - 동작 안 함: "데이터베이스가 최적화됨" — 평가자가 독립적으로 검증할 방법 없음

## 좋은 조건문의 공식 가이드

1. **측정 가능한 종료 상태 1개**: 테스트 결과, 빌드 exit code, 파일 수, 빈 큐
2. **검증 방법 명시**: "`npm test`가 exit 0", "`git status`가 clean"
3. **실행 중 제약**: "다른 테스트 파일은 수정하지 않는다"
4. **바운드 권장**: "or stop after 20 turns" — 매 턴 진행 상황이 보고되고 평가자가 판정

## 공식 사용 사례

- 모듈을 새 API로 마이그레이션 — 모든 호출부가 컴파일되고 테스트 통과할 때까지
- 설계 문서 구현 — 모든 인수 조건이 충족될 때까지
- 큰 파일 분할 — 각 모듈이 크기 예산 이하가 될 때까지
- 라벨된 이슈 백로그 처리 — 큐가 빌 때까지

## 실행 환경 / 제한

- 대화형 터미널, `-p` 비대화형, Desktop 앱, Remote Control 모두 지원
- 비대화형: `claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"` — 단일 호출로 완료까지 실행, Ctrl+C로 중단
- **trust dialog를 수락한 워크스페이스에서만** 동작 (평가자가 hooks 시스템의 일부)
- `disableAllHooks` 또는 enterprise `allowManagedHooksOnly` 설정 시 사용 불가 (이유를 안내함)
- 평가 토큰 비용은 메인 턴 대비 미미

## Resume 동작

- 세션 종료 시 활성 goal은 `--resume` / `--continue`로 복원됨
- 턴 수, 타이머, 토큰 기준선은 resume 시 리셋
- 달성되거나 해제된 goal은 복원되지 않음

## 관련 기능 비교

| 기능 | 트리거 | 종료 조건 |
|---|---|---|
| `/goal` | 턴 완료 | 평가자가 조건 충족 확인 |
| `/loop` | 시간 간격 | 수동 중지 또는 모델 판단 |
| Stop hook | 턴 완료 | 커스텀 스크립트/프롬프트 |
| Auto mode | 단일 턴 | 툴 승인만 자동화 (턴 반복 아님) |

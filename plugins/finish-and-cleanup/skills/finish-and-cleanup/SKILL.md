---
name: finish-and-cleanup
description: |
  작업 마무리 루틴 — PR 머지 → 배포 watch → 스모크 확인 → 기록 → 워크트리/브랜치/리소스
  정리 → main 최신화까지를 한 번에 처리하는 체크리스트형 스킬.

  다음 상황에서 반드시 사용 — 단, 사용자가 마무리 국면 신호를 **명시적으로**
  보냈을 때만:
  - "PR 머지해줘", "머지하고 배포까지 확인해", "배포 잘 됐는지 봐줘"
  - "워크트리 정리해", "정리하자", "마무리하자", "main 최신으로 pull 하자"
  - 기능/버그픽스 작업이 끝나서 사용자가 ship을 지시했을 때

  자동 발동 금지: PR이 머지됐다는 사실만으로 이 스킬을 실행하지 말 것.
  머지 후에도 같은 세션에서 작업이 이어질 수 있다 — 클린업(워크트리·브랜치
  삭제)은 사용자가 마무리를 명시했을 때만 진행한다.

  사용 금지: 작업 결과를 **폐기**하는 경우("작업 폐기해줘", "테스트 런이었어") —
  그건 정리 대상이 다르다(머지 없이 worktree·브랜치 폐기만). 그 경우에도 아래
  "폐기 변형" 절만 참고할 수 있다.
---

# finish-and-cleanup

작업 세션의 꼬리에서 매번 반복되는 "머지 → 배포 확인 → 기록 → 청소" 시퀀스를
표준화한다. 각 단계는 **이전 단계의 성공 확인 후** 진행하고, 단계별 결과를 한 줄씩
사용자에게 보고한다.

> 이 스킬은 레포 중립적이다. 머지 base 브랜치·배포 트리거·스모크 확인 방법은
> 프로젝트마다 다르므로, 아래 **프로젝트별 규칙** 절을 각자 환경에 맞게 채워
> 쓰거나, 해당 repo 의 `CLAUDE.md` / `.github/workflows` 를 진실의 원천으로 삼는다.

## 전체 절차 (체크리스트)

1. **사전 점검** — 머지 전에 깨진 것을 올리지 않는다.
   - `git status`: 커밋 안 된 변경 없는지. 있으면 커밋할지 사용자에게 확인.
   - 해당 프로젝트의 테스트/린트가 있으면 실행(또는 CI 통과 확인).
   - push 안 된 커밋이 있으면 push.
2. **PR 생성/머지**
   - PR이 없으면 생성: base 브랜치는 아래 [프로젝트별 규칙](#프로젝트별-규칙) 표를 따른다.
   - 머지는 기본 **squash**. 제목은 해당 레포 커밋 컨벤션(예: Conventional Commits —
     `type(scope): 설명`).
   - 머지는 사용자가 명시 요청했을 때만. 스킬이 자동 발동된 경우 머지 직전 1회 확인.
3. **배포 watch** — 머지가 배포를 트리거하는 레포에서만.
   - 트리거된 워크플로 확인: `gh run list --branch <base> --limit 3`
   - 백그라운드로 추적: `gh run watch <run-id> --exit-status` 를
     `run_in_background` 로. **타임아웃/끊김이 잦으므로** watch 가 죽으면 같은
     run-id 로 재시도(re-arm)하고, 그래도 안 되면 `gh run view <run-id>` 폴링으로 전환.
   - 실패 시: 로그 확인(`gh run view --log-failed`). 호스팅(Cloud Run/Vercel 등)
     로그 진단 스킬이 있으면 연계. 수동 폴백이 정의된 레포는 그 명령 사용.
4. **스모크 확인** — 배포 성공 후 실제로 떠 있는지.
   - 프로젝트별 규칙 표의 확인 URL/명령으로 1회 검증하고, 사용자가 직접 볼 수 있는
     prod URL을 제시한다.
5. **기록(worklog)**
   - 머지를 세션 안에서 실행했고 PostToolUse hook 등으로 worklog 작성을 안내하도록
     설정돼 있으면 그 안내를 따른다. 안내가 없거나 세션 밖에서 머지됐다면 작업 노트를
     직접 남긴다(worklog 류 스킬이 있으면 호출). 같은 작업 노트가 이미 있으면
     status만 merged로 갱신.
6. **클린업** — 남기면 다음 세션에서 혼란을 일으키는 것들.
   - **실행 조건**: 사용자가 마무리를 명시했을 때만. 머지 직후라도 같은 세션에서
     작업이 이어질 수 있으므로, 머지됐다는 사실만으로 워크트리/브랜치를 자동
     삭제하지 않는다. 스킬이 마무리 신호 없이 진행 중이면 이 단계 전에 1회 확인.
   - 작업 worktree 제거: `git worktree remove <path>` (+ `git worktree prune`)
   - 로컬 브랜치 삭제, 머지된 원격 브랜치 삭제(squash 머지 시 GitHub 자동 삭제
     설정 여부 확인)
   - 백그라운드 모니터/dev 서버/tmux pane 등 이 작업용으로 띄운 프로세스 종료
   - 작업 중 다운로드한 시크릿 파일(`.env.*` 등)이 repo 밖 임시 위치에 있으면 삭제.
     repo 안 `.env*`는 gitignore 확인만.
7. **main 최신화** — 본체 체크아웃에서 `git checkout main && git pull`.

마지막에 전체 결과를 요약한다: 머지된 PR 번호/제목, 배포 run 결과, 스모크 결과,
정리한 리소스 목록, 기록 여부.

## 프로젝트별 규칙

머지 base·배포 트리거·확인 방법은 레포마다 다르다. 환경에 맞게 아래 표를 채워
쓴다(없으면 repo `CLAUDE.md` / `.github/workflows` 를 우선한다).

| 레포 유형 | PR base | 머지 후 배포 | 확인 방법 |
|---|---|---|---|
| main 머지 = prod 자동 배포 모노레포 | `main` (작업 브랜치는 main에서 분기) | **main 머지 → prod 자동 배포** (GH Actions, 서비스별 path filter — `.github/workflows/deploy-*.yml`) | `gh run watch`; 클라우드 콘솔/CLI로 리비전 확인. 실패 시 수동 배포 폴백 가능 |
| release 브랜치 운영 레포 | `release/<YYYY-MM-DD>` — 기준 브랜치에서 분기. 없으면 생성부터: `git checkout <base> && git pull && git checkout -b release/<오늘날짜> && git push -u origin HEAD` | release 브랜치 정책에 따름 (자동 prod 아님) | 배포 담당 파이프라인 확인 후 prod URL 제시 |
| Vercel/Netlify 등 PaaS 프론트 | `main` | push/머지 시 자동 배포 | 플랫폼 CLI(`vercel ls` 등) 또는 deployments 대시보드, prod URL 접속 |
| 그 외 | `main` 기본, repo `CLAUDE.md` 우선 | repo `CLAUDE.md` / `.github/workflows` 확인 | — |

> devops 설정 파일(`deploy-*.yml`, 서비스 config 등)을 CLI/자동화로만 관리하는
> 레포에서는 그 파일을 손으로 고치지 말고 해당 repo 의 규칙(CLAUDE.md)을 따른다.

## 배포 watch 가 끊겼을 때

`gh run watch` 백그라운드 작업은 네트워크/타임아웃으로 종종 죽는다. 죽었다고 배포가
실패한 것이 아니다:

```bash
gh run view <run-id> --json status,conclusion   # 현재 상태 먼저 확인
# in_progress 면 watch 재-arm, completed 면 conclusion 으로 판정
```

watch 를 2회 이상 재시도해도 불안정하면 60초 간격 폴링으로 전환하고 사용자에게
전환 사실을 알린다.

## 폐기 변형 (머지 없이 정리)

"이 작업 폐기해줘 / 테스트였어" 인 경우: 머지·배포·기록을 모두 건너뛰고,
미push 커밋과 브랜치를 의도적으로 버린다는 점을 **삭제 전에 한 번 확인**받은 뒤
worktree 제거 → 로컬/원격 브랜치 삭제 → 띄운 프로세스 정리 → 폐기 내역 요약만 한다.
팀(agent team) 런이면 teammate shutdown → 팀 삭제를 먼저.

## 관련 스킬

- `session-handover` — 마무리가 아니라 "진행 중 작업을 다음 세션으로 잇기"가 목적일 때.
- 배포/호스팅 로그 진단 스킬 — 배포 실패·스모크 실패 시 로그 조사에 연계.
- 작업 기록(worklog) 스킬 — 5단계에서 호출.

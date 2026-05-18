# 우리 팀 도구 인벤토리

> 2026 Q1 기준

작성: DevTools 팀

---

## 들어가며

워크스페이스에 깔린 도구들 정리해봤어요. 새로 들어온 동료가 한눈에 볼 수 있게 표 한 장으로.

---

## 전체 도구 목록

아래 표가 핵심입니다. 카테고리별로 정리해뒀어요.

| 카테고리 | 도구 | 용도 | 진입점 |
|---|---|---|---|
| 빌드 | task | 태스크 자동화 | `task <name>` |
| 빌드 | pnpm | 노드 패키지 매니저 | `pnpm <cmd>` |
| 빌드 | uv | Python 패키지 매니저 | `uv <cmd>` |
| 런타임 | mise | 도구 버전 관리 | `mise install` |
| CI/CD | gh | GitHub CLI | `gh pr ...` |
| CI/CD | cxdm | DevOps CLI | `cxdm <area> <cmd>` |
| 클라우드 | gcloud | GCP SDK | `gcloud ...` |
| 클라우드 | aws | AWS SDK | `aws ...` |
| DB | psql | Postgres CLI | `psql ...` |
| DB | supabase | Supabase CLI | `supabase ...` |
| 옵저버빌리티 | langfuse | LLM trace 조회 | `langfuse-cli ...` |
| 디버그 | playwright | 브라우저 자동화 | `npx playwright ...` |

---

## 마무리

이 목록은 분기마다 한 번씩 업데이트해요. 추가하고 싶은 도구가 있으면 PR 주세요.

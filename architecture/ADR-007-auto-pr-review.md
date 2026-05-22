# ADR-007 — GitHub Actions PR 자동 코드 리뷰 시스템

**상태:** 채택  
**날짜:** 2026-05-22  
**결정자:** 김범진 (PM/팀장)

---

## 배경

PR이 열리거나 팀원이 리뷰·코멘트를 남길 때마다 팀장이 직접 diff를 읽고 `docs/`에 리뷰 보고서를 수동으로 작성하고 있었다. 이 작업은 반복적이고 시간이 많이 걸리며, 빠른 피드백 루프를 방해했다.

## 결정

PR 관련 GitHub 이벤트가 발생하면 GitHub Actions가 자동으로 Claude API를 호출해 코드 리뷰 보고서를 생성하고 `docs/pr-review/`에 커밋한다.

## 트리거 → 동작 매핑

| GitHub 이벤트 | 동작 |
|---|---|
| `pull_request` (opened / synchronize / reopened) | diff 전체를 Claude에 넘겨 **신규 리뷰 보고서 생성** |
| `pull_request_review` (submitted) | 기존 보고서에 **팀원 리뷰 노트 추가** |
| `pull_request_review_comment` (created) | 기존 보고서에 **인라인 코멘트 노트 추가** |

## 출력 형식

`docs/pr-review/pr{번호}_code_review.md`

```
# PR #{번호} 코드 리뷰 보고서
헤더 (제목, 작성자, 날짜, 트리거, 대상 파일 목록)

## 코드 줄별 설명
파일별 | 줄 | 코드 | 설명 | 테이블

## 문제점
번호별 — 위치, 현재 코드, 설명

## 개선점
번호별 — 위치, 수정 전 코드, 수정 후 코드, 해결점
```

## 구현 파일

| 파일 | 역할 |
|---|---|
| `.github/workflows/auto-pr-review.yml` | 트리거·권한·스텝 정의 |
| `.github/scripts/generate_pr_review.py` | GitHub API + Anthropic API 호출, 파일 저장 |
| `.github/pr-review-template.md` | 수동 작성용 참고 템플릿 |

## 사전 조건

- GitHub 레포 Settings → Secrets → `ANTHROPIC_API_KEY` 등록
- 워크플로우 권한: `contents: write`, `pull-requests: read`

## 무한 루프 방지

워크플로우 커밋 메시지 끝에 `[skip ci]`를 붙이고, `if: github.actor != 'github-actions[bot]'` 조건으로 봇 커밋에 의한 재실행을 차단한다.

## gitignore 변경

`docs/` 전체는 로컬 전용으로 유지하되, `docs/pr-review/`만 예외 처리(`!docs/pr-review/`)해서 git에 추적된다.

## 선택하지 않은 대안

| 대안 | 이유 |
|---|---|
| PR 코멘트로 리뷰 게시 | 파일로 남기는 것이 검색·아카이빙에 유리 |
| Claude Code CLI 사용 | GitHub Actions 러너에 설치·인증 복잡도가 높음 |
| GPT-4o 사용 | 프로젝트 전반이 Anthropic Claude 기반 |

## 결과

- 팀장의 수동 리뷰 초안 작성 시간 단축
- 모든 PR에 동일한 형식의 리뷰 보고서가 자동으로 생성됨
- 팀원 리뷰·코멘트가 같은 파일에 기록되어 PR 히스토리를 한눈에 파악 가능

# ADR-007 — 로컬 데몬 PR 자동 코드 리뷰 시스템

**상태:** 채택  
**날짜:** 2026-05-22  
**결정자:** 김범진 (PM/팀장)

---

## 배경

PR이 열리거나 커밋이 추가될 때마다 팀장이 직접 diff를 읽고 리뷰 보고서를 수동으로 작성하고 있었다. 반복적이고 시간이 많이 걸림.

## 결정

맥북 로컬 데몬(launchd)이 2분마다 GitHub API를 폴링 → 새 PR 또는 커밋 감지 → `claude -p`로 리뷰 생성 → `docs/pr-review/` 에 로컬 저장.

- GitHub에 코멘트 달지 않음
- git push 없음 — `docs/` 전체 gitignore

## 동작 흐름

```
launchd (2분 인터벌)
  └─ healtheat_pr_review_run.sh
       └─ healtheat_pr_review_poll.py
            ├─ GitHub API: 열린 PR 목록 조회
            ├─ 신규 or updated_at 변경 PR 감지
            ├─ claude -p (cwd = 레포 디렉토리)
            └─ docs/pr-review/pr{번호}_code_review.md 저장
```

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

## 구현 파일 (모두 로컬, 레포 외부)

| 파일 | 역할 |
|---|---|
| `~/.claude/scripts/healtheat_pr_review_poll.py` | 폴링·리뷰 생성·저장 메인 스크립트 |
| `~/.claude/scripts/healtheat_pr_review_run.sh` | launchd 래퍼 (환경변수 주입) |
| `~/.claude/scripts/healtheat_config.env` | GITHUB_TOKEN 저장 |
| `~/Library/LaunchAgents/com.healtheat.pr-review.plist` | launchd 2분 인터벌 설정 |

## 제약 조건

- MAC 주소 `f2:12:02:35:51:2f` 맥북에서만 실행
- 2026-06-05 (시험일) 폴링 비활성화
- GITHUB_TOKEN: repo read 권한 필요 (write 불필요)

## 선택하지 않은 대안

| 대안 | 이유 |
|---|---|
| GitHub Actions + Anthropic API | API 키 없음, Max 구독만 보유 |
| GitHub Actions → 로컬 webhook | NAT 뒤 맥북에 외부 접근 불가 |
| GitHub PR 코멘트로 게시 | 요청하지 않은 기능 |

## 결과

- 팀장 수동 리뷰 초안 작성 시간 단축
- 모든 PR에 동일한 형식의 리뷰 보고서 자동 생성
- 로컬 전용 — 팀원 레포에 영향 없음

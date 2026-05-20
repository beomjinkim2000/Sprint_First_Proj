---
type: concept
title: "운영 결정사항"
created: 2026-05-19
updated: 2026-05-19
tags:
  - workflow
  - decisions
status: active
related:
  - "[[workflow/roles]]"
  - "[[workflow/git-strategy]]"
  - "[[workflow/task-management]]"
  - "[[experiment/log]]"
---

# 운영 결정사항

> 팀이 합의한 운영 방식 요약. 상세 내용은 각 링크 참고.

## 태스크 관리

- GitHub Issues + GitHub Projects 사용
- 프로젝트 권한: 팀장 Admin / 팀원 Read
- 스토리포인트: 이슈 제목 앞에 `[숫자]` 표기 — 1(30분) / 2(반나절) / 3(하루) / 5(하루 이상, 쪼갤 것)

→ 상세: [[workflow/task-management]]

## Git 전략

- GitHub Flow (develop 브랜치 없음)
- `feature/{이슈번호}-{label}-{설명}` → main으로 PR
- 머지 조건: **팀장 approve 필수** (예외 없음)
- `interfaces.md` 건드리는 PR → 팀장 필수 리뷰 (예외 없음)
- PR 머지 후 GitHub 원격 feature 브랜치 삭제 (로컬은 유지해도 무방)
- Kaggle 제출 시 `git tag v0.1-submission`

→ 상세: [[workflow/git-strategy]]

## 코드/파일 구조

- 노트북은 탐색·시각화 전용 (01_eda, 02_visualize_bbox)
- 학습은 코렙에서 `!git clone` → `!python train.py --config configs/default.yaml`
- 로직은 전부 `.py`, 노트북은 import해서 결과 확인만

→ 상세: [[architecture/folder-structure]]

## 실험 로그 형식

| 버전 | 날짜 | 모델 | 변경사항 | val mAP@50 | Kaggle Score | 비고 |
|---|---|---|---|---|---|---|
| v0.1 | - | yolov8n | 파이프라인 첫 완성 | - | - | baseline |

- 실험마다 한 줄 추가
- 변경사항은 직전 버전 대비 한 가지만

→ 상세: [[experiment/log]]

## 일일 운영

- 매일 디스코드 3줄 스탠드업: 어제 한 것 / 오늘 할 것 / 블로커
- 이슈 우선순위: data → dataset → model → train → predict → submission
- v0.1 완료 후 회고 1회 ("잘된 것 1개, 아쉬운 것 1개")

---

## Connections

- [[workflow/git-strategy]] — 브랜치 전략 상세
- [[workflow/task-management]] — 이슈/Projects 구성
- [[workflow/roles]] — 팀원 역할 분담

---
type: meta
title: "Sprint First Project Index"
updated: 2026-05-19
tags:
  - meta
  - index
status: evergreen
related:
  - "[[Overview]]"
  - "[[architecture/folder-structure]]"
  - "[[architecture/module-design]]"
  - "[[architecture/interfaces]]"
  - "[[workflow/task-management]]"
  - "[[workflow/git-strategy]]"
  - "[[workflow/roles]]"
  - "[[experiment/log]]"
---

# Sprint First Project — Index

> 경구약제 이미지 인식 객체 탐지 프로젝트 (코드잇 AI 초급)
> 팀장: 김범진 | 팀원 4명 | 모델: YOLOv8 | 제출: Kaggle submission.csv

Navigation: [[Overview]] | [[experiment/log]]

---

## Architecture

- [[architecture/folder-structure]] — 프로젝트 디렉토리 구조
- [[architecture/module-design]] — 모듈별 책임과 입출력
- [[architecture/interfaces]] — **팀 인터페이스 계약서 (변경 시 팀장 승인 필요)**

---

## Workflow

- [[workflow/kickoff]] — **역할별 지금 당장 할 일 (여기서 시작)**
- [[workflow/task-management]] — GitHub Issues & Projects 구성 (이슈 목록, Label, Milestone)
- [[workflow/git-strategy]] — Git branch / PR / 리뷰 규칙
- [[workflow/roles]] — 팀원 역할 분담 (모듈별)
- [[workflow/decisions]] — 운영 결정사항 (태스크 관리, Git, 실험 로그 형식)

---

## 협업일지

| 최근 수정 |
| --- |

- [[_templates/협업일지]] — 작성 양식
- [[협업일지/김범진(PM)]] | [[협업일지/황원재(Data)]] | [[협업일지/유재열(Model)]] | [[협업일지/박창준(Exp)]]

---

## Experiment

- [[experiment/log]] — 버전별 실험 결과 및 mAP 트래킹

---

## v0.1 태스크 현황

| # | 작업 | 담당 | 마감 | 상태 |
| --- | --- | --- | --- | --- |
| 22 | [setup] YOLOv8 설치 및 예제 실행 확인 | YuJY9897 | 2026-05-21 | in-progress |
| 23 | [model] build_model() 스켈레톤 구현 | YuJY9897 | 2026-05-21 | todo |
| 24 | [inference] predict.py 스켈레톤 구현 | cjkj1234 | 2026-05-21 | todo |
| 4 | [setup] Github repo 생성 및 branch 전략 설정 | beomjinkim2000 | 2026-05-21 | todo |
| 5 | [setup] 폴더 구조 생성 및 빈 파일 커밋 | beomjinkim2000 | 2026-05-21 | todo |
| 6 | [setup] interfaces.md 작성 | beomjinkim2000 | 2026-05-21 | todo |
| 7 | [setup] pyproject.toml 및 .gitignore 작성 | beomjinkim2000 | 2026-05-21 | todo |
| 8 | [data] 원본 데이터 구조 확인 및 annotation 컬럼 파악 | zipdid, beomjinkim2000 | 2026-05-21 | todo |
| 10 | [data] bbox 시각화 노트북 작성 | zipdid, beomjinkim2000 | 2026-05-22 | todo |
| 11 | [dataset] Dataset 클래스 구현 (dataset.py) | zipdid | 2026-05-22 | todo |
| 12 | [dataset] transforms 구현 (transforms.py) | zipdid | 2026-05-22 | todo |
| 13 | [dataset] train/val split 구현 (split.py) | zipdid | 2026-05-22 | todo |
| 9 | [data] EDA 노트북 작성 (01_eda.ipynb) | zipdid, beomjinkim2000 | 2026-05-22 | todo |
| 14 | [model] baseline 모델 구현 (build_model) | YuJY9897 | 2026-05-23 | todo |
| 15 | [train] train loop 구현 (engine/train.py) | YuJY9897 | 2026-05-23 | todo |
| 16 | [train] evaluate 구현 (engine/evaluate.py) | YuJY9897 | 2026-05-23 | todo |
| 17 | [train] checkpoint 저장/로드 구현 | YuJY9897 | 2026-05-23 | todo |
| 18 | [inference] predict 구현 (engine/predict.py) | cjkj1234 | 2026-05-23 | todo |
| 19 | [submission] make_submission.py 구현 | beomjinkim2000 | 2026-05-24 | todo |
| 20 | [submission] 첫 번째 Kaggle 제출 | beomjinkim2000 | 2026-05-25 | todo |
| 21 | [docs] README 초안 작성 | beomjinkim2000 | 2026-05-25 | todo |

---

## 1차 목표

```
train → predict → submission.csv → Kaggle 제출
성능보다 파이프라인 완성 먼저
```

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

```dataview
TABLE file.mtime as "최근 수정"
FROM "협업일지"
WHERE file.name != "_index"
SORT file.mtime DESC
LIMIT 6
```
---

## Experiment

- [[experiment/log]] — 버전별 실험 결과 및 mAP 트래킹

---

## v0.1 태스크 현황

→ [[workflow/task-management]]

---

## 1차 목표

```
train → predict → submission.csv → Kaggle 제출
성능보다 파이프라인 완성 먼저
```

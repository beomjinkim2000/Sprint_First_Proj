---
type: meta
title: "Sprint First Project Index"
updated: 2026-05-19
tags:
  - meta
  - index
status: evergreen
related:
  - "[[00_overview]]"
  - "[[architecture/folder-structure]]"
  - "[[architecture/module-design]]"
  - "[[architecture/interfaces]]"
  - "[[workflow/task-management]]"
  - "[[workflow/git-strategy]]"
  - "[[workflow/roles]]"
  - "[[workflow/pm-checklist]]"
  - "[[experiment/log]]"
---

# Sprint First Project — Index

> 경구약제 이미지 인식 객체 탐지 프로젝트 (코드잇 AI 초급)
> 팀장: 김범진 | 팀원 4명 | 모델: YOLOv8 | 제출: Kaggle submission.csv

Navigation: [[00_overview]] | [[experiment/log]]

---

## Architecture

- [[architecture/folder-structure]] — 프로젝트 디렉토리 구조
- [[architecture/module-design]] — 모듈별 책임과 입출력
- [[architecture/interfaces]] — **팀 인터페이스 계약서 (변경 시 팀장 승인 필요)**

---

## Workflow

- [[workflow/task-management]] — GitHub Issues & Projects 구성 (Backlog, Label, Milestone, 자동화)
- [[workflow/git-strategy]] — Git branch / PR / 리뷰 규칙
- [[workflow/roles]] — 팀원 역할 분담 (모듈별)
- [[workflow/decisions]] — 운영 결정사항 (태스크 관리, Git, 실험 로그 형식)

---

## 협업일지

- [[협업일지/_template]] — 협업일지 작성 양식
- [[협업일지/김범진(PM)/]] — 김범진
- [[협업일지/zipdid/]] — zipdid
- [[협업일지/YuY9897/]] — YuY9897
- [[협업일지/cjkj1234/]] — cjkj1234

---

## Experiment

- [[experiment/log]] — 버전별 실험 결과 및 mAP 트래킹

---

## 1차 목표

```
train → predict → submission.csv → Kaggle 제출
성능보다 파이프라인 완성 먼저
```

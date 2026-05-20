---
type: meta
title: "Sprint First Project Index"
updated: 2026-05-20
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
  - "[[architecture/pipeline]]"
  - "[[experiment/log]]"
---

# Sprint First Project — Index

> 경구약제 이미지 인식 객체 탐지 프로젝트 (코드잇 AI 초급)
> 팀장: 김범진 | 팀원 4명 | 모델: YOLOv8 | 제출: Kaggle submission.csv

Navigation: [[Overview]] | [[experiment/log]]

---

## Architecture

- [[architecture/pipeline]] — **전체 실행 파이프라인 & 파일별 담당자 (여기서 흐름 확인)**
- [[architecture/folder-structure]] — 프로젝트 디렉토리 구조
- [[architecture/module-design]] — 모듈별 책임과 입출력
- [[architecture/interfaces]] — **팀 인터페이스 계약서 (변경 시 팀장 승인 필요)**

---

## Workflow

- [[workflow/kickoff]] — **역할별 지금 당장 할 일 (여기서 시작)**
- [[workflow/roles]] — 팀원 역할 분담 (모듈별)
- [[workflow/dev-rules]] — 개발 규칙 (인터페이스 변경, 소통 방법)
- [[workflow/task-management]] — GitHub Issues & Projects 구성 (이슈 목록, Label, Milestone)
- [[workflow/git-strategy]] — Git branch / PR / 리뷰 규칙
- [[workflow/decisions]] — 운영 결정사항 (태스크 관리, Git, 실험 로그 형식)

---

## 협업일지

```dataviewjs
// @prerender from="협업일지" group-by-folder link-to-index limit=6
const all = dv.pages('"협업일지"').where(p => p.file.name !== "index");
const best = {};
for (const p of all) {
  const folder = p.file.folder.split('/').pop();
  if (!best[folder] || p.file.name > best[folder].file.name) {
    best[folder] = p;
  }
}
const rows = Object.values(best)
  .sort((a, b) => b.file.name.localeCompare(a.file.name))
  .slice(0, 6)
  .map(p => {
    const folder = p.file.folder.split('/').pop();
    return [dv.fileLink(p.file.folder + "/index", false, folder), p.file.name.slice(0, 10)];
  });
dv.table(["팀원", "최근 작성"], rows);
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

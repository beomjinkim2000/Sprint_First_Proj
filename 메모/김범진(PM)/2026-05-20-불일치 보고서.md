---
type: memo
date: 2026-05-20
author: 김범진(PM)
title: "아키텍처 문서 불일치 항목 정리"
---

# 아키텍처 문서 불일치 항목 — 2026-05-20

pipeline.md 작성 과정에서 발견한 기존 Obsidian 문서와 현재 설계 간 불일치 목록.
전부 이 날짜에 수정 완료.

---

## 1. src/utils/visualize.py — 제거 대상

- **불일치**: `folder-structure.md`, `module-design.md`에 `visualize.py` 항목이 남아 있었음
- **현재 설계**: 시각화는 `notebooks/02_visualize_bbox.ipynb` 인라인으로 대체 (ADR-007)
- **수정**: 두 파일에서 `visualize.py` 항목 삭제, 노트북으로 교체

---

## 2. src/engine/postprocess.py — 누락

- **불일치**: `folder-structure.md`, `module-design.md`, `roles.md`에 `postprocess.py` 항목 없었음
- **현재 설계**: NMS / confidence 필터링을 `predict.py`에서 분리해 `postprocess.py`로 독립 (ADR-006)
- **수정**: 세 파일에 `postprocess.py` 항목 추가 (정: 박창준, 부: 유재열)

---

## 3. src/utils/ — config.py, collate.py, validate.py 누락

- **불일치**: `folder-structure.md`, `module-design.md`, `roles.md`에 세 파일 없었음
- **현재 설계**: 팀장(김범진) 담당 유틸리티로 확정 (ADR-003, pipeline.md Step 0)
- **수정**: 세 파일에 항목 추가

---

## 4. 루트 predict.py — folder-structure.md 누락

- **불일치**: `folder-structure.md`에 루트 `predict.py` 항목 없었음 (train.py만 있었음)
- **현재 설계**: `predict.py`는 전체 이미지 순회 진입점 (Step 2a/2b 모두)
- **수정**: `folder-structure.md`에 루트 `predict.py` 추가

---

## 5. tests/mock_dataset.py — 누락

- **불일치**: `folder-structure.md`에 `tests/` 폴더 자체가 없었음
- **현재 설계**: MockDataset 텐서 사용 테스트 정책 확정 (ADR-004)
- **수정**: `folder-structure.md`에 `tests/mock_dataset.py` 추가

---

## 6. 팀원 실명 — roles.md 누락

- **불일치**: `roles.md` 표에 GitHub ID만 있고 실명 없었음
- **수정**: 각 GitHub ID 옆에 실명 추가 (황원재, 유재열, 박창준)

---

## 7. evaluate.py 담당 이중 사용 — roles.md 미반영

- **불일치**: `roles.md`에서 `evaluate.py`가 유재열(Model) 단일 담당으로만 표기
- **현재 설계**: Step 1(학습 중 val)은 유재열 정, Step 2a(예측 후 성능)는 박창준 정 (ADR-009)
- **수정**: roles.md에 Step 구분 명시

---

## 8. 카카오톡 → 디스코드 교체

- **불일치**: `workflow/dev-rules.md` (line 78), `workflow/kickoff.md` (line 99)에 "카톡"으로 소통 명시
- **현재 설계**: 팀 내 소통은 Discord로 통일
- **수정**: 두 파일에서 "카톡" → "디스코드" 교체, CLAUDE.md에 커뮤니케이션 규칙 섹션 추가

---

## 수정된 파일 목록

| 파일 | 수정 내용 |
|---|---|
| `architecture/folder-structure.md` | postprocess.py 추가, visualize.py 제거, config/collate/validate 추가, predict.py 추가, tests/ 추가 |
| `architecture/module-design.md` | postprocess.py 추가, visualize.py 제거, config/collate/validate 추가, 파이프라인 다이어그램 수정 |
| `workflow/roles.md` | 실명 추가, postprocess.py 추가, evaluate.py Step 구분, utils 전체 목록 반영 |
| `workflow/dev-rules.md` | 카톡 → 디스코드 |
| `workflow/kickoff.md` | 카톡 → 디스코드 |
| `Code_IT_Team_1_FirstProject/CLAUDE.md` | 커뮤니케이션 규칙 섹션 추가 |

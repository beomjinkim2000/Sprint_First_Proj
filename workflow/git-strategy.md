---
type: concept
title: "Git Branch & PR 전략"
created: 2026-05-19
updated: 2026-05-19
tags:
  - workflow
  - git
  - collaboration
status: mature
related:
  - "[[index]]"
  - "[[workflow/roles]]"
  - "[[workflow/task-management]]"
---

# Git Branch & PR 전략

## 브랜치 구조 (GitHub Flow)

```
main   ← 항상 실행 가능한 상태. PR 없이 직접 push 금지
  ├── feature/{이슈번호}-{label}-{짧은설명}
  └── fix/{이슈번호}-{label}-{짧은설명}
```

> develop 브랜치 없음. feature → main 직행.

### 브랜치 이름 예시

```bash
feature/8-data-structure-check
feature/11-dataset-class
feature/15-train-loop
fix/19-submission-format
```

---

## 작업 시작 전 필수 루틴

```bash
# GitHub 이슈와 브랜치 자동 연결 (권장)
gh issue develop {이슈번호} --checkout --branch-name feature/{이슈번호}-{label}-{짧은설명}

# 예시
gh issue develop 8 --checkout --branch-name feature/8-data-structure-check
```

> `gh issue develop`을 쓰면 GitHub 이슈 페이지 사이드바 "Development" 섹션에 브랜치가 자동 연결됨.

```bash
# gh CLI 없을 경우 대체 방법
git checkout main
git pull origin main
git checkout -b feature/8-data-structure-check
```

> 이걸 안 하면 남이 merge한 변경사항 없이 작업하다가 충돌남.

---

## main 브랜치 Protection Rule

> GitHub repo → Settings → Branches → Add rule

- `main` 직접 push 금지
- PR 필수 (최소 approve 1명)
- `interfaces.md` 변경 PR → 팀장 필수 리뷰 (예외 없음)

---

## PR 규칙

1. feature 브랜치에서 작업 후 `main`으로 PR
2. PR 제목: `[#11] Dataset 클래스 구현`
3. PR 본문 필수 항목: 작업 내용 + 테스트 결과 (실행 출력 or 스크린샷)
4. 머지 조건: **팀장 approve 필수** (예외 없음)
5. Merge 후 GitHub 원격 feature 브랜치 삭제 (로컬은 유지해도 무방)

### PR 리뷰 시 확인사항

- `interfaces.md` 형식 준수 여부
- 완료 기준 코드 실행 결과 첨부 여부
- GitHub 원격 feature 브랜치 삭제 여부

---

## PR 본문 템플릿

```markdown
## 작업 내용
- PillDataset 클래스 구현 (src/data/dataset.py)
- target_dict 형식: interfaces.md 기준 준수

## 테스트
python -c "
from src.data.dataset import PillDataset
ds = PillDataset('data/processed', split='train')
img, target = ds[0]
print(img.shape, target['boxes'].shape)
"
# 출력: torch.Size([3, 640, 640]) torch.Size([2, 4])

## 관련 이슈
closes #8
```

---

## 최종 제출 직전

```bash
git checkout main
git pull origin main
git tag v0.1-submission
git push origin v0.1-submission
```

> Kaggle 제출 전날 팀장이 직접 수행.

---

## Connections

- [[workflow/task-management]] — 이슈 번호가 branch 이름에 들어감
- [[workflow/decisions]] — Git 전략 확정 결정사항
- [[architecture/interfaces]] — 인터페이스 변경 시 PR에서 확인

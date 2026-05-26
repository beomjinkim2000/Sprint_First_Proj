---
type: concept
title: "YOLOv8"
tags: [concept, model, detection]
related:
  - "[[concepts/mAP]]"
  - "[[concepts/Bounding Box]]"
  - "[[concepts/Transfer Learning]]"
  - "[[concepts/NMS]]"
  - "[[architecture/실행 파이프라인]]"
  - "[[workflow/실험 전략]]"
---

# YOLOv8

Ultralytics가 만든 실시간 객체 탐지 모델. YOLO(You Only Look Once) 계열 8번째 버전.

## YOLO가 나온 이유 — 1-stage vs 2-stage

기존 R-CNN 계열(2-stage)은 이미지에서 후보 영역(Region Proposal)을 먼저 뽑고, 그 각각에 분류기를 돌리는 방식이다. 정확하지만 느리다.

YOLO는 이미지 전체를 한 번만 통과시켜 위치(bbox)와 클래스를 동시에 예측한다(1-stage). 파이프라인이 단순하고 실시간 처리가 가능하다.

| 방식 | 대표 모델 | 특징 |
|---|---|---|
| 2-stage | R-CNN, Fast R-CNN, Faster R-CNN | 정확, 느림 |
| 1-stage | YOLO, SSD | 빠름, 실용적 |

## YOLO 버전별 핵심 변화

### v1 — 그리드 셀 기반 예측

이미지를 S×S 그리드로 나눠 각 셀이 B개의 bbox와 C개의 클래스 확률을 동시에 예측한다.

```
출력 텐서: S×S×(B×5 + C)
예: PASCAL VOC → 7×7×30 (S=7, B=2, C=20)
```

- 45 FPS 실시간 처리
- 한계: 그리드 셀당 예측 수 제한, 작은 객체에서 오차 큼

### v2 — 앵커 박스 도입

| 개선 | 내용 |
|---|---|
| 배치 정규화 | 전 Conv 레이어에 추가 → mAP +2%, 드롭아웃 제거 |
| 앵커 박스 | bbox를 직접 예측 대신, 미리 정의된 박스 기준 오프셋 예측 |
| k-means 클러스터링 | 앵커 크기를 수작업이 아닌 학습 데이터 분포에서 자동 산출 |
| 직접 위치 예측 | 좌표를 그리드 셀 내 상대값(0~1)으로 제한 → 학습 안정화 |
| 멀티 스케일 학습 | 10 배치마다 입력 해상도 변경(320~608px) |
| Darknet-19 | 19개 Conv + 5 Pooling, 경량화된 backbone |

### v3 — 멀티 스케일 + 더 깊은 backbone

- **Darknet-53**: 잔차 연결(Residual) 추가, 53개 Conv 레이어
- **3가지 스케일**에서 예측: 13×13(큰 객체), 26×26(중간), 52×52(작은 객체)
- **앵커 박스 9개**: k-means로 뽑은 후 스케일당 3개씩 배분
- **클래스 예측**: softmax → 독립 sigmoid (다중 라벨 지원)

---

## YOLOv8 구조 — Backbone / Neck / Head

v3까지는 단순한 FPN 구조였고, v8은 여기서 C2f 블록·앵커 프리·분리 헤드로 한 단계 더 발전했다.

```
입력 이미지
    ↓
Backbone (CSPDarknet + SPPF)   레이어 0~9
    ↓
Neck (FPN + PANet)              레이어 10~21
    ↓
Head (Detect)                   레이어 22
    ↓
bbox + class 예측
```

### Backbone — 특징 추출기 (레이어 0~9)

입력 이미지에서 저수준(엣지, 텍스처)부터 고수준(형태, 의미) 특징까지 단계적으로 추출한다. 레이어가 깊어질수록 해상도는 낮아지고 의미 정보는 풍부해진다.

- **C2f 블록**: Cross-Stage Partial + 2 bottleneck. v3의 C3보다 경량화
- **SPPF**: 마지막 레이어. 여러 크기 풀링으로 넓은 맥락을 압축
- COCO 33만 장으로 사전학습된 가중치 사용

### Neck — 멀티스케일 특징 합성 (레이어 10~21)

backbone에서 나온 여러 해상도의 특징맵을 합쳐서, 작은 객체·큰 객체 모두 잡을 수 있도록 만든다.

**FPN (Feature Pyramid Network) — 위쪽 방향(top-down)**
- 상위 레이어(의미 풍부) → 업샘플링 → 하위 레이어(고해상도)와 결합
- Lateral connection(1×1 conv)으로 채널 수를 맞춘 뒤 element-wise 덧셈

**PANet — 아래쪽 방향(bottom-up) 추가**
- FPN 위에 다시 아래→위 경로를 추가해 공간 정보 손실을 보완
- 결과: P3(52×52), P4(26×26), P5(13×13) 세 스케일 특징맵 출력

```
Backbone 출력
  C3(52×52) ──────────────────────→ FPN top-down → P3 (작은 객체)
  C4(26×26) ──────────────────────→ FPN top-down → P4
  C5(13×13) → SPPF → FPN top-down → P5 (큰 객체)
                                        ↓ PANet bottom-up 재통합
```

### Head — 예측 레이어 (레이어 22, Detect)

v8은 **앵커 프리(Anchor-Free)** + **분리 헤드(Decoupled Head)** 를 채택했다.

- 앵커 박스 없이 그리드 셀마다 직접 bbox 중심·크기를 예측
- cv2(box 예측)와 cv3(class 예측)를 분리 → 두 태스크 간 간섭 제거

```
cv2: Conv → Conv → Conv2d  ← bbox 좌표 (x, y, w, h) × 3 스케일
cv3: Conv → Conv → Conv2d  ← 클래스 확률 (C개) × 3 스케일
```

cv3 마지막 Conv2d는 클래스 수에 맞춰 새로 초기화됨 → [[concepts/Transfer Learning]] 참고.

---

## 모델 크기 종류

| 모델 | 파라미터 | mAP (COCO) | 특징 |
|---|---|---|---|
| yolov8n | 3.2M | 37.3 | nano, 가장 빠름 |
| yolov8s | 11.2M | 44.9 | small |
| yolov8m | 25.9M | 50.2 | medium |
| yolov8l | 43.7M | 52.9 | large |
| yolov8x | 68.2M | 53.9 | extra, 가장 정확 |

이 프로젝트 기준선: `yolov8n` → [[workflow/실험 전략]] #54에서 s/m 비교 예정.

## Ultralytics 사용법

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")          # COCO pretrained 로드
model.train(data="configs/pill.yaml", epochs=50, imgsz=640)

results = model.predict(source="test_images/", conf=0.5)
```

## 데이터 포맷 요구사항

학습 시 YOLO 포맷 txt 라벨 필요:
```
class_id  cx_norm  cy_norm  w_norm  h_norm
```
자세한 내용 → [[concepts/Bounding Box]]

## 관련 개념

- [[concepts/Transfer Learning]] — pretrained 가중치 활용, freeze 전략, backbone/neck/head param 분리
- [[concepts/NMS]] — 중복 박스 제거 (Ultralytics 내장)
- [[concepts/mAP]] — 성능 평가 지표
- [[concepts/Loss]] — bbox regression + classification loss

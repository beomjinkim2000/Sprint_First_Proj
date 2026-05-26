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

입력 이미지에서 저수준(엣지, 텍스처)부터 고수준(형태, 의미) 특징까지 단계적으로 추출한다. Conv 레이어를 거칠 때마다 stride=2로 해상도가 절반씩 줄고, 채널은 늘어난다.

```
640×640 → 320×320 → 160×160 → 80×80 → 40×40 → 20×20
(해상도 ↓, 채널 ↑, 의미 정보 ↑)
```

COCO 33만 장으로 사전학습된 가중치 사용.

#### C2f 블록이란

C2f = **Cross Stage Partial** 구조에 **2개의 Bottleneck**을 쌓은 것.

핵심 아이디어: 특징맵을 두 갈래로 나눠서, 한 갈래만 연산을 거치고 나머지는 그냥 통과시킨 뒤 마지막에 합친다.

```
입력 특징맵
    │
    ├──→ [Conv → Bottleneck1 → Bottleneck2] ─→┐
    │                                           Concat → Conv → 출력
    └──→ [그냥 통과] ────────────────────────→┘
```

- **왜 좋은가**: 통과 경로가 gradient를 직접 앞까지 흘려줘서 기울기 소실이 줄어든다. 전체 연산을 반만 하면서 표현력은 비슷하게 유지.
- **v3 C3와 차이**: C3는 bottleneck을 전부 직렬로 쌓지만, C2f는 각 bottleneck 출력을 중간중간 concat해서 더 풍부한 특징을 만든다.

```python
# Ultralytics 코드에서 C2f 확인
from ultralytics.nn.modules import C2f
import torch

x = torch.randn(1, 64, 80, 80)
block = C2f(64, 64, n=2)  # n=bottleneck 개수
out = block(x)
print(out.shape)  # → (1, 64, 80, 80)
```

#### SPPF란 (Spatial Pyramid Pooling - Fast)

backbone 마지막에 위치. **여러 크기의 맥락 정보를 한꺼번에 압축**하는 역할.

**원래 SPP (병렬 방식)**:
```
입력 → MaxPool(5×5)  ─→┐
     → MaxPool(9×9)  ─→ Concat → 출력
     → MaxPool(13×13)─→┘
```
3개 풀링을 동시에 돌려서 결과를 이어붙임. 느리다.

**SPPF (순차 방식)**:
```
입력 → MaxPool(5×5) → MaxPool(5×5) → MaxPool(5×5) → Concat → 출력
         [pool1]          [pool2]          [pool3]
```
같은 크기(5×5)를 3번 순차로 돌린다. pool1의 수용 영역=5, pool2=9(pool1 위에), pool3=13(pool2 위에). SPP와 결과가 거의 같은데 속도는 2배 빠르다.

- **왜 필요한가**: backbone 끝에서 20×20짜리 특징맵이 나오는데, 각 픽셀이 "원본 이미지에서 얼마나 넓은 영역을 보고 있느냐"(수용 영역)를 다양하게 늘려준다. 큰 알약이든 작은 알약이든 이 레이어에서 한 번에 맥락을 잡을 수 있게 됨.
- 출력 크기는 입력과 동일 → 뒤 neck으로 그대로 전달

```python
# SPPF 위치 확인
for i, layer in enumerate(model.model.model):
    if type(layer).__name__ == "SPPF":
        print(f"layer {i}: SPPF")  # → layer 9
```

### Neck — 멀티스케일 특징 합성 (레이어 10~21)

backbone을 거치면 20×20짜리 특징맵만 남는데, 이걸로는 작은 객체를 탐지할 수 없다. Neck이 하는 일은 **해상도가 다른 특징맵들을 합쳐서 크고 작은 객체를 동시에 잡을 수 있는 세 가지 출력을 만드는 것**이다.

#### 업샘플링이 필요한 이유

backbone이 깊어질수록 해상도가 줄어드는 건 어쩔 수 없다. stride=2 Conv 때문에 640×640 입력이 20×20까지 줄어든다.

문제: 깊은 레이어(20×20)는 의미 정보가 풍부하지만 공간 해상도가 너무 낮다. 80×80짜리 알약 하나가 20×20 특징맵에서는 1~2픽셀로 뭉개진다.

해결: 깊은 레이어의 "의미 정보"를 업샘플링으로 크기를 키운 뒤, 얕은 레이어의 "공간 정보"와 합친다.

```
깊은 레이어 (20×20, 의미 풍부, 공간 정보 적음)
    ↓ ×2 업샘플링 (Nearest Neighbor: 픽셀을 단순 복제)
    (40×40)
    ↓ Concat
얕은 레이어 (40×40, 의미 부족, 공간 정보 풍부)
    ↓
합쳐진 특징맵 (40×40, 의미 + 공간 정보 모두 있음)
```

**Nearest Neighbor 업샘플링**: 가장 가까운 픽셀 값을 그냥 복제해서 해상도를 2배로 늘림. 학습 파라미터 없고 빠르다.

```
[1, 2]    →    [1, 1, 2, 2]
[3, 4]         [1, 1, 2, 2]
               [3, 3, 4, 4]
               [3, 3, 4, 4]
```

**FPN (top-down) — 깊은 → 얕은 방향**
- 가장 깊은 레이어부터 위로 올라가면서 업샘플링 후 concat
- 의미 정보를 고해상도로 퍼뜨리는 과정

**PANet (bottom-up) — 얕은 → 깊은 방향 추가**
- FPN만 하면 얕은 레이어의 공간 정보가 깊은 레이어까지 잘 안 전달됨
- FPN 결과 위에 다시 아래→위 경로를 추가해 보완

```
Backbone
  C5(20×20) ─→ SPPF ─→ P5(20×20) ────────────────────────→ Head (큰 객체)
                              ↓ ×2 업샘플 + Concat
  C4(40×40) ────────────────→ P4(40×40) ──────────────────→ Head (중간 객체)
                                    ↓ ×2 업샘플 + Concat
  C3(80×80) ──────────────────────→ P3(80×80) ────────────→ Head (작은 객체)
              ← ← ← ← ← ← ← PANet bottom-up 재통합 ← ← ←
```

결과: 세 스케일(80×80, 40×40, 20×20)에서 각각 Head에 특징맵 전달.

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

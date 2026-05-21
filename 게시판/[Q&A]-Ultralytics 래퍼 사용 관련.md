---
글쓴사람: 유재열(Model)
날짜: 2026-05-21 12:42
상태: 해결됨
tags:
  - qna
---
<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">질문</span><hr style="flex:1;margin:0"></div>






train.py를 만들면서 한 가지 의문점에 부딪혔는데
Ultralytics 래퍼를 쓰지 않으면 현재 loss값을 알 수 없습니다.
loss를 저희 내부에서 자체적으로 구현하기엔 복잡하다고 합니다.

Ultralytics 래퍼를 쓰면 전처리, 후처리를 자동으로 해주는데
전처리에서는 이미지 포맷처리, 크기 조정, 텐서 변환, 채널 순서 변환, 차원추가, 정규화 device등등을 해주고
후처리에서 NMS적용, 클래스 id, 이름 ,score정리, 시각화용 plot생성까지 모두 해준다고 합니다.

이러면 전,후 처리에서 할일의 일부를 Ultralytics 래퍼가 해주는거 같아서 Ultralytics 래퍼를 쓰지 않도록 했는데 loss값 추출에서 이 부분이 걸립니다..

Ultralytics 래퍼를 쓰는게 맞을까요 아닐까요


++15:21
Ultralytics 래퍼를 쓰면 제 베이스라인 코드가

from ultralytics import YOLO  
def build_model_u(model_name: str) -> YOLO:  
return YOLO(f"{model_name}.pt")

딸랑 이 3줄이 되버린답니다.  
그렇다면 아무것도 안한게 되겠죠... 추가로 위에 쓴 전,후처리도 많은걸 Ultralytics래퍼가 처리해줄겁니다..

그래서 생각한 방안 1 loss계산을 위한 내부 loss클래스만 참고하거나 가져와서 쓴다.  
그러면 가져온 Ultralytics loss클래스가 원하는 포맷 변환이 필요하다고 합니다.  
xyxy를 xywh로 바꾸기, 이미지 크기로 나눠서 0~1 정규화, batch_idx 추가

사실상 Ultralytics에 loss를 계산하는 내부 클래스만 가져오는게 좋을 것 같습니다.
저는 이렇게 진행하려고 합니다.
어서 찬반을 내주세요
사실상 전,후처리 하시는분들이 달라지는건 없습니다. 하하하

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">답변</span><hr style="flex:1;margin:0"></div>

> [!note] 김범진(PM)
> 3줄 요약
>
> - bbox 기본 형식은 `dataset.py`에서 **xyxy 절대 픽셀**로 유지하고, `engine/train.py`에서만 `v8DetectionLoss`용 형식으로 변환하는 방향입니다.
> - 이유는 `dataset.py` 출력이 학습뿐 아니라 evaluation, IoU, NMS, mAP 등 여러 곳에서 같이 쓰이기 때문입니다.
> - 그래서 loss용 변환은 `engine/train.py`, submission용 변환은 `make_submission.py`에서 각각 처리하는 구조로 가면 될 것 같습니다.
>
> 현재 구조는 아래처럼 생각하고 있습니다.
>
> <baseline.py>  
> Ultralytics 로드 → `yolo.model`을 래퍼에서 분리 → `baseline.py`의 `build_model()`에서 `_adapt_num_class(model)` 수행 → 각 detection head에서 `cv3`의 마지막 `Conv2d`를 클래스 수에 맞게 교체 → 수정된 `nn.Module`을 `engine/train.py`로 전달
>
> <engine/train.py>  
> `model.train()` → 옵티마이저, LR 스케줄러, `v8DetectionLoss` 생성 → epoch / batch 단위 학습 → 데이터 포맷 변환 (전처리 완료 전까지는 `MockDataset`으로 테스트 가능) → validation → `evaluate.py` 호출 → `.pt` 저장
>
> 여기서 포맷 변환은 `engine/train.py`에서 처리하는 방향으로 보고 있습니다. 이유는 아래와 같습니다.
>
> 1. `dataset.py` 출력은 `train.py` 하나만 쓰지 않음
>     - `dataset.py`의 bbox는 `xyxy` 형식으로 유지
>     - 이 형식은 PyTorch / torchvision 기준에서도 많이 쓰는 형식이라 `IoU`, `NMS`, `mAP`, evaluation 쪽에서 그대로 활용하기 편합니다.
> 2. `v8DetectionLoss`가 요구하는 bbox 형식이 별도임
>     - 캐글 submission CSV도 `xywh` 형식이지만, `v8DetectionLoss`에서 쓰는 `xywh`와는 좌표 기준이 다릅니다.
>
> 차이점은 아래와 같습니다.
>
> - `bbox.py`의 `xyxy_to_xywh`  
>     → 좌상단 기준 `(x, y, w, h)`
> - `v8DetectionLoss` 입력  
>     → 중심점 기준 `(cx, cy, w, h)`
>
> 즉 `w`, `h`는 같지만 `x`, `y` 기준점이 다르기 때문에 `bbox.py` 변환 함수를 그대로 쓰면 loss 계산이 맞지 않습니다.
>
> 추가로 `v8DetectionLoss` 입력을 위해서는
>
> 1. `xyxy → cxcywh` 변환
> 2. 좌표를 `0~1` 범위로 정규화
> 3. 배치 단위로 합치면서 각 box 앞에 몇 번째 이미지 소속인지 batch index를 붙여 하나의 텐서로 구성
>
> 이 과정이 필요합니다.
>
> 그래서 bbox 좌표 흐름은 아래처럼 생각하고 있습니다.
>
> `dataset.py` 출력  
> → `xyxy` 절대 픽셀
>
> `engine/train.py`  
> → `v8DetectionLoss` 입력용 변환 (`cxcywh + normalize + batch index`)  
> → 학습 loss 계산
>
> `evaluate / postprocess`  
> → `xyxy` 그대로 사용
>
> `postprocess.py` 출력  
> → `xyxy` 절대 픽셀
>
> `make_submission.py`  
> → `bbox.py`에서 변환
>
> `submission.csv`  
> → `xywh` (캐글 제출 형식)
>
> 앞으로 할 일
>
> `baseline.py`
>
> - `build_model(model_name, num_classes)` → `build_model(cfg)`로 변경
> - 필요한 설정값을 `cfg`에서 읽도록 수정
>
> `engine/train.py`
>
> - 옵티마이저 세팅
> - LR 스케줄러 세팅
> - `v8DetectionLoss` 세팅
> - 포맷 변환 코드 작성 (`MockDataset`으로 먼저 테스트)
> - 배치 학습 루프 작성
> - validation 루프 작성
> - checkpoint 저장
>
> `engine/evaluate.py`
>
> - `mAP@0.5`
> - `mAP@0.5:0.95`
> - 황원재님,박창준님과 인터페이스 확인 필요

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">댓글</span><hr style="flex:1;margin:0"></div>


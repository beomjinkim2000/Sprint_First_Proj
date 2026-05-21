---
글쓴사람: 유재열(Model)
날짜: 2026-05-21 12:42
상태: 미해결
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


<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">댓글</span><hr style="flex:1;margin:0"></div>


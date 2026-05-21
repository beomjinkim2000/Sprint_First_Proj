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

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">답변</span><hr style="flex:1;margin:0"></div>

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">댓글</span><hr style="flex:1;margin:0"></div>


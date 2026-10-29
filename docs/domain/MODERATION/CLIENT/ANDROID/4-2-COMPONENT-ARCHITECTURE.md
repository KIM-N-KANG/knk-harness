# 4-2 Android MODERATION 구성

기준: [연동 계약](../4-1-CONTRACT.md).

<br>

### 4-2-1 모듈과 의존

신고는 report 기능 모듈이 소유한다. common, network, designsystem과 analytics를 사용하며 신고가 필요한 기능만 report에 의존한다. 공용 모듈에서 신고 기능을 역참조하지 않는다.

시트는 상태와 동작 콜백을 받고, 공용 컨트롤러가 사유 선택과 제출, 결과 통지를 처리한다. 화면마다 전송과 분석 절차를 복제하지 않는다. 데이터 계층은 reason enum 이름을 보내고 본문 없는 성공을 처리한다.

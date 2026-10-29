# 웹 NOTIFICATION 구성

기준: [공통 연동 계약](../CONTRACT.md), [웹 표현](LAYOUT.md).

<br>

### 책임

| 경계 | 책임 |
|---|---|
| notices | 공용 문구, 태그 배지, 기기 읽음 저장소, 헤더 버튼과 목록 및 상세 |
| notifications | 안 읽은 수와 헤더 버튼, 분류별 알림함. 탭 패널이 자기 당김 스크롤러 소유 |
| my notifications | 계정 수신 설정, 기기 권한 안내, 처리 결과 |
| 루트 | 회원과 필수 동의 판정 뒤 토큰 동기화 및 광고 질문 조립 |
| Firebase 래퍼 | Messaging 지연 초기화, 토큰 발급과 폐기, 전경 구독 |
| 서비스 워커 | compat 초기화와 배경 알림 클릭 이동. 오프라인 캐싱 없음 |

공지 태그 배지와 알림 카드 라벨은 같은 태그 이름 원본을 사용한다. 페이지는 얇은 서버 컴포넌트로 화면만 조립한다. Firebase는 FCM getToken과 deleteToken을 사용하고 FID 기반 register로 대체하지 않는다.

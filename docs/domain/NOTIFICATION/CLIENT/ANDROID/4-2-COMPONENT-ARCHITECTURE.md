# 4-2 Android NOTIFICATION 구성

기준: [연동 계약](../4-1-CONTRACT.md), [Android 표현](3-3-LAYOUT.md).

<br>

### 4-2-1 소유권

| 모듈 | 책임 |
|---|---|
| notification | FirebaseMessagingService, 등록기와 토큰 API, 권한, 수신과 표시, 수신 동의 |
| notification inbox | 회원 알림 API, 분류별 목록과 커서, 읽음 상태와 화면 |
| notification consent | 재질문 시트, 처리 결과와 질문 단계 저장소 |
| notice | 공개 공지 API, 목록과 상세, 기기 읽음 기록과 안 읽음 판정 |
| app | google-services 플러그인, 권한 UI와 세션 종료 연결, 헤더와 목적지 조립 |
| navigation | 허용 URL의 내부 목적지 해석 |
| common과 create | 검수 화면 관찰 포트와 해당 기능의 구현. 알림 트레이가 표시 직전 질의 |

공개 공지는 무인증 클라이언트, 회원 알림은 인증 클라이언트를 사용한다. 알림 읽음의 본문 없는 성공은 공용 오류 변환 경로로 처리한다.

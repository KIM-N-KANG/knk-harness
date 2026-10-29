# Android NOTIFICATION 화면 구성

기준: [공통 화면](../INFORMATION-ARCHITECTURE.md), [Android 요구사항](REQUIREMENTS.md).

<br>

### 목적지

공지 목록과 상세, 알림함 및 설정은 메인 셸 없는 전체 화면이다. 홈, 채팅과 제작의 종은 회원 알림함으로, 마이 공지사항 메뉴는 공지 목록으로 간다. 알림 설정은 마이와 알림함에서 연다.

| 허용 HTTPS 주소 | 목적지 |
|---|---|
| manyak.app 또는 www.manyak.app의 /stories/{id} | 스토리 상세 |
| 같은 호스트 /my/credits | PAYMENT 충전 화면, tab 쿼리는 해당 도메인의 초기 탭 계약 적용 |
| 같은 호스트 /studio | 기존 제작 탭 |
| 같은 호스트 /notices | 공지 목록 |
| 같은 호스트 /notices/{noticeId} | 공지 목록 위 상세 |

기본 포트만 허용하며 사용자 정보가 포함된 URL은 거절한다. 그 밖의 푸시 URL은 홈으로 간다. 알림함은 해석 불가 때 공지 ID와 스토리 ID를 대체로 사용한다.

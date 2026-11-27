# 4-2 컴포넌트 구조: iOS

기준: [iOS 연동 계약](4-1-CONTRACT.md), [iOS 표현](3-3-LAYOUT.md).

<br>

### 4-2-1 타깃과 책임

| 타깃 | 책임 |
|---|---|
| `ManyakNotification` | Firebase Messaging, APNs 기기 토큰을 받는 함수, 토큰 등록기와 토큰 API, 권한 조회와 요청, 알림 센터 위임 객체(앞 표시 판단과 탭 응답 해석), 세션 종료 알림 정리 항목 |
| `ManyakNotification` 알림함 | 회원 알림 API, 분류별 목록과 커서, 읽음 상태와 화면, 안 읽은 수 조회 |
| `ManyakNotification` 동의 | 알림 설정, 재질문 시트, 처리 결과와 질문 단계 저장 |
| `ManyakNotice` | 공개 공지 API, 목록과 상세, 기기 읽음 기록과 안 읽음 판정 |
| 앱 타깃 `Manyak` | Firebase 초기화, APNs 등록 요청과 결과 전달, 위임 객체 지정, 권한 요청과 안내 순서, 세션 종료 조정자의 서버 토큰 삭제 연결과 정리 항목 등록, 헤더 종과 마이 배지 조립, 탭 진입을 외부 진입 보류로 연결 |
| `ManyakNavigation` | 허용 URL의 내부 목적지 해석 |
| `ManyakCommon`, `ManyakCreate` | 검수 결과 대기 화면 관찰 포트와 그 구현. 앞 표시 판단이 질의 |
| `ManyakMy` | 마이 알림 섹션의 알림 설정과 공지사항 메뉴. 새 공지 배지는 앱 타깃이 내린 값 |

공개 공지는 인증 없는 클라이언트, 회원 알림과 토큰 API는 인증 클라이언트를 쓴다. 알림 읽음의 본문 없는 성공은 공용 변환으로 처리한다. ([IOS 기반 네트워크 요청](../../../../platform/CLIENT/IOS/3-EXECUTION.md#3-2-네트워크-요청))

알림 센터 위임 객체는 앱 전체에 하나이며 `ManyakNotification`이 구현하고 앱 타깃만 지정한다. APNs 기기 토큰은 앱 타깃이 받아 `ManyakNotification`에 넘기고 Firebase Messaging이 앱 위임 메서드를 가로채지 않게 한다. ([I-146](DECISIONS.md#i-146)) 홈, 채팅과 제작의 종 버튼과 마이 배지는 값과 이동 콜백만 받고 `ManyakNotification`과 `ManyakNotice`를 직접 참조하지 않는다. 알림 정리 항목은 `UserScopedStore`를 따르고 앱 타깃의 등록 배열에 등록한다.

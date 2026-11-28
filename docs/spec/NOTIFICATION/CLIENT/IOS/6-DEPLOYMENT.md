# 6 배포: iOS

기준: [iOS 실행](4-4-EXECUTION.md), [iOS 검증](5-1-VERIFICATION.md).

<br>

### 6-1 설정과 외부 공급자

| 대상 | 조건 |
|---|---|
| Firebase 앱 | 기존 Firebase 프로젝트에 번들 ID `app.manyak`의 iOS 앱을 추가. `GoogleService-Info.plist`는 저장소에 커밋 ([IOS 기반 빌드와 환경](../../../../platform/CLIENT/IOS/5-DEPLOYMENT.md#5-1-빌드와-환경)) |
| APNs 인증 키 | Apple Developer 계정에서 만든 APNs 인증 키를 Firebase 프로젝트의 iOS 앱에 등록. 개발과 운영 APNs 환경에 같은 키를 씀. 키 파일과 값은 저장소와 문서에 두지 않음 |
| 앱 기능 | 앱 타깃에 푸시 알림 기능. 백그라운드 모드의 원격 알림과 앱 확장 타깃은 두지 않음 |
| Firebase 가로채기 | 앱 `Info.plist`에서 Firebase Messaging의 앱 위임 가로채기를 끔 ([I-146](DECISIONS.md#i-146)) |
| 권한 문구 | 알림 권한 요청 창의 문구는 시스템 문구. 앱이 설명 문구를 따로 두지 않음 |

APNs 키를 바꾸거나 폐기하면 Firebase 프로젝트의 키만 바꾸고 앱 빌드는 바꾸지 않는다. 키가 없거나 무효이면 서버 발송이 실패하고 앱 동작은 바뀌지 않는다.

<br>

### 6-2 호환과 출시 조건

- 토큰 등록은 서버가 iOS `platform` 값과 표시형 알림을 해당 환경에 배포한 뒤에 켠다. Debug의 dev 서버 검증은 dev 서버가, 등록을 켠 Release 빌드의 출시는 운영 서버가 먼저 바뀌어야 한다. iOS 첫 출시는 이 서버 변경의 운영 배포를 선행 조건으로 두며 푸시 없는 출시 분기를 두지 않는다. STORY 완성 중 카드의 알림 안내 문구는 그대로 쓴다. ([I-140](DECISIONS.md#i-140), [I-149](DECISIONS.md#i-149), [STORY iOS 목록과 상세](../../../STORY/CLIENT/IOS/3-3-LAYOUT.md#3-3-1-목록과-상세))
- 서버 페이로드에 `deepLink`나 `recipientId`가 없으면 탭은 홈이고 앱이 앞에 있을 때는 표시하지 않는다. 알 수 없는 `type`도 같은 deepLink 규칙으로 처리한다.
- 알림 읽음과 공지 읽음의 저장 범위를 합치지 않는다. 별도의 토큰 영속 큐를 배포 조건으로 두지 않는다.
- 앱 열기 전용 스킴은 [공통 UI IOS 실행](../../../../ui/IOS/4-4-EXECUTION.md#4-4-1-앱-열기-링크와-푸시-진입)을 따르며 Universal Links 설정은 이 알림 계약에 포함하지 않는다.

실제 기기에서 앞, 백그라운드와 종료 상태의 수신과 탭, 권한 거부, 계정 전환을 확인한다. 단위 테스트만으로 표시와 시스템 권한의 성공을 판정하지 않는다.

# 6 Android NOTIFICATION 배포

기준: [Android 실행](4-4-EXECUTION.md), [Android 검증](5-1-VERIFICATION.md).

<br>

### 6-1 호환과 적용

FCM 설정과 google-services 플러그인은 앱 조립 경계에 둔다. 실제 설정 파일과 토큰을 문서에 넣지 않는다. 별도의 토큰 영속 큐를 배포 조건으로 추가하지 않는다.

기존 PendingIntent의 deepLink 없는 payload와 광고 질문의 이전 단일 플래그를 계속 해석한다. 알림 읽음과 공지 읽음의 저장 범위를 합치지 않는다. HTTPS App Links의 intent-filter와 assetlinks.json은 이 알림 계약에 포함하지 않으며 앱 열기 전용 스킴은 공용 앱 링크 문서를 따른다.

실제 앱의 전경과 배경, 종료 상태 수신 및 탭, 권한 거부, 계정 전환을 기기에서 검증한다. JVM 테스트만으로 표시와 OS 권한의 성공을 판정하지 않는다.

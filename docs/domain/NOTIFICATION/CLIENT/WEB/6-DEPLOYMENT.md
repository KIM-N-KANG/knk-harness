# 6 웹 NOTIFICATION 배포

기준: [웹 실행](4-4-EXECUTION.md), [웹 검증](5-1-VERIFICATION.md).

<br>

### 6-1 설정과 호환

- NEXT_PUBLIC_FIREBASE_API_KEY, NEXT_PUBLIC_FIREBASE_PROJECT_ID, NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID, NEXT_PUBLIC_FIREBASE_APP_ID, NEXT_PUBLIC_FIREBASE_VAPID_KEY가 모두 있어야 활성화한다. 실제 값은 문서에 기록하지 않는다.
- production 여부로 차단하지 않으며 보안 컨텍스트인 localhost에서도 검증할 수 있다. E2E는 VAPID 키를 비워 실제 푸시를 끈다.
- 매니페스트는 /manifest.webmanifest, 아이콘은 192, 512와 maskable 형식이다. icon-192.png 경로는 서버 MANYAK_PUSH_WEB_ICON_URL 기본값과 일치해야 한다.
- 서비스 워커는 Firebase 공개 설정을 등록 URL의 쿼리로 받는다. 응답은 no-store, 등록은 updateViaCache none이며 compat 스크립트는 gstatic CDN에서 받는다.
- 설정 없는 빌드에서 권한 질문과 토큰 등록을 시도하지 않는다. 배포 후에는 실제 브라우저와 iOS 설치본의 배경 수신 및 기존 창 이동을 별도로 확인한다.

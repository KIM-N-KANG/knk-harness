# 웹 NOTIFICATION 실행

기준: [연동 계약](../CONTRACT.md), [웹 상태](STATE-MANAGEMENT.md).

<br>

### 목록과 읽음

- 공지와 알림 목록은 nextCursor를 그대로 다음 요청에 사용하고 끝 sentinel 교차로 다음 페이지를 읽는다. 실패 뒤 자동 재요청은 중단한다.
- 공지 상세 성공 뒤 읽음을 기록하고 404는 미존재 화면으로 구분한다. 본문은 whitespace-pre-wrap으로 그린다.
- 한 건과 모두 읽음 mutation은 onMutate에서 캐시된 모든 분류 페이지의 대상 readAt을 갱신하고 onSettled에서 unread-count를 무효화한다. 모두 읽음만 실패 스냅숏으로 복원한다.
- 알림 링크는 푸시 링크 해석을 재사용해 서비스 origin의 상대 경로로 바꾸고 실패하면 noticeId, storyId 순서로 대체한다.

<br>

### 토큰과 클릭

1. 현재 회원과 필수 동의, 권한 granted를 확인한다. 발급 시작과 서비스 워커 등록 직후 각각 navigator.onLine을 확인한다.
2. FCM 토큰을 발급해 platform WEB으로 PUT하고 성공한 토큰을 저장한다. 권한 변경과 online 이벤트에서 다시 판정한다.
3. 회원 종료 정리가 저장 토큰 DELETE와 SDK deleteToken을 fire-and-forget으로 실행한다. 실패가 로그아웃을 막지 않는다.
4. 서비스 워커는 importScripts 전에 notificationclick을 등록하고 stopImmediatePropagation으로 SDK의 focus 전용 처리를 막는다.
5. data.FCM_MSG의 fcmOptions.link, notification.click_action, data.deepLink 순서로 링크를 찾는다. 같은 origin만 쿼리를 보존해 사용하며 없거나 다른 origin이면 루트로 보낸다.
6. 같은 origin 창은 navigate 후 focus한다. 창이 없거나 이동이 실패하면 clients.openWindow를 사용한다.

배경 표시는 브라우저의 webpush.notification이 담당하므로 recipientId를 대조하지 못한다. 전경 구독은 현재 회원과 일치한 메시지만 토스트로 표시한다.

<br>

### 권한과 동의

회원 판정 뒤 페이지 로드당 한 번 기기 권한 질문과 회원 재진입 횟수를 처리한다. 신규 필수 동의 제출 클릭에서는 사용자 제스처 안에서 권한을 먼저 요청한 뒤 동의 저장과 선택 답 전달을 진행한다. 루트가 선택 답과 재질문 신호를 구독하며 허용은 GET으로 서비스 값을 확인하고 광고만 켠 PUT, 거절은 질문 기록으로 처리한다.

설정 저장은 세 값을 모두 보내고 광고를 끌 때 야간도 false로 보낸다. 처리 결과 시각은 응답 시각이 아닌 사용자 의사 표시 시각을 사용한다. 필수 동의와 신규 가입 안내가 끝난 뒤에만 재질문 시트를 열고 시트와 설정이 같은 처리 결과 다이얼로그를 사용한다.

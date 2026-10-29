# 5-1 웹 NOTIFICATION 검증

기준: [공통 검증](../5-1-VERIFICATION.md), [웹 실행](4-4-EXECUTION.md).

각 사례의 ID, 조건과 기대 결과 및 기존 자동화 표시는 보존한다. 표시는 이번 실행이나 배포 완료를 뜻하지 않는다. 실제 환경과 결과는 PR 및 CI에 기록한다.

<br>

### 5-1-1 알림 설정과 푸시

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-NOTIFICATIONS-01 | P0 | 게스트 | 경로 직접 진입 | `/login`으로 replace 이동 | ✅ e2e `my/notifications` | [웹 접근 조건](../../../APP/CLIENT/WEB/3-1-INFORMATION-ARCHITECTURE.md#3-1-1-셸과-문서) |
| MY-NOTIFICATIONS-02 | P0 | 회원 | 마이 > 알림 > "알림 설정" 탭 | 뒤로가기 헤더 "알림 설정" + (브라우저 알림을 못 받으면) 상태 배너 + 서비스 알림(켜짐)·광고 알림(꺼짐) 스위치 줄(광고 라벨 옆 개인정보 처리방침 외부 링크 아이콘). 야간 줄 없음. 조회 중에는 스위치 자리에 골격 | ✅ e2e `my/notifications` | 웹 PWA 푸시 알림 설정 화면 |
| MY-NOTIFICATIONS-03 | P0 | 회원, 광고 꺼짐 | 광고 알림 스위치 탭 | `PUT /users/me/push-settings`에 세 값 전체(`marketingPush: true`) 전송 → 처리 결과 다이얼로그(제목 + "전송자: …"·"일시: …"·"처리 내용: 광고 알림 수신 동의 완료" + 전체 폭 확인) → 닫으면 야간 광고 허용 줄 표시 | ✅ e2e `my/notifications` | 웹 PWA 푸시, §4-3-5 푸시 수신 동의 |
| MY-NOTIFICATIONS-04 | P0 | 회원, 광고·야간 켜짐 | 광고 알림 스위치 탭 | 야간도 함께 `false`인 본문 전송, "광고 알림 수신 동의 철회 완료" 통지, 야간 줄 사라짐 | ✅ e2e `my/notifications` | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-05 | P1 | 회원 | 서비스 알림 스위치 탭 | 통지 없이 저장. 저장 5xx면 "알림 설정을 저장하지 못했어요" 토스트 + 스위치 원복 | ✅ e2e `my/notifications` | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-06 | P1 | 설정 조회 5xx | 진입 | 목록 대신 "알림 설정을 불러오지 못했어요" + "다시 시도하기" 버튼. 재시도 성공 시 스위치 표시 | ✅ e2e `my/notifications` | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-07 | P1 | 푸시 활성 빌드, 권한 `default` | 배너 확인 → "알림 켜기" 탭 | 배너 "브라우저 알림 설정이 꺼져 있어요" + 버튼, 스위치 줄은 비활성. 허용하면 배너가 사라지고 줄이 활성으로 바뀌며 토큰 PUT 발생. 거부하면 "브라우저 알림이 차단되어 있어요" 토스트와 차단 배너. 차단 배너의 "방법 보기"는 사이트 설정 허용 안내 다이얼로그를 연다 | 수동(실기기) | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-08 | P1 | iOS Safari 탭(비설치본) | 배너 확인 | 홈 화면 추가 안내 배너, 버튼 없음, 스위치 줄 비활성 | 수동(실기기) | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-09 | P2 | 회원, 광고 켜짐 | 야간 광고 허용 탭 | 야간만 `true`인 본문 전송, "야간 광고 알림 수신 동의 완료" 통지 | 수동 | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-10 | P1 | 푸시 활성 빌드, 회원, 알림 권한 허용, 오프라인 | 열린 화면에서 토큰 동기화 시도 후 네트워크 연결 복구 | 오프라인에서는 Firebase 토큰 발급을 건너뜀. 복구 후 회원 상태와 권한이 유효하면 토큰 발급과 PUT을 자동 재시도. 복구 전에 로그아웃한 경우 등록하지 않음 | ◐ 단위 `tests/lib/push/messaging.test.ts`(발급 차단과 복구 후 직접 재호출), 이벤트와 실기기 동작은 수동 | [웹 PWA 푸시 토큰 등록](AGENTS.md) |
| MY-NOTIFICATIONS-11 | P1 | 푸시 활성 빌드, 회원, 앱 창이 이미 열려 있음(iOS 홈 화면 설치본 포함) | 백그라운드 푸시 알림 탭 | 새 창 없이 열린 창이 `deepLink`(쿼리 유지)로 이동하고 앞으로 옴. 창이 없으면 새 창으로 연다. 링크가 없거나 다른 origin이면 앱 홈 | ◐ 단위 `tests/lib/push/firebase-messaging-sw.test.ts`(창 이동·새 창·origin 검사), 실기기 동작은 수동 | [웹 PWA 푸시 표시](AGENTS.md) |

<br>

### 5-1-2 공지사항

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-NOTICES-01 | P0 | 게스트, 30일 안에 게시된 공지 있음, 읽음 기록 없음 | 홈 진입 → 헤더 확인 | 오른쪽에 secondary 로그인 버튼, 그 오른쪽에 확성기 아이콘 버튼(접근 이름 "새 공지사항 있음")과 아이콘 오른쪽 위 빨간 점 | ✅ e2e `notices/notices` | FE-SCREEN-014 진입점·안 읽은 공지 표시 |
| MY-NOTICES-02 | P0 | 회원, 안 읽은 알림 0건 | 채팅·제작·마이 진입 → 헤더 확인 | 채팅·제작에는 로그인 버튼 없이 종 버튼(접근 이름 "알림", `/notifications`로 이동)만, 마이 헤더에는 종 버튼 없음. 회원 헤더에서 공지사항으로 바로 가는 버튼은 없음 | ✅ e2e `notices/notices` | [웹 상단 헤더](../../../APP/CLIENT/WEB/3-2-INTERACTION-FLOWS.md#3-2-1-기록과-뒤로가기), FE-SCREEN-015 진입점 |
| MY-NOTICES-13 | P0 | 게스트/회원, 읽음 기록 없음, 공지 있음 | 마이 > 알림 섹션 확인 → "공지사항" 메뉴 탭 → 목록만 보고 뒤로가기 | 알림 설정(회원만) 아래 확성기 아이콘 "공지사항" 메뉴와 라벨 오른쪽 연한 빨간 "새 공지" 배지. 탭하면 `/notices`, 목록만 보고 돌아오면 배지가 그대로 남음 | ✅ e2e `notices/notices` | FE-SCREEN-014 진입점·안 읽은 공지 표시 |
| MY-NOTICES-03 | P0 | 게스트, 읽음 기록 없음, 공지 2건(모두 30일 안, 태그 UPDATE·MAINTENANCE) | 헤더 공지 버튼 탭 → 목록 확인 → 첫 줄 탭 → 뒤로가기 → 뒤로가기 | `/notices`로 이동, "공지사항" 뒤로가기 헤더, 줄마다 태그 배지("업데이트" 보조색, "점검" 주의색)·제목·게시일(`YYYY-MM-DD`)이 좌우를 채우고 두 줄 모두 굵은 제목과 제목 끝 작은 빨간 점(sr 텍스트 "새 공지"). 상세를 열면 `manyak:notice-read-ids`에 그 ID가 기록되고 목록으로 돌아오면 그 줄만 점이 꺼짐. 홈으로 돌아와도 안 읽은 공지가 남아 헤더 점 유지 | ✅ e2e `notices/notices` | FE-SCREEN-014 안 읽은 공지 표시·목록 |
| MY-NOTICES-04 | P1 | 첫 공지는 읽음 기록 있음, 둘째는 없음, 셋째는 게시 30일 초과 | `/notices` 진입 → 둘째 줄 탭 → 홈까지 뒤로가기 | 둘째 공지에만 점. 둘째를 읽고 홈으로 돌아오면 헤더 버튼 접근 이름이 "공지사항"으로 바뀌고 점 없음 | ✅ e2e `notices/notices` | FE-SCREEN-014 안 읽은 공지 표시 |
| MY-NOTICES-05 | P0 | `nextCursor`가 있는 20건 | 목록 끝까지 스크롤 | 받은 `nextCursor`를 그대로 실어 다음 페이지를 요청하고 아래에 이어 붙임. "더 보기" 버튼 없음 | ✅ e2e `notices/notices` | FE-SCREEN-014 목록, [웹 커서 목록](../../../PAYMENT/CLIENT/WEB/4-4-EXECUTION.md#4-4-1-정책과-체험-내역) |
| MY-NOTICES-06 | P1 | 다음 페이지 조회 실패 | 목록 끝까지 스크롤 | 기존 목록을 유지하고 아래 재시도 버튼만 표시, 자동 재요청 중단 | 수동 | FE-SCREEN-014 상태 |
| MY-NOTICES-07 | P1 | 공지 0건 / 첫 조회 5xx | `/notices` 진입 | 0건이면 "아직 등록된 공지가 없어요"와 헤더 점 없음. 5xx면 "공지사항을 불러오지 못했어요" + "다시 시도하기", 탭하면 다시 조회해 목록 표시 | ✅ e2e `notices/notices` | FE-SCREEN-014 상태 |
| MY-NOTICES-08 | P0 | 목록 표시됨, 상세 200(태그 UPDATE) | 첫 줄 탭 | `/notices/{noticeId}`로 이동. "공지사항" 뒤로가기 헤더 아래 "업데이트" 태그 배지, `h1` 제목, "게시 YYYY-MM-DD", 줄바꿈을 살린 평문 본문(`white-space: pre-wrap`). 게시일과 같은 날 수정이면 "수정" 표시 없음 | ✅ e2e `notices/notices` | FE-SCREEN-014 상세 |
| MY-NOTICES-09 | P1 | `updatedAt`이 게시일 다음 날 | 상세 주소 직접 진입 → 뒤로가기 | "게시 …" 옆에 "수정 YYYY-MM-DD" 표시. 주소로 바로 연 상세의 뒤로가기는 `/notices`로 교체 이동 | ✅ e2e `notices/notices` | FE-SCREEN-014 상세, [웹 화면 전환](../../../APP/CLIENT/WEB/3-2-INTERACTION-FLOWS.md#3-2-1-기록과-뒤로가기) |
| MY-NOTICES-10 | P1 | 상세 404 | 상세 주소 직접 진입 | "공지를 찾을 수 없어요" + "공지사항 목록으로" 링크, 탭하면 `/notices` | ✅ e2e `notices/notices` | FE-SCREEN-014 상태 |
| MY-NOTICES-11 | P2 | 헤더 점 표시 중, 안 읽은 공지 1건 | 푸시 딥링크로 그 공지 상세 직접 진입 → 홈 복귀 | 그 공지가 읽음으로 기록되고 헤더 점과 마이 배지가 사라짐 | 수동 | FE-SCREEN-014 안 읽은 공지 표시 |
| MY-NOTICES-12 | P2 | 주소로 바로 연 `/notices` | 뒤로가기 헤더 탭 | 홈(`/`)으로 교체 이동 | 수동 | [웹 화면 전환](../../../APP/CLIENT/WEB/3-2-INTERACTION-FLOWS.md#3-2-1-기록과-뒤로가기) |
| MY-NOTICES-14 | P1 | 공지 목록이 맨 위 | 목록을 아래로 당겼다 놓기 | 홈과 같은 표시자("당겨서 새로고침" → "놓으면 새로고침" → "새로고침 중")로 첫 페이지부터 다시 조회하고 응답 전까지 기존 줄 유지 | ✅ e2e `notices/notices` | [웹 화면 전환](../../../APP/CLIENT/WEB/3-2-INTERACTION-FLOWS.md#3-2-1-기록과-뒤로가기) |
| MY-NOTICES-15 | P2 | 공지 목록과 상세 조회 성공 | 목록과 상세 주소로 직접 진입, 홈 공지 버튼에서 목록으로 이동한 뒤 상세 열기와 뒤로가기 | 모든 진입과 이동에서 웹 Spec의 기본 문서 제목 유지 | ✅ e2e `notices/notices` | [문서 열람과 검색 노출](../../../APP/CLIENT/WEB/2-2-REQUIREMENTS.md#2-2-1-지원과-접근성) |

<br>

### 5-1-3 알림함

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-INBOX-01 | P0 | 게스트 | `/notifications` 직접 진입 → 홈 헤더 확인 | 로그인 화면으로 교체 이동. 홈 헤더에는 `/notices`로 가는 확성기 아이콘 공지사항 버튼 | ✅ e2e `notifications/notifications` | FE-SCREEN-015 진입점 |
| MY-INBOX-02 | P0 | 회원, 안 읽은 수 total 2(소식 1·활동 1) | 홈 진입 → 헤더 종 버튼 탭 | 종 버튼 접근 이름 "새 알림 있음"과 오른쪽 위 빨간 점, 로그인 버튼 없음. 탭하면 `/notifications`, "알림" 뒤로가기 헤더 오른쪽에 보조 버튼 "모두 읽음"과 톱니 아이콘(접근 이름 "알림 설정", `/my/notifications`로 이동), 소식 탭이 선택되고 두 탭 라벨 옆에 점 | ✅ e2e `notifications/notifications` | FE-SCREEN-015 진입점·구성 |
| MY-INBOX-03 | P0 | 소식 2건(안 읽은 공지 알림 태그 UPDATE, 읽은 이벤트 알림) | 소식 탭 카드 확인 | 카드마다 분류 라벨(공지는 "업데이트", 이벤트는 "이벤트")·상대 시각·제목·본문. 안 읽은 카드만 굵은 제목과 제목 끝 빨간 점(sr "안 읽음"), 읽은 카드는 보조색 | ✅ e2e `notifications/notifications` | FE-SCREEN-015 카드 |
| MY-INBOX-04 | P0 | 안 읽은 공지 알림, 상세 200 | 카드 탭 → 뒤로가기 | `POST .../{notificationId}/read` 1회 뒤 `/notices/{noticeId}` 상세로 이동. 돌아오면 그 카드의 점이 꺼지고 소식 탭 라벨 점도 꺼짐 | ✅ e2e `notifications/notifications` | FE-SCREEN-015 읽음과 이동 |
| MY-INBOX-05 | P0 | 활동 2건(안 읽은 완성, 읽은 검토 결과) | 활동 탭 탭 → 카드 확인 → "모두 읽음" 탭 → 뒤로가기 | "스토리 완성"·"검토 결과" 라벨 카드. 모두 읽음은 `POST .../read-all` 1회, 두 탭의 점과 카드 점이 꺼지고 버튼은 비활성. 홈으로 돌아오면 헤더 점이 없고 접근 이름 "알림" | ✅ e2e `notifications/notifications` | FE-SCREEN-015 읽음과 이동 |
| MY-INBOX-06 | P1 | `nextCursor`가 있는 20건 | 소식 목록 끝까지 스크롤 | 받은 `nextCursor`를 그대로 실어 다음 페이지를 이어 붙임 | ✅ e2e `notifications/notifications` | FE-SCREEN-015 카드 |
| MY-INBOX-07 | P1 | 소식·활동 0건 / 첫 조회 5xx | `/notifications` 진입 → 활동 탭 | 0건이면 소식 "아직 받은 소식이 없어요", 활동 "아직 활동 알림이 없어요"와 비활성 모두 읽음. 5xx면 "알림을 불러오지 못했어요" + "다시 시도하기", 탭하면 다시 조회 | ✅ e2e `notifications/notifications` | FE-SCREEN-015 상태 |
| MY-INBOX-08 | P1 | 모두 읽음 요청 5xx | "모두 읽음" 탭 | 카드와 점이 원래대로 돌아오고 "알림을 읽음 처리하지 못했어요" 토스트 | 수동 | FE-SCREEN-015 읽음과 이동 |
| MY-INBOX-09 | P1 | `deepLink`가 서비스 origin이 아닌 알림, `noticeId`·`storyId` 없음 | 카드 탭 | 이동 없이 읽음만 기록(카드는 링크가 아닌 버튼) | ◐ 단위 `tests/features/notifications/inbox/utils/notification-link` | FE-SCREEN-015 읽음과 이동 |
| MY-INBOX-10 | P2 | 주소로 바로 연 `/notifications` | 뒤로가기 헤더 탭 | 홈(`/`)으로 교체 이동 | 수동 | [웹 화면 전환](../../../APP/CLIENT/WEB/3-2-INTERACTION-FLOWS.md#3-2-1-기록과-뒤로가기) |
| MY-INBOX-11 | P1 | 목록이 맨 위 | 아래로 당겼다 놓기 | 홈과 같은 표시자로 그 탭의 첫 페이지부터 다시 조회 | 수동 | [웹 화면 전환](../../../APP/CLIENT/WEB/3-2-INTERACTION-FLOWS.md#3-2-1-기록과-뒤로가기) |
| MY-INBOX-12 | P2 | 회원, 알림함 조회 성공 | 알림함 주소로 직접 진입, 홈 헤더 종 버튼으로 알림함 열기 | 두 진입 모두 웹 Spec의 기본 문서 제목 유지 | ✅ e2e `notifications/notifications` | [문서 열람과 검색 노출](../../../APP/CLIENT/WEB/2-2-REQUIREMENTS.md#2-2-1-지원과-접근성) |
| MY-INBOX-13 | P1 | 활동에 `CREDIT_EXPIRY_REMINDER` 알림 1건(`deepLink` 이프 충전) | 활동 탭 카드 확인 → 카드 탭 | 카드 위 줄에 "이프 만료" 라벨. 탭하면 읽음을 기록하고 `deepLink`의 이프 충전 탭으로 이동 | 수동 | FE-SCREEN-015 카드, KNK-1842 |
| MY-INBOX-14 | P1 | 활동에 `STORY_TAKEN_DOWN` 알림 1건(`deepLink` `/studio`) | 활동 탭 카드 확인 → 카드 탭 | 카드 위 줄에 "공개 제한" 라벨과 서버가 보낸 제목·본문. 탭하면 읽음을 기록하고 제작 탭으로 이동 | 수동 | FE-SCREEN-015 카드, KNK-1886 |

공지, 설정과 알림함은 각각 NOTIFICATION-US-001, NOTIFICATION-US-004와 NOTIFICATION-US-002를 검증한다. 푸시 수신과 클릭은 NOTIFICATION-US-003이며 실제 브라우저의 권한과 배경 수신은 별도로 확인한다.

# 5-1 검증: 안드로이드

기준: [공통 검증](../5-1-VERIFICATION.md), [Android 실행](4-4-EXECUTION.md).

각 사례의 ID, 조건과 기대 결과 및 기존 자동화 표시는 보존한다. 표시는 이번 실행이나 배포 완료를 뜻하지 않는다. 실제 환경과 결과는 PR 및 CI에 기록한다.

공지의 기존 A01, A03과 A06은 회원 헤더가 공지로 이동하던 때의 검증 기록이다. 현재 회원 헤더는 알림함으로 이동하므로 공지 진입은 마이 메뉴로 확인하고 헤더 점은 서버 알림 수를 기준으로 판정한다.

<br>

### 5-1-1 공지사항

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-NOTICES-A01 | P0 | Android 회원, 30일 안에 게시된 공지 있음, 읽음 기록 없음 | 홈·채팅·제작 탭 헤더 확인 → 마이 탭 헤더 확인 | 홈·채팅·제작 헤더 오른쪽에 종 아이콘 버튼(접근 이름 "새 공지사항 있음")과 오른쪽 위 빨간 점. 마이 헤더에는 없음 | ✅ 수동(에뮬레이터, `captures/KNK-1819`) | FE-SCREEN-014 진입점 |
| MY-NOTICES-A02 | P0 | Android 회원, 안 읽은 공지 있음 | 마이 > 알림 섹션 확인 | 알림 설정 아래 확성기 아이콘 "공지사항" 메뉴와 라벨 오른쪽 연한 빨간 "새 공지" 배지. 탭하면 목록 | ✅ 수동(에뮬레이터) | FE-SCREEN-014 진입점 |
| MY-NOTICES-A03 | P0 | Android, 읽음 기록 없음, 공지 3건 | 헤더 공지 버튼 탭 → 첫 줄 탭 → 뒤로가기 → 뒤로가기 → 모든 줄을 열고 홈 복귀 | 목록은 굵은 제목과 제목 끝 빨간 점(보조 기술 이름 "새 공지"), 줄을 누르면 앱 공통 리플, 상세는 제목·"게시 YYYY-MM-DD"·줄바꿈 살린 본문. 돌아오면 연 줄만 점이 꺼지고 홈 헤더 점은 유지, 모두 열면 헤더 점과 마이 배지가 꺼짐 | ✅ 수동(에뮬레이터) · unit `notice/NoticeViewModelsTest`·`NoticeUnreadTest` | FE-SCREEN-014 안 읽은 공지 표시 |
| MY-NOTICES-A04 | P1 | Android, 앱 종료 상태 | 공지 게시 푸시 탭(또는 `manyak://manyak.app/notices/{noticeId}` 앱 열기 링크) → 뒤로가기 | 그 공지 상세가 열리고 읽음으로 기록. 뒤로가기는 공지 목록, 다시 뒤로가기는 홈 | ✅ 수동(에뮬레이터, `am start -a VIEW`) · unit `app/ExternalEntryTest`·`navigation/DeepLinkTest` | [Android 알림](AGENTS.md) |
| MY-NOTICES-A05 | P1 | Android, 없는 `noticeId` | 딥링크로 상세 진입 → "공지사항 목록으로" 탭 | "공지를 찾을 수 없어요" + 보조 안내 + "공지사항 목록으로" 버튼, 탭하면 목록. 읽음 기록 없음 | ✅ 수동(에뮬레이터) · unit `NoticeViewModelsTest` | FE-SCREEN-014 상태 |
| MY-NOTICES-A06 | P1 | Android, 앱 실행 뒤 비행기 모드 | 헤더 공지 버튼 탭 → 비행기 모드 해제 → "다시 시도" 탭 | "공지사항을 불러오지 못했어요" + "다시 시도"(앱 공통 문구). 재시도하면 목록 표시. 안 읽음 점은 조회 실패 동안 꺼짐 | ✅ 수동(에뮬레이터) | FE-SCREEN-014 상태, [Android 공지사항](../../../../ui/ANDROID/3-3-LAYOUT.md#3-3-1-셸과-조작) |
| MY-NOTICES-A08 | P1 | Android, 목록 표시됨 | 목록을 당겨 새로고침 → 비행기 모드에서 다시 당김 | 당김 표시자가 돌고 목록을 다시 읽음. 오프라인이면 기존 목록을 그대로 두고 "새로고침하지 못했어요" 토스트. 골격·빈 상태·실패 화면에서는 당김 없음 | ✅ 수동(에뮬레이터) · unit `NoticeViewModelsTest` | [Android 공지사항](../../../../ui/ANDROID/3-3-LAYOUT.md#3-3-1-셸과-조작) |
| MY-NOTICES-A07 | P2 | Android, `nextCursor`가 있는 21건 이상 | 목록 끝까지 스크롤, 다음 페이지 실패 유도 | 끝에 닿으면 다음 페이지를 이어 붙이고, 실패하면 기존 목록 아래 "다시 시도"만 표시하고 자동 재요청 없음 | ◐ unit `NoticeViewModelsTest`(dev에 3건뿐이라 화면은 미확인) | FE-SCREEN-014 목록·상태 |

<br>

### 5-1-2 알림함과 푸시

| ID | 유저 스토리 | 사전조건과 절차 | 기대 결과 | 수단 |
|---|---|---|---|---|
| NOTIFICATION-ANDROID-01 | NOTIFICATION-US-002 | 소식과 활동, 느린 조회 중 읽음과 모두 읽음, 실패 | 늦은 조회가 읽음을 되돌리지 않음, 모두 읽음 실패 전체 복원 | 목록 ViewModel 테스트 |
| NOTIFICATION-ANDROID-02 | NOTIFICATION-US-002 | 목록 회전, 공지와 스토리 및 제작 진입, 뒤로가기 | 탭 및 위치 유지, 상세는 알림함 복귀, 제작은 기존 탭 새로고침 | 기기와 내비게이션 테스트 |
| NOTIFICATION-ANDROID-03 | NOTIFICATION-US-003 | 회원과 동의 전환, 같은 토큰과 새 세션, 늦은 PUT 및 403 | 직렬 등록과 직전 재검증, 세대가 일치한 종료만 반영 | 등록 및 세션 테스트 |
| NOTIFICATION-ANDROID-04 | NOTIFICATION-US-003 | recipient 불일치, Pending과 프로필 대기 5초, 로그아웃 | 미확인 수신 폐기, 표시 직전 재확인, 트레이와 보류 정리 | 수신 테스트와 기기 |
| NOTIFICATION-ANDROID-05 | NOTIFICATION-US-003 | 허용 및 금지 링크, deepLink 없는 이전 payload, 로그인 중 프로세스 종료 | 목적지 규칙, 수신자 재확인, 목적지 복원, 중복 상세 없음 | 링크 테스트와 기기 |
| NOTIFICATION-ANDROID-06 | NOTIFICATION-US-003 | 같은 제출본 검수 결과 대기, 표시 후 2분, 다른 제출본 | 관찰 중 중복만 억제, 서로 다른 알림 유지, 잠금 화면 제목만 | 표시 테스트와 기기 |
| NOTIFICATION-ANDROID-07 | NOTIFICATION-US-004 | 선택 동의, 첫 거절 후 재진입 1~3회, 두 번째 거절과 재로그인 | 필수 동의 독립, 세 번째 재질문, 종료 기록과 회원 격리 | 동의 테스트와 기기 |
| NOTIFICATION-ANDROID-08 | NOTIFICATION-US-004 | 광고와 야간 변경, 서비스 변경, 저장 실패, 기기 알림 차단 | 전체 저장과 야간 동시 해제, 성공 광고 변경만 통지, 실패 복원 | 설정 테스트와 기기 |

공지 원문 사례는 NOTIFICATION-US-001에 대응한다. 신규 시나리오는 실행 완료 표시가 아니다.

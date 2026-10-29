# 5-1 Android 공용 검증

기준: [공통 검증](../5-1-VERIFICATION.md), [실행](4-4-EXECUTION.md).

<br>

### 5-1-1 시나리오

| ID | 유저 스토리 | 사전조건과 절차 | 기대 결과 | 수단 |
|---|---|---|---|---|
| CLIENT-ANDROID-01 | CLIENT-US-001 | 네 탭 순회, 스크롤 뒤 복귀, 다른 탭과 홈에서 뒤로가기 | 탭별 위치 보존, 다른 탭은 홈, 홈은 앱 밖 | 기기와 내비게이션 테스트 |
| CLIENT-ANDROID-02 | CLIENT-US-001 | 시트와 잠금, 회전, 테마 변경, 프로세스 재생성 | 오버레이와 입력은 구성 변경 유지, 프로세스는 저장 완료 상태만 복구 | 기기와 상태 테스트 |
| CLIENT-ANDROID-03 | CLIENT-US-001 | SSE 중단, 요청 취소와 중복 Intent, 화면 정지와 복귀 | 취소 오류 미보고, single-flight, effect 중복 재생 없음 | ViewModel 테스트 |
| CLIENT-ANDROID-04 | CLIENT-US-002 | 마이 서비스 안내와 법적 문서 열기, 회전 | 공통 본문, 웹 전용 게스트 안내, 문서 위치 유지 | 기기 |
| CLIENT-ANDROID-05 | CLIENT-US-003 | 테마 세 값 전환, 앱 재실행 | 즉시 반영, 저장 선택과 표시 일치 | 기기 |
| CLIENT-ANDROID-06 | CLIENT-US-004 | 전용 링크의 상세, 공지, 미지원 경로와 로그인 전 진입 | 허용 목적지와 홈 대체, 로그인 후 소비, 일반 https는 브라우저 | 링크 테스트와 기기 |
| CLIENT-ANDROID-07 | CLIENT-US-001 | 제스처와 3버튼, 키보드 및 접근성으로 탭과 시트 조작 | 안전 영역 확보, 이름과 선택 한 번 낭독, 닫기 문구 | 기기 |
| CLIENT-ANDROID-08 | CLIENT-US-001 | 이미지 배경과 그림 탭, 회전과 프로세스 종료 | 그림 탭 유지, 배경 즉시 닫기, URL과 제스처 복원 범위 일치 | 뷰어 테스트와 기기 |

<br>

### 5-1-2 구조와 관측

모듈 변경은 checkModuleArchitecture와 루트 check를 실행하고 허용 의존, PSI 참조, Hilt 생성, Manifest, 경로 직렬화와 저장 식별자 호환을 확인한다. PSI 검사는 import alias, 완전 수식 이름과 typealias를 포함하지만 reflection이나 완전한 의미 분석을 보장하지 않는다.

device ID 주입 전 이벤트와 setOnce의 순서, 설치 귀속 재시도와 완료 키, 로그아웃 후 귀속 재발화 방지, screen_name과 breadcrumb 및 민감 정보 제외를 확인한다. release의 Crashlytics 수집과 mapping은 해당 빌드 증거로 검증한다.

자동화와 실제 기기 결과를 구분하며 신규 시나리오는 실행 완료 표시가 아니다. 실제 명령과 실행 결과는 구현 저장소와 PR 및 CI를 기준으로 한다.

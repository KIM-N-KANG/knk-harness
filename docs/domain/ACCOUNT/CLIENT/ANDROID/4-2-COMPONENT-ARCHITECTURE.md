# 4-2 ACCOUNT Android 구성

<br>

### 4-2-1 모듈과 공용 포트

| 구성 | 책임과 경계 |
|---|---|
| `auth` | 소셜 서버 인증, 가입 대기, 토큰과 세션. `network`의 `SessionTokenAccess` 구현 |
| `legal` | 동의 조회와 기록, 루트 수명의 동의 상태 및 시트. `common`의 `MemberConsent` 구현 |
| `my` | 프로필, 초대와 페르소나의 기준 저장소. 같은 DataStore에 인스턴스 중복 금지 |
| `common`의 `PersonaAccess` | 상세가 목록과 생성 항목의 미리 선택을 관찰. 변경은 마이 저장소 |
| `SignupOnboardingWriter` | `my`의 초대와 `home`의 스토리 온보딩이 각각 등록. 신규 토큰 발급 시 `auth`가 모두 호출 |
| `app` | 루트 내비게이션, 세션 종료 조정자와 `UserScopedStore` 목록 조립 |
| 네트워크와 분석 | 요청 시 식별자 포트 사용. 네트워크의 분석 SDK 직접 의존 금지 |

Hilt의 Singleton, ViewModel과 제작 저장소의 ActivityRetained 수명을 사용한다. 별도 사용자 세션 Component는 두지 않는다. 인증 클라이언트, 인터셉터, 토큰 관리자, 재발급 API와 무인증 클라이언트의 순환은 지연 주입과 단일 재발급으로 끊는다. ([Android 모듈 규칙](../../../../client/ANDROID/4-2-COMPONENT-ARCHITECTURE.md#4-2-1-책임과-의존))

<br>

### 4-2-2 화면 조립

| 구성 | 경계 |
|---|---|
| Navigation 3 | typed `NavKey`, 인증과 메인 back stack 분리. 기능 ViewModel에 back stack 주입 금지 |
| 경로 | 복원 가능한 식별자만 포함, 목적지에서 재조회. 생성 시 ViewModel에 주입, 저장 상태에서 경로 재해석 금지 |
| 회원 그래프 | 서버 동의와 동의 ViewModel 완료를 모두 확인한 뒤 생성, 외부 목적지 소비 |
| 세션 전환 | 이전 stack 폐기. 로그아웃 처리자가 별도로 화면 이동하지 않음 |
| 법적 문서 | 두 그래프에서 진입 가능. 동의 중에는 문서별 ViewModel 키의 Dialog로 시트 위 표시 |
| 프로필 편집 | 초기 프로필, 입력과 시트 상태는 화면 ViewModel. 검증은 순수 함수, 변경 요청은 저장소 |
| 페르소나 | 생성과 수정 폼 공유, 소개 조립과 분해는 순수 함수. 상세의 선택은 공용 포트로 연결 |

회원 안내는 루트의 알림 권한 응답 뒤 선택 동의, 초대와 재질문을 연결한다. 초대는 메인 탭 화면이 맨 위이고 홈이 선택된 경우에만 표시한다.

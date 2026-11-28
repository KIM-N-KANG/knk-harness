# 4-2 컴포넌트 구조: iOS

<br>

### 4-2-1 모듈과 공용 포트

| 구성 | 책임과 경계 |
|---|---|
| `ManyakAuth` | 제공자 SDK 로그인, 소셜 서버 인증, 가입 대기, Keychain 토큰, `SessionState`, `SessionGate`, 재발급 직렬화와 시작 판정. `ManyakNetwork`의 토큰 포트 구현. Google Sign-In과 Kakao SDK 타입을 밖으로 공개하지 않음 |
| `ManyakLogin` | 로그인 화면. 제공자 호출은 `ManyakAuth`의 계약으로만 |
| `ManyakLegal` | 동의 조회와 기록, 앱 루트 수명의 동의 상태와 시트, 법적 문서 화면. `ManyakCommon`의 `MemberConsent` 구현 |
| `ManyakMy` | 프로필, 초대와 페르소나의 기준 저장소와 마이, 편집, 초대, 탈퇴 화면. 같은 저장 키를 쓰는 인스턴스 중복 금지 |
| `ManyakCommon`의 `PersonaAccess` | 상세가 목록과 생성 항목의 미리 선택을 관찰. 변경은 `ManyakMy` 저장소 |
| `ManyakCommon`의 `UserScopedStore` | 회원 데이터 정리 계약. 기기 suite와 회원 suite도 `ManyakCommon`이 제공 |
| `SignupOnboardingWriter` | `ManyakMy`의 초대와 `ManyakOnboarding`의 스토리 온보딩이 구현. 신규 가입 토큰 발급 때 `ManyakAuth`가 등록된 구현을 모두 호출 |
| `ManyakDesignSystem` | 홈과 마이가 함께 쓰는 사업자 정보 푸터, 이미지 캐시 비우기 |
| 앱 타깃 `Manyak` | 루트 선택, `SessionTerminationCoordinator`, `UserScopedStore`와 `SignupOnboardingWriter` 등록 배열, 회원 데이터 자동 조회, 제공자 복귀 URL 전달 |
| 네트워크와 분석 | 요청 때 식별자 포트 사용. `ManyakNetwork`는 Amplitude SDK에 직접 의존하지 않음 |

회원 세션 수명의 별도 객체 묶음을 두지 않고 앱 수명 객체, 명시적 종료와 정리 계약으로 회원 데이터를 다룬다. 인증 요청 계층, 토큰 포트, 재발급 액터와 무인증 요청 계층의 순환은 재발급을 무인증 계층으로 보내고 조립 객체가 생성 순서를 정해 끊는다. ([IOS 모듈과 허용 의존](../../../../platform/CLIENT/IOS/1-COMPONENT-ARCHITECTURE.md#1-2-모듈과-허용-의존), [공용 포트와 조립](../../../../platform/CLIENT/IOS/1-COMPONENT-ARCHITECTURE.md#1-4-공용-포트와-조립))

<br>

### 4-2-2 화면 조립

| 구성 | 경계 |
|---|---|
| 라우터 | 앱 타깃 소유. 로그인 그래프 스택과 메인 셸의 탭 스택 분리. 기능 Store에 라우터와 경로 주입 금지 |
| 라우트 | 식별자만 싣고 목적지에서 재조회. 화면 Store는 라우트 인자를 이니셜라이저로 받음 |
| 회원 루트 | 서버 동의와 동의 Store의 완료를 모두 확인한 뒤 생성. 외부 진입은 그 뒤 소비 |
| 세션 전환 | 이전 루트, 스택과 시트 폐기. 로그아웃 처리자가 따로 화면 이동하지 않음 |
| 법적 문서 | 로그인 그래프와 탭 스택 모두에서 진입. 동의 중에는 문서마다 Store를 가진 전체 화면 덮개로 시트 위 표시 |
| 프로필 편집 | 초기 프로필, 입력과 시트 상태는 화면 Store. 검증은 순수 함수, 변경 요청은 저장소. 미저장 변경이나 저장 중에는 화면이 가장자리 밀기를 끄고 뒤로 버튼을 이탈 확인으로 바꿈 ([I-068](DECISIONS.md#i-068)) |
| 제공자 화면 표시 | SDK가 요구하는 표시 기준 화면은 앱 타깃이 현재 창에서 찾아 `ManyakAuth`에 넘김. Store와 Domain은 UIKit 타입을 받지 않음 |
| 사업자 정보 | `ManyakDesignSystem`의 푸터. 값은 `ManyakDesignSystem` String Catalog에 항목마다 따로 두어 통신판매업 신고번호와 호스팅서비스 제공자처럼 값 하나만 바꿈. 공정위 주소는 푸터가 직접 열고 문서 링크는 콜백으로 라우터가 법적 문서 경로에 연결 |
| 페르소나 | 생성과 수정 폼 공유, 소개 조립과 분해는 순수 함수. 상세의 선택은 공용 포트로 연결 |

회원 안내는 루트가 알림 권한 응답 뒤 선택 동의, 초대와 재질문을 차례로 연결한다. 초대는 메인 셸에서 홈 탭이 선택되고 홈 탭 스택이 루트이며 열린 시트와 전체 화면 덮개가 없을 때만 표시한다.

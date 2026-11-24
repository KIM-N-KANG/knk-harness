# DECISIONS.md

현재 적용 기준은 각 명세에 두고 결정 당시의 이유와 대체 관계는 이 문서에 기록한다.

<br>

### 1. 기록 규칙

- 결정 하나를 표 하나로 기록한다. 기존 ID, 날짜, 당시 상태와 근거를 유지한다.
- 상태와 구현 설명은 원본의 기록 시점을 기준으로 해석한다. 현재 적용 여부나 배포 완료를 과거 기록만으로 단정하지 않는다.
- 결정이 바뀌면 새 ID로 기록하고 대체하는 결정과 적용 범위를 명시한다.
- 원문에 구분되지 않은 배경, 대안과 영향은 추측해서 보충하지 않는다.

<br>

### 2. 결정 기록

<br>

<a id="a-003"></a>
<a id="a-003-clean-architecture-전면-적용을-하지-않음"></a>

**A-003. Clean Architecture 전면 적용을 하지 않음**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-22 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | 모든 동작에 별도 계층, UseCase를 둘지 검토했다. |
| 채택 | 실제 책임이 있는 계층만 두며 단순 위임 UseCase를 만들지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 형식적 계층과 반복 코드를 늘리지 않기 위해서이다. |
| 영향 | 의존, 소유 경계는 유지하되 구체 현재 규칙은 모듈 설계가 소유한다. |
| 근거 | [이관 원문 A:163](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L163-L175) |

<br>

<a id="a-005"></a>
<a id="a-005-ui-상태-관리를-직접-구성"></a>

**A-005. UI 상태 관리를 직접 구성**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-22 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | MVI 프레임워크 도입과 작은 공통 기반을 비교했다. |
| 채택 | Intent, Event, 순수 reduce, State, Effect 기반 MviViewModel을 사용한다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 필요한 상태, 효과 규칙을 직접 통제하고 불필요한 프레임워크 제약을 피한다. |
| 영향 | 순서, 포화, 재수집 계약을 공통 기반에서 검증한다. |
| 근거 | [이관 원문 A:253](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L253-L263) |

<br>

<a id="a-006"></a>
<a id="a-006-crashlytics로-앱-크래시-수집"></a>

**A-006. Crashlytics로 앱 크래시 수집**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-22 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | 웹, 서버와 Sentry로 통일할지 Android용 수집 도구를 선택할지 검토했다. |
| 채택 | Crashlytics와 Amplitude를 사용하고 Firebase Analytics를 추가하지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 제품 분석 SDK를 중복 도입하지 않고 수동 breadcrumb와 요청 상관 키로 도구 분리 비용을 제한한다. |
| 영향 | API 24~29 ANR 공백을 수용하며 event-local request_id, release 수집, R8 매핑 업로드를 관리한다. |
| 근거 | [이관 원문 A:269](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L269-L286) |

<br>

<a id="a-023"></a>
<a id="a-023-구성-변경의-activity-재생성을-수용"></a>

**A-023. 구성 변경의 Activity 재생성을 수용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-28 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | 방향, 테마, 글자 크기 변경에서 화면 상태와 리소스를 함께 복원해야 했다. |
| 채택 | configChanges, screenOrientation을 선언하지 않고 수명에 맞는 상태 저장을 사용한다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 리소스 재적용을 직접 재현하지 않고 큰 화면의 방향 잠금 예외에도 대응하기 위해서이다. |
| 영향 | 구성 변경과 프로세스 종료를 별도로 검증하며 당시 최대 글자 크기, 가로 레이아웃은 잔여로 남았다. |
| 근거 | [이관 원문 A:1537](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L1537-L1573) |

<br>

<a id="a-027"></a>
<a id="a-027-오픈소스-고지는-의존성에서-생성"></a>

**A-027. 오픈소스 고지는 의존성에서 생성**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-31 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | 수동 라이선스 목록은 의존성 변경과 어긋날 수 있다. |
| 채택 | 빌드 의존성 기반 생성 목록을 사용한다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 직접 작성한 목록을 별도로 유지하지 않기 위해서이다. |
| 영향 | 빌드와 고지 생성 경로를 함께 유지한다. |
| 근거 | [이관 원문 A:1023](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L1023-L1028) |

<br>

<a id="a-038"></a>
<a id="a-038-기능-단위-모듈과-내부-패키지-계층"></a>

**A-038. 기능 단위 모듈과 내부 패키지 계층**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-09-05 |
| 상태 | Accepted |
| 배경 | 중앙 core에 업무 소유권과 계층별 Gradle 모듈이 모여 있었다. |
| 채택 | 기능을 최상위 모듈로, entity/domain/data/presentation을 내부 패키지로 둔다. 공유 신고는 report가 소유한다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | common에 신고를 두면 network/designsystem 역참조가 생기고 화면별 복제는 제출, 분석 규칙을 중복시킨다. |
| 영향 | 계층의 컴파일 격리 대신 PSI 경계 검사, 리뷰가 필요하다. 이전 core 배치 규칙을 대체하며 API, 저장 형식 변경은 포함하지 않는다. |
| 근거 | [이관 전 원문](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/planning/android-module-architecture.md#L11-L23) |

<br>

<a id="a-047"></a>
<a id="a-047-release-빌드에-r8-축소난독화-적용"></a>

**A-047. release 빌드에 R8 축소, 난독화 적용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-09-26 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | v1.1.1은 R8을 끈 채 출시했고, Play Console이 DEX 난독화 비율 1%를 기준 미달로 표시했다(2027년 2월까지 해결하지 않으면 공개, 게시가 제한될 수 있음). 앱이 이름이나 리플렉션에 기대는 곳과 라이브러리 consumer rules의 빈틈을 확인해야 했다. |
| 채택 | release만 AGP `optimization { enable = true }`로 코드, 리소스 축소와 난독화를 켜고, keep 규칙은 `app/proguard-rules.pro` 한 파일에 consumer rules로 부족한 곳만 둔다. 현재는 분석 이벤트가 `::class.simpleName`으로 보내는 `DomainError` 하위 타입 이름과, 오류 원인 enum 필드를 이름으로 읽는 카카오 SDK 모델(카카오 공식 규칙)이다. Crashlytics 매핑 업로드는 `mappingFileUploadEnabled = true`로 명시한다. debug는 켜지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | Crashlytics 플러그인은 `variant.isMinifyEnabled`로 업로드 여부를 정하는데 `optimization` DSL로 켠 R8을 그 값이 반영하지 않아, 명시하지 않으면 매핑 없이 난독화된 스택만 쌓인다. 규칙을 넓게 잡으면 축소 효과가 줄고 어떤 규칙이 왜 필요한지 흐려지므로, 실제로 깨진 곳만 이유와 함께 둔다. 카카오 규칙이 없으면 카카오 토큰이 없는 상태에서 앱 시작 직후 `NoSuchFieldException`으로 크래시한다. |
| 영향 | `bundleRelease`가 Crashlytics로 매핑을 올리고 AAB에도 매핑이 실려 Play 역난독에 쓰인다. 새 라이브러리나 이름, 리플렉션에 기대는 코드를 더하면 R8을 켠 빌드로 해당 흐름을 확인한다. 로컬 업로드 키로 서명한 release는 운영 로그인이 되지 않아, 로그인 뒤 흐름은 같은 규칙으로 R8을 켠 debug 빌드(dev 서버)로 검증한다. |
| 근거 | [KNK-1408](https://kimandkang.atlassian.net/browse/KNK-1408), [Android 계획](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/docs/plans/r8-minification.md) |

<br>

<a id="a-093"></a>
<a id="a-093-기반-모듈은-core-화면-기능-모듈은-feature-아래에-둠"></a>

**A-093. 기반 모듈은 core, 화면 기능 모듈은 feature 아래에 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-09 |
| 상태 | Accepted |
| 배경 | A-038 이후 17개 런타임 모듈이 모두 루트 폴더에 나란히 있어, 폴더만 보고는 기반 모듈과 화면 기능 모듈을 구분할 수 없었다. |
| 채택 | 기반 모듈(common, designsystem, navigation, analytics, network, auth)과 공유 신고 report는 `core/`, 화면 기능 모듈은 `feature/` 아래에 둔다. Gradle 경로도 폴더를 따라 `:core:<모듈>`, `:feature:<모듈>`로 등록하고 app과 build-logic은 루트에 남긴다. 모듈 수, 소유권, 의존 규칙과 Kotlin 패키지(`app.manyak.<모듈>`)는 바꾸지 않는다. `checkModuleArchitecture`가 각 모듈이 정해진 그룹 경로에 등록됐는지도 검사한다. |
| 대안 | 폴더만 옮기고 `projectDir`로 기존 Gradle 경로(`:home`)를 유지하는 방식. 수정 범위는 작지만 폴더 위치와 Gradle 경로, 모듈 단위 명령이 서로 다른 구조를 가리킨다. |
| 이유 | 폴더, Gradle 경로, 타입 안전 프로젝트 접근자(`projects.feature.home`)가 같은 구조를 가리켜 하나만 보고도 위치를 알 수 있다. report는 chat, studio, story가 함께 쓰는 공유 업무라 `feature/`에 두면 기능 간 의존처럼 보인다. 패키지를 유지해 라우트 직렬화 이름, Hilt 생성 코드, R8 규칙에 영향이 없다. |
| 영향 | 모듈 단위 명령이 `./gradlew :feature:chat:testDebugUnitTest`처럼 바뀐다. 이전 기능 계획의 `:chat:` 형태 명령은 당시 기준 기록이다. `:core`, `:feature`는 빌드 파일 없이 하위 모듈을 묶기만 하는 중간 프로젝트이며 경계 검사 대상이 아니다. 하네스와 Android 문서의 소스 링크를 새 폴더로 옮겼다. |
| 대체 관계 | [A-038](#a-038)의 "기능을 최상위 모듈로" 중 폴더와 Gradle 경로의 배치만 대체한다. 기능 단위 모듈, 내부 패키지 계층, report의 신고 소유는 유지한다. |
| 근거 | [KNK-2049](https://kimandkang.atlassian.net/browse/KNK-2049), [Android 계획](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/docs/plans/module-folder-grouping.md), [참고 구조](https://github.com/Nexters/Satto-Android/tree/develop) |

<br>

<a id="a-094"></a>
<a id="a-094-여러-모듈이-쓰는-테스트-도우미는-테스트-전용-core-testing에-둠"></a>

**A-094. 여러 모듈이 쓰는 테스트 도우미는 테스트 전용 core/testing에 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-09 |
| 상태 | Accepted |
| 배경 | 11개 모듈의 테스트 39개가 `Dispatchers.setMain`, `resetMain` 설정을 각자 반복했고, core 계약을 구현한 Fake가 chat과 create에 같은 내용으로 따로 있었다. |
| 채택 | 테스트 소스 세트에서만 의존하는 `:core:testing`을 두고 `MainDispatcherRule`과 둘 이상의 모듈이 같은 동작으로 쓰는 core 계약의 Fake를 모은다. `checkModuleArchitecture`는 테스트 설정의 의존을 따로 모아 testing을 테스트에서만 허용하고, 프로덕션 의존과 프로덕션 코드의 참조는 실패시킨다. testing은 common에만 의존한다. 한 모듈만 쓰거나 모듈마다 동작이 다른 Fake(프로필, 세션)는 각 모듈의 `src/test`에 남긴다. |
| 대안 | Gradle test fixtures로 계약 모듈 옆에 Fake를 두는 방식. 계약이 common과 auth에 흩어져 모듈마다 설정이 필요하고, 메인 디스패처 규칙처럼 계약과 무관한 도우미를 둘 곳이 없다. |
| 이유 | 디스패처 교체를 JUnit Rule 하나로 모으면 설정 누락과 되돌리기 누락이 사라진다. Fake를 강제로 하나로 합치면 테스트마다 다른 전제가 흐려지므로 같은 동작인 것만 모은다. 기능 간 테스트 의존은 여전히 막는다. |
| 영향 | 디스패처를 쓰는 테스트는 `@get:Rule val mainDispatcherRule = MainDispatcherRule()`을 쓰고, 같은 디스패처로 `runTest`를 돌릴 때는 `MainDispatcherRule(dispatcher)`로 넘긴다. testing은 런타임 모듈 수에 포함하지 않는다. |
| 대체 관계 | 없음. 한 모듈 안에서 여러 테스트가 쓰는 Fake를 그 모듈의 `src/test` 공유 패키지에 두고 기능 간 테스트 의존을 두지 않는 [모듈 재구성 계획](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/docs/plans/module-reorganization.md#21-화면과-테스트)의 규칙은 유지한다. |
| 근거 | [KNK-2049](https://kimandkang.atlassian.net/browse/KNK-2049), [Android 계획](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/docs/plans/core-testing-module.md), [Android 공식 모듈화 패턴의 테스트 모듈](https://developer.android.com/topic/modularization/patterns#test-modules) |

<br>

<a id="a-097"></a>
<a id="a-097-pr-전-코드-리뷰와-에뮬레이터-화면-검사를-둠"></a>

**A-097. PR 전 코드 리뷰와 에뮬레이터 화면 검사를 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-23 |
| 상태 | Accepted |
| 배경 | 앱에는 스크린샷 테스트 도구가 없고, 화면 확인 규칙은 `installDebug` 뒤 `adb exec-out screencap`으로 전후를 비교한다는 한 줄뿐이라 대상 화면과 점검 항목, 기기 설정 복구가 작업마다 달랐다. PR 전 diff 리뷰 절차도 없어 정적 검사가 잡지 못하는 규칙(디자인 토큰, 문구 위치, `reduce` 순수성, 라우트 식별자, 구성 변경)은 작성자가 직접 기억해야 했다. 웹은 같은 날 [W-046](../WEB/DECISIONS.md#w-046)으로 PR 전 UI 검사와 코드 리뷰를 도입했다. |
| 채택 | 모든 새 PR 전에 저장소의 pr-review 스킬로 diff를 리뷰하고, UI를 바꾼 PR은 ui-review 스킬로 debug 빌드를 에뮬레이터에 설치해 `android` CLI의 캡처와 레이아웃 트리로 [4-3](4-VERIFICATION.md#4-3-pr-전-리뷰와-화면-검사)의 항목을 확인한다. 결과는 PR 본문에 남기고 머지 조건은 CI의 `check`와 `assembleDebug`로 유지한다. 리뷰에 쓰는 공식 Android 스킬(`android/skills`)은 skills CLI로 받아 커밋과 해시를 `skills-lock.json`에 고정한다. |
| 대안 | 스크린샷 테스트 도구(Roborazzi 등) 도입: 웹이 W-046에서 걷어낸 기준 이미지 갱신 비용이 같은 형태로 생긴다.<br>기존 screencap 전후 비교만 유지: 점검 항목과 기기 설정 복구가 작업마다 계속 달라진다. |
| 이유 | 웹과 같은 PR 전 절차로 맞추고, 화면을 실행해 보는 검사와 diff를 읽는 리뷰를 나눠 서로 독립적으로 돌린다. `android` CLI는 셸 명령이라 Claude Code와 Codex에서 같은 스킬로 쓸 수 있다. |
| 영향 | 화면 표현은 머지 조건에 들어가지 않는다. 회원 화면은 로그인된 에뮬레이터 상태에 기대므로 로그아웃 상태면 확인하지 못한 범위로 남는다. 검사는 앱 데이터를 지우는 명령과 소셜 로그인을 쓰지 않는다. 변경 전 비교는 요청한 경우에만 별도 worktree의 기준 빌드로 한다. |
| 근거 | [KNK-2132](https://kimandkang.atlassian.net/browse/KNK-2132), [W-046](../WEB/DECISIONS.md#w-046) |

<br>

<a id="a-098"></a>
<a id="a-098-기능-계획-문서를-저장소에서-없애고-pr-본문에-둠"></a>

**A-098. 기능 계획 문서를 저장소에서 없애고 PR 본문에 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-23 |
| 상태 | Accepted |
| 배경 | 앱 저장소의 `docs/plans/`에 기능 계획 66개와 저장소 기준 문서 `_project.md`가 있었다. 완료한 계획은 같은 기능의 PR 본문과 기록이 겹쳤고, [A-093](#a-093) 이전의 모듈 경로가 남아 저장소 검색 결과에 섞였다. 웹은 [KNK-2131](https://kimandkang.atlassian.net/browse/KNK-2131)에서 저장소의 계획 문서를 지웠다. |
| 채택 | 앱 저장소의 `docs/`를 지운다. 기능 계획과 실행 결과는 PR 본문에, 선택의 이유는 하네스 결정 기록에 둔다. `_project.md` 중 저장소가 소유하는 값(서버 주소 주입, 평문 통신 범위, Gradle 힙, 새 모듈의 CI 게이트 연결)만 앱 `AGENTS.md`로 옮긴다. 하네스 결정 기록이 근거로 걸던 계획 링크는 삭제 직전 커밋(`27b9c46b`)의 고정 링크로 바꾼다. |
| 대안 | 완료 계획만 지우고 `_project.md`는 `docs/PROJECT.md`로 유지<br>지금처럼 계획을 저장소에 보관 |
| 이유 | 웹과 같이 계획 기록을 PR 한 곳으로 모으고, 저장소가 소유하는 값은 매 세션 읽히는 `AGENTS.md` 한 곳에 둔다. |
| 영향 | 앱 `AGENTS.md`가 몇 줄 길어진다. 과거 계획은 git 이력과 고정 링크로만 볼 수 있다. 기존 결정의 내용과 ID는 바꾸지 않고 근거 링크의 주소만 바꿨다. |
| 근거 | [KNK-2132](https://kimandkang.atlassian.net/browse/KNK-2132) |

<br>

<a id="a-099"></a>
<a id="a-099-버튼의-주-색은-브랜드-원색으로-둠"></a>

**A-099. 버튼의 주 색은 브랜드 원색으로 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-24 |
| 상태 | Accepted (DESIGN.md 기록에서 옮김) |
| 배경 | 주 버튼 배경 후보는 로고와 같은 브랜드 원색 `brand`(#05A66B)와 한 단계 어두운 `backgroundBrandBold`(#00804B)였다. 원색 위 흰 글자의 대비는 3.15로 AA 기준에 못 미친다. |
| 채택 | 주 버튼과 FAB의 배경은 `brand`로 두고 `backgroundBrandBold`는 눌림 상태에만 쓴다. M3 슬롯 파생(primary = `backgroundBrandBold`)은 안전망이라 버튼 색을 명시한다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 웹 primary와 같은 값으로 맞추는 것을 흰 글자 대비 3.15보다 우선했다. |
| 영향 | 주 버튼 글자 대비가 AA에 못 미친다. 같은 문제가 있는 조합은 DESIGN.md의 쓰면 안 되는 조합과 함께 관리한다. |
| 근거 | [DESIGN.md 브랜드](../../../../../manyak-android/DESIGN.md#브랜드), [이동 전 기록](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/DESIGN.md) |

<br>

<a id="a-100"></a>
<a id="a-100-눌림-피드백을-테마의-리플-하나로-둠"></a>

**A-100. 눌림 피드백을 테마의 리플 하나로 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-09-03 |
| 상태 | Accepted (DESIGN.md 기록에서 옮김) |
| 배경 | 2026-08-24에는 리플을 앱 전체에서 껐다(별도 결정 ID 없음). 배경색이 없는 카드와 행은 눌림을 알릴 수단이 없었다. |
| 채택 | `ManyakTheme`이 `LocalRippleConfiguration`으로 `overlayPressed` 색과 농도를 내리고 호버, 포커스, 드래그 농도는 0으로 둔다. 선택 표시가 피드백을 맡는 자리(하단 탭, 밑줄 탭, 선택 컨트롤이 있는 행, 이미지 뷰어 닫기 영역)만 리플을 끈다. 축소 같은 다른 눌림 애니메이션은 더하지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 채움이 없는 요소에도 같은 규칙으로 눌림을 말하려면 반투명 리플 하나가 필요했다. |
| 영향 | 2026-08-24의 리플 전역 끄기를 대체한다. 길게 누르기는 열릴 때 `LongPress` 햅틱을 한 번 울린다. |
| 근거 | [DESIGN.md 모션](../../../../../manyak-android/DESIGN.md#모션), [이동 전 기록](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/DESIGN.md) |

<br>

<a id="a-101"></a>
<a id="a-101-디자인-토큰-사본을-두지-않고-kotlin-파일을-기준으로-둠"></a>

**A-101. 디자인 토큰 사본을 두지 않고 Kotlin 파일을 기준으로 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-08-29, 2026-11-24 |
| 상태 | Accepted |
| 배경 | 토큰 값은 웹과 공유하는 디자인 토큰에서 왔지만 생성기가 앱 저장소 밖에 있다. 앱 저장소의 `design/design-tokens.json` 사본은 아무도 읽지 않고 손으로만 맞추다 어긋났다. DESIGN.md의 YAML front matter와 산문 표도 같은 값을 다시 적어 2026-11에는 다크 `backgroundNeutral`처럼 코드와 다른 값이 남았다. |
| 채택 | 2026-08-29에 토큰 JSON 사본을 지웠고 Style Dictionary 같은 생성기를 두지 않는다. 2026-11-24에 DESIGN.md의 front matter를 지우고 `core/designsystem`의 Kotlin 토큰 파일을 값의 기준으로 둔다. DESIGN.md는 토큰의 용도, 금지 조합과 공용 컴포넌트 규칙을 적는다. 2026-08-29에 다크 `textSubtlest`와 `textDisabled`를 한 단계 밝게 올린 값은 유지한다. |
| 대안 | 생성기를 앱 빌드에 연결: 토큰 변경 빈도에 비해 Android 빌드에 Node 의존을 얹는 비용이 크다. |
| 이유 | 사람이 옮겨 적는 값은 기준을 한 곳에 정해야 어긋났을 때 어느 쪽이 맞는지 판단할 수 있다. DESIGN.md의 여백, 크기, 모양, 모션, 타이포 표는 화면을 만들 때 바로 보는 참고로 남기고, 값이 다르면 Kotlin이 기준이다. 어긋남이 실제로 생긴 색은 산문에서 값을 빼고 용도만 적는다. |
| 영향 | 값을 바꾸면 Kotlin 토큰 파일과 DESIGN.md 표를 같은 커밋에서 고친다. 웹과 공유하는 값이면 PR에 웹 변경 필요를 적는다. 두 클라이언트의 값이 같은지는 자동으로 확인하지 못한다. |
| 근거 | [KNK-2132](https://kimandkang.atlassian.net/browse/KNK-2132), [이동 전 DESIGN.md](https://github.com/KIM-N-KANG/manyak-android/blob/27b9c46bb5b7dcad1b9bb9a50f7ec18c3d1c8f31/DESIGN.md) |

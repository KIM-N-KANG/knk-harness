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
| 날짜 | 2026-09-05, 상태: Accepted |
| 상태 | 원문에 별도 상태 기록 없음 |
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
| 근거 | [KNK-1408](https://kimandkang.atlassian.net/browse/KNK-1408), [Android 계획](../../../../../manyak-android/docs/plans/r8-minification.md) |

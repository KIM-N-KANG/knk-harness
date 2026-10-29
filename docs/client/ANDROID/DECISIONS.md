# 공용 ANDROID 결정 기록

확정된 결정의 ID, 당시 상태와 본문을 보존한다. 현재 적용 범위는 후속 결정과 번호 문서를 함께 확인한다.

<br>

<a id="a-003"></a>

## A-003. Clean Architecture 전면 적용을 하지 않음

- 결정일: 2026-08-22 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:163](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L163-L175)
- **맥락:** 모든 동작에 별도 계층·UseCase를 둘지 검토했습니다.
- **결정:** 실제 책임이 있는 계층만 두며 단순 위임 UseCase를 만들지 않습니다.
- **이유:** 형식적 계층과 반복 코드를 늘리지 않기 위해서입니다.
- **주요 영향:** 의존·소유 경계는 유지하되 구체 현재 규칙은 모듈 설계가 소유합니다.

<br>

<a id="a-005"></a>

## A-005. UI 상태 관리를 직접 구성

- 결정일: 2026-08-22 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:253](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L253-L263)
- **맥락:** MVI 프레임워크 도입과 작은 공통 기반을 비교했습니다.
- **결정:** Intent·Event·순수 reduce·State·Effect 기반 MviViewModel을 사용합니다.
- **이유:** 필요한 상태·효과 규칙을 직접 통제하고 불필요한 프레임워크 제약을 피합니다.
- **주요 영향:** 순서·포화·재수집 계약을 공통 기반에서 검증합니다.

<br>

<a id="a-006"></a>

## A-006. Crashlytics로 앱 크래시 수집

- 결정일: 2026-08-22 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:269](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L269-L286)
- **맥락:** 웹·서버와 Sentry로 통일할지 Android용 수집 도구를 선택할지 검토했습니다.
- **결정:** Crashlytics와 Amplitude를 사용하고 Firebase Analytics를 추가하지 않습니다.
- **이유:** 제품 분석 SDK를 중복 도입하지 않고 수동 breadcrumb와 요청 상관 키로 도구 분리 비용을 제한합니다.
- **주요 영향:** API 24~29 ANR 공백을 수용하며 event-local request_id·release 수집·R8 매핑 업로드를 관리합니다.

<br>

<a id="a-010"></a>

## A-010. Navigation 3 사용

- 결정일: 2026-08-23 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:145](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L145-L155)
- **맥락:** 탭 셸에서 백스택·상태 소유 방식을 선택했습니다.
- **결정:** Navigation 3의 명시적 백스택과 복원 가능한 라우트 키를 사용합니다.
- **이유:** 탭·세션·퍼널 백스택을 앱이 직접 소유하기 위해서입니다.
- **주요 영향:** 딥링크·푸시 진입 매핑과 키 직렬화는 앱이 관리합니다.

<br>

<a id="a-011"></a>

## A-011. 셸이 공용 헤더와 탭 소유

- 결정일: 2026-08-23 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:415](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L415-L426)
- **맥락:** 화면별 헤더와 탭을 반복 구성할지 검토했습니다.
- **결정:** 메인 셸이 chrome을 소유하고 각 탭은 콘텐츠를 제공합니다.
- **이유:** 전환 중 공용 UI가 사라지거나 위치가 달라지는 것을 막습니다.
- **주요 영향:** 전체 화면 목적지는 셸 위에 쌓고 탭별 상태를 보존합니다.

<br>

<a id="a-023"></a>

## A-023. 구성 변경의 Activity 재생성을 수용

- 결정일: 2026-08-28 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:1537](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L1537-L1573)
- **맥락:** 방향·테마·글자 크기 변경에서 화면 상태와 리소스를 함께 복원해야 했습니다.
- **결정:** configChanges·screenOrientation을 선언하지 않고 수명에 맞는 상태 저장을 사용합니다.
- **이유:** 리소스 재적용을 직접 재현하지 않고 큰 화면의 방향 잠금 예외에도 대응하기 위해서입니다.
- **주요 영향:** 구성 변경과 프로세스 종료를 별도로 검증하며 당시 최대 글자 크기·가로 레이아웃은 잔여로 남았습니다.

<br>

<a id="a-027"></a>

## A-027. 오픈소스 고지는 의존성에서 생성

- 결정일: 2026-08-31 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:1023](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L1023-L1028)
- **맥락:** 수동 라이선스 목록은 의존성 변경과 어긋날 수 있습니다.
- **결정:** 빌드 의존성 기반 생성 목록을 사용합니다.
- **이유:** 직접 작성한 목록을 별도로 유지하지 않기 위해서입니다.
- **주요 영향:** 빌드와 고지 생성 경로를 함께 유지합니다.

<br>

<a id="a-028"></a>

## A-028. 뒤로가기 전환은 수평 이동

- 결정일: 2026-09-03 · 기록 확정 상태: Accepted
- 대체 관계: [A-015](../../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-015)의 전환 방식만 부분 대체
- 근거: [이관 원문 A:351](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L351-L361)
- **맥락:** 교차 페이드로는 들어오고 나가는 방향이 드러나지 않았습니다.
- **결정:** 일반 진입·뒤로가기는 수평 이동, 퍼널 덮개는 별도 수직 전환을 사용합니다.
- **이유:** 사용자가 화면 관계와 이동 방향을 이해하도록 하기 위해서입니다.
- **주요 영향:** 교차 페이드 결정의 전환 부분만 대체하고 닫기의 의미는 유지합니다.

<br>

<a id="a-038"></a>

## A-038. 기능 단위 모듈과 내부 패키지 계층

- 결정일: 2026-09-05 · 상태: Accepted
- **맥락:** 중앙 core에 업무 소유권과 계층별 Gradle 모듈이 모여 있었습니다.
- **선택:** 기능을 최상위 모듈로, entity/domain/data/presentation을 내부 패키지로 둡니다. 공유 신고는 report가 소유합니다.
- **이유:** common에 신고를 두면 network/designsystem 역참조가 생기고 화면별 복제는 제출·분석 규칙을 중복시킵니다.
- **주요 영향:** 계층의 컴파일 격리 대신 PSI 경계 검사·리뷰가 필요합니다. 이전 core 배치 규칙을 대체하며 API·저장 형식 변경은 포함하지 않습니다.
- 근거: [이관 전 원문](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/planning/android-module-architecture.md#L11-L23)

<br>

<a id="a-047"></a>

## A-047. release 빌드에 R8 축소·난독화 적용

- 결정일: 2026-09-26 · 기록 확정 상태: Accepted
- **맥락:** v1.1.1은 R8을 끈 채 출시했고, Play Console이 DEX 난독화 비율 1%를 기준 미달로 표시했습니다(2027년 2월까지 해결하지 않으면 공개·게시가 제한될 수 있음). 앱이 이름이나 리플렉션에 기대는 곳과 라이브러리 consumer rules의 빈틈을 확인해야 했습니다.
- **결정:** release만 AGP `optimization { enable = true }`로 코드·리소스 축소와 난독화를 켜고, keep 규칙은 `app/proguard-rules.pro` 한 파일에 consumer rules로 부족한 곳만 둡니다. 현재는 분석 이벤트가 `::class.simpleName`으로 보내는 `DomainError` 하위 타입 이름과, 오류 원인 enum 필드를 이름으로 읽는 카카오 SDK 모델(카카오 공식 규칙)입니다. Crashlytics 매핑 업로드는 `mappingFileUploadEnabled = true`로 명시합니다. debug는 켜지 않습니다.
- **이유:** Crashlytics 플러그인은 `variant.isMinifyEnabled`로 업로드 여부를 정하는데 `optimization` DSL로 켠 R8을 그 값이 반영하지 않아, 명시하지 않으면 매핑 없이 난독화된 스택만 쌓입니다. 규칙을 넓게 잡으면 축소 효과가 줄고 어떤 규칙이 왜 필요한지 흐려지므로, 실제로 깨진 곳만 이유와 함께 둡니다. 카카오 규칙이 없으면 카카오 토큰이 없는 상태에서 앱 시작 직후 `NoSuchFieldException`으로 크래시합니다.
- **주요 영향:** `bundleRelease`가 Crashlytics로 매핑을 올리고 AAB에도 매핑이 실려 Play 역난독에 쓰입니다. 새 라이브러리나 이름·리플렉션에 기대는 코드를 더하면 R8을 켠 빌드로 해당 흐름을 확인합니다. 로컬 업로드 키로 서명한 release는 운영 로그인이 되지 않아, 로그인 뒤 흐름은 같은 규칙으로 R8을 켠 debug 빌드(dev 서버)로 검증합니다.
- 근거: [KNK-1408](https://kimandkang.atlassian.net/browse/KNK-1408), [Android 계획](../../../../manyak-android/docs/plans/r8-minification.md)

<br>

<a id="a-071"></a>

## A-071. 웹의 앱 열기 링크를 https 대신 전용 스킴으로 받기

- 날짜: 2026-10-13
- 상태: 확정
- 범위: `MainActivity` intent-filter, `PushEntry`의 앱 열기 진입, 웹 앱 안내 배너의 intent 링크

웹 앱 안내 배너([웹 W-033](../WEB/DECISIONS.md#w-033))는 패키지를 명시한 `intent://` 링크로 앱을 엽니다. 받는 쪽을 autoVerify 없는 `https://manyak.app` 필터로 두면 Android 12 이상에서는 다른 앱의 일반 링크가 그대로 브라우저로 가지만, minSdk 24인 이 앱은 Android 11 이하에서 다른 앱(메일, 메신저 등)의 manyak.app 링크마다 앱 선택창을 띄웁니다. 그래서 https 링크와 겹치지 않는 전용 스킴 `manyak://manyak.app`만 받고, 웹은 `scheme=manyak`으로 엽니다. 앱이 없을 때 브라우저가 플레이스토어를 여는 동작은 같습니다.

진입은 새 타입을 만들지 않고 기존 `PushEntry`에 `TYPE_APP_LINK`를 더해 보류, 로그인 뒤 소비, 프로세스 복원 경로를 그대로 씁니다. 특정 회원에게 보낸 링크가 아니라 수신자 비교를 건너뛰고, 경로는 https로 옮겨 푸시와 같은 `DeepLink` 해석을 씁니다. https App Links(autoVerify, `assetlinks.json`)는 KNK-927에서 따로 다룹니다.

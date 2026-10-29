# ANDROID 결정 기록

확정된 결정의 ID, 당시 상태와 본문을 보존한다. 현재 적용 기준과 후속 결정은 해당 문서에서 확인한다.


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

<a id="a-028"></a>

## A-028. 뒤로가기 전환은 수평 이동

- 결정일: 2026-09-03 · 기록 확정 상태: Accepted
- 대체 관계: [A-015](../../../STORY/CLIENT/ANDROID/DECISIONS.md#a-015)의 전환 방식만 부분 대체
- 근거: [이관 원문 A:351](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L351-L361)
- **맥락:** 교차 페이드로는 들어오고 나가는 방향이 드러나지 않았습니다.
- **결정:** 일반 진입·뒤로가기는 수평 이동, 퍼널 덮개는 별도 수직 전환을 사용합니다.
- **이유:** 사용자가 화면 관계와 이동 방향을 이해하도록 하기 위해서입니다.
- **주요 영향:** 교차 페이드 결정의 전환 부분만 대체하고 닫기의 의미는 유지합니다.


<br>

<a id="a-071"></a>

## A-071. 웹의 앱 열기 링크를 https 대신 전용 스킴으로 받기

- 날짜: 2026-10-13
- 상태: 확정
- 범위: `MainActivity` intent-filter, `PushEntry`의 앱 열기 진입, 웹 앱 안내 배너의 intent 링크

웹 앱 안내 배너([웹 W-033](../WEB/DECISIONS.md#w-033))는 패키지를 명시한 `intent://` 링크로 앱을 엽니다. 받는 쪽을 autoVerify 없는 `https://manyak.app` 필터로 두면 Android 12 이상에서는 다른 앱의 일반 링크가 그대로 브라우저로 가지만, minSdk 24인 이 앱은 Android 11 이하에서 다른 앱(메일, 메신저 등)의 manyak.app 링크마다 앱 선택창을 띄웁니다. 그래서 https 링크와 겹치지 않는 전용 스킴 `manyak://manyak.app`만 받고, 웹은 `scheme=manyak`으로 엽니다. 앱이 없을 때 브라우저가 플레이스토어를 여는 동작은 같습니다.

진입은 새 타입을 만들지 않고 기존 `PushEntry`에 `TYPE_APP_LINK`를 더해 보류, 로그인 뒤 소비, 프로세스 복원 경로를 그대로 씁니다. 특정 회원에게 보낸 링크가 아니라 수신자 비교를 건너뛰고, 경로는 https로 옮겨 푸시와 같은 `DeepLink` 해석을 씁니다. https App Links(autoVerify, `assetlinks.json`)는 KNK-927에서 따로 다룹니다.

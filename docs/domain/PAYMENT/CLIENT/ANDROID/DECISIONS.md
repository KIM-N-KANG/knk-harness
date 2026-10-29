# PAYMENT Android 결정 기록

확정된 결정의 ID, 당시 상태와 본문을 보존한다. 현재 계약은 번호 문서에서 확인한다.

<br>

<a id="a-080"></a>

## A-080. 이프 충전 링크의 tab 쿼리로 처음 열 탭을 정하기

- 결정일: 2026-10-25 · 기록 확정 상태: Accepted
- 대체 관계: [A-045](../../../../adr/1-3-android-adr.md#a-045-알림-진입-목적지는-서버-deeplink를-정본으로-해석)의 "이프 충전의 `tab` 쿼리는 읽지 않습니다"와 "탭 파라미터는 두 번째 사용처가 생기기 전에는 라우트에 싣지 않습니다"를 대체합니다. `deepLink` 정본 해석, 허용 호스트와 경로, 해석 실패 시 홈, `type` 하위 호환 매핑은 유지합니다.
- **맥락:** 서버가 이프 만료 예정 알림 `CREDIT_EXPIRY_REMINDER`를 추가하고(KNK-1835), 클라이언트가 반영되면 그 `deepLink`를 이프 내역으로 가는 `/my/credits?tab=history`로 바꿉니다. 출석 리마인드는 이미 `/my/credits?tab=free`입니다. 탭 값은 웹과 `purchase`, `free`, `history`로 맞췄고 웹도 같은 쿼리를 읽습니다(KNK-1842). A-045 당시에는 사용처가 무료 탭 하나라 기본 선택만으로 도착했지만, 내역 탭이 두 번째 사용처가 됐습니다.
- **결정:** `DeepLink`는 `/my/credits`의 쿼리에서 `tab`만 골라 값이 정확히 `history`이면 `MyCreditChargeRoute(openHistory = true)`로 엽니다. 웹 전용 `purchase`, 모르는 값, 대소문자가 다른 값, 쿼리 없음은 무료 충전 탭입니다. UTM 같은 다른 쿼리는 무시합니다. `CreditChargeScreen`은 이 값을 선택 탭의 `rememberSaveable` 초기값으로만 쓰고, 탭 전환을 라우트나 URL에 다시 쓰지 않습니다.
- **이유:** Android 이프 충전의 탭은 무료 충전과 내역 둘이라 Boolean 하나로 충분하고, 라우트가 `my`의 탭 열거형을 참조하지 않아 기능 모듈 직접 참조 금지 규칙을 지킵니다. 탭은 여전히 목적지가 아니라 화면 상태라 처음 탭만 라우트로 받고 이후 선택은 구성 변경에서만 유지합니다. 모르는 값을 무료 탭으로 여는 것은 웹 전용 구매 탭 링크나 나중에 생길 값이 오류 없이 기본 화면에 도착하게 하기 위해서입니다.
- **주요 영향:** `MyCreditChargeRoute`가 `data object`에서 기본값 있는 `data class`로 바뀌어 앱 안의 진입은 `MyCreditChargeRoute()`로 무료 충전 탭을 엽니다. Android에 구매 탭이 생기면 Boolean을 탭 값으로 바꿔야 합니다. `deepLink`가 없는 출석 리마인드의 `type` 매핑은 무료 충전 탭 그대로입니다. 웹 앱 열기 링크([A-071](../../../../adr/1-3-android-adr.md#a-071-웹의-앱-열기-링크를-https-대신-전용-스킴으로-받기))는 경로만 https로 옮기고 쿼리를 버리므로 그 경로로는 항상 무료 충전 탭이 열립니다.
- 근거: [KNK-1843](https://kimandkang.atlassian.net/browse/KNK-1843), [KNK-1840](https://kimandkang.atlassian.net/browse/KNK-1840), [KNK-1843 계획](../../../../../../manyak-android/docs/plans/knk-1843-credit-charge-tab-query.md)

<br>

<a id="a-081"></a>

## A-081. 이프 부족 시트의 출석 계약과 절차를 common에 두고 간편 제작은 저장한 뒤 퍼널을 걷어내기

- 결정일: 2026-10-25 · 기록 확정 상태: Accepted
- **맥락:** 회원 이프 부족 안내를 토스트에서 바텀 시트로 바꾸면서(KNK-1841) 시트에서 화면 이동 없이 출석하게 됐습니다. 출석 요청은 `my`의 `CreditRepository`에만 있었고, 시트를 여는 채팅방(`chat`)과 간편 제작 추가 정보 단계(`create`)는 `my`를 참조할 수 없습니다. 간편 제작은 완성 요청과 함께 제작 탭으로 떠나므로 퍼널 안에서 알리려면 완성 전 잔액 선검사가 필요하고, 충전으로 떠날 때 입력을 지킬 방법도 정해야 했습니다. 웹은 초안을 저장한 뒤 퍼널 칸을 이프 충전으로 바꾸고, 돌아와 퍼널을 다시 여는 동작은 히스토리 복귀가 복잡해 두지 않았습니다(KNK-1844).
- **결정:** 출석 요청을 `common`의 `AttendanceClaimer` 계약으로 올리고 `my`의 `CreditRepository`가 이를 상속해 같은 구현을 바인딩합니다. `AttendanceResult`도 `common`으로 옮깁니다. 시트 열기(프로필 재조회), 출석, 충전 중 잠금, 닫기의 절차는 `common`의 `CreditShortageController`가 맡고, 상태는 `StoryReportController`처럼 각 ViewModel 상태에 올립니다. 분석 이벤트는 유료 동작을 아는 ViewModel이 보냅니다. 시트 UI와 문구는 `designsystem`이 갖습니다. 간편 제작의 충전은 버튼 임시 저장과 같은 경로로 저장을 기다려 성공했을 때만 퍼널 이탈을 처리하고, `app`이 퍼널을 걷어낸 뒤 제작 탭 위에 이프 충전을 쌓습니다.
- **이유:** 화면 기능끼리 직접 참조하지 않는 규칙을 지키면서 출석 구현을 한 곳에 둡니다. 절차를 두 ViewModel에 되풀이하면 겹친 요청 거르기와 닫기 잠금이 갈라질 수 있고, 별도 Gradle 모듈은 클래스 하나에 과합니다. `common`은 `analytics`에 의존하지 않아 분석은 ViewModel에 남깁니다. 저장 경로를 버튼 저장과 같게 두면 서버 초안과 기기 안 초안, 충돌과 실패 안내를 새로 만들지 않습니다. 퍼널을 백스택에 남기면 돌아와 같은 퍼널을 다시 여는 동작이 생기는데, 웹과 같이 이어서 만들기는 제작 탭 카드로만 합니다.
- **주요 영향:** 이프 충전 화면의 출석과 시트의 출석이 같은 구현을 씁니다. 출석 결과 문구는 `my`와 `designsystem`에 같은 값으로 두 벌 있습니다. 간편 제작에서 충전으로 떠나면 퍼널의 편집 상태는 사라지고 저장한 초안만 남습니다. 제작 탭으로 떠난 뒤 확정된 완성 실패는 [A-077](../../../STORY/CLIENT/ANDROID/DECISIONS.md#a-077)대로 한 문구로 알립니다.
- 근거: [공통 이프 부족 처리](../2-2-REQUIREMENTS.md#2-2-5-이프-부족과-입력-보존), [KNK-1845](https://kimandkang.atlassian.net/browse/KNK-1845), [KNK-1844](https://kimandkang.atlassian.net/browse/KNK-1844), [KNK-1845 계획](../../../../../../manyak-android/docs/plans/knk-1845-credit-shortage-sheet.md)

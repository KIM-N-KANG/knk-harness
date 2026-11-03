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

<a id="a-080"></a>
<a id="a-080-이프-충전-링크의-tab-쿼리로-처음-열-탭을-정하기"></a>

**A-080. 이프 충전 링크의 tab 쿼리로 처음 열 탭을 정하기**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-10-25 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | 서버가 이프 만료 예정 알림 `CREDIT_EXPIRY_REMINDER`를 추가하고(KNK-1835), 클라이언트가 반영되면 그 `deepLink`를 이프 내역으로 가는 `/my/credits?tab=history`로 바꾼다. 출석 리마인드는 이미 `/my/credits?tab=free`이다. 탭 값은 웹과 `purchase`, `free`, `history`로 맞췄고 웹도 같은 쿼리를 읽는다(KNK-1842). A-045 당시에는 사용처가 무료 탭 하나라 기본 선택만으로 도착했지만, 내역 탭이 두 번째 사용처가 됐다. |
| 채택 | `DeepLink`는 `/my/credits`의 쿼리에서 `tab`만 골라 값이 정확히 `history`이면 `MyCreditChargeRoute(openHistory = true)`로 연다. 웹 전용 `purchase`, 모르는 값, 대소문자가 다른 값, 쿼리 없음은 무료 충전 탭이다. UTM 같은 다른 쿼리는 무시한다. `CreditChargeScreen`은 이 값을 선택 탭의 `rememberSaveable` 초기값으로만 쓰고, 탭 전환을 라우트나 URL에 다시 쓰지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | Android 이프 충전의 탭은 무료 충전과 내역 둘이라 Boolean 하나로 충분하고, 라우트가 `my`의 탭 열거형을 참조하지 않아 기능 모듈 직접 참조 금지 규칙을 지킨다. 탭은 여전히 목적지가 아니라 화면 상태라 처음 탭만 라우트로 받고 이후 선택은 구성 변경에서만 유지한다. 모르는 값을 무료 탭으로 여는 것은 웹 전용 구매 탭 링크나 나중에 생길 값이 오류 없이 기본 화면에 도착하게 하기 위해서이다. |
| 영향 | `MyCreditChargeRoute`가 `data object`에서 기본값 있는 `data class`로 바뀌어 앱 안의 진입은 `MyCreditChargeRoute()`로 무료 충전 탭을 연다. Android에 구매 탭이 생기면 Boolean을 탭 값으로 바꿔야 한다. `deepLink`가 없는 출석 리마인드의 `type` 매핑은 무료 충전 탭 그대로이다. 웹 앱 열기 링크([A-071](../../../../ui/ANDROID/DECISIONS.md#a-071))는 경로만 https로 옮기고 쿼리를 버리므로 그 경로로는 항상 무료 충전 탭이 열린다. |
| 대체 관계 | [A-045](../../../NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-045)의 "이프 충전의 `tab` 쿼리는 읽지 않습니다"와 "탭 파라미터는 두 번째 사용처가 생기기 전에는 라우트에 싣지 않습니다"를 대체한다. `deepLink` 정본 해석, 허용 호스트와 경로, 해석 실패 시 홈, `type` 하위 호환 매핑은 유지한다. |
| 근거 | [KNK-1843](https://kimandkang.atlassian.net/browse/KNK-1843), [KNK-1840](https://kimandkang.atlassian.net/browse/KNK-1840), [KNK-1843 계획](../../../../../../manyak-android/docs/plans/knk-1843-credit-charge-tab-query.md) |

<br>

<a id="a-081"></a>
<a id="a-081-이프-부족-시트의-출석-계약과-절차를-common에-두고-간편-제작은-저장한-뒤-퍼널을-걷어내기"></a>

**A-081. 이프 부족 시트의 출석 계약과 절차를 common에 두고 간편 제작은 저장한 뒤 퍼널을 걷어내기**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-10-25 |
| 상태 | Accepted (원문 기록 기준) |
| 배경 | 회원 이프 부족 안내를 토스트에서 바텀 시트로 바꾸면서(KNK-1841) 시트에서 화면 이동 없이 출석하게 됐다. 출석 요청은 `my`의 `CreditRepository`에만 있었고, 시트를 여는 채팅방(`chat`)과 간편 제작 추가 정보 단계(`create`)는 `my`를 참조할 수 없다. 간편 제작은 완성 요청과 함께 제작 탭으로 떠나므로 퍼널 안에서 알리려면 완성 전 잔액 선검사가 필요하고, 충전으로 떠날 때 입력을 지킬 방법도 정해야 했다. 웹은 초안을 저장한 뒤 퍼널 칸을 이프 충전으로 바꾸고, 돌아와 퍼널을 다시 여는 동작은 히스토리 복귀가 복잡해 두지 않았다(KNK-1844). |
| 채택 | 출석 요청을 `common`의 `AttendanceClaimer` 계약으로 올리고 `my`의 `CreditRepository`가 이를 상속해 같은 구현을 바인딩한다. `AttendanceResult`도 `common`으로 옮긴다. 시트 열기(프로필 재조회), 출석, 충전 중 잠금, 닫기의 절차는 `common`의 `CreditShortageController`가 맡고, 상태는 `StoryReportController`처럼 각 ViewModel 상태에 올린다. 분석 이벤트는 유료 동작을 아는 ViewModel이 보낸다. 시트 UI와 문구는 `designsystem`이 갖는다. 간편 제작의 충전은 버튼 임시 저장과 같은 경로로 저장을 기다려 성공했을 때만 퍼널 이탈을 처리하고, `app`이 퍼널을 걷어낸 뒤 제작 탭 위에 이프 충전을 쌓는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 화면 기능끼리 직접 참조하지 않는 규칙을 지키면서 출석 구현을 한 곳에 둔다. 절차를 두 ViewModel에 되풀이하면 겹친 요청 거르기와 닫기 잠금이 갈라질 수 있고, 별도 Gradle 모듈은 클래스 하나에 과하다. `common`은 `analytics`에 의존하지 않아 분석은 ViewModel에 남긴다. 저장 경로를 버튼 저장과 같게 두면 서버 초안과 기기 안 초안, 충돌과 실패 안내를 새로 만들지 않는다. 퍼널을 백스택에 남기면 돌아와 같은 퍼널을 다시 여는 동작이 생기는데, 웹과 같이 이어서 만들기는 제작 탭 카드로만 한다. |
| 영향 | 이프 충전 화면의 출석과 시트의 출석이 같은 구현을 쓴다. 출석 결과 문구는 `my`와 `designsystem`에 같은 값으로 두 벌 있다. 간편 제작에서 충전으로 떠나면 퍼널의 편집 상태는 사라지고 저장한 초안만 남는다. 제작 탭으로 떠난 뒤 확정된 완성 실패는 [A-077](../../../STORY/CLIENT/ANDROID/DECISIONS.md#a-077)대로 한 문구로 알린다. |
| 근거 | [공통 이프 부족 처리](../2-2-REQUIREMENTS.md#2-2-5-이프-부족과-입력-보존), [KNK-1845](https://kimandkang.atlassian.net/browse/KNK-1845), [KNK-1844](https://kimandkang.atlassian.net/browse/KNK-1844), [KNK-1845 계획](../../../../../../manyak-android/docs/plans/knk-1845-credit-shortage-sheet.md) |

<br>

<a id="a-092"></a>
<a id="a-092-이프-내역의-조회-계약과-절차를-common에-행과-목록-표현을-designsystem에-두고-채팅-메뉴와-충전-화면이-함께-쓰기"></a>

**A-092. 이프 내역의 조회 계약과 절차를 common에, 행과 목록 표현을 designsystem에 두고 채팅 메뉴와 충전 화면이 함께 쓰기**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-04 |
| 상태 | Accepted |
| 배경 | 공통 결정 [C-005](../../../CHAT/CLIENT/DECISIONS.md#c-005)가 채팅 메뉴 시트 안에서 이프 충전 내역 탭과 같은 행으로 내역을 보이게 했고, 머리글에 새로고침을 둔다. 내역 API, entity와 행 UI는 `my`에만 있었고 채팅방(`chat`)은 `my`를 참조할 수 없다. 웹은 내역 목록을 my 공용 위치로 옮겨 두 화면이 같은 컴포넌트를 쓴다(KNK-2022). |
| 채택 | 내역 줄 entity와 `CreditTransactionReader` 조회 계약을 `common`으로 올리고 `my`의 `CreditRepository`가 상속해 같은 구현을 바인딩한다. 목록 상태(`CreditHistoryUiState`), 상태 전이와 첫 페이지, 다음 페이지, 다시 읽기 절차(`CreditHistoryController`)는 [A-081](#a-081)의 부족 절차처럼 `common`에 두고 각 ViewModel 상태에 올린다. 사유 라벨, 대상, 날짜와 금액 문구도 `common`이 붙인다. 행, 골격, 빈 상태, 오류와 다음 페이지 자리, 목록 끝 감지는 값과 콜백만 받는 `designsystem` 표현으로 옮긴다. 채팅 메뉴의 내역 상태는 채팅방 ViewModel이 들고, 떠날 때 진행 중인 조회를 취소한다. 내역 화면의 뒤로가기는 시트 내용의 `BackHandler`가 받는다. |
| 대안 | 내역 전용 Gradle 모듈을 만드는 안은 entity 하나와 화면 둘을 위해 모듈 경계와 의존 검사를 늘려 채택하지 않았다. `app`이 `my`의 내역 화면을 채팅 메뉴에 끼워 넣는 안은 하위 UI 전용 ViewModel이 필요해 채택하지 않았다. 시트의 `shouldDismissOnBackPress`를 내역에서 끄는 안은 M3 1.4 시트 창이 만들 때의 값만 읽어 바꿔도 반영되지 않았다. |
| 이유 | 화면 기능끼리 직접 참조하지 않는 규칙을 지키면서 내역 조회와 표현을 한 곳에 둔다. 상태 전이를 공용 순수 함수로 두면 두 ViewModel의 reduce가 같은 규칙을 쓴다. 채팅방은 생성과 재연결 입력을 막지 않아야 해서 조회를 화면 범위의 자식 작업으로 돌린다. |
| 영향 | 충전 화면의 내역 조회도 같은 절차를 쓰며 첫 페이지와 다음 페이지가 화면 입력을 막지 않는다. 충전 화면의 당겨서 새로고침도 같은 다시 읽기 상태를 쓴다. 원장 사유와 내역 문구 리소스가 `my`에서 `common`과 `designsystem`으로 옮겨졌다. 잔액 카드는 바탕색을 받아 채팅 메뉴 시트에서 시트 위 보조 채움을 쓴다. |
| 근거 | [공통 내역 진입](../2-2-REQUIREMENTS.md#2-2-4-보상과-내역), [CHAT Android 3-3](../../../CHAT/CLIENT/ANDROID/3-3-LAYOUT.md#3-3-1-배치와-접근성), [KNK-2023](https://kimandkang.atlassian.net/browse/KNK-2023) |

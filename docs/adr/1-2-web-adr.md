# 1-2-web-adr

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | v0.1 |
| 작성일 | 2026-09-09 |
| 수정일 | 2026-09-14 |
| 대상 | 마냑 웹 클라이언트 |
| 작성 목적 | 웹 전용 기술 결정의 맥락·선택·이유·영향과 대체 관계를 보존합니다. |
| 대상 저장소 | [manyak-web](../../../manyak-web) |

## 읽는 순서

- **처음 보는 사람** — 기록 규칙을 읽고, 목차에서 관련 주제의 기록으로 이동합니다. 문서 작성일·수정일은 개별 결정일과 구분합니다.
- **구현자** — [현재 스펙](../spec/3-2-web-spec.md)과 해당 설계를 먼저 확인하고, 선택 이유가 필요한 지점의 ADR을 읽습니다. 과거 기록을 현재 동작의 기준으로 사용하지 않습니다.
- **리뷰·변경 작성자** — 관련 결정과 후속 대체 관계를 함께 확인합니다. 확정된 본문은 보존하고 새 기록에 대체하는 ID·범위를 남깁니다.

<a id="결정-목록"></a>

## 목차

- [기록 규칙](#기록-규칙)
- [W-001. SSE를 fetch와 ReadableStream으로 수신](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-001) — 원문 미기재
- [W-002. 게스트 서재 초기 상태를 세 가지로 구분](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-002) — 원문 미기재
- [W-003. BFF를 백엔드 호출과 토큰 보관의 단일 창구로 사용](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-003) — 원문 미기재
- [W-004. 이관 제출 뒤 게스트 ID를 일괄 정리](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-004) — 원문 미기재
- [W-005. 로그인 핸드오프 데이터를 ID 스냅숏으로 식별](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-005) — 원문 미기재
- [W-006. 공유 진입을 헤더 버튼으로 표시](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-006) — 원문 미기재
- [W-007. 계정 연동에 별도 NextAuth 공급자 사용](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-007) — 2026-08-01
- [W-008. 제작 재개 의도를 URL 대신 세션스토리지에 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-008) — 2026-08-27
- [W-009. 인앱 진입 차단을 로그인 시점 핸드오프로 대체](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-009) — 원문 미기재
- [W-010. 인앱 복귀 정리는 핸드오프 상태 조회로 판정](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-010) — 원문 미기재
- [W-011. 동의 전 로그인은 탭 표시로 판정해 fail-closed 로그아웃](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-011) — 2026-09-19
- [W-012. 게스트 체험은 별도 동의 후 허용](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-012) — 2026-09-20
- [W-013. 게스트 제작 동의는 스토리라인 생성 직전에 확인](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-013) — 2026-09-20
- [W-014. 인앱 로그인을 Auth.js 팝업으로 시작하고 로그인 화면 유지](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-014) — 2026-09-19
- [W-015. 팝업 참조 단절과 인증 취소를 구분](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-015) — 2026-09-20
- [W-016. 게스트 동의의 정본을 서버 기록으로 전환](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-016) — 2026-09-20
- [W-017. 편집 초안을 같은 키의 목록으로 확장](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-017) — 2026-09-22
- [W-018. 웹 푸시는 Firebase 토큰 SDK와 제작 직후 프롬프트로 도입](../domain/NOTIFICATION/CLIENT/WEB/DECISIONS.md#w-018) — 2026-09-22

- [W-019. 제작 로컬 저장을 Dexie 트랜잭션으로 전환](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-019) — 2026-09-26
- [W-020. 간편 제작 편집 저장을 버튼·단계 이동·화면 숨김으로 제한](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-020) — 2026-10-01
- [W-021. 일반 제작 이미지는 브라우저에서 잘라 JPEG로 올림](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-021) — 2026-10-01
- [W-022. 동의 전에는 세션을 만들지 않고 Credentials로 가입을 완료](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-022) — 2026-10-05
- [W-023. 결제 복귀 화면은 결제 전 충전 화면까지 히스토리를 되감음](../domain/PAYMENT/CLIENT/WEB/DECISIONS.md#w-023) — 2026-10-05
- [W-024. 완성 중 표지를 Android와 같은 로고 마스코트 애니메이션으로 바꿈](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-024) — 2026-10-06
- [W-025. 채팅 실시간 이미지 대기를 마스코트가 인물을 그리는 애니메이션으로 바꿈](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-025) — 2026-10-06 · 그림 구성은 W-027에서 일부 대체
- [W-026. 완성 중 표지 안무를 웹이 먼저 개편하고 Android가 같은 값으로 따라옴](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-026) — 2026-10-06
- [W-027. 채팅 실시간 이미지 대기 그림을 창가 인물화 한 장으로 바꾸고 붓을 몸과 따로 움직임](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-027) — 2026-10-07
- [W-028. 히스토리 이동으로 돌아온 문서와 OAuth 오류 화면에서 끝내지 않은 로그인을 정리](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-028) — 2026-10-07

- [W-029. 공개 오리지널 상세만 서버 렌더링하고 개인화는 다시 조회](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-029), 2026-10-08
- [W-030. 탭으로 나가는 이동은 Navigation API로 아래 탭 기록까지 되돌아감](#w-030), 2026-10-09
- [W-033. 앱 안내 배너는 클라이언트에서 판정하고 패키지를 명시한 intent로 앱을 연다](#w-033), 2026-10-12
- [W-034. refresh 재발급은 브라우저에서 한 번으로 묶는다](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-034), 2026-10-15
- [W-035. 겹치는 operationId는 메서드와 경로로 생성 이름을 고정](#w-035), 2026-10-15
- [W-036. 회원 일반 제작 임시 저장본은 서버에만 둔다](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-036), 2026-10-16
- [W-037. 회원 간편 제작 초안은 세션 고정 ID로 서버에 두고 진행 기록은 기기 안에 남긴다](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-037), 2026-10-16
- [W-038. 회원은 만들고 있는 스토리 카드가 5장이면 새 제작을 막는다](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-038), 2026-10-17
- [W-039. 간편 제작은 단계를 옮겨도 저장하지 않는다](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-039), 2026-10-17
- [W-040. 로그인 핸드오프의 복구 경로를 제거](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-040), 2026-10-19
- [W-041. Android 앱 열기가 일어나지 않으면 플레이스토어 주소로 직접 이동](#w-041), 2026-10-20
- [W-042. 로그인한 세션의 재동의는 로그아웃 없이 시트로 받는다](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-042), 2026-10-21
- [W-043. 재동의가 필요 없는 문서 개정은 서버 요구 버전을 올리지 않는다](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-043), 2026-10-22

---

핵심 결정 당시의 맥락·선택·이유·영향을 기록합니다. 현재 계약은 해당 스펙, 현재 구조는 해당 설계를 따릅니다.

## 기록 규칙

[공통 기록 규칙](1-1-client-adr.md#기록-규칙)을 따릅니다. 이 파일의 식별자는 `W-NNN`이며 새 결정은 아래에 추가합니다. 과거 기록은 2026-09-09에 원문에서 이관했으며 날짜 미기재는 추정하지 않았습니다.

<a id="w-001"></a>

## W-001. SSE를 fetch와 ReadableStream으로 수신

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-001)에서 확인한다.

<a id="w-002"></a>

## W-002. 게스트 서재 초기 상태를 세 가지로 구분

결정 기록을 도메인 세트로 옮겼다. ([W-002](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-002))

<a id="w-003"></a>

## W-003. BFF를 백엔드 호출과 토큰 보관의 단일 창구로 사용

결정 기록을 도메인 세트로 옮겼다. ([W-003](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-003))

<a id="w-004"></a>

## W-004. 이관 제출 뒤 게스트 ID를 일괄 정리

결정 기록을 도메인 세트로 옮겼다. ([W-004](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-004))

<a id="w-005"></a>

## W-005. 로그인 핸드오프 데이터를 ID 스냅숏으로 식별

결정 기록을 도메인 세트로 옮겼다. ([W-005](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-005))

<a id="w-006"></a>

## W-006. 공유 진입을 헤더 버튼으로 표시

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-006)에서 확인한다.

<a id="w-007"></a>

## W-007. 계정 연동에 별도 NextAuth 공급자 사용

결정 기록을 도메인 세트로 옮겼다. ([W-007](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-007))

<a id="w-008"></a>

## W-008. 제작 재개 의도를 URL 대신 세션스토리지에 기록

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-008)에서 확인한다.

<a id="w-009"></a>

## W-009. 인앱 진입 차단을 로그인 시점 핸드오프로 대체

결정 기록을 도메인 세트로 옮겼다. ([W-009](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-009))

<a id="w-010"></a>

## W-010. 인앱 복귀 정리는 핸드오프 상태 조회로 판정

결정 기록을 도메인 세트로 옮겼다. ([W-010](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-010))

<a id="w-011"></a>

## W-011. 동의 전 로그인은 탭 표시로 판정해 fail-closed 로그아웃

결정 기록을 도메인 세트로 옮겼다. ([W-011](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-011))

<a id="w-012"></a>

## W-012. 게스트 체험은 별도 동의 후 허용

결정 기록을 도메인 세트로 옮겼다. ([W-012](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-012))

<a id="w-013"></a>

## W-013. 게스트 제작 동의는 스토리라인 생성 직전에 확인

결정 기록을 도메인 세트로 옮겼다. ([W-013](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-013))

<a id="w-014"></a>

## W-014. 인앱 로그인을 Auth.js 팝업으로 시작하고 로그인 화면 유지

결정 기록을 도메인 세트로 옮겼다. ([W-014](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-014))

<a id="w-015"></a>

## W-015. 팝업 참조 단절과 인증 취소를 구분

결정 기록을 도메인 세트로 옮겼다. ([W-015](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-015))

<a id="w-016"></a>

## W-016. 게스트 동의의 정본을 서버 기록으로 전환

결정 기록을 도메인 세트로 옮겼다. ([W-016](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-016))

<a id="w-017"></a>

## W-017. 편집 초안을 같은 키의 목록으로 확장

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-017)에서 확인한다.

<a id="w-018"></a>

## W-018. 웹 푸시는 Firebase 토큰 SDK와 제작 직후 프롬프트로 도입

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/WEB/DECISIONS.md#w-018)에서 확인한다.

<a id="w-019"></a>

## W-019. 제작 로컬 저장을 Dexie 트랜잭션으로 전환

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-019)에서 확인한다.

<a id="w-020"></a>

## W-020. 간편 제작 편집 저장을 버튼·단계 이동·화면 숨김으로 제한

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-020)에서 확인한다.

<a id="w-021"></a>

## W-021. 일반 제작 이미지는 브라우저에서 잘라 JPEG로 올림

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-021)에서 확인한다.

<a id="w-022"></a>

## W-022. 동의 전에는 세션을 만들지 않고 Credentials로 가입을 완료

결정 기록을 도메인 세트로 옮겼다. ([W-022](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-022))

<a id="w-023"></a>

## W-023. 결제 복귀 화면은 결제 전 충전 화면까지 히스토리를 되감음

PAYMENT 내용은 도메인 문서에서 관리한다. ([W-023](../domain/PAYMENT/CLIENT/WEB/DECISIONS.md#w-023))

<a id="w-024"></a>

## W-024. 완성 중 표지를 Android와 같은 로고 마스코트 애니메이션으로 바꿈

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-024)에서 확인한다.

<a id="w-025"></a>

## W-025. 채팅 실시간 이미지 대기를 마스코트가 인물을 그리는 애니메이션으로 바꿈

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-025)에서 확인한다.

<a id="w-026"></a>

## W-026. 완성 중 표지 안무를 웹이 먼저 개편하고 Android가 같은 값으로 따라옴

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-026)에서 확인한다.

<a id="w-027"></a>

## W-027. 채팅 실시간 이미지 대기 그림을 창가 인물화 한 장으로 바꾸고 붓을 몸과 따로 움직임

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/WEB/DECISIONS.md#w-027)에서 확인한다.

<a id="w-028"></a>

## W-028. 히스토리 이동으로 돌아온 문서와 OAuth 오류 화면에서 끝내지 않은 로그인을 정리

결정 기록을 도메인 세트로 옮겼다. ([W-028](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-028))

<a id="w-029"></a>

## W-029. 공개 오리지널 상세만 서버 렌더링하고 개인화는 다시 조회

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-029)에서 확인한다.

<a id="w-030"></a>

## W-030. 탭으로 나가는 이동은 Navigation API로 아래 탭 기록까지 되돌아감

- 결정일: 2026-10-09, 기록 확정 상태: Accepted
- 근거: [웹 화면 전환 규칙](../spec/3-2-web-spec.md#화면-전환-규칙), [Android 내비게이션과 화면 계약](../spec/3-3-android-spec.md#3-3-3-내비게이션화면-계약)
- **맥락:** 제작 화면 나가기와 스토리, 채팅 삭제는 지금 화면을 탭으로 교체해, 그 탭에서 들어온 경우 같은 탭이 기록에 두 번 남아 뒤로가기 한 번이 아무 변화를 만들지 않았습니다. Android는 쌓인 화면을 걷어내고 하단 탭을 엽니다. 웹은 지나온 기록을 지울 수 없고, 앱 안 이동 추적은 진입 이후 이동이 있었는지만 알아 아래 기록이 어느 화면인지 모릅니다.
- **결정:** Navigation API `entries()`에서 가장 가까운 아래 탭 기록을 찾아 `history.go`로 되돌아갑니다. 갈 탭과 다르면 되돌아간 뒤 갈 탭을 `push`해 걷어낸 화면을 앞으로 가기에서도 없앱니다. API가 없거나 아래 탭 기록이 없으면, 또는 그 기록이 이전 문서에 있으면 지금처럼 교체합니다. 이전 문서로 돌아가면 문서를 다시 열어 떠나며 띄운 토스트가 사라지고 이어서 이동할 수도 없습니다. 이 결정은 KNK-1566의 일반 제작 승인 뒤 채팅방 아래 화면(채팅 목록)도 Android처럼 새 스토리 상세로 대체합니다.
- **이유:** 진입점마다 출발 화면을 표시해 넘기면 공유 링크, 온보딩, 카드처럼 진입 경로가 늘 때마다 표시를 빠뜨릴 수 있고, 새로고침으로 표시가 사라집니다. 브라우저가 가진 실제 기록을 읽으면 진입 경로와 관계없이 같은 판정을 합니다. 결제 복귀(W-023)에서 `entries()`를 쓰지 않은 이유는 다른 출처를 지나면 그 이전 항목이 보이지 않기 때문이며, 여기서는 아래 탭 기록이 같은 출처라 해당하지 않습니다.
- **주요 영향:** Navigation API가 없는 브라우저는 같은 탭이 두 번 쌓이는 기존 동작을 유지합니다. 탭 기록이 이전 문서에 있는 경우(새로고침, 로그인 복귀 뒤)도 같은 탭이 두 번 쌓일 수 있습니다. 하단 탭끼리의 이동은 계속 교체라 탭 화면의 뒤로가기는 Android와 달리 홈으로 가지 않습니다.

<a id="w-031"></a>

## W-031. 오버레이 뒤로가기 닫기를 히스토리 레이어 매니저로 통합

- 결정일: 2026-10-09, 기록 확정 상태: Accepted
- 근거: [공통 오버레이와 뒤로가기](../spec/3-1-client-spec.md#3-1-2-공통-계약과-플랫폼-경계), [웹 화면 전환 규칙](../spec/3-2-web-spec.md#화면-전환-규칙), [W-028](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-028), [W-030](#w-030)
- **맥락:** 뒤로가기 가로채기가 `useCloseOnBack`, `usePreventPageLeave`, 게스트 동의 프로바이더에 흩어져 각자 더미 히스토리 항목을 쌓았고, 시트 27종 중 4종만 뒤로가기로 닫혔습니다. Android는 시스템 뒤로가기로 모든 시트를 닫습니다. 같은 클릭에서 드로어 닫기와 다이얼로그 열기가 겹치면 각자의 `history.back()`과 `pushState`가 어긋났고, 제작 퍼널 위에 시트가 열리면 시트의 뒤로가기가 퍼널 가드에도 닿았습니다.
- **결정:** 더미 히스토리 항목 방식을 유지하되 전역 레이어 스택 하나가 더미 쌓기와 되감기를 큐로 직렬화하고 캡처 단계 `popstate` 리스너로 맨 위 레이어에만 전달합니다. `Drawer`·`Dialog`·`AlertDialog` 래퍼가 기본으로 레이어를 열어 새 시트도 코드 없이 뒤로가기로 닫히고, 뒤로가기에 다른 의미를 주는 시트만 `closeOnBack`을 끕니다. 사용자 조작 없이 열린 오버레이는 더미를 쌓지 않습니다. 시트 안에서 떠나는 이동은 `leaveLayers`로 더미를 먼저 소비합니다.
- **이유:** Navigation API의 traverse 취소는 Chromium 계열에만 있어 Safari·Firefox용 더미 폴백을 함께 가져가야 하므로 보류했습니다. 시트마다 훅을 붙이는 방식은 누락이 반복됐고 더미 순서를 조율하는 곳이 없었습니다. Chrome은 조작 없이 쌓인 항목을 뒤로가기에서 건너뛰므로(W-028) 자동으로 열린 오버레이는 더미를 쌓아도 보장되지 않고 앞으로가기에 빈 칸만 남깁니다.
- **주요 영향:** 시트 안에서 `router.push`·`replace`·전체 이동을 부르는 새 코드는 `leaveLayers`를 거쳐야 돌아올 때 빈 칸이 남지 않습니다. 자동으로 열린 시트는 지금처럼 뒤로가기가 화면을 떠납니다. 주소로 바로 연 제작 화면은 첫 입력 전까지 이탈 확인이 없습니다. 되감기 대기 중 사용자가 뒤로가기를 한 번 더 누르면 그 입력은 되감기 결과로 흡수됩니다.

<a id="w-032"></a>

## W-032. 소셜 로그인은 팝업을 기본으로 하고 복귀는 로그인 화면 칸을 교체

결정 기록을 도메인 세트로 옮겼다. ([W-032](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-032))

<a id="w-033"></a>

## W-033. 앱 안내 배너는 클라이언트에서 판정하고 패키지를 명시한 intent로 앱을 연다

- 결정일: 2026-10-12, 기록 확정 상태: Accepted
- 근거: [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너), [앱 안내 배너 구조](../design/1-1-web-design.md#앱-안내-배너-웹), [KNK-1630](https://kimandkang.atlassian.net/browse/KNK-1630)
- **맥락:** 모바일 웹 방문자를 Android 앱과 iOS 홈 화면 설치본으로 안내하는 배너가 필요했습니다. 노출은 브라우저 종류, 홈 화면 설치본 여부, 접속 회차에 따라 달라지고, Android 앱에는 외부 링크를 받는 intent-filter와 App Links가 없었습니다.
- **결정:** 노출은 클라이언트에서 UA와 브라우저 저장소로 판정합니다. Android 앱 열기는 App Links 대신 `package=app.manyak`를 명시한 `intent://` 링크로 하고, 앱은 전용 스킴 `manyak://manyak.app` intent-filter로 받습니다. 어트리뷰션 SDK의 스마트 배너는 쓰지 않습니다.
- **이유:** 서버 판정은 홈을 매 요청 동적 렌더로 바꾸면서도 접속 회차와 설치본 여부를 알 수 없어 결국 클라이언트 판정이 섞입니다. 패키지를 명시한 intent는 도메인 검증 없이 설치 여부에 따라 앱 또는 플레이스토어로 갑니다. 받는 쪽을 검증되지 않은 https 필터로 두면 Android 11 이하(minSdk 24)에서 다른 앱의 manyak.app 링크마다 앱 선택창이 떠서, https 링크와 겹치지 않는 전용 스킴을 씁니다. SDK는 비용, 웹과 앱 양쪽 도입, 처리방침 개정이 필요합니다.
- **주요 영향:** 배너는 하이드레이션 뒤 나타납니다. 앱이 열렸는지 플레이스토어로 갔는지 웹에서 구분할 수 없어 설치는 Play Console과 referrer로 봅니다. App Links와 설치 뒤 목적지 복원은 후속(KNK-927, 디퍼드 딥링크)입니다.

<a id="w-034"></a>

## W-034. refresh 재발급은 브라우저에서 한 번으로 묶는다

결정 기록을 도메인 세트로 옮겼다. ([W-034](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-034))

<a id="w-035"></a>

## W-035. 겹치는 operationId는 메서드와 경로로 생성 이름을 고정

- 결정일: 2026-10-15, 기록 확정 상태: Accepted
- 근거: [요청 흐름](../design/1-1-web-design.md#요청-흐름), [KNK-1655](https://kimandkang.atlassian.net/browse/KNK-1655)
- **맥락:** 백엔드(Springdoc)는 Java 메서드 이름으로 operationId를 만들고, 이름이 겹치면 스캔 순서대로 `get`, `get_1`, `get_2`처럼 순번을 붙입니다. Orval은 이 값으로 훅 이름(`useGet1`)을 만듭니다. 임시 저장 API(`story-draft-controller`)가 추가되자 순번이 하나씩 밀려 `useList1` 같은 import가 깨졌고, `useGet3`은 이름이 남은 채 화풍 목록 대신 장르 목록을 가리켰습니다.
- **결정:** Orval 입력 변환기(`input.override.transformer`)로 스펙을 생성 전에 고칩니다. 순번 접미사(`_숫자`)를 뗀 기본 이름이 둘 이상인 operationId는 모두 HTTP 메서드와 경로 이름으로 바꾸고(`GET /api/v1/stories/submissions/{id}` → `getStoriesSubmissionsById`), 겹치지 않는 이름은 그대로 둡니다. API와 Zod 생성에 같은 변환기를 씁니다.
- **이유:** 메서드와 경로는 API 계약 자체라 백엔드 메서드가 늘거나 스캔 순서가 바뀌어도 변하지 않습니다. 같은 이름이 다른 API를 가리키는 일은 없어집니다. 모든 이름을 경로로 바꾸면 이미 쓰는 고유 이름(`getStoryDetail` 등)까지 바뀌어, 겹치는 이름만 바꿉니다. 근본 해결은 백엔드가 `@Operation(operationId = ...)`로 고유 이름을 다는 것이지만 백엔드 코드라 웹에서 정하지 않습니다.
- **주요 영향:** 지금 고유한 이름도 나중에 백엔드에 같은 이름의 메서드가 생기면 경로 이름으로 바뀌어 import가 깨집니다. 다만 다른 API를 가리키지 않고 typecheck에서 드러납니다. 경로가 바뀌면 이름도 바뀝니다. 생성 훅 이름은 길어집니다.

<a id="w-036"></a>

## W-036. 회원 일반 제작 임시 저장본은 서버에만 둔다

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-036)에서 확인한다.

<a id="w-037"></a>

## W-037. 회원 간편 제작 초안은 세션 고정 ID로 서버에 두고 진행 기록은 기기 안에 남긴다

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-037)에서 확인한다.

<a id="w-038"></a>

## W-038. 회원은 만들고 있는 스토리 카드가 5장이면 새 제작을 막는다

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-038)에서 확인한다.

<a id="w-039"></a>

## W-039. 간편 제작은 단계를 옮겨도 저장하지 않는다

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/WEB/DECISIONS.md#w-039)에서 확인한다.

<a id="w-040"></a>

## W-040. 로그인 핸드오프의 복구 경로를 제거

결정 기록을 도메인 세트로 옮겼다. ([W-040](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-040))

<a id="w-041"></a>

## W-041. Android 앱 열기가 일어나지 않으면 플레이스토어 주소로 직접 이동

- 결정일: 2026-10-20, 기록 확정 상태: Accepted
- 근거: [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너), [앱 안내 배너 구조](../design/1-1-web-design.md#앱-안내-배너-웹), [KNK-1716](https://kimandkang.atlassian.net/browse/KNK-1716)
- **보완 범위:** [W-033](#w-033)의 "패키지를 명시한 intent는 설치 여부에 따라 앱 또는 플레이스토어로 간다"를 보완합니다. intent 링크로 앱을 여는 방식은 유지합니다.
- **맥락:** Android 인스타그램 인앱 브라우저는 앱이 없으면 intent 링크를 받고 아무것도 열지 않습니다. 실기기(Galaxy S25, Android 17) logcat에서 액티비티 시작 기록이 없었고, `S.browser_fallback_url`을 넣어도 같았습니다. 같은 화면에서 `market://`과 `https://play.google.com` 주소는 플레이스토어를 열었습니다.
- **결정:** Android 앱 열기를 누른 뒤 0.7초 안에 문서가 한 번도 숨겨지지 않으면 `https://play.google.com/store/apps/details?id=app.manyak`(배너 referrer 포함)로 이동합니다. intent 링크에는 `browser_fallback_url`을 넣지 않습니다.
- **이유:** 인앱 브라우저가 intent를 버리는지 웹에서 미리 알 수 없어, iOS 인앱 외부 전환 실패 판정과 같은 문서 숨김 감지로 실패를 판단합니다. 대기 1.5초는 실패한 사용자가 체감할 만큼 길었고, 카카오톡에서 앱 실행 시도부터 플레이스토어가 뜨기까지 수십 ms였으므로 0.7초로 줄였습니다. `market://` 대신 https 주소를 쓰는 이유는 플레이스토어가 없는 기기에서도 웹 페이지로 열리기 때문입니다.
- **주요 영향:** 인스타그램에서 앱이 없으면 0.7초 뒤 플레이스토어가 열립니다. 앱이 설치된 느린 기기에서 0.7초 안에 앱이 뜨지 않으면 플레이스토어가 함께 열릴 수 있습니다. Chrome과 카카오톡은 기존처럼 플레이스토어를 바로 열고 두 번 열지 않습니다.

<a id="w-042"></a>

## W-042. 로그인한 세션의 재동의는 로그아웃 없이 시트로 받는다

결정 기록을 도메인 세트로 옮겼다. ([W-042](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-042))

<a id="w-043"></a>

## W-043. 재동의가 필요 없는 문서 개정은 서버 요구 버전을 올리지 않는다

결정 기록을 도메인 세트로 옮겼다. ([W-043](../domain/ACCOUNT/CLIENT/WEB/DECISIONS.md#w-043))

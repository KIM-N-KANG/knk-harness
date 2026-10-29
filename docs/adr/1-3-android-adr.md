# 1-3-android-adr

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | v0.1 |
| 작성일 | 2026-09-09 |
| 수정일 | 2026-10-28 |
| 대상 | 마냑 Android 네이티브 앱 |
| 작성 목적 | Android 전용 기술 결정의 맥락·선택·이유·영향과 대체 관계를 보존합니다. |
| 대상 저장소 | [manyak-android](../../../manyak-android) |

## 읽는 순서

- **처음 보는 사람** — 기록 규칙을 읽고, 목차에서 관련 주제의 기록으로 이동합니다. 문서 작성일·수정일은 개별 결정일과 구분합니다.
- **구현자** — [현재 스펙](../spec/3-3-android-spec.md)과 해당 설계를 먼저 확인하고, 선택 이유가 필요한 지점의 ADR을 읽습니다. 과거 기록을 현재 동작의 기준으로 사용하지 않습니다.
- **리뷰·변경 작성자** — 관련 결정과 후속 대체 관계를 함께 확인합니다. 확정된 본문은 보존하고 새 기록에 대체하는 ID·범위를 남깁니다.

<a id="결정-목록"></a>

## 목차

- [기록 규칙](#기록-규칙)
- [A-001. 제작 진행을 Preferences DataStore에 저장](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-001) — 원문 미기재
- [A-002. 로그인 필수 사용자 모델](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-002) — 2026-08-03
- [A-003. Clean Architecture 전면 적용을 하지 않음](#a-003-clean-architecture-전면-적용을-하지-않음) — 2026-08-22
- [A-004. 세션 스코프 Hilt 컴포넌트를 두지 않음](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-004) — 2026-08-22
- [A-005. UI 상태 관리를 직접 구성](#a-005-ui-상태-관리를-직접-구성) — 2026-08-22
- [A-006. Crashlytics로 앱 크래시 수집](#a-006-crashlytics로-앱-크래시-수집) — 2026-08-22
- [A-007. 토큰을 Keystore로 암호화해 저장](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-007) — 2026-08-22
- [A-008. 부팅 세대를 포함한 토큰 만료 판정](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-008) — 2026-08-22
- [A-009. 앱이 device_id 생성](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-009) — 2026-08-22
- [A-010. Navigation 3 사용](#a-010-navigation-3-사용) — 2026-08-23
- [A-011. 셸이 공용 헤더와 탭 소유](#a-011-셸이-공용-헤더와-탭-소유) — 2026-08-23
- [A-012. 제작 단계를 별도 목적지로 구성](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-012) — 2026-08-23
- [A-013. 스토리라인이 키워드 목적지를 대체](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-013) — 2026-08-25
- [A-014. 제작 진행 저장소를 Room으로 통합](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-014) — 2026-08-25
- [A-015. 제작 퍼널 이탈과 교차 페이드](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-015) — 2026-08-26
- [A-016. 제작 탭을 분리해 네 탭 구성](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-016) — 2026-08-26
- [A-017. 목록 카드에서 스토리 삭제 제공](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-017) — 2026-08-27
- [A-018. 이미지 뷰어는 상세 내부 상태](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-018) — 2026-08-27
- [A-019. 상세에서 채팅 진입 시 상세 유지](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-019) — 2026-08-27
- [A-020. 편집 저장을 버튼과 백그라운드 전환으로 제한](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-020) — 2026-08-27
- [A-021. 내 스토리를 가로 행 목록으로 표시](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-021) — 2026-08-28
- [A-022. 빈 채팅 목록의 제작 진입 단일화](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-022) — 2026-08-28
- [A-023. 구성 변경의 Activity 재생성을 수용](#a-023-구성-변경의-activity-재생성을-수용) — 2026-08-28
- [A-024. 채팅 메시지를 밴드로 표시](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-024) — 2026-08-29
- [A-025. 법적 WebView 경로 이탈 감지 제거](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-025) — 2026-08-30
- [A-026. 초대에 Android 공유 시트 사용](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-026) — 2026-08-31
- [A-027. 오픈소스 고지는 의존성에서 생성](#a-027-오픈소스-고지는-의존성에서-생성) — 2026-08-31
- [A-028. 뒤로가기 전환은 수평 이동](#a-028-뒤로가기-전환은-수평-이동) — 2026-09-03
- [A-029. 카드 옵션을 다이얼로그로 통일](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-029) — 2026-09-03
- [A-030. 상세의 isOwner로 삭제 메뉴 제공](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-030) — 2026-09-03
- [A-031. 퍼널 닫기는 항상 확인](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-031) — 2026-09-03
- [A-032. 푸시 삭제와 수신자 검증을 분리](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-032) — 2026-09-08
- [A-033. 알림 권한 요청은 메인 그래프 첫 진입](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-033) — 2026-09-08
- [A-034. 알림 수신자를 payload로 재검증](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-034) — 2026-09-08
- [A-035. 로그아웃 후 제작 데이터를 계정별 보존](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-035) — 2026-09-08
- [A-036. 완성 요청을 편집 행에서 분리하고 보존 이전](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-036) — 2026-09-08
- [A-037. 보이는 완성 카드만 주기 조회](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-037) — 2026-09-09
- [A-038. 기능 단위 모듈과 내부 패키지 계층](#a-038-기능-단위-모듈과-내부-패키지-계층) — 2026-09-05
- [A-039. 알림 기능을 notification 모듈에 배치](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-039) — 2026-09-08
- [A-040. 광고 알림 동의는 첫 진입 시트로 묻고 즉시 통지](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-040) — 2026-09-11
- [A-041. 인물 이미지 뷰어를 화면 상태로 공용화](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-041) — 2026-09-17
- [A-042. 카드 옵션·상세 옵션·채팅 메뉴를 바텀 시트로 통일](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-042) — 2026-09-18
- [A-043. 채팅 공유를 앱에 적용하고 Android 공유 시트로 전달](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-043) — 2026-09-18
- [A-044. 약관 동의 시트를 legal이 소유하고 광고 동의는 선택 항목과 재진입 재질문으로 받음](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-044) — 2026-09-20
- [A-045. 알림 진입 목적지는 서버 deepLink를 정본으로 해석](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-045) — 2026-09-20
- [A-046. 편집 초안을 퍼널 세션 ID 키의 여러 행으로 확장](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-046) — 2026-09-23
- [A-047. release 빌드에 R8 축소·난독화 적용](#a-047-release-빌드에-r8-축소난독화-적용) — 2026-09-26
- [A-048. 채팅 안내 투어를 같은 컴포지션의 오버레이로 그리고 뒤로가기를 건너뛰기로 처리](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-048) — 2026-09-26

- [A-049. 상세 삭제는 제작 탭으로 복귀하고 좋아요 성공은 홈 카드에 전달](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-049), 2026-10-03
- [A-050. 실시간 이미지 안내의 수명과 시트 위 오버레이](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-050) - 2026-10-04
- [A-051. 필수 동의 확인을 분석 식별과 푸시 등록의 선행 조건으로 공유](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-051) - 2026-10-04
- [A-052. 필수 동의를 로그인 화면에서 완료한 뒤 회원 그래프 구성](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-052) - 2026-10-04
- [A-053. 로컬 제작 카드의 진입과 인물 편집 상태 소유권](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-053) - 2026-10-04
- [A-054. 저장 세션의 시작 화면과 새 로그인 동의 흐름 분리](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-054) - 2026-10-04
- [A-055. 임시 저장 성공을 토스트와 시간 잠금으로 안내](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-055) - 2026-10-04
- [A-056. 검수 제출본을 화면 수명으로 조회하고 알림을 제작 탭에 연결](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-056) - 2026-10-05
- [A-057. 제공 장르 검색과 이전 초안 호환](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-057) - 2026-10-05
- [A-058. 장르 검색 선택 토글과 대표 칩 순서 유지](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-058) - 2026-10-05
- [A-059. 장르 검색 캐시와 지연 로딩 표시](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-059) - 2026-10-05
- [A-060. 장르 검색 로딩 표시 기준 조정](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-060) - 2026-10-05
- [A-061. 일반 제작의 별도 초안 테이블과 제출 접수 경계](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-061) - 2026-10-05
- [A-062. 일반 제작과 수정의 공용 폼 및 이미지 자르기 소유권](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-062) - 2026-10-05
- [A-063. 잃을 것 없는 제작 이탈과 제작 화면 전환 통일](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-063) - 2026-10-05
- [A-064. 동의 전 가입 대기를 세션 없이 auth 메모리에 두기](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-064) - 2026-10-05
- [A-065. 완성 중 표지를 로고 마스코트 애니메이션으로 바꾸기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-065) - 2026-10-06
- [A-066. 채팅 실시간 이미지 대기를 마스코트가 인물을 그리는 애니메이션으로 바꾸기](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-066) - 2026-10-07
- [A-067. 완성 중 표지 안무를 웹 개편 값으로 따라가기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-067) - 2026-10-07
- [A-068. 채팅 실시간 이미지 대기 그림을 웹 개편 값의 창가 인물화 한 장으로 따라가기](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-068) - 2026-10-07
- [A-069. 필수 동의 시트에 로그아웃 버튼을 두고 시작 화면 조회 실패에는 두지 않기](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-069) - 2026-10-08
- [A-070. 페르소나를 마이가 소유하고 상세에는 좁은 공용 계약으로 열기](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-070) - 2026-10-09
- [A-071. 웹의 앱 열기 링크를 https 대신 전용 스킴으로 받기](#a-071-웹의-앱-열기-링크를-https-대신-전용-스킴으로-받기) - 2026-10-13
- [A-072. 간편 제작 화풍을 기존 초안 JSON에 더하고 스토리라인을 다시 만들어도 남기기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-072) - 2026-10-14
- [A-073. 표지 위 뱃지에 웹과 같은 배경 흐림을 GraphicsLayer로 적용하기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-073) - 2026-10-14
- [A-074. 일반 제작 임시 저장본을 서버 초안으로 옮기고 Room에는 이관 전 초안과 접수 연결만 남기기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-074) - 2026-10-16
- [A-075. 간편 제작 초안을 세션 ID로 서버에 두고 진행 기록에 서버 초안 버전 열을 더하기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-075) - 2026-10-17
- [A-076. 새 제작 상한을 FAB에서 보이는 초안 카드로 판정하고 제작 탭 첫 조회를 한 스켈레톤으로 덮기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-076) - 2026-10-17
- [A-077. 완성 실패를 추가 정보 단계 초안으로 되돌리고 실패 카드를 없애기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-077) - 2026-10-17
- [A-078. 채팅 생성 이어받기를 화면 ViewModel의 재연결 루프로 두고 409를 상세로 가르기](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-078) - 2026-10-17
- [A-079. 공지 읽음 기록을 기기 DataStore에 두고 안 읽음 판정을 셸 수명 ViewModel 하나에 모으기](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-079) - 2026-10-24
- [A-080. 이프 충전 링크의 tab 쿼리로 처음 열 탭을 정하기](../domain/PAYMENT/CLIENT/ANDROID/DECISIONS.md#a-080) - 2026-10-25
- [A-081. 이프 부족 시트의 출석 계약과 절차를 common에 두고 간편 제작은 저장한 뒤 퍼널을 걷어내기](../domain/PAYMENT/CLIENT/ANDROID/DECISIONS.md#a-081) - 2026-10-25
- [A-082. 입력 수위 거절을 키워드 단계로 돌려보내고 완성 거절은 원 응답으로 알리기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-082) - 2026-10-27
- [A-083. 신규 가입 온보딩을 메인 백스택의 루트로 두고 완료를 기기 안 회원 귀속 표시로 판정하기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-083) - 2026-10-28
- [A-084. 로그인 화면의 가입 보상을 버튼을 가리키지 않는 흐린 유리 배지로 알리기](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-084) - 2026-10-28
- [A-085. 홈 카드에서 좋아요 수를 빼고 상세의 좋아요 성공을 홈으로 전달하지 않기](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-085) - 2026-10-28

---

핵심 결정 당시의 맥락·선택·이유·영향을 기록합니다. 현재 계약은 해당 스펙, 현재 구조는 해당 설계를 따릅니다.

## 기록 규칙

[공통 기록 규칙](1-1-client-adr.md#기록-규칙)을 따릅니다. 이 파일의 식별자는 `A-NNN`이며 새 결정은 아래에 추가합니다. 과거 기록은 2026-09-09에 원문에서 이관했으며 날짜 미기재는 추정하지 않았습니다.

<a id="a-001"></a>

## A-001. 제작 진행을 Preferences DataStore에 저장

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-001)에서 확인한다.

<a id="a-002"></a>

## A-002. 로그인 필수 사용자 모델

결정 기록을 도메인 세트로 옮겼다. ([A-002](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-002))

<a id="a-003"></a>

## A-003. Clean Architecture 전면 적용을 하지 않음

- 결정일: 2026-08-22 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:163](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L163-L175)
- **맥락:** 모든 동작에 별도 계층·UseCase를 둘지 검토했습니다.
- **결정:** 실제 책임이 있는 계층만 두며 단순 위임 UseCase를 만들지 않습니다.
- **이유:** 형식적 계층과 반복 코드를 늘리지 않기 위해서입니다.
- **주요 영향:** 의존·소유 경계는 유지하되 구체 현재 규칙은 모듈 설계가 소유합니다.

<a id="a-004"></a>

## A-004. 세션 스코프 Hilt 컴포넌트를 두지 않음

결정 기록을 도메인 세트로 옮겼다. ([A-004](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-004))

<a id="a-005"></a>

## A-005. UI 상태 관리를 직접 구성

- 결정일: 2026-08-22 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:253](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L253-L263)
- **맥락:** MVI 프레임워크 도입과 작은 공통 기반을 비교했습니다.
- **결정:** Intent·Event·순수 reduce·State·Effect 기반 MviViewModel을 사용합니다.
- **이유:** 필요한 상태·효과 규칙을 직접 통제하고 불필요한 프레임워크 제약을 피합니다.
- **주요 영향:** 순서·포화·재수집 계약을 공통 기반에서 검증합니다.

<a id="a-006"></a>

## A-006. Crashlytics로 앱 크래시 수집

- 결정일: 2026-08-22 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:269](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L269-L286)
- **맥락:** 웹·서버와 Sentry로 통일할지 Android용 수집 도구를 선택할지 검토했습니다.
- **결정:** Crashlytics와 Amplitude를 사용하고 Firebase Analytics를 추가하지 않습니다.
- **이유:** 제품 분석 SDK를 중복 도입하지 않고 수동 breadcrumb와 요청 상관 키로 도구 분리 비용을 제한합니다.
- **주요 영향:** API 24~29 ANR 공백을 수용하며 event-local request_id·release 수집·R8 매핑 업로드를 관리합니다.

<a id="a-007"></a>

## A-007. 토큰을 Keystore로 암호화해 저장

결정 기록을 도메인 세트로 옮겼다. ([A-007](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-007))

<a id="a-008"></a>

## A-008. 부팅 세대를 포함한 토큰 만료 판정

결정 기록을 도메인 세트로 옮겼다. ([A-008](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-008))

<a id="a-009"></a>

## A-009. 앱이 device_id 생성

결정 기록을 도메인 세트로 옮겼다. ([A-009](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-009))

<a id="a-010"></a>

## A-010. Navigation 3 사용

- 결정일: 2026-08-23 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:145](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L145-L155)
- **맥락:** 탭 셸에서 백스택·상태 소유 방식을 선택했습니다.
- **결정:** Navigation 3의 명시적 백스택과 복원 가능한 라우트 키를 사용합니다.
- **이유:** 탭·세션·퍼널 백스택을 앱이 직접 소유하기 위해서입니다.
- **주요 영향:** 딥링크·푸시 진입 매핑과 키 직렬화는 앱이 관리합니다.

<a id="a-011"></a>

## A-011. 셸이 공용 헤더와 탭 소유

- 결정일: 2026-08-23 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:415](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L415-L426)
- **맥락:** 화면별 헤더와 탭을 반복 구성할지 검토했습니다.
- **결정:** 메인 셸이 chrome을 소유하고 각 탭은 콘텐츠를 제공합니다.
- **이유:** 전환 중 공용 UI가 사라지거나 위치가 달라지는 것을 막습니다.
- **주요 영향:** 전체 화면 목적지는 셸 위에 쌓고 탭별 상태를 보존합니다.

<a id="a-012"></a>

## A-012. 제작 단계를 별도 목적지로 구성

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-012)에서 확인한다.

<a id="a-013"></a>

## A-013. 스토리라인이 키워드 목적지를 대체

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-013)에서 확인한다.

<a id="a-014"></a>

## A-014. 제작 진행 저장소를 Room으로 통합

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-014)에서 확인한다.

<a id="a-015"></a>

## A-015. 제작 퍼널 이탈과 교차 페이드

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-015)에서 확인한다.

<a id="a-016"></a>

## A-016. 제작 탭을 분리해 네 탭 구성

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-016)에서 확인한다.

<a id="a-017"></a>

## A-017. 목록 카드에서 스토리 삭제 제공

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-017)에서 확인한다.

<a id="a-018"></a>

## A-018. 이미지 뷰어는 상세 내부 상태

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-018)에서 확인한다.

<a id="a-019"></a>

## A-019. 상세에서 채팅 진입 시 상세 유지

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-019)에서 확인한다.

<a id="a-020"></a>

## A-020. 편집 저장을 버튼과 백그라운드 전환으로 제한

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-020)에서 확인한다.

<a id="a-021"></a>

## A-021. 내 스토리를 가로 행 목록으로 표시

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-021)에서 확인한다.

<a id="a-022"></a>

## A-022. 빈 채팅 목록의 제작 진입 단일화

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-022)에서 확인한다.

<a id="a-023"></a>

## A-023. 구성 변경의 Activity 재생성을 수용

- 결정일: 2026-08-28 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:1537](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L1537-L1573)
- **맥락:** 방향·테마·글자 크기 변경에서 화면 상태와 리소스를 함께 복원해야 했습니다.
- **결정:** configChanges·screenOrientation을 선언하지 않고 수명에 맞는 상태 저장을 사용합니다.
- **이유:** 리소스 재적용을 직접 재현하지 않고 큰 화면의 방향 잠금 예외에도 대응하기 위해서입니다.
- **주요 영향:** 구성 변경과 프로세스 종료를 별도로 검증하며 당시 최대 글자 크기·가로 레이아웃은 잔여로 남았습니다.

<a id="a-024"></a>

## A-024. 채팅 메시지를 밴드로 표시

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-024)에서 확인한다.

<a id="a-025"></a>

## A-025. 법적 WebView 경로 이탈 감지 제거

결정 기록을 도메인 세트로 옮겼다. ([A-025](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-025))

<a id="a-026"></a>

## A-026. 초대에 Android 공유 시트 사용

결정 기록을 도메인 세트로 옮겼다. ([A-026](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-026))

<a id="a-027"></a>

## A-027. 오픈소스 고지는 의존성에서 생성

- 결정일: 2026-08-31 · 기록 확정 상태: Accepted
- 근거: [이관 원문 A:1023](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L1023-L1028)
- **맥락:** 수동 라이선스 목록은 의존성 변경과 어긋날 수 있습니다.
- **결정:** 빌드 의존성 기반 생성 목록을 사용합니다.
- **이유:** 직접 작성한 목록을 별도로 유지하지 않기 위해서입니다.
- **주요 영향:** 빌드와 고지 생성 경로를 함께 유지합니다.

<a id="a-028"></a>

## A-028. 뒤로가기 전환은 수평 이동

- 결정일: 2026-09-03 · 기록 확정 상태: Accepted
- 대체 관계: [A-015](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-015)의 전환 방식만 부분 대체
- 근거: [이관 원문 A:351](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-3-android-app.md#L351-L361)
- **맥락:** 교차 페이드로는 들어오고 나가는 방향이 드러나지 않았습니다.
- **결정:** 일반 진입·뒤로가기는 수평 이동, 퍼널 덮개는 별도 수직 전환을 사용합니다.
- **이유:** 사용자가 화면 관계와 이동 방향을 이해하도록 하기 위해서입니다.
- **주요 영향:** 교차 페이드 결정의 전환 부분만 대체하고 닫기의 의미는 유지합니다.

<a id="a-029"></a>

## A-029. 카드 옵션을 다이얼로그로 통일

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-029)에서 확인한다.

<a id="a-030"></a>

## A-030. 상세의 isOwner로 삭제 메뉴 제공

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-030)에서 확인한다.

<a id="a-031"></a>

## A-031. 퍼널 닫기는 항상 확인

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-031)에서 확인한다.

<a id="a-032"></a>

## A-032. 푸시 삭제와 수신자 검증을 분리

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-032)에서 확인한다.

<a id="a-033"></a>

## A-033. 알림 권한 요청은 메인 그래프 첫 진입

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-033)에서 확인한다.

<a id="a-034"></a>

## A-034. 알림 수신자를 payload로 재검증

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-034)에서 확인한다.

<a id="a-035"></a>

## A-035. 로그아웃 후 제작 데이터를 계정별 보존

결정 기록을 도메인 세트로 옮겼다. ([A-035](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-035))

<a id="a-036"></a>

## A-036. 완성 요청을 편집 행에서 분리하고 보존 이전

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-036)에서 확인한다.

<a id="a-037"></a>

## A-037. 보이는 완성 카드만 주기 조회

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-037)에서 확인한다.

<a id="a-038"></a>

## A-038. 기능 단위 모듈과 내부 패키지 계층

- 결정일: 2026-09-05 · 상태: Accepted
- **맥락:** 중앙 core에 업무 소유권과 계층별 Gradle 모듈이 모여 있었습니다.
- **선택:** 기능을 최상위 모듈로, entity/domain/data/presentation을 내부 패키지로 둡니다. 공유 신고는 report가 소유합니다.
- **이유:** common에 신고를 두면 network/designsystem 역참조가 생기고 화면별 복제는 제출·분석 규칙을 중복시킵니다.
- **주요 영향:** 계층의 컴파일 격리 대신 PSI 경계 검사·리뷰가 필요합니다. 이전 core 배치 규칙을 대체하며 API·저장 형식 변경은 포함하지 않습니다.
- 근거: [이관 전 원문](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/planning/android-module-architecture.md#L11-L23)

<a id="a-039"></a>

## A-039. 알림 기능을 notification 모듈에 배치

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-039)에서 확인한다.

<a id="a-040"></a>

## A-040. 광고 알림 동의는 첫 진입 시트로 묻고 즉시 통지

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-040)에서 확인한다.

<a id="a-041"></a>

## A-041. 인물 이미지 뷰어를 화면 상태로 공용화

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-041)에서 확인한다.

<a id="a-042"></a>

## A-042. 카드 옵션·상세 옵션·채팅 메뉴를 바텀 시트로 통일

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-042)에서 확인한다.

<a id="a-043"></a>

## A-043. 채팅 공유를 앱에 적용하고 Android 공유 시트로 전달

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-043)에서 확인한다.

<a id="a-044"></a>

## A-044. 약관 동의 시트를 legal이 소유하고 광고 동의는 선택 항목과 재진입 재질문으로 받음

결정 기록을 도메인 세트로 옮겼다. ([A-044](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-044))

## A-045. 알림 진입 목적지는 서버 deepLink를 정본으로 해석

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-045)에서 확인한다.

<a id="a-046"></a>

## A-046. 편집 초안을 퍼널 세션 ID 키의 여러 행으로 확장

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-046)에서 확인한다.

<a id="a-047"></a>

## A-047. release 빌드에 R8 축소·난독화 적용

- 결정일: 2026-09-26 · 기록 확정 상태: Accepted
- **맥락:** v1.1.1은 R8을 끈 채 출시했고, Play Console이 DEX 난독화 비율 1%를 기준 미달로 표시했습니다(2027년 2월까지 해결하지 않으면 공개·게시가 제한될 수 있음). 앱이 이름이나 리플렉션에 기대는 곳과 라이브러리 consumer rules의 빈틈을 확인해야 했습니다.
- **결정:** release만 AGP `optimization { enable = true }`로 코드·리소스 축소와 난독화를 켜고, keep 규칙은 `app/proguard-rules.pro` 한 파일에 consumer rules로 부족한 곳만 둡니다. 현재는 분석 이벤트가 `::class.simpleName`으로 보내는 `DomainError` 하위 타입 이름과, 오류 원인 enum 필드를 이름으로 읽는 카카오 SDK 모델(카카오 공식 규칙)입니다. Crashlytics 매핑 업로드는 `mappingFileUploadEnabled = true`로 명시합니다. debug는 켜지 않습니다.
- **이유:** Crashlytics 플러그인은 `variant.isMinifyEnabled`로 업로드 여부를 정하는데 `optimization` DSL로 켠 R8을 그 값이 반영하지 않아, 명시하지 않으면 매핑 없이 난독화된 스택만 쌓입니다. 규칙을 넓게 잡으면 축소 효과가 줄고 어떤 규칙이 왜 필요한지 흐려지므로, 실제로 깨진 곳만 이유와 함께 둡니다. 카카오 규칙이 없으면 카카오 토큰이 없는 상태에서 앱 시작 직후 `NoSuchFieldException`으로 크래시합니다.
- **주요 영향:** `bundleRelease`가 Crashlytics로 매핑을 올리고 AAB에도 매핑이 실려 Play 역난독에 쓰입니다. 새 라이브러리나 이름·리플렉션에 기대는 코드를 더하면 R8을 켠 빌드로 해당 흐름을 확인합니다. 로컬 업로드 키로 서명한 release는 운영 로그인이 되지 않아, 로그인 뒤 흐름은 같은 규칙으로 R8을 켠 debug 빌드(dev 서버)로 검증합니다.
- 근거: [KNK-1408](https://kimandkang.atlassian.net/browse/KNK-1408), [Android 계획](../../../manyak-android/docs/plans/r8-minification.md)

<a id="a-048"></a>

## A-048. 채팅 안내 투어를 같은 컴포지션의 오버레이로 그리고 뒤로가기를 건너뛰기로 처리

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-048)에서 확인한다.

<a id="a-049"></a>

## A-049. 상세 삭제는 제작 탭으로 복귀하고 좋아요 성공은 홈 카드에 전달

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-049)에서 확인한다.

<a id="a-050"></a>

## A-050. 실시간 이미지 안내의 수명과 시트 위 오버레이

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-050)에서 확인한다.

## A-051. 필수 동의 확인을 분석 식별과 푸시 등록의 선행 조건으로 공유

결정 기록을 도메인 세트로 옮겼다. ([A-051](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-051))

## A-052. 필수 동의를 로그인 화면에서 완료한 뒤 회원 그래프 구성

결정 기록을 도메인 세트로 옮겼다. ([A-052](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-052))

<a id="a-053"></a>

## A-053. 로컬 제작 카드의 진입과 인물 편집 상태 소유권

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-053)에서 확인한다.

## A-054. 저장 세션의 시작 화면과 새 로그인 동의 흐름 분리

결정 기록을 도메인 세트로 옮겼다. ([A-054](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-054))

<a id="a-055"></a>

## A-055. 임시 저장 성공을 토스트와 시간 잠금으로 안내

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-055)에서 확인한다.

<a id="a-056"></a>

## A-056. 검수 제출본을 화면 수명으로 조회하고 알림을 제작 탭에 연결

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-056)에서 확인한다.

## A-057. 제공 장르 검색과 이전 초안 호환

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-057)에서 확인한다.

## A-058. 장르 검색 선택 토글과 대표 칩 순서 유지

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-058)에서 확인한다.

## A-059. 장르 검색 캐시와 지연 로딩 표시

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-059)에서 확인한다.

## A-060. 장르 검색 로딩 표시 기준 조정

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-060)에서 확인한다.

## A-061. 일반 제작의 별도 초안 테이블과 제출 접수 경계

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-061)에서 확인한다.

## A-062. 일반 제작과 수정의 공용 폼 및 이미지 자르기 소유권

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-062)에서 확인한다.

## A-063. 잃을 것 없는 제작 이탈과 제작 화면 전환 통일

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-063)에서 확인한다.

## A-064. 동의 전 가입 대기를 세션 없이 auth 메모리에 두기

결정 기록을 도메인 세트로 옮겼다. ([A-064](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-064))

## A-065. 완성 중 표지를 로고 마스코트 애니메이션으로 바꾸기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-065)에서 확인한다.

## A-066. 채팅 실시간 이미지 대기를 마스코트가 인물을 그리는 애니메이션으로 바꾸기

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-066)에서 확인한다.

## A-067. 완성 중 표지 안무를 웹 개편 값으로 따라가기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-067)에서 확인한다.

## A-068. 채팅 실시간 이미지 대기 그림을 웹 개편 값의 창가 인물화 한 장으로 따라가기

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-068)에서 확인한다.

## A-069. 필수 동의 시트에 로그아웃 버튼을 두고 시작 화면 조회 실패에는 두지 않기

결정 기록을 도메인 세트로 옮겼다. ([A-069](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-069))

## A-070. 페르소나를 마이가 소유하고 상세에는 좁은 공용 계약으로 열기

결정 기록을 도메인 세트로 옮겼다. ([A-070](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-070))

## A-071. 웹의 앱 열기 링크를 https 대신 전용 스킴으로 받기

- 날짜: 2026-10-13
- 상태: 확정
- 범위: `MainActivity` intent-filter, `PushEntry`의 앱 열기 진입, 웹 앱 안내 배너의 intent 링크

웹 앱 안내 배너([웹 W-033](1-2-web-adr.md#w-033))는 패키지를 명시한 `intent://` 링크로 앱을 엽니다. 받는 쪽을 autoVerify 없는 `https://manyak.app` 필터로 두면 Android 12 이상에서는 다른 앱의 일반 링크가 그대로 브라우저로 가지만, minSdk 24인 이 앱은 Android 11 이하에서 다른 앱(메일, 메신저 등)의 manyak.app 링크마다 앱 선택창을 띄웁니다. 그래서 https 링크와 겹치지 않는 전용 스킴 `manyak://manyak.app`만 받고, 웹은 `scheme=manyak`으로 엽니다. 앱이 없을 때 브라우저가 플레이스토어를 여는 동작은 같습니다.

진입은 새 타입을 만들지 않고 기존 `PushEntry`에 `TYPE_APP_LINK`를 더해 보류, 로그인 뒤 소비, 프로세스 복원 경로를 그대로 씁니다. 특정 회원에게 보낸 링크가 아니라 수신자 비교를 건너뛰고, 경로는 https로 옮겨 푸시와 같은 `DeepLink` 해석을 씁니다. https App Links(autoVerify, `assetlinks.json`)는 KNK-927에서 따로 다룹니다.

## A-072. 간편 제작 화풍을 기존 초안 JSON에 더하고 스토리라인을 다시 만들어도 남기기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-072)에서 확인한다.

## A-073. 표지 위 뱃지에 웹과 같은 배경 흐림을 GraphicsLayer로 적용하기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-073)에서 확인한다.

## A-074. 일반 제작 임시 저장본을 서버 초안으로 옮기고 Room에는 이관 전 초안과 접수 연결만 남기기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-074)에서 확인한다.

<a id="a-075"></a>

## A-075. 간편 제작 초안을 세션 ID로 서버에 두고 진행 기록에 서버 초안 버전 열을 더하기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-075)에서 확인한다.

<a id="a-076"></a>

## A-076. 새 제작 상한을 FAB에서 보이는 초안 카드로 판정하고 제작 탭 첫 조회를 한 스켈레톤으로 덮기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-076)에서 확인한다.

<a id="a-077"></a>

## A-077. 완성 실패를 추가 정보 단계 초안으로 되돌리고 실패 카드를 없애기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-077)에서 확인한다.

<a id="a-078"></a>

## A-078. 채팅 생성 이어받기를 화면 ViewModel의 재연결 루프로 두고 409를 상세로 가르기

CHAT 결정은 [도메인 기록](../domain/CHAT/CLIENT/ANDROID/DECISIONS.md#a-078)에서 확인한다.

<a id="a-079"></a>

## A-079. 공지 읽음 기록을 기기 DataStore에 두고 안 읽음 판정을 셸 수명 ViewModel 하나에 모으기

NOTIFICATION 결정은 [도메인 기록](../domain/NOTIFICATION/CLIENT/ANDROID/DECISIONS.md#a-079)에서 확인한다.

<a id="a-080"></a>

## A-080. 이프 충전 링크의 tab 쿼리로 처음 열 탭을 정하기

PAYMENT 내용은 도메인 문서에서 관리한다. ([A-080](../domain/PAYMENT/CLIENT/ANDROID/DECISIONS.md#a-080))

<a id="a-081"></a>

## A-081. 이프 부족 시트의 출석 계약과 절차를 common에 두고 간편 제작은 저장한 뒤 퍼널을 걷어내기

PAYMENT 내용은 도메인 문서에서 관리한다. ([A-081](../domain/PAYMENT/CLIENT/ANDROID/DECISIONS.md#a-081))

<a id="a-082"></a>

## A-082. 입력 수위 거절을 키워드 단계로 돌려보내고 완성 거절은 원 응답으로 알리기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-082)에서 확인한다.

<a id="a-083"></a>

## A-083. 신규 가입 온보딩을 메인 백스택의 루트로 두고 완료를 기기 안 회원 귀속 표시로 판정하기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-083)에서 확인한다.

<a id="a-084"></a>

## A-084. 로그인 화면의 가입 보상을 버튼을 가리키지 않는 흐린 유리 배지로 알리기

결정 기록을 도메인 세트로 옮겼다. ([A-084](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-084))

<a id="a-085"></a>

## A-085. 홈 카드에서 좋아요 수를 빼고 상세의 좋아요 성공을 홈으로 전달하지 않기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-085)에서 확인한다.

<a id="a-086"></a>

## A-086. 신규 가입 초대 코드 안내를 가입한 다음 실행의 홈 탭에서 띄우기

결정 기록을 도메인 세트로 옮겼다. ([A-086](../domain/ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-086))

<a id="a-087"></a>

## A-087. 간편 제작 공개 범위를 기본 공개로 기존 초안 JSON에 더하고 기본값은 비워 두기

STORY 결정은 [도메인 기록](../domain/STORY/CLIENT/ANDROID/DECISIONS.md#a-087)에서 확인한다.

# 3-1 계약

이 문서는 관리자 웹 대시보드 그룹과 이프 내역 화면이 부르는 BFF 경로와 서버 계약의 대응, 웹이 보내는 쿼리와 계약을 쓰는 방식의 차이를 정한다.

요청과 응답 필드, 실패 응답의 기준은 BACKEND 계약에, BFF의 검증과 전달은 데이터 연동에 있다. ([BACKEND 4-2 계약](../BACKEND/4-2-CONTRACT.md), [3-2 데이터 연동](3-2-DATA-INTEGRATION.md))

<br>

### 3-1-1 경로 대응

브라우저는 같은 출처의 BFF 경로만 부른다. BFF 경로는 서버 경로에서 `/api/v1/admin` 접두를 `/api`로 바꾼 것이다.

| 화면과 탭 | BFF 경로 | 서버 계약 |
|---|---|---|
| 개요 요약 카드 | `GET /api/dashboard/summary` | [4-2-3 대시보드 요약](../BACKEND/4-2-CONTRACT.md#4-2-3-대시보드-요약) |
| 개요 일별 추이, 분석 | `GET /api/dashboard/charts` | [4-2-4 대시보드 차트](../BACKEND/4-2-CONTRACT.md#4-2-4-대시보드-차트) |
| 개요 Amplitude 사용자 지표 | `GET /api/dashboard/analytics` | [4-2-17 분석 지표](../BACKEND/4-2-CONTRACT.md#4-2-17-분석-지표) |
| 개요 앱 설치 | `GET /api/dashboard/play-installs` | [4-2-18 설치 지표](../BACKEND/4-2-CONTRACT.md#4-2-18-설치-지표) |
| 유입 분석 광고 캠페인 선택 | `GET /api/campaigns` | [4-2-19 캠페인 목록](../BACKEND/4-2-CONTRACT.md#4-2-19-캠페인-목록) |
| 유입 분석 캠페인 추이 | `GET /api/campaigns/analytics` | [4-2-20 캠페인 추이](../BACKEND/4-2-CONTRACT.md#4-2-20-캠페인-추이) |
| 유입 분석 간편 제작 퍼널 | `GET /api/campaigns/funnels/creation` | [4-2-21 캠페인 간편 제작 퍼널](../BACKEND/4-2-CONTRACT.md#4-2-21-캠페인-간편-제작-퍼널) |
| 유입 분석 상세 진입 퍼널 | `GET /api/campaigns/funnels/story-detail` | [4-2-22 캠페인 상세 진입 퍼널](../BACKEND/4-2-CONTRACT.md#4-2-22-캠페인-상세-진입-퍼널) |
| 유입 분석 유입 소스 | `GET /api/campaigns/sources` | [4-2-23 캠페인 유입 소스](../BACKEND/4-2-CONTRACT.md#4-2-23-캠페인-유입-소스) |
| 사용자 활동 | `GET /api/users/activity` | [4-2-24 사용자 활동](../BACKEND/4-2-CONTRACT.md#4-2-24-사용자-활동) |
| 리텐션 | `GET /api/users/retention` | [4-2-25 사용자 리텐션](../BACKEND/4-2-CONTRACT.md#4-2-25-사용자-리텐션) |
| 세션 | `GET /api/users/sessions` | [4-2-26 사용자 세션](../BACKEND/4-2-CONTRACT.md#4-2-26-사용자-세션) |
| 신규 가입자 | `GET /api/users/signups` | [4-2-27 신규 가입자](../BACKEND/4-2-CONTRACT.md#4-2-27-신규-가입자) |
| 전환 퍼널 | `GET /api/conversion/funnels/{funnel}` | [4-2-28 전환 퍼널](../BACKEND/4-2-CONTRACT.md#4-2-28-전환-퍼널) |
| 채팅 턴 도달률 | `GET /api/conversion/turn-reach` | [4-2-29 채팅 턴 도달률](../BACKEND/4-2-CONTRACT.md#4-2-29-채팅-턴-도달률) |
| 기능 사용과 안정성 | `GET /api/quality/client` | [4-2-30 기능 사용과 안정성](../BACKEND/4-2-CONTRACT.md#4-2-30-기능-사용과-안정성) |
| 채팅 옵션 비중 | `GET /api/quality/chat-options` | [4-2-31 채팅 옵션 비중](../BACKEND/4-2-CONTRACT.md#4-2-31-채팅-옵션-비중) |
| AI 비용 | `GET /api/quality/ai-cost` | [4-2-32 AI 비용](../BACKEND/4-2-CONTRACT.md#4-2-32-ai-비용) |
| 이프 내역 | `GET /api/credits/transactions` | [4-2-13 이프 내역](../BACKEND/4-2-CONTRACT.md#4-2-13-이프-내역) |

<br>

### 3-1-2 보내는 쿼리

| 화면과 탭 | 쿼리 |
|---|---|
| 기간을 받는 모든 요청 | `from`, `to`<br>화면이 정한 범위를 KST 날짜로 보냄<br>`days`는 보내지 않음 |
| 유입 분석의 캠페인 추이와 두 퍼널 | `campaign`<br>선택하거나 입력한 값 |
| 유입 분석 상세 진입 퍼널 | `storyId`<br>입력한 값이 있을 때만<br>없으면 서버가 캠페인 목록의 대상 스토리를 씀 |
| 유입 분석 유입 소스 | 기간만 |
| 전환 퍼널 | 경로의 `funnel`<br>`platform`은 스토리 제작, 상세 진입 채팅, 게스트 한도 로그인에서만<br>`storyId`는 상세 진입 채팅에서 값이 있을 때만 |
| 기능 사용과 안정성 | `platform`의 `all`, `web`, `android` |
| 리텐션 | 기간만<br>플랫폼은 응답의 세 항목 가운데 화면에서 고름 |
| 이프 내역 | `direction`, `date`, `page`, `size`, `sort`, `order`<br>기본 `page=1`, `size=20`, `order=desc` |

- 간편 제작 퍼널의 광고 구분은 서버로 보내지 않는다. 응답의 세 값 가운데 화면에서 고른다.
- 기간 오류가 있거나 필요한 조건이 비어 있으면 요청을 보내지 않는다.

<br>

### 3-1-3 응답을 쓰는 방식

| 응답 값 | 웹의 처리 |
|---|---|
| `pendingDates` | 준비 중 알림과 차트 끊김<br>비어 있지 않으면 60초 뒤 같은 요청을 다시 보냄 |
| `todayActiveUsers`가 `null` | "준비 중"으로 표시하고 60초 뒤 다시 요청 |
| `monthlyActiveUsers`가 `null` | "준비 중"으로 표시하고 60초 뒤 다시 요청 |
| Amplitude 지표와 서버 DB 지표의 `asOf` | 탭 제목 아래에 KST 시각으로 "{시각} KST 집계 기준" |
| 설치 지표의 `asOf` | Play 기준 날짜를 바꾸지 않고 "집계 기준 날짜 {날짜} (Play 기준 태평양 시간)" |
| 계약이 `null`이라고 정한 비율과 비용 | 정보 구조에 정한 문구로 표시 |
| `campaign`, `storyId`, `platform` | 서버가 적용한 값을 화면의 조건 표시에 씀 |

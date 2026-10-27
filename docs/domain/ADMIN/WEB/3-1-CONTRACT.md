# 3-1 계약

이 문서는 관리자 웹 대시보드 그룹과 이프 내역, 검수 제출 화면, 스토리 상세의 스토리 설정 구역과 공개 중단, 스토리와 채팅의 목록과 상세가 부르는 BFF 경로와 서버 계약의 대응, 웹이 보내는 쿼리와 계약을 쓰는 방식의 차이를 정한다.

요청과 응답 필드, 실패 응답의 기준은 BACKEND 계약에, BFF의 검증과 전달은 데이터 연동에 있다. ([BACKEND 4-2 계약](../BACKEND/4-2-CONTRACT.md), [3-2 데이터 연동](3-2-DATA-INTEGRATION.md))

<br>

### 3-1-1 경로 대응

브라우저는 같은 출처의 BFF 경로만 부른다. BFF 경로는 서버 경로에서 `/api/v1/admin` 접두를 `/api`로 바꾼 것이다.

| 화면과 탭 | BFF 경로 | 서버 계약 |
|---|---|---|
| 개요 요약 카드 | `GET /api/dashboard/summary` | [4-2-3 대시보드 요약](../BACKEND/4-2-CONTRACT.md#4-2-3-대시보드-요약) |
| 개요 일별 추이, 분석 | `GET /api/dashboard/charts` | [4-2-4 대시보드 차트](../BACKEND/4-2-CONTRACT.md#4-2-4-대시보드-차트) |
| 개요 오늘 활성 사용자 카드 | `GET /api/dashboard/analytics` | [4-2-18 분석 지표](../BACKEND/4-2-CONTRACT.md#4-2-18-분석-지표) |
| 개요 앱 설치 카드, 유입 분석 앱 설치 | `GET /api/dashboard/play-installs` | [4-2-19 설치 지표](../BACKEND/4-2-CONTRACT.md#4-2-19-설치-지표) |
| 유입 분석 광고 캠페인 선택 | `GET /api/campaigns` | [4-2-20 캠페인 목록](../BACKEND/4-2-CONTRACT.md#4-2-20-캠페인-목록) |
| 유입 분석 캠페인 추이 | `GET /api/campaigns/analytics` | [4-2-21 캠페인 추이](../BACKEND/4-2-CONTRACT.md#4-2-21-캠페인-추이) |
| 유입 분석 간편 제작 퍼널 | `GET /api/campaigns/funnels/creation` | [4-2-22 캠페인 간편 제작 퍼널](../BACKEND/4-2-CONTRACT.md#4-2-22-캠페인-간편-제작-퍼널) |
| 유입 분석 상세 진입 퍼널 | `GET /api/campaigns/funnels/story-detail` | [4-2-23 캠페인 상세 진입 퍼널](../BACKEND/4-2-CONTRACT.md#4-2-23-캠페인-상세-진입-퍼널) |
| 유입 분석 유입 소스 | `GET /api/campaigns/sources` | [4-2-24 캠페인 유입 소스](../BACKEND/4-2-CONTRACT.md#4-2-24-캠페인-유입-소스) |
| 유입 분석 푸시 열람 | `GET /api/campaigns/push-opens` | [4-2-36 푸시 열람](../BACKEND/4-2-CONTRACT.md#4-2-36-푸시-열람) |
| 사용자 활동 | `GET /api/users/activity` | [4-2-25 사용자 활동](../BACKEND/4-2-CONTRACT.md#4-2-25-사용자-활동) |
| 리텐션 | `GET /api/users/retention` | [4-2-26 사용자 리텐션](../BACKEND/4-2-CONTRACT.md#4-2-26-사용자-리텐션) |
| 세션 | `GET /api/users/sessions` | [4-2-27 사용자 세션](../BACKEND/4-2-CONTRACT.md#4-2-27-사용자-세션) |
| 신규 가입자 | `GET /api/users/signups` | [4-2-28 신규 가입자](../BACKEND/4-2-CONTRACT.md#4-2-28-신규-가입자) |
| 전환 퍼널 | `GET /api/conversion/funnels/{funnel}` | [4-2-29 전환 퍼널](../BACKEND/4-2-CONTRACT.md#4-2-29-전환-퍼널) |
| 채팅 턴 도달률 | `GET /api/conversion/turn-reach` | [4-2-30 채팅 턴 도달률](../BACKEND/4-2-CONTRACT.md#4-2-30-채팅-턴-도달률) |
| 기능 사용과 안정성 | `GET /api/quality/client` | [4-2-31 기능 사용과 안정성](../BACKEND/4-2-CONTRACT.md#4-2-31-기능-사용과-안정성) |
| 채팅 옵션 비중 | `GET /api/quality/chat-options` | [4-2-32 채팅 옵션 비중](../BACKEND/4-2-CONTRACT.md#4-2-32-채팅-옵션-비중) |
| AI 비용 | `GET /api/quality/ai-cost` | [4-2-33 AI 비용](../BACKEND/4-2-CONTRACT.md#4-2-33-ai-비용) |
| 인프라 서비스와 요청, 저장소 | `GET /api/infra/metrics` | [4-2-34 인프라 지표](../BACKEND/4-2-CONTRACT.md#4-2-34-인프라-지표) |
| 인프라 DB 테이블 | `GET /api/infra/db-tables` | [4-2-35 DB 테이블 크기](../BACKEND/4-2-CONTRACT.md#4-2-35-db-테이블-크기) |
| 이프 내역 | `GET /api/credits/transactions` | [4-2-14 이프 내역](../BACKEND/4-2-CONTRACT.md#4-2-14-이프-내역) |
| 검수 제출 목록 | `GET /api/moderation/submissions` | [MODERATION 4-2-8 관리자 제출본 목록](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-8-관리자-제출본-목록) |
| 검수 제출 상세 | `GET /api/moderation/submissions/{submissionId}` | [MODERATION 4-2-9 관리자 제출본 상세](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-9-관리자-제출본-상세) |
| 검수 보류 해제 | `POST /api/moderation/holds/{submissionId}/release` | [MODERATION 4-2-7 보류 해제](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-7-보류-해제) |
| 스토리 공개 중단 | `POST /api/moderation/stories/{storyId}/takedown` | [MODERATION 4-2-10 공개 중단](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-10-공개-중단) |
| 스토리 상세의 스토리 설정 | `GET /api/stories/{storyId}/settings` | [4-2-7 스토리 설정](../BACKEND/4-2-CONTRACT.md#4-2-7-스토리-설정) |
| 스토리 목록과 범위 목록 | `GET /api/stories` | [4-2-5 스토리 목록](../BACKEND/4-2-CONTRACT.md#4-2-5-스토리-목록) |
| 스토리 상세 | `GET /api/stories/{storyId}` | [4-2-6 스토리 상세](../BACKEND/4-2-CONTRACT.md#4-2-6-스토리-상세) |
| 채팅 목록과 범위 목록 | `GET /api/chats` | [4-2-8 채팅 목록](../BACKEND/4-2-CONTRACT.md#4-2-8-채팅-목록) |
| 채팅 상세 | `GET /api/chats/{chatId}` | [4-2-9 채팅 상세](../BACKEND/4-2-CONTRACT.md#4-2-9-채팅-상세) |

- 검수 제출의 세 경로, 스토리 공개 중단 경로, 스토리 설정 경로는 서버 OpenAPI의 관리자 문서에 있어야 BFF가 생성 스키마로 검증하고 전달한다. 관리자 저장소의 생성 코드는 서버 OpenAPI를 다시 받아 만든다.

<br>

### 3-1-2 보내는 쿼리

| 화면과 탭 | 쿼리 |
|---|---|
| 기간을 받는 모든 요청 | `from`, `to`<br>화면이 정한 범위를 KST 날짜로 보냄<br>`days`는 보내지 않음 |
| 개요 오늘 활성 사용자 카드 | `from`과 `to` 모두 KST 오늘<br>페이지의 기간을 보내지 않음 |
| 설치 지표 | 쿼리 없음 |
| 유입 분석의 캠페인 추이와 두 퍼널 | `campaign`<br>선택하거나 입력한 값 |
| 유입 분석 상세 진입 퍼널 | `storyId`<br>입력한 값이 있을 때만<br>없으면 서버가 캠페인 목록의 대상 스토리를 씀 |
| 유입 분석 유입 소스 | 기간만 |
| 전환 퍼널 | 경로의 `funnel`<br>`platform`은 간편 제작, 상세 진입 채팅, 게스트 한도 로그인에서만<br>`storyId`는 상세 진입 채팅에서 값이 있을 때만 |
| 기능 사용과 안정성 | `platform`의 `all`, `web`, `android` |
| 리텐션 | 기간만<br>플랫폼은 응답의 세 항목 가운데 화면에서 고름 |
| 인프라 지표 | 기간만 |
| DB 테이블 크기 | `limit=20` |
| 이프 내역 | `direction`, `date`, `page`, `size`, `sort`, `order`<br>기본 `page=1`, `size=20`, `order=desc` |
| 검수 제출 목록 | `status`, `from`, `to`, `q`, `memberId`, `storyId`, `page`, `size`, `sort`, `order`<br>값이 있는 것만<br>기본 `page=1`, `size=20`, `sort=createdAt`, `order=desc` |
| 검수 보류 해제 | 본문 `reason`<br>앞뒤 공백을 지운 1~500자 |
| 스토리 공개 중단 | 본문 `reasonCode`와 `memo`<br>`memo`는 앞뒤 공백을 지운 1~500자일 때만 싣고 비면 뺌 |
| 스토리 목록, 채팅 목록, 범위 목록의 삭제 필터 | 포함은 `deleted=include`<br>삭제된 스토리만과 삭제된 채팅만은 `deleted=only`<br>제외는 `deleted`를 보내지 않음<br>범위 목록은 `memberId`나 `storyId`와 함께 보냄 |

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
| AI 비용의 `asOf` | Langfuse 출처 툴팁의 "{받은 시각} KST" |
| 인프라 지표와 DB 테이블 크기의 `asOf` | 출처 툴팁의 "{받은 시각} KST"<br>캐시로 응답한 값이면 그 캐시를 만든 시각 |
| 설치 지표의 `asOf` | Play 기준 날짜를 바꾸지 않고 "집계 기준 날짜 {날짜} (Play 기준 태평양 시간)" |
| 계약이 `null`이라고 정한 비율과 비용 | 정보 구조에 정한 문구로 표시 |
| `campaign`, `storyId`, `platform` | 서버가 적용한 값을 화면의 조건 표시에 씀 |
| 스토리의 `takenDownAt`, `takedownReason` | `takenDownAt`이 `null`이 아니면 정보 구조의 공개 중단 표시와 버튼 숨김 ([2-1-16 스토리 공개 중단](2-1-INFORMATION-ARCHITECTURE.md#2-1-16-스토리-공개-중단)) |
| 스토리와 채팅의 `deletedAt` | `null`이 아니면 정보 구조의 삭제 표시 ([2-1-15 삭제된 스토리와 채팅](2-1-INFORMATION-ARCHITECTURE.md#2-1-15-삭제된-스토리와-채팅))<br>스토리 설정 응답의 `deletedAt`은 쓰지 않고 상세 응답의 값으로 표시 |

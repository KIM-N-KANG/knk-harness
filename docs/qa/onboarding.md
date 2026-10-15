# onboarding

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-10-15 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 게스트·신규 가입 온보딩의 수동 QA와 E2E 검수 기준을 정의합니다. |
| 화면 | 온보딩 페이지(FE-SCREEN-007, `/onboarding`. 게이트는 서버 프록시·페이지 가드) · 신규 가입 초대 코드 모달 바텀 시트(FE-SCREEN-008, 루트 레이아웃 마운트) · 앱 안내 배너(루트 레이아웃, 모든 화면 최상단) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [웹 사용자 모델](../spec/3-2-web-spec.md#웹-사용자-모델), [`2-user-stories.md`](../spec/2-user-stories.md) US-2-5·US-8-3, [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너) |
| 관련 E2E | `manyak-web/e2e/smoke/onboarding.spec.ts`, `manyak-web/e2e/my/invite.spec.ts`(신규 가입 바텀 시트), `manyak-web/e2e/visual/onboarding-visual.spec.ts`, `manyak-web/e2e/seo/crawler-indexing.spec.ts`(크롤러 게이트 우회), `manyak-web/e2e/smoke/app-banner.spec.ts`, `manyak-web/e2e/visual/app-banner-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [ONBD-GUEST — 게스트 환영 온보딩 페이지](#onbd-guest--게스트-환영-온보딩-페이지)
- [ONBD-INVITE — 신규 가입(회원) 초대 코드 온보딩](#onbd-invite--신규-가입회원-초대-코드-온보딩)
- [ONBD-BANNER — 앱 안내 배너](#onbd-banner--앱-안내-배너)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

## ONBD-GUEST — 게스트 환영 온보딩 페이지

기준: [계약·구조](../spec/3-2-web-spec.md#fe-screen-007-온보딩-페이지).

`visual/onboarding-visual`은 원본 WebP로 화면을 비교하며 Next.js 이미지 최적화 응답의 로딩 검사는 하지 않습니다. 첫 화면 이미지가 일정 간격으로 바뀌므로 모션 감소로 첫 장에 고정해 찍습니다. 이미지 `complete`·`naturalWidth`의 별도 대기 조건도 두지 않습니다. 테마별 원본 자산 검증은 ONBD-GUEST-25의 `smoke/onboarding`이 담당합니다.

| ID             | P   | 사전조건                                                 | 절차                                  | 기대 결과                                                                                                                                                                                                                              | 자동화                                   | 근거                                                      |
| ------------- | -- | ------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------- |
| ONBD-GUEST-01 | P0 | 게스트, 로컬 데이터 없음(첫 방문) | `/`·`/chats`·`/studio`·`/my` 각각 진입 | `/onboarding`으로 이동(주소 교체). 두 줄 제목 "눈을 떠보니" / "스토리 속 주인공이 되었다" 표시. 맨 위에서는 헤더가 보이지 않고 첫 화면 이미지 카드가 화면 꼭대기부터 보임. 첫 화면을 지나 내려가면 로고만 있는 헤더가 완전히 보이며 이동 버튼과 하단 고정 CTA는 없음(KNK-1185, KNK-1644) | ✅ e2e `smoke/onboarding` | US-2-5, FE-SCREEN-007 |
| ONBD-GUEST-02 | P1 | ONBD-GUEST-01 | 본문 구성 확인 | 첫 화면은 본문 스크롤 영역 한 화면을 사방 여백을 두고 채우는 둥근 이미지 카드이며, 이미지 아래쪽에 두 줄 제목과 설명 "키워드로 만든 스토리를 채팅으로 직접 이어가요"가 보임. 그 아래 기능 소개 5개(장르 키워드를 흩어 놓은 스토리 만들기, 스토리라인과 이미지 스타일, 스토리 완성, 채팅, 오리지널 스토리)가 제목, 카드 갤러리(각 3장), 섹션 버튼으로 이어지고, 서비스 정보 푸터가 뒤따름. 카드는 둥근 회색 박스 안에 스크린샷 일부를 잘라 넣고 아래에 제목과 설명을 붙임. 문구는 FE-SCREEN-007을 따르며 입력 방식 변경과 채팅 공유 소개는 없음. 배경은 단색이고 장식용 그라데이션이 없음. 게스트 한도와 로그인 혜택 안내 카드는 없음(게스트 한도 안내는 서비스 안내 화면 MY-INFO와 생성, 채팅 화면의 이프 팝오버가 담당) | ✅ e2e `smoke/onboarding`(카드 순서, 화면), `visual/onboarding-visual`(첫 화면) | FE-SCREEN-007, 구현(`onboarding-hero`, `onboarding-feature`), KNK-1004, KNK-1644 |
| ONBD-GUEST-15 | P1 | 온보딩 페이지 표시됨 | 첫 화면부터 천천히 스크롤했다가 다시 위로 스크롤 | 첫 화면 카드가 스크롤에 맞춰 화면 가득 넓어진 뒤 지나감. 기능 소개 제목이 지나가면 갤러리가 본문 스크롤 영역에 붙고, 스크롤을 따라 섹션별 전환으로 다음 카드가 가운데에 옴. 스토리 만들기와 스토리 완성은 옆으로 흐르고(양옆 카드 가장자리 보임), 스토리라인과 이미지 스타일과 오리지널 스토리는 앞 카드가 비스듬히 날아가며 뒤 카드가 나오고(뒤 카드가 위로 살짝 겹쳐 보이고, 스토리라인과 이미지 스타일은 왼쪽, 오른쪽 순, 오리지널 스토리는 오른쪽, 왼쪽 순으로 빠짐), 채팅은 다음 카드가 아래에서 올라와 덮으며 지나간 카드가 위로 쌓임. 겹치는 전환에서 캡션이 겹쳐 비치지 않음. 카드 사이를 지날 때 말고는 한 장이 가운데에 멈춰 있고, 아래 점이 지금 카드를 표시함. 위로 스크롤하면 반대로 움직임 | ◐ e2e `smoke/onboarding`(카드별 가운데 위치, 이미지). 전환 모습은 수동 | FE-SCREEN-007, 구현(`onboarding-hero`, `onboarding-feature`, `onboarding-gallery`), KNK-1644 |
| ONBD-GUEST-16 | P1 | OS 모션 감소(prefers-reduced-motion) 설정 | 온보딩 페이지 진입과 스크롤 | 첫 화면 이미지가 첫 장에 고정되고, 첫 화면과 섹션 등장이 이동 없이 투명도만 바뀜. 스크롤 신호는 움직이지 않고, 누르면 즉시 첫 기능 소개로 이동함. 갤러리는 스크롤을 직접 따라 움직임 | 수동 | FE-SCREEN-007, 구현(`onboarding-hero`, `onboarding-feature`) |
| ONBD-GUEST-17 | P2 | 온보딩 페이지 진입 직후 | 첫 화면 관찰 후 스크롤 | 이미지 카드가 나타난 뒤 로고 → 제목 첫 줄 → 둘째 줄 → 설명 → 스크롤 신호 순으로 약 2초에 걸쳐 미세한 블러가 걷히며 아래에서 떠오름. 이미지는 4초마다 1.2초에 걸쳐 다음 장으로 바뀌며 전환 중 밝기가 출렁이지 않음. 기능 소개 제목은 화면에 들어올 때 한 번 떠오르고, 스토리 만들기 소개의 장르 키워드가 제목보다 먼저 흩어지며 나타남 | 수동 | FE-SCREEN-007, 구현(`onboarding-screen`, `onboarding-hero`, `onboarding-feature`), KNK-1004, KNK-1644 |
| ONBD-GUEST-04 | P0 | 온보딩 페이지 표시됨 | 스토리 만들기, 스토리라인과 이미지 스타일, 스토리 완성 섹션 아래 버튼을 각각 탭 | `manyak:onboarding-seen`에 `'1'` 저장 + `/studio/story/simple`로 주소 교체 이동. 뒤로가기로 온보딩에 돌아오지 않음. 분석 `source=section`과 `section` 값(`create`, `storyline`, `complete`). 게스트도 동의 시트 없이 키워드 단계가 열림 | ✅ e2e `smoke/onboarding`(스토리 만들기 섹션 버튼) | US-2-5, FE-SCREEN-007, KNK-1185, KNK-1644 |
| ONBD-GUEST-11 | P0 | 온보딩 페이지 표시됨                              | 채팅과 오리지널 스토리 섹션 아래 버튼을 각각 탭                                             | 홈(`/`)으로 주소 교체 이동. `manyak:onboarding-seen`에 `'1'` 저장되어 새로고침·재진입에도 온보딩으로 이동하지 않음. 분석 `source=section`과 `section` 값(`chat`, `originals`). 로고 탭은 홈으로 가지 않고 본문을 맨 위로 되돌림(KNK-1185, 기존 로고 홈 이동 대체)                                                                                                                                       | ✅ e2e `smoke/onboarding`           | FE-SCREEN-007, 구현(`onboarding-screen`), KNK-1185 |
| ONBD-GUEST-12 | P0 | ONBD-GUEST-04로 `/studio/story/simple` 진입, 키워드 스텝 | 브라우저·기기 뒤로가기 또는 헤더 뒤로가기                       | 사이트를 벗어나지 않고 제작(`/studio`)으로 이동. 퍼널 뒤로가기는 진입 경로와 관계없이 제작 화면으로 대체 이동한다                                                                                                                                                                                                    | ✅ e2e `smoke/onboarding`           | 구현(`use-story-create-funnel`), KNK-988 |
| ONBD-GUEST-13 | P1 | `manyak:onboarding-seen = '1'`                    | `/onboarding` 직접 접근                                         | 온보딩 내용을 보여주지 않고 홈(`/`)으로 되돌림                                                                                                                                                                                                                                                                       | ✅ e2e `smoke/onboarding`           | 구현(`onboarding-screen`)                |
| ONBD-GUEST-05 | P0 | `manyak:onboarding-seen = '1'`                    | `/` 재진입                                                      | 온보딩으로 이동하지 않고 홈이 바로 표시됨                                                                                                                                                                                                                                                                            | ✅ e2e `smoke/onboarding`           | US-8-3, FE-SCREEN-007                    |
| ONBD-GUEST-06 | P1 | 온보딩 미열람 + 로컬 스토리 또는 채팅 ID 1개 이상 | `/` 진입 | 온보딩을 노출하지 않음. 열람 쿠키가 없으면 서버가 일단 온보딩으로 보내지만 가드가 쿠키를 심고 원래 목적지로 즉시 되돌리며, 이후 방문부터는 리다이렉트 없음 | ✅ e2e `smoke/onboarding` | FE-SCREEN-007 진입 조건 |
| ONBD-GUEST-07 | P2 | 첫 방문 | 첫 응답 관찰 | 홈이 그려지지 않고 서버 리다이렉트로 온보딩이 바로 표시됨(깜빡임 없음) | ✅ e2e `smoke/onboarding`(응답 URL) | FE-SCREEN-007 진입 조건 |
| ONBD-GUEST-08 | P1 | 회원 로그인 상태, 서버 데이터 없음 | `/` 진입 | 게스트 온보딩으로 이동하지 않음(비로그인 세션에서만 노출) | ◐ e2e `my/invite`(pending 회원만) | FE-SCREEN-007 노출 조건 |
| ONBD-GUEST-09 | P2 | 첫 방문 조건 충족 | `/studio/story/simple`·`/chats/{id}`·`/login`·`/terms` 등으로 직접 진입 | 온보딩으로 이동하지 않음. 프록시 매처가 메인 4탭(`/`·`/chats`·`/studio`·`/my`)만 대상 — 그 외 경로는 게이팅 없음 | 수동 | [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸), 구현(`proxy`) |
| ONBD-GUEST-10 | P2 | 프라이빗 모드 등 쿠키·localStorage 차단 환경           | 첫 진입 → CTA → 재진입                                          | 저장 실패는 조용히 무시되어 매 진입마다 온보딩으로 다시 이동할 수 있음(쿠키만 차단이면 가드가 열람 상태를 보고 목적지로 되돌림, ⚠️2)                                                                                                                                                                                                      | 수동                                | 구현(`onboarding-storage`)               |
| ONBD-GUEST-20 | P1 | 첫 방문 조건 충족 | `/?utm_source=th&utm_medium=social&utm_campaign=organic&utm_content=bio`로 진입 | 리다이렉트된 `/onboarding` URL에 원본 쿼리(UTM 4개)와 `from=/`가 모두 유지됨. 화이트리스트가 아닌 전체 쿼리 전달이므로 임의 파라미터도 동일하게 보존 | ✅ e2e `smoke/onboarding` | FE-SCREEN-007 진입 조건, KNK-695 |
| ONBD-GUEST-21 | P1 | 쿠키·로컬 데이터 없음 | 검색 크롤러 User-Agent(예: Googlebot, Search Console URL 검사 도구 `Google-InspectionTool`)로 `/` 요청 | 온보딩으로 리다이렉트되지 않고 홈이 200으로 응답됨. 메인 4탭 모두 동일. 인앱브라우저(카카오톡·다음 앱·네이버 앱) UA는 크롤러로 판정되지 않고 기존대로 온보딩으로 이동 | ✅ e2e `seo/crawler-indexing` | KNK-699·988·1461, 구현(`search-crawler`·`proxy`) |
| ONBD-GUEST-22 | P2 | 온보딩 페이지 표시됨 | 하단 영역 확인 | 하단 고정 액션 영역·스크롤 하단 페이드 없음(랜딩 끝이 푸터라 경계 페이드가 불필요, KNK-1185) | ✅ e2e `smoke/onboarding`·`visual/onboarding-visual` | [웹 레이아웃](../design/1-1-web-design.md#레이아웃-구조), KNK-1185 |
| ONBD-GUEST-23 | P1 | 온보딩 페이지 표시됨 | 본문을 끝까지 스크롤 | 기능 소개마다 갤러리 아래에 섹션 버튼(스토리 만들기, 스토리라인과 이미지 스타일, 스토리 완성은 프라이머리 톤, 채팅과 오리지널 스토리는 회색 톤, 오른쪽 끝 원 안 화살표)이 갤러리와 함께 붙어 있음. 오리지널 스토리 갤러리 뒤에는 별도 시작 섹션 없이 푸터(로고, 서비스 한 줄 소개, 서비스 안내/이용약관/개인정보 처리방침 새 탭 링크, 문의 이메일 `mailto`, 인스타그램 새 탭 링크, `© {연도} 김앤강`, Google Play 상표 고지)가 이어짐. 서비스 한 줄 소개 아래에 한국어 Google Play 공식 배지가 있고, 누르면 Play 스토어 앱 페이지가 새 탭으로 열리며 온보딩은 그대로임. 첫 화면을 지난 뒤로 헤더(로고)가 계속 보이고, 로고를 탭하면 본문이 맨 위로 부드럽게 되돌아감(모션 감소 시 즉시) | ✅ e2e `smoke/onboarding`(섹션 버튼, 시작 섹션 없음, 푸터 링크 href, Google Play 배지 href, 로고 맨 위로) | FE-SCREEN-007, KNK-1185, KNK-1644 |
| ONBD-GUEST-25 | P1 | 온보딩 미열람, 저장한 테마와 시스템 테마가 서로 다름 | 라이트, 다크 각각 기능 소개 갤러리를 처음부터 끝까지 스크롤 | FE-SCREEN-007의 테마 규칙에 따라 카드마다 저장한 테마의 스크린샷만 접근 가능하며 15장 모두 정상 로딩됨. 첫 화면 이미지는 두 테마에서 같음 | ✅ e2e `smoke/onboarding`(실제 WebP 원본으로 테마와 자산 로딩 검증, 이미지 최적화는 검증 제외) | [웹 온보딩](../spec/3-2-web-spec.md#fe-screen-007-온보딩-페이지) |
| ONBD-GUEST-26 | P1 | 온보딩 미열람, 테마 설정은 시스템 | 시스템 테마를 라이트 → 다크 → 라이트로 변경 | FE-SCREEN-007의 테마 규칙에 따라 새로고침 없이 해당 테마 스크린샷으로 전환됨 | ✅ e2e `smoke/onboarding` | [웹 온보딩](../spec/3-2-web-spec.md#fe-screen-007-온보딩-페이지) |
| ONBD-GUEST-28 | P2 | 화면 높이가 낮은 기기(예: iPhone SE) 또는 상단 앱 안내 배너 표시 | 첫 화면과 갤러리 확인 | 첫 화면 카드와 갤러리가 본문 스크롤 영역 높이에 맞음. 카드와 그 아래 제목, 설명, 점이 잘리거나 겹치지 않음 | 수동 | FE-SCREEN-007, 구현(`onboarding-feature`), KNK-1644 |
| ONBD-GUEST-29 | P1 | 온보딩 페이지 표시됨 | 맨 위에서 천천히 스크롤해 첫 화면을 지났다가 다시 맨 위로 | 맨 위에서는 헤더가 보이지 않고 로고도 누를 수 없음. 내려갈수록 헤더가 점점 진해지고, 첫 화면 이미지 아래쪽 끝이 헤더에 닿을 즈음 완전히 보이며 이후 갤러리 구간에서도 유지됨. 갤러리 카드와 버튼이 헤더에 가려지지 않음. 맨 위로 돌아오면 다시 사라짐 | ◐ e2e `smoke/onboarding`(맨 위 숨김, 첫 화면 이후 표시). 점점 나타나는 모습은 수동 | FE-SCREEN-007, 구현(`onboarding-header`), KNK-1644 |
| ONBD-GUEST-30 | P2 | 온보딩 페이지 표시됨 | 맨 위에서 첫 화면 아래쪽을 지켜본 뒤 스크롤 신호를 탭. 다시 맨 위로 돌아와 손으로 조금 스크롤 | 첫 화면 카드 아래쪽 가운데에 아래 방향 꺾쇠 하나가 설명 다음에 나타나, 약 2초 간격으로 천천히 아래로 내려갔다 옅어지며 돌아옴. 제목과 설명은 왼쪽 정렬을 유지하고 꺾쇠와 겹치지 않음. 탭하면 첫 기능 소개(스토리 만들기)가 시작되는 위치까지 부드럽게 스크롤되며 주소와 열람 상태는 그대로임. 스크롤을 시작하면 꺾쇠가 바로 사라지고 맨 위로 돌아오면 다시 보임 | ◐ e2e `smoke/onboarding`(탭하면 첫 기능 소개까지 이동, 이동 후 숨김). 움직임은 수동 | FE-SCREEN-007, 구현(`onboarding-hero`) |

## ONBD-INVITE — 신규 가입(회원) 초대 코드 온보딩

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID             | P   | 사전조건                                                 | 절차                                  | 기대 결과                                                                                                                                                                                                                              | 자동화                                   | 근거                                                      |
| -------------- | --- | -------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| ONBD-INVITE-01 | P0  | 신규 가입 회원(`inviteOnboardingPending: true`)          | 첫 화면 진입                          | 모달 바텀 시트 표시: 제목 "초대 코드를 등록하면" / "N 이프를 받을 수 있어요"(N은 `GET /credits/policies`의 `inviteReward`), 설명 "지금은 건너뛰고 나중에 등록해도 돼요", 초대 코드 입력 + 세로 버튼 두 개("등록하기" 주 스타일, "닫기" 고스트 스타일, 웹은 xs·내용 너비·가운데 정렬, 등록 버튼과 8px 간격). 제목·설명 8px, 설명·폼 32px 간격. 닫기(X) 버튼 없음. 초점은 입력란이 아니라 시트에 있어 모바일 키보드가 자동으로 올라오지 않음. 게스트 온보딩과 동시 표시되지 않음 | ✅ e2e `my/invite` · visual `onboarding-visual` | FE-SCREEN-008, §3-1-7 이프 정책 수치 표시, 구현(`invite-onboarding-sheet`), KNK-1045·1095 |
| ONBD-INVITE-02 | P0  | ONBD-INVITE-01                                           | 배경 탭 또는 ESC 입력                 | 세션 플래그 소비(`inviteOnboardingPending: false` 저장) 후 닫힘. 새로고침·재방문에도 다시 뜨지 않음(단 ONBD-INVITE-05 재시도 화면에서는 닫기 재시도로 동작)                                                                             | ✅ e2e `my/invite`                       | FE-SCREEN-008, 구현(`invite-onboarding-sheet`)            |
| ONBD-INVITE-03 | P1  | 세션 갱신 API가 5xx로 실패                               | 배경 탭 또는 ESC 입력                 | 바텀 시트 유지 + "창을 닫지 못했어요" 토스트. 새로고침 시 다시 표시(플래그 미소비)                                                                                                                                                    | ✅ e2e `my/invite`                       | 구현(`invite-onboarding-sheet`)                           |
| ONBD-INVITE-04 | P0  | ONBD-INVITE-01                                           | 유효한 코드 입력 → "등록하기"         | "친구 초대 보상으로 N 이프를 받았어요" 토스트 + 바텀 시트 닫힘. 새로고침 후에도 다시 열리지 않음                                                                                                                                 | ✅ e2e `my/invite`                       | FE-SCREEN-008                                             |
| ONBD-INVITE-05 | P1  | 코드 적립 성공 + 세션 저장 실패                          | 등록 완료 관찰                        | 코드를 다시 청구하지 않고 입력 폼 대신 "N 이프는 정상 지급되었지만, 창을 닫는 데 실패했어요" 안내 + "닫기"(재시도) 버튼 표시(웹 xs·내용 너비·가운데 정렬)                                                                                                       | ✅ e2e `my/invite`                       | 구현(`invite-onboarding-sheet`)                           |
| ONBD-INVITE-06 | P1  | 게스트 온보딩 조건을 만족하는 상태                       | 로그인 등으로 세션이 인증 상태로 전환 | 온보딩 페이지로 이동하지 않고 홈에 머무르며 초대 코드 바텀 시트만 1개 표시됨                                                                                                                                                          | ✅ e2e `my/invite`                       | 구현(`onboarding-redirect`·`invite-onboarding-sheet`)     |
| ONBD-INVITE-07 | P2  | 등록 또는 닫기 처리 진행 중                              | 버튼·입력 상태 확인                   | 입력창과 "닫기"·"등록하기" 버튼이 모두 잠기고, 등록 버튼은 크기를 유지한 중앙 스피너 표시. 적립 후 저장 재시도 화면(ONBD-INVITE-05)의 "닫기" 버튼도 재시도 중 같은 방식의 스피너로 전환                                                                                                                                              | ◐ e2e `my/invite`(적립 후 저장 대기만)   | FE-SCREEN-008 등록 중 상태                                |
| ONBD-INVITE-08 | P2  | ONBD-INVITE-01, 잘못된 코드(예: 내 코드, 서버 모킹 필요) | 코드 입력 → "등록하기"                | 바텀 시트 유지 + `/my/invite`와 동일한 사유별 인라인 오류(`aria-invalid`·`role=alert`). 보상 미지급                                                                                                                                   | ✅ e2e `my/invite`                       | FE-SCREEN-008 코드 입력, 구현(`invite-onboarding-sheet`)  |
| ONBD-INVITE-09 | P0  | ONBD-INVITE-01                                           | "닫기" 탭                            | 배경 탭·ESC와 동일하게 세션 플래그 소비(`inviteOnboardingPending: false` 저장) 후 닫힘. 새로고침·재방문에도 다시 뜨지 않음. 코드 입력 자격(계정당 1회)은 남아 이후 `/my/invite`에서 등록 가능. 저장이 5xx로 실패하면 ONBD-INVITE-03과 동일하게 유지 + "창을 닫지 못했어요" 토스트 | ✅ e2e `my/invite`                       | FE-SCREEN-008, KNK-1045                                   |

## ONBD-BANNER — 앱 안내 배너

기준: [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너). Android 앱 진입은 앱 버전(KNK-1632 반영 여부)에 따라 다르므로 실기기 케이스에 앱 버전을 함께 기록합니다.

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| ONBD-BANNER-01 | P0 | Android Chrome, 첫 접속 | 홈 진입 | 헤더 위에 Android 배너(문구, 앱 열기, 닫기) 표시 | ✅ e2e `smoke/app-banner` | [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너) |
| ONBD-BANNER-02 | P1 | Android Chrome | 새 탭으로 2, 3, 4번째 접속 | 2, 4번째는 미노출, 3번째는 노출 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-03 | P0 | Android 카카오톡 인앱 | 접속할 때마다 진입 | 매 접속 Android 배너 표시 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-04 | P0 | Android, KNK-1632 반영 앱 설치 | 스토리 상세에서 앱 열기 | 앱이 열리고 같은 스토리 상세로 진입 | ◐ e2e `smoke/app-banner`(링크 주소만) | 같음, KNK-1632 |
| ONBD-BANNER-05 | P0 | Android, 앱 미설치 | 앱 열기 | 플레이스토어 앱의 마냑 페이지가 열림. 인앱 브라우저에서도 Play 웹페이지가 아니라 플레이스토어 앱으로 이동 | 수동 | 같음 |
| ONBD-BANNER-06 | P1 | Android, 앱 설치 | 스토리 상세가 아닌 화면에서 앱 열기 | 앱 홈이 열림 | ◐ e2e `smoke/app-banner`(링크 주소만) | 같음 |
| ONBD-BANNER-07 | P0 | iOS 카카오톡, 인스타그램 인앱 | 열기 | 외부 브라우저에서 같은 화면이 열림 | 수동 | 같음 |
| ONBD-BANNER-08 | P1 | iOS 인앱, 외부 전환이 막힌 앱 | 열기 후 1.5초 대기 | 외부 브라우저 안내 시트가 열리고 링크 복사하기로 현재 주소가 복사됨 | ✅ e2e `smoke/app-banner`(시트 표시) | 같음 |
| ONBD-BANNER-09 | P1 | iPhone Safari 26 이상, 첫 접속 | 추가하기, 기기 뒤로가기 | 스크린샷 4장 안내 시트가 열리고 뒤로가기로 닫히며 화면은 그대로 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-10 | P1 | iOS, 안내대로 홈 화면에 추가 | 홈 화면 아이콘으로 실행 | 배너가 보이지 않음 | 수동 | 같음 |
| ONBD-BANNER-11 | P1 | Android Chrome, 첫 접속 | 닫기, 같은 탭 새로고침, 새 탭으로 2, 3번째 접속 | 닫은 탭에서는 다시 보이지 않고 3번째 접속에 다시 표시 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-12 | P1 | Android Chrome, 데스크톱 | 서비스 안내, 이용약관, 개인정보 처리방침, 데스크톱 홈 진입 | 배너 미노출. 문서 화면만 본 접속은 세지 않음 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-13 | P2 | 기기 동작 줄이기 설정 | 배너 표시와 닫기 | 높이 애니메이션 없이 표시되고 사라짐 | 수동 | 같음 |
| ONBD-BANNER-14 | P2 | Android Chrome, 홈 목록 스크롤 | 배너 닫기 후 탭 전환 왕복 | 탭별 스크롤 위치 복원이 어긋나지 않음 | 수동 | 같음 |
| ONBD-BANNER-15 | P2 | Android, 앱 미설치 | 앱 열기로 설치 | Play Console 설치 귀속에 `utm_source=manyak_web`, `utm_medium=app_banner`가 남음 | 수동 | 같음 |
| ONBD-BANNER-16 | P1 | iOS Chrome 또는 iOS 18 이하 Safari, 첫 접속 | 추가하기 | 스크린샷 없이 텍스트 2단계와 공유 버튼 안내가 보임 | ✅ e2e `smoke/app-banner`(iOS Chrome) | 같음 |
| ONBD-BANNER-17 | P1 | iPhone Safari 26 실기기 | 안내 시트에서 스크린샷을 좌우로 넘기고 실제로 따라 하기 | 가로 스와이프가 시트 닫기와 겹치지 않고, 안내대로 홈 화면에 추가됨. 스크린샷에서 개인 정보가 보이지 않음 | 수동 | 같음 |
| ONBD-BANNER-18 | P2 | Android Chrome, 배너 표시 | 키보드나 스크린 리더로 닫기 | 배너가 사라지고 포커스가 배너 아래 화면으로 이동 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-19 | P2 | iOS 인앱 | 열기를 1.5초 안에 여러 번 누르기, 또는 전환된 뒤 1.5초 안에 돌아오기 | 실패 안내 이벤트는 한 번만 나가고, 전환됐다 돌아온 경우에는 실패 안내 시트를 띄우지 않음 | ✅ e2e `smoke/app-banner` | 같음 |

## ⚠️ 확인 필요

이 문서의 자동화 표시는 이번 실행·배포 완료를 뜻하지 않습니다.

통합한 ID(번호 재사용 금지):

- `ONBD-GUEST-14` → ONBD-GUEST-01
- `ONBD-GUEST-24` → ONBD-GUEST-04

폐기한 ID(번호 재사용 금지):

- `ONBD-GUEST-27`: 온보딩 장면 카드 줄의 마우스 드래그. 스크롤 소개로 바뀌며 카드 줄이 사라짐(KNK-1644)

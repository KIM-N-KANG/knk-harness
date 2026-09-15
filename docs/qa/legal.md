# legal

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-09-14 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 약관·개인정보 처리방침의 수동 QA와 E2E 검수 기준을 정의합니다. |
| 화면 | 서비스 이용약관 `/terms` · 개인정보 처리방침 `/privacy`(FE-SCREEN-010, `(legal)` 그룹 — 로고 홈 링크 헤더, 탭 없음) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [`3-1-client-spec.md §3-1-3(FE-SCREEN-010·011)`](../spec/3-1-client-spec.md), [`2-user-stories.md`](../spec/2-user-stories.md) US-9(로그인·회원 전환) |
| 관련 E2E | `manyak-web/e2e/legal/legal.spec.ts`, `manyak-web/e2e/my/service-info.spec.ts`(서비스 안내 진입), `manyak-web/e2e/visual/legal-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [LEGAL-ENTRY — 진입 경로·접근·홈 이동](#legal-entry--진입-경로접근홈-이동)
- [LEGAL-DOC — 콘텐츠 렌더](#legal-doc--콘텐츠-렌더)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

## LEGAL-ENTRY — 진입 경로·접근·홈 이동

기준: [계약·구조](../spec/3-2-web-spec.md#문서-열람과-검색-노출).

| ID           | P   | 사전조건        | 절차                  | 기대 결과                                                                                                                                                                         | 자동화                                            | 근거                         |
| -------------- | --- | ------------------------------------------ | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------ |
| LEGAL-ENTRY-01 | P0 | 게스트 | `/login` 진입 | 중앙 콘텐츠와 분리된 화면 최하단에 "로그인하면 서비스 이용약관과 개인정보 처리방침에 / 동의하는 것으로 간주해요"를 두 줄로 고지 + 밑줄 링크 2개 표시. 별도 동의 체크박스 없음 | ✅ e2e `legal/legal` | US-9-6, FE-SCREEN-008 약관 동의 고지, KNK-1037 |
| LEGAL-ENTRY-02 | P0  | `/login` 표시됨                            | "서비스 이용약관" 링크 탭                                    | 새 브라우저 탭에서 `/terms`가 열리고 원래 `/login` 탭은 유지. 로고 헤더 + 본문 조문 표시                                         | ✅ e2e `legal/legal`            | US-9-6, FE-SCREEN-010 진입점         |
| LEGAL-ENTRY-03 | P0  | `/login` 표시됨                            | "개인정보 처리방침" 링크 탭                                  | 새 브라우저 탭에서 `/privacy`가 열리고 원래 `/login` 탭은 유지. 로고 헤더 + 본문 표시                                             | ✅ e2e `legal/legal`            | FE-SCREEN-010 진입점                 |
| LEGAL-ENTRY-04 | P1  | 게스트(비로그인)                           | `/terms`·`/privacy` URL 직접 진입                             | 라우트 가드 없이 두 페이지 모두 열람 가능                                                                                     | ◐ e2e `legal/legal`(`/terms`만) | FE-SCREEN-010 검수 기준              |
| LEGAL-ENTRY-05 | P1  | 회원 로그인 상태                           | `/terms`·`/privacy` 진입                                      | 게스트와 동일하게 열람 가능(회원/게스트 무관)                                                                                 | 수동                            | FE-SCREEN-010                        |
| LEGAL-ENTRY-06 | P1  | `/terms`·`/privacy` 표시됨                 | 헤더 마냑 로고 탭                                             | 홈(`/`)으로 이동                                                                                                               | ✅ e2e `legal/legal`            | FE-SCREEN-010 검수 기준              |
| LEGAL-ENTRY-08 | P1 | 서비스 안내(`/about`) 표시됨 | "약관 및 정책"의 "서비스 이용약관"·"개인정보 처리방침" 링크 각각 탭 | 각 링크 뒤에 새 창 아이콘이 보이고, 새 브라우저 탭에서 `/terms`·`/privacy`를 각각 열며 원래 `/about` 탭 유지 — 로그인 후에도 접근 가능한 상시 진입점 | ✅ e2e `my/service-info` | FE-SCREEN-011 |

## LEGAL-DOC — 콘텐츠 렌더

기준: [계약·구조](../design/1-1-web-design.md#법적-콘텐츠-소스-웹).

| ID           | P   | 사전조건        | 절차                  | 기대 결과                                                                                                                                                                         | 자동화                                            | 근거                         |
| ------------ | --- | --------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ---------------------------- |
| LEGAL-DOC-01 | P1  | `/terms` 진입   | 본문 확인·세로 스크롤 | 제1조(목적)~제16조(문의처)·부칙까지 조문 섹션이 순서대로 렌더. 개인 운영 주체, 만 14세 이상 이용 조건, Google·Kakao 계정, 게스트 이관, 이프, 공개·공유, AI 평가 데이터 조건을 포함하고 끝까지 스크롤 가능 | ◐ e2e `legal/legal`·`visual/legal-visual`(상단만) · unit `tests/features/legal/content.test.ts` | FE-SCREEN-010 화면 구성      |
| LEGAL-DOC-02 | P1  | `/privacy` 진입 | 본문 확인·세로 스크롤 | 도입 문단 + "1. 개인정보처리자와 적용 범위"~"18. 개인정보 처리방침의 변경"·부칙 섹션 렌더. 웹·Android 실제 처리 항목, 보유기간, 위탁·국외 이전, 권리 행사, 보호책임자·이메일 포함 | ◐ e2e `legal/legal`·`visual/legal-visual`(상단만) · unit `tests/features/legal/content.test.ts` | FE-SCREEN-010 화면 구성      |
| LEGAL-DOC-03 | P1 | 두 페이지 각각 | 본문 최상단 확인 | 본문 최상단에 문서 제목(h1) + "시행일 {날짜} · {버전}" 표기. 값은 `terms-content.ts`·`privacy-content.ts` 정본과 일치 | ✅ e2e `legal/legal` | FE-SCREEN-010 검수 기준 |
| LEGAL-DOC-04 | P2 | 두 페이지 각각 | 헤더 구성 확인 | 홈과 같은 크기의 마냑 로고 링크만 표시하고 접근 가능한 이름은 "홈으로 이동". 뒤로가기·헤더 문서 제목·하단 탭 없음 | ✅ e2e `legal/legal`·`visual/legal-visual` | FE-SCREEN-010, [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸) |
| LEGAL-DOC-05 | P1  | `/privacy` 진입 | 행태정보 고지 확인    | "12. 행태정보의 수집 및 맞춤형 광고" 섹션에 광고 사업자(Meta Platforms, Inc.)·수집 항목(입력 원문 제외)·수집 방법(Meta 픽셀)·목적·보유 기간·이용자 통제 수단 고지. 국외 이전(7)·쿠키(11) 조항에도 Meta 반영 | ✅ e2e `legal/legal`(섹션 렌더) · unit `tests/features/legal/content.test.ts`(문구 계약) | KNK-616 Meta 픽셀 사전 고지  |
| LEGAL-DOC-06 | P1 | `/privacy` 진입 | AI 처리·평가 고지 확인 | "13. AI 처리와 평가 데이터 활용" 섹션에 생성 처리(OpenAI·DeepSeek), Langfuse 일본 리전 원문 저장, 품질 점검·평가 데이터·평가 지표 활용, 1년 보유, 자체 AI 모델 비학습, 제공자별 훈련 조건(OpenAI 기본 비학습·DeepSeek 정책상 가능), 평가 제외·삭제 요청 수단 고지 | ✅ e2e `legal/legal`(섹션 렌더) · unit `tests/features/legal/content.test.ts`(문구 계약) | 처리방침 콘텐츠 정본, `6-analytics.md` §6-7 |
| LEGAL-DOC-07 | P2  | 두 페이지 각각  | 브라우저 탭 제목 확인 | `서비스 이용약관 - 마냑`·`개인정보 처리방침 - 마냑`(읽기 쉬운 띄어쓰기를 적용한 탭 제목 + 서비스명, 정본 `src/features/legal/constants.ts`, [§3-2-4](../spec/3-2-web-spec.md))                    | ✅ e2e `legal/legal`                              | 구현(`terms`·`privacy` page), KNK-713·KNK-1037 |
| LEGAL-DOC-08 | P1  | 두 페이지 각각  | 이용 연령 조항 확인 | 약관 제3조와 처리방침 제14항이 서비스를 만 14세 이상으로 제한하고, 만 14세 미만 이용 사실을 알게 된 경우 이용 중지·삭제 절차를 안내 | ✅ unit `tests/features/legal/content.test.ts` | 2026-08-29 사용자 정책 결정 |
| LEGAL-DOC-09 | P1 | `/privacy` 진입 | 보유·위탁·국외 이전 확인 | 삭제된 회원·스토리·채팅, 피드백, Langfuse 원문의 1년 보유와 OpenSearch 14일·CloudWatch 30일·백업 최대 7일을 구분하고 AWS·Vercel·Cloudflare·AI·분석·오류·피드백 수탁자 및 국외 이전 항목을 표시 | ✅ unit `tests/features/legal/content.test.ts` | 처리방침 콘텐츠 정본, 각 레포 구현 |

## ⚠️ 확인 필요

이 문서의 자동화 표시는 이번 실행·배포 완료를 뜻하지 않습니다.

통합한 ID(번호 재사용 금지):

- `LEGAL-ENTRY-07` → LEGAL-DOC-04

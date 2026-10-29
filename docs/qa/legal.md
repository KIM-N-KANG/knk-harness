# legal

이 문서의 케이스는 [ACCOUNT 웹 검증](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md)으로 옮겼다. 아래 절은 기존 링크의 진입점이다.

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-10-22 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 약관·개인정보 처리방침의 수동 QA와 E2E 검수 기준을 정의합니다. |
| 화면 | 서비스 이용약관 `/terms` · 개인정보 처리방침 `/privacy`(FE-SCREEN-010, `(legal)` 그룹 — 링크 없는 로고 헤더, 탭 없음) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [`3-1-client-spec.md §3-1-3(FE-SCREEN-010·011)`](../spec/3-1-client-spec.md), [`2-user-stories.md`](../spec/2-user-stories.md) US-9(로그인·회원 전환) |
| 관련 E2E | `manyak-web/e2e/legal/legal.spec.ts`, `manyak-web/e2e/my/service-info.spec.ts`(서비스 안내 진입), `manyak-web/e2e/visual/legal-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [LEGAL-ENTRY — 진입 경로·접근](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-11-legal-entry-진입-경로-접근)
- [LEGAL-DOC — 콘텐츠 렌더](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-12-legal-doc-콘텐츠-렌더)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

## LEGAL-ENTRY — 진입 경로·접근

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-11 LEGAL-ENTRY: 진입 경로, 접근](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-11-legal-entry-진입-경로-접근))

## LEGAL-DOC — 콘텐츠 렌더

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-12 LEGAL-DOC: 콘텐츠 렌더](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-12-legal-doc-콘텐츠-렌더))

## ⚠️ 확인 필요


ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-20 법적 문서 공개 검증](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-20-법적-문서-공개-검증))

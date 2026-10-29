# PAYMENT 공통 결정 기록

확정된 결정의 ID, 당시 상태와 본문을 보존한다. 현재 계약은 번호 문서에서 확인한다.

현재 앱 결제 제외 범위는 백엔드의 16번 결정에 근거한다. ([PAYMENT 백엔드 결정](../BACKEND/DECISIONS.md))

<br>

<a id="c-003"></a>

## C-003. 이프 수치는 서버 정책에서 표시

- 결정일: 2026-09-01 · 기록 확정 상태: Accepted
- 근거: [이관 원문 C:696](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-1-client.md#L696-L706), [이관 원문 C:1213](https://github.com/KIM-N-KANG/knk-harness/blob/2d77abce078b75e168d8f924e3759e3bb624515a/docs/product-specs/3-1-client.md#L1213-L1223)
- **맥락:** 화면에 복제한 이프 수치가 운영 정책 변경과 어긋날 수 있었습니다.
- **결정:** 사용 지점은 서버 정책값을 표시하고 서비스 안내에는 이프 적립·소모 수치를 모아 두지 않습니다.
- **이유:** 서버와 여러 화면에 같은 수치를 수동 관리하지 않기 위해서입니다.
- **주요 영향:** 조회 전·실패 시 확정된 기본값 대신 자리표시를 사용합니다.

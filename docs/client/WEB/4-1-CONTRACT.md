# 4-1 웹 공용 연동

기준: [공통 연동](../4-1-CONTRACT.md), [웹 표현](3-3-LAYOUT.md).

<br>

### 4-1-1 생성과 전송

백엔드 API_BASE_URL과 Orval의 OpenAPI 환경은 같은 대상을 사용한다. 스키마는 /v3/api-docs를 기준으로 하며 중복 operationId만 메서드와 경로로 안정화한다. /api/v1을 제외하고 경로 변수는 By 이름으로 구분하며 유일한 기존 ID는 유지한다. 성공 응답 타입은 2xx, 오류는 상태를 포함하는 FetchError로 취급한다.

브라우저는 같은 출처 BFF로 요청하고 인증 전달 및 타임아웃은 [ACCOUNT 연동](../../domain/ACCOUNT/CLIENT/WEB/4-1-CONTRACT.md)을 따른다.

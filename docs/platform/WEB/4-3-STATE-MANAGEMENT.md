# 4-3 상태 관리: 웹

기준: [구성](4-2-COMPONENT-ARCHITECTURE.md).

<br>

### 4-3-1 공통 상태 수명

| 상태 | 저장과 복원 |
|---|---|
| 서버 조회 | Query 기본 retry=false, staleTime=60초, refetchOnWindowFocus=false, throwOnError=false. 개별 계약의 명시적 예외만 적용 |
| 이미지 뷰어 | 열린 URL과 제스처 상태. 도메인 화면이 대상 소유, 확대와 이동은 뷰어 수명 |

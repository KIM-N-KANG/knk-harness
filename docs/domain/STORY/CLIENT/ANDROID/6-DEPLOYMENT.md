# 6 배포: 안드로이드

<br>

### 6-1 저장 호환

| 전환 | 보존 |
|---|---|
| Room v1에서 v2 | 레거시 완성 요청을 pending으로 옮기고 해석하지 못한 원문 보존 |
| v2에서 v3 | 빈 ownerId는 다음 회원 세션에 귀속 |
| v3에서 v4 | 편집 테이블 기본 키 변경. 이전 초안은 legacy-ID와 빈 createdAt으로 이관 |
| 일반 제작 테이블 | v5 구조 유지. 서버 이관 전 초안과 접수 연결 행만 남김 |
| v5에서 v6 | pending과 completion에 nullable serverDraftVersion 추가. 이전 행은 기기 세션 |
| 서버 초안 | schemaVersion 1과 두 플랫폼 payload 호환. 다른 mode 또는 버전은 불러오기 실패 |

Destructive migration을 사용하지 않는다. [검증](5-1-VERIFICATION.md)에서 이전 초안과 접수 연결, 계정 격리와 구성 변경을 확인한다. 실행 환경과 결과는 PR 및 CI에 남긴다.

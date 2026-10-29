# 6 웹 STORY 배포

<br>

### 6-1 호환 조건

| 대상 | 조건 |
|---|---|
| 이미지 업로드 | presign의 Content-Type과 버킷 CORS origin을 맞춘다. 운영 upload_cors_allowed_origins는 manyak.app |
| 제작 저장소 | 이전 localStorage와 IndexedDB 기록을 성공 확인 전에 삭제하지 않는다. 복구 requestId, 최초 저장 시각과 서버 초안 연결을 유지 |
| 서버 초안 | schemaVersion 1의 두 플랫폼 호환을 확인한다. 지원하지 않는 버전은 읽기 실패로 처리 |
| 공개 렌더 | 오리지널 목록 캐시는 최대 60초 늦을 수 있으므로 상세의 현재 PUBLIC과 PUBLISHED를 다시 확인 |
| 검증 | [웹 검증](5-1-VERIFICATION.md)의 저장, 복구, 수정과 검색 노출을 확인하고 실행 환경과 결과는 PR 및 CI에 남긴다 |

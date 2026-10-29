# Android MODERATION 검증

기준: [공통 검증](../VERIFICATION.md), [상태 관리](STATE-MANAGEMENT.md).

<br>

### 시나리오

| ID | 유저 스토리 | 절차 | 기대 결과 | 수단 |
|---|---|---|---|---|
| MODERATION-ANDROID-01 | MODERATION-US-001 | 상세와 제작 및 채팅 메뉴에서 신고 진입 | 앞 옵션 닫힘, 참조 storyId 일치, 삭제된 대상 진입 없음 | 기기와 API 요청 확인 |
| MODERATION-ANDROID-02 | MODERATION-US-001 | 사유와 상세 입력 후 회전, 500자 초과 | 선택과 입력 유지, 상한 적용, TalkBack 선택 상태 전달 | 기기 |
| MODERATION-ANDROID-03 | MODERATION-US-001 | 느린 요청 중 연타와 닫기, 실패 뒤 재전송 | 요청 중복 방지와 잠금, 실패 입력 보존 | 컨트롤러 검증과 기기 |
| MODERATION-ANDROID-04 | MODERATION-US-001 | 201 접수, 닫은 뒤 다시 열기, 공백 상세 전송 | 성공 토스트와 닫기, 새 입력, detail null | 기기와 API 요청 확인 |

시나리오 정의는 테스트 실행이나 자동화 완료가 아니다. 실제 결과는 PR과 CI에 남긴다.

# 5-1 검증: iOS

기준: [공통 검증](../5-1-VERIFICATION.md), [상태 관리](4-3-STATE-MANAGEMENT.md).

<br>

### 5-1-1 시나리오

| ID | 유저 스토리 | 절차 | 기대 결과 | 수단 |
|---|---|---|---|---|
| MODERATION-IOS-01 | MODERATION-US-001 | 스토리 상세 옵션, 제작 카드 옵션, 채팅 목록 카드 옵션과 채팅방 메뉴에서 신고 진입. 삭제된 참조 스토리 | 앞 시트가 닫힌 뒤 신고 시트, 참조 storyId와 `source` 일치, 삭제된 대상 진입 없음 | 시뮬레이터와 API 요청 확인 |
| MODERATION-IOS-02 | MODERATION-US-001 | 사유 선택과 상세 입력, 이모지가 섞인 500 단위 경계 입력과 붙여넣기, 경계에서 한글 조합, VoiceOver | UTF-16 500 상한과 글자 미분할, 조합 유지, 글자 수 표시 일치, 선택 상태와 전송 중 비활성 상태 낭독 | Store 테스트와 시뮬레이터 |
| MODERATION-IOS-03 | MODERATION-US-001 | 느린 요청 중 연타, 끌어내리기, 바깥 탭과 닫기. 실패 뒤 재전송 | 요청 한 번, 시트 잠금과 끌기 표시 유지, 실패 입력 보존과 짧은 토스트 | `URLProtocol` 대역 Store 테스트와 시뮬레이터 |
| MODERATION-IOS-04 | MODERATION-US-001 | 201 접수, 닫은 뒤 다시 열기, 공백과 줄바꿈뿐인 상세 전송 | 짧은 토스트와 닫힘, 새 입력, detail null과 `has_detail` false, 분석에 상세 원문 없음 | 시뮬레이터와 API 요청 확인 |
| MODERATION-IOS-05 | MODERATION-US-001 | 전송 중 앱 열기 링크로 다른 탭 이동, Dynamic Type 최대 접근성 크기에서 키보드 열기 | 시트가 닫히고 결과는 토스트로만 표시, 상세 입력과 신고하기가 키보드에 가리지 않음 | 시뮬레이터 |

시나리오 정의는 테스트 실행이나 자동화 완료가 아니다. 실제 결과는 PR과 CI에 남긴다.

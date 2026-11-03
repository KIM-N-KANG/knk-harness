# 4-3 상태 관리: 안드로이드

<br>

### 4-3-1 소유와 수명

| 상태 | 소유와 수명 |
|---|---|
| 입력, 진행 응답과 잠금 | 채팅방 ViewModel. 구성 변경 유지 |
| 설정 시트와 투어 스텝 | ViewModel. 구성 변경 때 같은 스텝 유지, 도달 이벤트 중복 없음 |
| 입력 수정 편집 | ViewModel의 대상 턴 ID와 고치던 입력. 구성 변경 유지, 기기 저장과 SavedStateHandle 없음. 대상 턴이 목록에 없으면 편집기를 그리지 않음 |
| 턴 확인 창 | ViewModel. 재생성, 입력 수정과 포크 중 하나. 입력 수정은 앞뒤 공백을 뺀 입력과 사라질 턴 수를 함께 보관 |
| 진행 중 숨김 | ViewModel의 대신하는 턴 ID와 입력 수정 여부. 확정, 실패와 정리에서 해제 |
| 포크 요청 | ViewModel 잠금. 원래 방이 스택에 남아 성공해도 이동 효과 뒤 해제 |
| 모델 시트와 헤더 숨김 | 화면 rememberSaveable |
| 메뉴의 이프 내역 | 채팅방 ViewModel. 메뉴 화면이면 없음. 구성 변경 유지, 돌아가기와 시트 닫기에서 비움. 프로세스 재시작 뒤 메뉴부터 |
| 뷰어 URL | 화면 ViewModel. 라우트와 저장 상태에 넣지 않음. 상세에서 이미지가 사라지면 닫기 |
| 이미지, 추천과 입력 모드 | 기기 DataStore의 `chat_realtime_image_enabled`, `chat_choices_enabled`, `chat_input_mode`. UserScopedStore 비참여 |
| 설정 읽기 | 진입 시 한 번 읽고 화면 상태가 기준. 저장 실패가 방금 선택을 되돌리지 않음 |
| 투어 기록 | 기기 DataStore `chat_tour_seen`. 계정 종료에서 유지 |
| 이미지 완료 횟수 | 기기 DataStore `chat_completed_turn_count`. 원자적으로 증가, 3에서 중단. IO 실패는 null |
| 이미지 안내 예약과 표시 | ViewModel Job과 상태. 영속 저장과 SavedStateHandle 없음 |
| 요청 설정 | StreamingTurn에 전송 시점 이미지 설정 보관. 요청과 진행 블록이 같은 값 사용 |
| 모델과 긴 응답 | 서버 상세 기준, 기기 저장 없음 |
| 블럭별 초점 | 컴포지션 수명의 FocusRequester와 현재 초점 |
| 로딩 높이 | rememberSaveable에 측정 높이 보관. 본문이 자랄 때까지 최소 높이 |

모델과 긴 응답 저장 실패는 그 사이 같은 필드를 다시 바꾸지 않았을 때만 이전 값으로 되돌린다. 공통 확정과 진행 상태의 경계를 적용한다. ([공통 4-3](../4-3-STATE-MANAGEMENT.md))

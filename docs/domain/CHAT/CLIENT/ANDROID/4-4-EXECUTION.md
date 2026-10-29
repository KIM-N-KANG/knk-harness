# 4-4 CHAT Android 실행

<br>

### 4-4-1 수신과 복귀

| 단계 | 실행 |
|---|---|
| 전송 계층 | 이어쓰기와 재생성 POST, 이어받기 GET. 연결 열린 뒤 실패는 Interrupted, 열기 전 실패는 상태를 가진 Failed |
| 첫 턴 | 공용 JSON의 null 생략 설정과 별개로 JsonElement를 사용해 lastTurnId null 명시 |
| 생성 추적 | started의 ID와 상세 generatingTurn을 따라 종료 사건까지 수신 |
| 재연결 | 첫 시도 포함 4회, 실패 간격 1초, 2초, 4초. 404, 503, 네트워크와 상세 실패는 다음 차례 |
| 오류 구분 | started 전 시작 거절은 Rejected, 서버 error는 Failed, 결과 불명은 Lost |
| 확정 | Completed, Failed, Rejected, Lost마다 상세 확인. 다른 생성이면 같은 streamJob에서 이어받기 |
| 재진입 | 새 ViewModel의 상세 조회. started마다 처음부터 오는 진행 조각 초기화 |
| 이탈 | viewModelScope 취소로 수신만 정리 |
| 백그라운드 | 구성 변경이 아닌 Activity ON_STOP에서 receiving일 때 streamJob 중단. ON_START에서 상세 확인, 같은 생성도 다시 추적 가능 |
| 목록 | 이어쓰기, 재생성과 재연결의 Completed에 myChatsChanges 신호. 가려진 목록도 조용히 갱신. 실패와 끊김은 ON_START 조회로 확인 |
| 모델 조회 | 진입 시 목록과 상세 조회. 모델 목록 실패가 방 열기를 막지 않으며 다시 시도할 때 재조회 |

<br>

### 4-4-2 안내와 입력

| 작업 | 실행 |
|---|---|
| 투어 판정 | 기기 기록과 0턴 및 생성 여부 검사, 200ms 뒤 재확인. 현재 스텝과 계측은 ViewModel |
| 투어 배치 | boundsInRoot로 대상 좌표 수집, 같은 컴포지션 오버레이. pointerInput과 BackHandler, 뒤 화면 clearAndSetSemantics |
| 이미지 예약 | 정상 이어쓰기 Completed의 원자 증가가 2이고 이미지 꺼짐이면 예약. 입력 잠금 해제 후 500ms 대기 |
| 예약 경합 | 다음 전송과 재생성 시작에 취소, 종료 후 재대기 |
| 이미지 안내 표시 | 시트 onExpanded 뒤 focusable Popup. 행과 팝업 좌표 차이로 하이라이트, 투명 Switch 의미 영역으로 실제 토글 연결 |
| 안내 닫기 | 켜기, 뒤로가기, 딤과 확인은 안내 상태만 종료. 퇴장 모션 뒤 딤과 카드 제거 |
| 초점 | 작성 버튼은 keepKeyboardOnTap. 칸을 비활성화하기 전에 남은 다음 칸 또는 이전 칸에 초점 이동 |
| 헤더 | 자식이 소비하지 않은 탭만 전달. 탭 시작 때 IME가 있으면 전환하지 않음 |

<br>

### 4-4-3 이미지와 앵커

| 구성 | 실행 |
|---|---|
| 허용 경로 | `/characters/generated/`, `/characters/originals/`, `/characters/uploaded/`, `/chat-images/`, `/scenes/originals/` |
| 파서 | 공통 저장 마커 규칙. 장면 경로는 대사 라벨 없이 SceneImage |
| 뷰어 | Coil 원본 크기와 Fit 영역, 현재 확대 및 이동을 되돌려 이미지 밖 탭 판정. 크기 미확인은 그림 없는 영역으로 판정 |
| 닫기 | 배경 탭은 떼는 즉시, 더블 탭 대기는 이미지 위 탭만 적용 |
| 상세 장면 이미지 | 뷰어만 열고 인물 이미지 클릭 이벤트는 보내지 않음 |
| 스트림 앵커 | 헤더 위 여백을 뺀 콘텐츠 시작부터 뷰포트 끝까지 패드 높이 계산 |
| 재생성 인덱스 | 목록의 AI 안내와 프롤로그 항목 수 반영 |
| 첫 조각 | 기존 로딩 페이드 종료와 본문 교체. 본문이 자랄 때까지 측정한 최소 높이 유지 |

표현과 복구 결과는 앞 단계에 정의한다. ([3-3](3-3-LAYOUT.md), [공통 4-4](../4-4-EXECUTION.md))

# AN-2-ANALYTICS-FRONTEND-SPEC

이 문서는 **마냑 MVP 웹 프론트엔드가 Amplitude와 Sentry로 남겨야 하는 분석 신호**를 정리합니다. 사용자가 스토리를 만들고 채팅을 이어가는 행동은 Amplitude로 측정하고, 브라우저 오류와 API 실패 재현 단서는 Sentry로 확인합니다.

프론트엔드는 에이전트와 운영자가 직접 읽을 수 있는 관측 경계입니다. 화면 이벤트, breadcrumb, API 요청 식별자를 같은 흐름 안에 묶어 프론트엔드 행동과 서버 로그가 끊기지 않게 합니다.

```text
§AN-2-1   목적              프론트엔드 분석 책임과 제외 범위
§AN-2-2   도구별 역할       Amplitude · Sentry 역할 분리
§AN-2-3   식별자 정책       anonymous_id · session_id · request_id · user_id
§AN-2-4   공통 이벤트 규칙  사용자 이벤트 · custom properties · 네이밍 컨벤션
§AN-2-5   MVP 우선 이벤트   출시 전 P0 · 안정화 후 P1 이벤트
§AN-2-6   퍼널 정의         스토리 목록 · 제작 · 상세 · 채팅 목록 · 채팅 · 피드백 퍼널
§AN-2-7   이벤트별 property 매핑  스토리 목록 · 제작 · 상세 · 채팅 · 피드백
§AN-2-8   Sentry 수집 기준  Tags · User · Breadcrumb · Exceptions
§AN-2-9   개인정보 원칙     원문 수집 금지와 대체 property
§AN-2-10  검수 체크리스트   출시 전 확인 항목
```

---

| 항목 | 값 |
| --- | --- |
| 버전 | v0.3 |
| 작성일 | 2026-06-23 |
| 대상 | 마냑 MVP 웹 프론트엔드 |
| 적용 도구 | Amplitude, Sentry |

| 관련 문서 | 연결 지점 |
| --- | --- |
| [`analytics-spec.md`](./analytics-spec.md) | 전체 이벤트·지표·퍼널 기준 |
| [`analytics-backend-spec.md`](./analytics-backend-spec.md) | API 요청 식별자와 서버 로그 상관관계 |
| [`analytics-ai-spec.md`](./analytics-ai-spec.md) | AI 응답 성공·실패 이벤트와 AI 호출 로그 연결 |

## AN-2-1 목적

프론트엔드 분석의 목적은 사용자가 스토리를 만들고 채팅을 시작한 뒤 이야기를 이어가는지 측정하는 것이다. MVP에서는 모든 화면과 클릭을 추적하지 않고, 스토리 제작의 화면 진입과 핵심 클릭, 채팅 퍼널, 피드백 제출만 우선 측정한다.

프론트엔드는 다음 데이터를 담당한다.

- Amplitude로 사용자 행동 이벤트를 수집한다.
- Sentry로 브라우저 오류와 사용자 행동 breadcrumb를 수집한다.
- 백엔드 API 호출에 `anonymous_id`, `session_id`, `request_id`를 전달해 서버 로그와 연결한다.
- 사용자가 입력한 원문, 이메일, 채팅 메시지는 분석 이벤트에 넣지 않는다.

## AN-2-2 도구별 역할

| 도구 | 역할 | MVP 적용 범위 |
| --- | --- | --- |
| Amplitude | 사용자 행동 분석 | 퍼널, 전환율, 이탈율, 추천 입력 사용률 |
| Sentry | 프론트엔드 오류 분석 | 렌더링 오류, 라우트 오류, API 실패, 사용자 행동 breadcrumb |

Amplitude는 사용자 행동의 기준 데이터로 사용한다. Sentry는 오류 재현과 장애 원인 파악에 사용한다. Sentry 이벤트 수는 지표 계산의 기준으로 사용하지 않는다.

## AN-2-3 식별자 정책

MVP에는 로그인 기능이 없다고 가정한다. 프론트엔드는 첫 방문 시 익명 식별자를 만들고 같은 브라우저에서 유지한다.

| property | 생성 위치 | 저장 위치 | 설명 |
| --- | --- | --- | --- |
| `anonymous_id` | 프론트엔드 | `localStorage` 또는 1st-party cookie | 같은 브라우저 사용자를 묶는 익명 ID |
| `session_id` | 프론트엔드 | 메모리와 `sessionStorage` | 한 번의 방문 흐름 ID. 마지막 이벤트 후 30분이 지나면 새로 만든다. |
| `request_id` | 프론트엔드 | 요청 단위 메모리 | API 요청과 서버 로그를 연결하는 ID |
| `user_id` | 없음 | 없음 | MVP에서는 `null`로 보낸다. |

로그인 기능을 도입하면 `anonymous_id`는 유지하고, 로그인 시점부터 `user_id`를 추가한다. Amplitude의 사용자 연결 기능을 사용할 때도 기존 익명 행동이 끊기지 않도록 연결한다.

## AN-2-4 공통 이벤트 규칙

모든 Amplitude 이벤트 이름은 `snake_case`를 사용한다. Amplitude에는 사용자가 보거나 누르거나 입력한 행동만 사용자 이벤트로 보낸다. 선택한 장르, 선택 개수, 키워드 추가 여부처럼 도메인에서 나온 값은 이벤트 이름으로 만들지 않고 custom properties에 담는다.

### AN-2-4-1 사용자 이벤트와 custom properties 구분

사용자 이벤트와 custom properties는 다음 기준으로 나눈다.

| 구분 | 기준 | 예시 |
| --- | --- | --- |
| 사용자 이벤트 | 사용자가 화면을 보거나 UI를 조작한 행동 | `story_create_step1_viewed`, `story_create_step1_genre_clicked`, `story_create_step3_complete_clicked` |
| custom properties | 행동이 일어난 순간의 선택 상태, 도메인 값, 결과 속성 | `selected_genre_ids`, `selected_genre_count`, `has_custom_keyword`, `custom_keyword_count` |

### AN-2-4-2 이벤트 네이밍 컨벤션

사용자 이벤트 이름은 기본적으로 `{page}_{action}_{event}` 형식을 사용한다. 화면 자체가 action이면 `{page}_{event}`까지 줄일 수 있다. 새 이벤트를 추가할 때는 화면 또는 화면 단계를 먼저 적고, 사용자가 조작한 대상과 행동을 뒤에 붙인다.

| 구성 | 설명 | 예시 |
| --- | --- | --- |
| `page` | 이벤트가 발생한 화면 또는 화면 단계 | `story_create_step1`, `story_create_step2`, `story_create_step3`, `chat_room` |
| `action` | 사용자가 조작한 UI 대상 또는 상태 | `genre`, `main_character`, `storyline`, `complete`, `suggestion` |
| `event` | 사용자 행동 또는 사용자에게 노출된 상태 | `viewed`, `shown`, `clicked`, `focused`, `submitted`, `scrolled`, `pull_to_refresh` |

네이밍 규칙은 다음처럼 적용한다.

| 규칙 | 설명 | 예시 |
| --- | --- | --- |
| 화면 진입은 `{page}_viewed`로 남긴다. | 기본 퍼널은 화면 진입 이벤트를 기준으로 계산한다. | `story_create_step1_viewed` |
| UI 클릭은 `{page}_{object}_clicked`로 남긴다. | 클릭 대상이 버튼이면 버튼의 목적을 `object`에 넣는다. | `story_create_step2_storyline_clicked`, `story_create_step3_complete_clicked` |
| 상태 노출은 `{page}_{state}_shown`으로 남긴다. | 로딩, 에러, 추천 노출처럼 사용자가 본 상태를 기록한다. | `story_create_step2_error_shown` |
| 입력창 포커스는 `{page}_{input}_focused`로 남긴다. | 실제 원문 입력값은 보내지 않고 입력 시작 여부만 남긴다. | `story_create_step3_extra_info_focused` |
| 도메인 값은 이벤트 이름에 넣지 않는다. | 선택된 장르 수, 커스텀 키워드 여부, 생성 시간은 property로 보낸다. | `has_custom_keyword`, `generation_time_ms` |
| 여러 화면에서 같은 의미로 쓰는 공통 전환 이벤트는 `{domain}_{action}_{event}`를 허용한다. | 화면 구분은 `screen_name`과 `source`로 보완한다. | `chat_start_clicked`, `user_message_sent` |

프론트엔드에서는 생성 성공이나 생성 실패처럼 서비스 결과만 뜻하는 이름을 사용자 이벤트로 쓰지 않는다. 생성 성공은 사용자가 다음 화면을 본 이벤트로 측정하고, 실패는 사용자에게 노출된 에러 상태인 `*_error_shown`으로 측정한다.

### AN-2-4-3 공통 properties

모든 이벤트에는 다음 properties를 포함한다.

| property | 설명 |
| --- | --- |
| `anonymous_id` | 익명 사용자 ID |
| `user_id` | MVP에서는 `null` |
| `session_id` | 세션 ID |
| `screen_name` | 현재 화면 이름 |
| `entry_point` | 진입 경로 |
| `device_type` | `mobile`, `tablet`, `desktop` |
| `story_count` | 사용자가 보유한 스토리 수 |
| `chat_count` | 사용자가 진행 중인 채팅 수 |
| `created_at` | 이벤트 발생 시각 |

`entry_point`는 MVP에서 다음 값만 사용한다.

| 값 | 의미 |
| --- | --- |
| `story_tab` | 하단 탭의 스토리 메뉴 |
| `chat_tab` | 하단 탭의 채팅 메뉴 |
| `feedback_tab` | 하단 탭의 피드백 메뉴 |
| `empty_state` | 빈 상태 화면의 CTA |
| `floating_button` | 플로팅 만들기 버튼 |
| `story_card` | 스토리 목록 카드 |
| `story_detail` | 스토리 상세 화면 |
| `chat_thread` | 채팅 목록의 채팅 항목 |

## AN-2-5 MVP 우선 이벤트

P0 이벤트는 출시 전에 반드시 심는다. P1 이벤트는 P0 이벤트가 안정적으로 수집된 뒤 추가한다.

| 우선순위 | 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- | --- |
| P0 | `story_list_viewed` | 스토리 목록 화면 진입 | `is_empty`, `story_count` |
| P0 | `story_create_cta_clicked` | `스토리 만들기` 또는 `만들기` 클릭 | `entry_point`, `is_empty`, `story_count`, `chat_count`, `screen_name`, `cta_type` |
| P0 | `story_create_step1_viewed` | Step1 키워드 선택 화면 진입 | `step`, `entry_point`, `screen_name` |
| P0 | `story_create_step1_next_clicked` | Step1에서 다음 버튼 클릭 | `step`, `selected_genre_ids`, `selected_genre_count`, `selected_main_character_ids`, `selected_main_character_count`, `selected_supporting_character_ids`, `selected_supporting_character_count`, `selected_keyword_count`, `has_custom_keyword`, `custom_keyword_count` |
| P0 | `story_create_step2_viewed` | Step2 스토리라인 후보 화면 진입 | `step`, `storyline_count`, `generation_time_ms` |
| P0 | `story_create_step2_storyline_clicked` | Step2에서 스토리라인 후보 클릭 | `step`, `storyline_index`, `storyline_count` |
| P0 | `story_create_step2_next_clicked` | Step2에서 다음 버튼 클릭 | `step`, `storyline_index`, `storyline_count` |
| P0 | `story_create_step3_viewed` | Step3 추가 정보 입력 화면 진입 | `step`, `storyline_index` |
| P0 | `story_create_step3_complete_clicked` | Step3에서 `스토리 완성하기` 클릭 | `step`, `storyline_index`, `extra_info_count`, `extra_info_length_bucket`, `total_duration_ms` |
| P0 | `story_card_clicked` | 스토리 카드 클릭 | `story_id`, `story_position`, `genre_tags` |
| P0 | `story_detail_viewed` | 스토리 상세 화면 진입 | `story_id`, `source`, `has_existing_chat`, `genre_tags`, `start_situation_count` |
| P0 | `chat_start_clicked` | `채팅 시작하기` 클릭 | `story_id`, `source`, `has_existing_chat` |
| P0 | `chat_list_viewed` | 채팅 목록 화면 진입 | `is_empty`, `chat_count` |
| P0 | `chat_thread_clicked` | 채팅 항목 클릭 | `chat_id`, `story_id`, `message_count`, `thread_position`, `last_active_at` |
| P0 | `chat_room_viewed` | 채팅방 진입 | `chat_id`, `story_id`, `message_count`, `entry_point` |
| P0 | `user_message_sent` | 사용자 메시지 전송 | `chat_id`, `story_id`, `turn_index`, `input_type`, `message_length_bucket` |
| P0 | `ai_response_received` | AI 응답 수신 | `chat_id`, `story_id`, `turn_index`, `response_time_ms` |
| P0 | `feedback_page_viewed` | 피드백 화면 진입 | `entry_point`, `last_screen_name` |
| P0 | `feedback_submitted` | 피드백 제출 성공 | `content_length`, `has_email` |
| P1 | `story_menu_clicked` | 스토리 카드의 메뉴 클릭 | `story_id`, `story_position` |
| P1 | `story_detail_scrolled` | 상세 설명 또는 시작 상황 영역 스크롤 | `story_id`, `source`, `scroll_depth` |
| P1 | `story_detail_back_clicked` | 뒤로가기 클릭 | `story_id`, `source` |
| P1 | `story_detail_menu_clicked` | 상세 화면 메뉴 클릭 | `story_id`, `source` |
| P1 | `chat_thread_menu_clicked` | 채팅 항목 메뉴 클릭 | `chat_id`, `story_id`, `thread_position` |
| P1 | `story_create_step1_genre_clicked` | Step1에서 장르 선택 또는 선택 해제 | `step`, `genre_id`, `is_selected_after_click`, `selected_genre_count`, `selected_keyword_count` |
| P1 | `story_create_step1_genre_tab_clicked` | Step1에서 장르 탭 클릭 | `step`, `selected_genre_count`, `selected_keyword_count` |
| P1 | `story_create_step1_main_character_clicked` | Step1에서 주인공 성격 선택 또는 선택 해제 | `step`, `main_character_id`, `is_selected_after_click`, `selected_main_character_count`, `selected_keyword_count` |
| P1 | `story_create_step1_supporting_character_clicked` | Step1에서 주변 인물 성격 선택 또는 선택 해제 | `step`, `supporting_character_id`, `is_selected_after_click`, `selected_supporting_character_count`, `selected_keyword_count` |
| P1 | `story_create_step1_custom_keyword_add_clicked` | Step1에서 직접 키워드 추가 클릭 | `step`, `custom_keyword_count`, `keyword_length` |
| P1 | `story_create_step2_loading_shown` | 스토리라인 생성 로딩 상태 노출 | `step`, `request_id` |
| P1 | `story_create_step2_error_shown` | Step2 스토리라인 생성 실패 상태 노출 | `step`, `error_code`, `generation_time_ms` |
| P1 | `story_create_step2_regenerate_clicked` | Step2에서 다시 만들기 클릭 | `step`, `storyline_count`, `previous_storyline_count` |
| P1 | `story_create_step2_reaction_clicked` | Step2에서 스토리라인 좋아요 또는 싫어요 클릭 | `step`, `storyline_index`, `reaction_type` |
| P1 | `story_create_step3_ai_suggestion_clicked` | Step3에서 AI 추천 추가 정보 클릭 | `step`, `storyline_index`, `suggestion_index`, `suggestion_count`, `extra_info_count` |
| P1 | `story_create_step3_extra_info_focused` | Step3에서 직접 입력창 포커스 | `step`, `storyline_index` |
| P1 | `story_create_step3_error_shown` | Step3 스토리 생성 실패 상태 노출 | `step`, `error_code`, `total_duration_ms` |
| P1 | `story_create_exit_clicked` | 제작 중 뒤로가기, 닫기, 나가기 클릭 | `step`, `exit_step`, `total_duration_ms` |
| P1 | `ai_suggestion_shown` | AI 추천 입력 노출 | `chat_id`, `story_id`, `suggestion_count`, `turn_index` |
| P1 | `ai_suggestion_clicked` | AI 추천 입력 선택 | `chat_id`, `story_id`, `suggestion_index`, `suggestion_count`, `turn_index` |
| P1 | `chat_input_focused` | 직접 입력창 포커스 | `chat_id`, `story_id`, `turn_index` |
| P1 | `ai_response_failed` | AI 응답 실패 | `chat_id`, `story_id`, `turn_index`, `error_code`, `response_time_ms` |
| P1 | `chat_room_exited` | 채팅방 나가기 | `chat_id`, `story_id`, `exit_after_turn` |
| P1 | `feedback_input_started` | 피드백 입력 시작 | `entry_point`, `last_screen_name` |
| P1 | `feedback_submit_clicked` | `피드백 보내기` 클릭 | `content_length`, `has_email` |
| P1 | `feedback_submit_failed` | 피드백 제출 실패 | `content_length`, `has_email`, `error_code` |

## AN-2-6 퍼널 정의

### AN-2-6-1 스토리 제작 퍼널

스토리 제작 기본 퍼널은 화면 진입 이벤트를 기준으로 본다. 화면 안 선택, 재생성, 반응, 추천 추가 정보 선택은 세부 행동 퍼널로 따로 본다.

| 순서 | 단계 | 이벤트 | 전환율 |
| --- | --- | --- | --- |
| 1 | Step1 키워드 선택 화면 진입 | `story_create_step1_viewed` | 기준 모수 |
| 2 | Step2 스토리라인 선택 화면 진입 | `story_create_step2_viewed` | Step2 진입 / Step1 진입 |
| 3 | Step3 추가 정보 입력 화면 진입 | `story_create_step3_viewed` | Step3 진입 / Step2 진입 |
| 4 | 완성 버튼 클릭 | `story_create_step3_complete_clicked` | 완성 클릭 / Step3 진입 |
| 5 | 생성된 스토리 상세 화면 진입 | `story_detail_viewed` with `source=story_create` | 상세 진입 / 완성 클릭 |
| 6 | 채팅 시작 | `chat_start_clicked` | 채팅 시작 / 생성된 스토리 상세 진입 |

Step1의 장르·성격·직접 키워드 선택 값은 `story_create_step1_next_clicked`의 custom properties로 함께 보낸다. Step2와 Step3의 AI 성공은 다음 화면 진입 또는 상세 화면 진입으로 판단하고, 실제 AI 성공·실패 원인은 백엔드·AI 로그에서 확인한다.

### AN-2-6-2 스토리 목록과 상세 퍼널

스토리 목록은 제작 진입과 기존 스토리 재방문을 나눠서 본다. 상세 화면은 채팅 시작 전환과 상세 정보 탐색을 함께 본다.

| 흐름 | 단계 | 이벤트 | 전환율 |
| --- | --- | --- | --- |
| 제작 진입 | 스토리 목록 화면 진입 | `story_list_viewed` | 기준 모수 |
| 제작 진입 | 스토리 만들기 클릭 | `story_create_cta_clicked` | CTA 클릭 / 스토리 목록 진입 |
| 제작 진입 | Step1 키워드 선택 화면 진입 | `story_create_step1_viewed` | Step1 진입 / CTA 클릭 |
| 기존 스토리 재방문 | 스토리 목록 화면 진입 | `story_list_viewed` | 기준 모수 |
| 기존 스토리 재방문 | 스토리 카드 클릭 | `story_card_clicked` | 카드 클릭 / 스토리 목록 진입 |
| 기존 스토리 재방문 | 스토리 상세 화면 진입 | `story_detail_viewed` with `source=story_list` | 상세 진입 / 카드 클릭 |
| 상세 전환 | 스토리 상세 화면 진입 | `story_detail_viewed` | 기준 모수 |
| 상세 전환 | 상세 내용 확인 | `story_detail_scrolled` | 상세 스크롤 / 상세 화면 진입 |
| 상세 전환 | 채팅 시작 클릭 | `chat_start_clicked` | 채팅 시작 / 상세 화면 진입 |
| 상세 전환 | 채팅방 진입 | `chat_room_viewed` | 채팅방 진입 / 채팅 시작 클릭 |

### AN-2-6-3 채팅 목록 퍼널

채팅 목록은 빈 목록에서 제작으로 이동하는 흐름과 기존 채팅으로 재진입하는 흐름을 나눠서 본다.

| 흐름 | 단계 | 이벤트 | 전환율 |
| --- | --- | --- | --- |
| 빈 목록 제작 진입 | 채팅 목록 화면 진입 | `chat_list_viewed` | 기준 모수 |
| 빈 목록 제작 진입 | 스토리 만들기 클릭 | `story_create_cta_clicked` | CTA 클릭 / 채팅 목록 진입 |
| 빈 목록 제작 진입 | Step1 키워드 선택 화면 진입 | `story_create_step1_viewed` | Step1 진입 / CTA 클릭 |
| 기존 채팅 재진입 | 채팅 목록 화면 진입 | `chat_list_viewed` | 기준 모수 |
| 기존 채팅 재진입 | 채팅 항목 클릭 | `chat_thread_clicked` | 채팅 항목 클릭 / 채팅 목록 진입 |
| 기존 채팅 재진입 | 채팅방 진입 | `chat_room_viewed` | 채팅방 진입 / 채팅 항목 클릭 |
| 기존 채팅 재진입 | 메시지 전송 | `user_message_sent` | 메시지 전송 / 채팅방 진입 |

### AN-2-6-4 채팅 퍼널

스토리 상세에서 채팅으로 이어지는지는 `chat_start_clicked`를 기준으로 본다. 채팅방 안에서의 몰입은 `chat_room_viewed`를 기준으로 본다.

| 순서 | 단계 | 이벤트 | 전환율 |
| --- | --- | --- | --- |
| 1 | 채팅 시작 클릭 | `chat_start_clicked` | 기준 모수 |
| 2 | 채팅방 진입 | `chat_room_viewed` | 채팅방 진입 / 채팅 시작 클릭 |
| 3 | 첫 입력 의도 | `chat_input_focused` 또는 `ai_suggestion_clicked` | 입력 의도 / 채팅방 진입 |
| 4 | 첫 메시지 전송 | `user_message_sent` with `turn_index=1` | 첫 메시지 / 채팅방 진입 |
| 5 | AI 응답 성공 | `ai_response_received` | AI 응답 / 사용자 메시지 |
| 6 | 2턴 진행 | `user_message_sent` with `turn_index=2` | 2턴 진행 / 첫 메시지 |
| 7 | 5턴 진행 | `user_message_sent` with `turn_index=5` | 5턴 진행 / 채팅방 진입 |

### AN-2-6-5 피드백 퍼널

피드백은 화면 진입, 입력 시작, 제출 클릭, 제출 성공과 실패를 분리해 본다.

| 순서 | 단계 | 이벤트 | 전환율 |
| --- | --- | --- | --- |
| 1 | 피드백 화면 진입 | `feedback_page_viewed` | 기준 모수 |
| 2 | 피드백 입력 시작 | `feedback_input_started` | 입력 시작 / 피드백 화면 진입 |
| 3 | 피드백 보내기 클릭 | `feedback_submit_clicked` | 제출 클릭 / 입력 시작 |
| 4 | 피드백 제출 성공 | `feedback_submitted` | 제출 성공 / 제출 클릭 |
| 5 | 피드백 제출 실패 | `feedback_submit_failed` | 제출 실패 / 제출 클릭 |

## AN-2-7 이벤트별 property 매핑

아래 표의 핵심 properties는 AN-2-4-3의 공통 properties 외에 이벤트별로 추가해서 보내는 값이다. 이벤트별 properties는 행동이 발생한 순간의 상태를 기준으로 채운다.

### AN-2-7-1 스토리 목록

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `story_list_viewed` | 스토리 목록 화면 진입 | `is_empty`, `story_count` |
| `story_create_cta_clicked` | `스토리 만들기` 또는 `만들기` 클릭 | `entry_point`, `is_empty`, `story_count`, `cta_type` |
| `story_card_clicked` | 스토리 카드 클릭 | `story_id`, `story_position`, `genre_tags` |
| `story_menu_clicked` | 스토리 카드의 메뉴 클릭 | `story_id`, `story_position` |

### AN-2-7-2 스토리 제작

스토리 제작 이벤트에는 `step`을 항상 포함한다. 아래 표는 `step`을 포함해 이벤트별로 추가해서 보내는 핵심 properties를 적는다. `step` 값은 `step1_keyword`, `step2_storyline`, `step3_extra_info` 중 하나로 보낸다.

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `story_create_step1_viewed` | Step1 키워드 선택 화면 진입 | `step`, `entry_point` |
| `story_create_step1_genre_tab_clicked` | Step1에서 장르 탭 클릭 | `step`, `selected_genre_count`, `selected_keyword_count` |
| `story_create_step1_genre_clicked` | Step1에서 장르 선택 또는 선택 해제 | `step`, `genre_id`, `is_selected_after_click`, `selected_genre_count`, `selected_keyword_count` |
| `story_create_step1_main_character_clicked` | Step1에서 주인공 성격 선택 또는 선택 해제 | `step`, `main_character_id`, `is_selected_after_click`, `selected_main_character_count`, `selected_keyword_count` |
| `story_create_step1_supporting_character_clicked` | Step1에서 주변 인물 성격 선택 또는 선택 해제 | `step`, `supporting_character_id`, `is_selected_after_click`, `selected_supporting_character_count`, `selected_keyword_count` |
| `story_create_step1_custom_keyword_add_clicked` | Step1에서 직접 키워드 추가 클릭 | `step`, `custom_keyword_count`, `keyword_length` |
| `story_create_step1_next_clicked` | Step1에서 다음 버튼 클릭 | `step`, `selected_genre_ids`, `selected_genre_count`, `selected_main_character_ids`, `selected_main_character_count`, `selected_supporting_character_ids`, `selected_supporting_character_count`, `selected_keyword_count`, `has_custom_keyword`, `custom_keyword_count` |
| `story_create_step2_loading_shown` | 스토리라인 생성 로딩 상태 노출 | `step`, `request_id` |
| `story_create_step2_viewed` | Step2 스토리라인 후보 화면 진입 | `step`, `storyline_count`, `generation_time_ms` |
| `story_create_step2_error_shown` | Step2 스토리라인 생성 실패 상태 노출 | `step`, `error_code`, `generation_time_ms` |
| `story_create_step2_regenerate_clicked` | Step2에서 다시 만들기 클릭 | `step`, `storyline_count`, `previous_storyline_count` |
| `story_create_step2_reaction_clicked` | Step2에서 스토리라인 좋아요 또는 싫어요 클릭 | `step`, `storyline_index`, `reaction_type` |
| `story_create_step2_storyline_clicked` | Step2에서 스토리라인 후보 클릭 | `step`, `storyline_index`, `storyline_count` |
| `story_create_step2_next_clicked` | Step2에서 다음 버튼 클릭 | `step`, `storyline_index`, `storyline_count` |
| `story_create_step3_viewed` | Step3 추가 정보 입력 화면 진입 | `step`, `storyline_index` |
| `story_create_step3_ai_suggestion_clicked` | Step3에서 AI 추천 추가 정보 클릭 | `step`, `storyline_index`, `suggestion_index`, `suggestion_count`, `extra_info_count` |
| `story_create_step3_extra_info_focused` | Step3에서 직접 입력창 포커스 | `step`, `storyline_index` |
| `story_create_step3_complete_clicked` | Step3에서 `스토리 완성하기` 클릭 | `step`, `storyline_index`, `extra_info_count`, `extra_info_length_bucket`, `total_duration_ms` |
| `story_create_step3_error_shown` | Step3 스토리 생성 실패 상태 노출 | `step`, `error_code`, `total_duration_ms` |
| `story_create_exit_clicked` | 제작 중 뒤로가기, 닫기, 나가기 클릭 | `step`, `exit_step`, `total_duration_ms` |

### AN-2-7-3 스토리 상세

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `story_detail_viewed` | 스토리 상세 화면 진입 | `story_id`, `source`, `has_existing_chat`, `genre_tags`, `start_situation_count` |
| `story_detail_scrolled` | 상세 설명 또는 시작 상황 영역 스크롤 | `story_id`, `source`, `scroll_depth` |
| `chat_start_clicked` | `채팅 시작하기` 클릭 | `story_id`, `source`, `has_existing_chat` |
| `story_detail_back_clicked` | 뒤로가기 클릭 | `story_id`, `source` |
| `story_detail_menu_clicked` | 상세 화면 메뉴 클릭 | `story_id`, `source` |

`source`는 `story_list`, `story_create`, `chat_list` 중 하나만 사용한다.

### AN-2-7-4 채팅 목록

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `chat_list_viewed` | 채팅 목록 화면 진입 | `is_empty`, `chat_count` |
| `story_create_cta_clicked` | 빈 채팅 목록에서 `스토리 만들기` 클릭 | `entry_point`, `is_empty`, `chat_count`, `screen_name` |
| `story_create_step1_viewed` | Step1 키워드 선택 화면 진입 | `entry_point`, `screen_name` |
| `chat_thread_clicked` | 채팅 항목 클릭 | `chat_id`, `story_id`, `message_count`, `thread_position`, `last_active_at` |
| `chat_thread_menu_clicked` | 채팅 항목 메뉴 클릭 | `chat_id`, `story_id`, `thread_position` |

### AN-2-7-5 채팅

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `chat_room_viewed` | 채팅방 진입 | `chat_id`, `story_id`, `message_count`, `entry_point` |
| `ai_suggestion_shown` | AI 추천 입력 노출 | `chat_id`, `story_id`, `suggestion_count`, `turn_index` |
| `ai_suggestion_clicked` | AI 추천 입력 선택 | `chat_id`, `story_id`, `suggestion_index`, `suggestion_count`, `turn_index` |
| `chat_input_focused` | 직접 입력창 포커스 | `chat_id`, `story_id`, `turn_index` |
| `user_message_sent` | 사용자 메시지 전송 | `chat_id`, `story_id`, `turn_index`, `input_type`, `message_length_bucket` |
| `ai_response_received` | AI 응답 수신 | `chat_id`, `story_id`, `turn_index`, `response_time_ms` |
| `ai_response_failed` | AI 응답 실패 | `chat_id`, `story_id`, `turn_index`, `error_code`, `response_time_ms` |
| `chat_room_exited` | 채팅방 나가기 | `chat_id`, `story_id`, `exit_after_turn` |

### AN-2-7-6 피드백

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `feedback_page_viewed` | 피드백 화면 진입 | `entry_point`, `last_screen_name` |
| `feedback_input_started` | 피드백 입력 시작 | `entry_point`, `last_screen_name` |
| `feedback_submit_clicked` | `피드백 보내기` 클릭 | `content_length`, `has_email` |
| `feedback_submitted` | 피드백 제출 성공 | `content_length`, `has_email` |
| `feedback_submit_failed` | 피드백 제출 실패 | `content_length`, `has_email`, `error_code` |

## AN-2-8 Sentry 수집 기준

Sentry에는 오류 분석에 필요한 최소 context만 넣는다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `screen_name`, `entry_point`, `story_id`, `chat_id`, `request_id` |
| User | `id: anonymous_id`, `ip_address: "{{auto}}"` |
| Breadcrumb | P0 행동 이벤트 이름, 주요 API 요청 시작과 종료 |
| Exceptions | 렌더링 오류, 라우트 오류, API 네트워크 오류, 예상하지 못한 5xx 응답 |

4xx 응답은 사용자가 복구할 수 있는 검증 오류라면 Sentry exception으로 보내지 않는다. 사용자 행동 분석이 필요한 경우 Amplitude 이벤트로만 기록한다.

## AN-2-9 개인정보 원칙

프론트엔드 분석 이벤트에는 원문을 넣지 않는다.

| 데이터 | 처리 방식 |
| --- | --- |
| 채팅 메시지 | `message_length_bucket`만 전송 |
| 피드백 본문 | `content_length`만 전송 |
| 이메일 | `has_email`만 전송 |
| 직접 추가 키워드 | `keyword_length`만 전송 |
| 사전 정의 키워드 | `keyword_id` 또는 관리되는 label만 전송 |

## AN-2-10 검수 체크리스트

- Amplitude 디버그 모드에서 P0 이벤트가 한 번씩 발생한다.
- `story_list_viewed`, `story_create_cta_clicked`, `story_card_clicked`, `chat_list_viewed`, `chat_thread_clicked`, `feedback_page_viewed`, `feedback_submitted`가 P0 이벤트로 수집된다.
- `anonymous_id`와 `session_id`가 새로고침 후에도 의도대로 유지된다.
- 같은 사용자 행동에서 Amplitude event, Sentry breadcrumb, API `request_id`가 연결된다.
- 채팅 메시지, 피드백 본문, 이메일, 직접 추가 키워드 원문이 이벤트 payload에 없다.
- `story_create_step1_viewed`부터 `story_detail_viewed` with `source=story_create`까지 스토리 제작 기본 퍼널을 Amplitude에서 계산할 수 있다.
- 스토리 목록, 스토리 상세, 채팅 목록, 피드백 퍼널을 Amplitude에서 계산할 수 있다.
- 채팅 첫 메시지 전송률과 2턴 이상 진행률을 Amplitude에서 계산할 수 있다.

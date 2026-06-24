# AN-1-ANALYTICS-SPEC

이 문서는 **마냑 서비스에서 사용자가 스토리를 만들고 채팅을 이어가는 흐름**을 측정하기 위한 최상위 분석 스펙입니다. 프론트엔드 이벤트, 백엔드 로그, AI 호출 로그를 같은 식별자와 지표 언어로 연결하는 기준 문서로 사용합니다.

이 문서는 긴 설명서가 아니라 분석 스펙의 지도 역할을 하며, 세부 구현 계약은 프론트엔드·백엔드·AI 서비스 문서로 나눕니다.

```text
§AN-1-1   분석 목적                 MVP 핵심 흐름과 분석 질문
§AN-1-2   식별자 정책               anonymous_id · session_id · story_id · chat_id
§AN-1-3   이벤트 공통 규칙          사용자 이벤트 · custom properties · 네이밍 컨벤션
§AN-1-4   핵심 지표 정의            제작 · 채팅 · 피드백 지표 계산식
§AN-1-5   스토리 제작 퍼널          제작 단계별 전환 이벤트
§AN-1-6   채팅 퍼널                 채팅 시작 · 첫 메시지 · 다중 턴 전환 이벤트
§AN-1-7   페이지별 이벤트 스펙      화면별 이벤트 카탈로그
§AN-1-8   개인정보와 원문 수집 원칙  원문 수집 금지와 대체 property
§AN-1-9   MVP 우선 적용 이벤트      P0 · P1 적용 순서
```

---

| 항목 | 값 |
| --- | --- |
| 버전 | v0.4 |
| 작성일 | 2026-06-24 |
| 대상 | 마냑 서비스 |
| 작성 목적 | MVP 출시 후 사용자가 스토리를 만들고 채팅을 이어가는 흐름을 측정하기 위한 최소 이벤트 스펙을 정의한다. |

| 세부 문서 | 역할 |
| --- | --- |
| [`analytics-frontend-spec.md`](./analytics-frontend-spec.md) | Amplitude 이벤트와 브라우저 Sentry 수집 기준 |
| [`analytics-backend-spec.md`](./analytics-backend-spec.md) | CloudWatch API 로그, 서버 Sentry, `ai_call_logs` 연결 기준 |
| [`analytics-ai-spec.md`](./analytics-ai-spec.md) | AI 호출 로그, 실패 코드, 토큰·latency 운영 지표 |

## AN-1-1 분석 목적

마냑 MVP 분석의 목적은 사용자가 다음 흐름을 자연스럽게 완료하는지 확인하는 것이다.

1. 스토리 목록에서 스토리 제작을 시작한다.
2. 키워드 선택, 스토리라인 선택, 추가 정보 입력을 거쳐 스토리를 완성한다.
3. 완성한 스토리의 상세 화면에서 채팅을 시작한다.
4. 채팅에서 첫 메시지를 보내고 여러 턴 동안 이야기를 이어간다.
5. 불편하거나 아쉬운 점을 피드백으로 남긴다.

핵심 질문과 지표는 다음과 같다.

| 핵심 질문 | 확인 지표 |
| --- | --- |
| 사용자가 스토리 제작을 시작하는가? | 제작 시작률 |
| 제작 중 어디서 막히는가? | 제작 단계별 이탈율, 취소율 |
| 스토리 생성이 채팅으로 이어지는가? | 스토리 상세 → 채팅 시작 전환율 |
| 채팅이 실제 몰입으로 이어지는가? | 첫 메시지 전송률, 2턴 이상 진행률, 5턴 이상 진행률 |
| 개선 포인트를 수집하고 있는가? | 피드백 제출률 |

## AN-1-2 식별자 정책

현재 MVP에는 로그인 기능이 없다. 따라서 `user_id`는 사용하지 않고, 익명 식별자를 기준으로 분석한다.

| property | 설명 | 생성 방식 |
| --- | --- | --- |
| `anonymous_id` | 같은 브라우저 사용자를 묶는 익명 ID | 첫 방문 시 `crypto.randomUUID()`로 생성하고 `localStorage` 또는 1st-party cookie에 저장 |
| `session_id` | 한 번의 방문 흐름 ID | 앱 진입 시 생성한다. 마지막 이벤트 후 30분이 지나면 새로 생성한다. |
| `user_id` | 로그인 사용자 ID | 현재는 `null`로 보낸다. 로그인 기능 도입 후 사용한다. |
| `story_id` | 스토리 식별자 | 스토리 생성 후 서버에서 발급한다. |
| `chat_id` | 채팅 식별자 | 채팅 시작 후 서버에서 발급한다. |

분석 기준은 다음과 같이 잡는다.

| 분석 목적 | 기준 식별자 |
| --- | --- |
| 한 번의 사용 흐름 안에서 퍼널 보기 | `session_id` |
| 재방문, 사용자 수, 중복 제거 보기 | `anonymous_id` |
| 스토리 단위 성과 보기 | `story_id` |
| 채팅 단위 성과 보기 | `chat_id` |

로그인 기능을 도입하면 `anonymous_id`는 계속 유지하고, 로그인 시점부터 `user_id`를 추가한다. 분석 도구가 `identify` 또는 `alias` 기능을 제공하면 기존 익명 행동과 로그인 사용자를 연결한다.

## AN-1-3 이벤트 공통 규칙

이벤트 이름은 `snake_case`를 사용한다. 프론트엔드 Amplitude 이벤트는 사용자가 보거나 누르거나 입력한 행동을 기준으로 남긴다. 선택한 장르, 선택 개수, 키워드 추가 여부처럼 비즈니스 로직이나 도메인에서 나온 값은 이벤트 이름으로 만들지 않고 custom properties에 담는다.

### AN-1-3-1 사용자 이벤트와 custom properties 구분

사용자 이벤트와 custom properties는 다음 기준으로 나눈다.

| 구분 | 기준 | 예시 |
| --- | --- | --- |
| 사용자 이벤트 | 사용자가 화면을 보거나 UI를 조작한 행동 | `story_create_step_viewed`, `story_create_option_clicked`, `story_create_complete_clicked` |
| custom properties | 행동이 일어난 순간의 도메인 값, 선택 상태, 결과 속성 | `selected_genre_ids`, `selected_genre_count`, `has_custom_keyword`, `custom_keyword_count` |

### AN-1-3-2 이벤트 네이밍 컨벤션

프론트엔드 사용자 이벤트는 기본적으로 `{domain}_{object}_{verb}` 형식을 사용한다. 이벤트 이름은 사용자가 한 행동 또는 사용자에게 노출된 상태만 표현한다. 화면명, 단계, 진입 경로, 선택값, AI feature, 에러 코드는 이벤트 이름에 넣지 않고 custom properties로 보낸다.

| 구성 | 설명 | 예시 |
| --- | --- | --- |
| `domain` | 기능 또는 사용자 흐름 | `story_create`, `story_detail`, `story_list`, `chat`, `feedback` |
| `object` | 사용자가 보거나 조작한 대상 | `step`, `next`, `complete`, `option`, `storyline`, `suggestion`, `input`, `error`, `loading` |
| `verb` | 사용자 행동 또는 사용자에게 노출된 상태 | `viewed`, `shown`, `clicked`, `focused`, `submitted`, `sent`, `received`, `failed`, `exited` |

네이밍 규칙은 다음처럼 적용한다.

| 규칙 | 설명 | 예시 |
| --- | --- | --- |
| 화면 진입은 `{screen_or_domain}_{object}_viewed`로 남긴다. | 단일 화면은 화면명을 쓰고, 단계형 flow는 `step`을 object로 쓴다. | `story_list_viewed`, `story_create_step_viewed` |
| 단계형 flow의 단계 번호는 이벤트명에 넣지 않는다. | 단계는 `step_number`, `step_name`으로 보낸다. | `story_create_step_viewed` with `step_number=1` |
| 버튼 클릭은 버튼 문구보다 의도를 쓴다. | `done` 대신 `next`, `complete`, `submit`, `exit`을 쓴다. | `story_create_next_clicked`, `story_create_complete_clicked` |
| 옵션 선택은 하나의 이벤트로 묶는다. | 장르, 주인공 성격, 주변 인물 성격은 `option_group`으로 구분한다. | `story_create_option_clicked` |
| 상태 노출은 `{domain}_{state}_shown`으로 남긴다. | 로딩과 에러는 `feature`, `step_number`, `error_code`로 구분한다. | `story_create_error_shown` |
| 입력창 포커스는 `{domain}_{input}_focused`로 남긴다. | 실제 원문 입력값은 보내지 않고 입력 시작 여부만 남긴다. | `story_create_extra_info_focused` |
| 도메인 값은 이벤트 이름에 넣지 않는다. | 선택된 장르 수, 커스텀 키워드 여부, 생성 시간은 property로 보낸다. | `has_custom_keyword`, `generation_time_ms` |
| 여러 화면에서 같은 의미로 쓰는 공통 전환 이벤트는 같은 이벤트명을 유지한다. | 화면 구분은 `screen_name`, `entry_point`, `source`로 보완한다. | `story_create_cta_clicked`, `chat_start_clicked`, `user_message_sent` |

생성 성공, 생성 실패처럼 서비스 결과를 나타내는 이벤트는 백엔드·AI 운영 로그에서 사용한다. 프론트엔드 사용자 퍼널에서는 `story_detail_viewed`처럼 사용자가 실제로 본 화면이나 `story_create_error_shown`처럼 노출된 상태로 연결한다.

### AN-1-3-3 공통 properties

모든 이벤트에는 다음 properties를 기본으로 포함한다.

| property | 설명 |
| --- | --- |
| `anonymous_id` | 익명 사용자 ID |
| `user_id` | 현재는 `null` |
| `session_id` | 세션 ID |
| `screen_name` | 현재 화면 이름 |
| `entry_point` | 진입 경로 |
| `flow_name` | 사용자가 진행 중인 흐름. 단계형 flow에서 필수 |
| `step_number` | 단계 번호. 단계형 flow에서 필수 |
| `step_name` | 단계 의미. 단계형 flow에서 필수 |
| `device_type` | 기기 유형 |
| `story_count` | 사용자가 보유한 스토리 수 |
| `chat_count` | 사용자가 진행 중인 채팅 수 |
| `created_at` | 이벤트 발생 시각 |

`entry_point` 값은 우선 다음 값만 사용한다.

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

## AN-1-4 핵심 지표 정의

| 영역 | 지표 | 계산식 |
| --- | --- | --- |
| 스토리 목록 | 빈 목록 CTA 클릭률 | `story_create_cta_clicked` 수 / `story_list_viewed` 수 where `is_empty=true` |
| 스토리 목록 | 빈 목록 → 제작 화면 진입률 | `story_create_step_viewed` 수 where `step_number=1` / `story_list_viewed` 수 where `entry_point=empty_state` |
| 스토리 목록 | CTA 클릭 → 제작 화면 진입률 | `story_create_step_viewed` 수 where `step_number=1` / `story_create_cta_clicked` 수 |
| 스토리 목록 | 스토리 카드 클릭률 | `story_card_clicked` 수 / `story_list_viewed` 수 where `is_empty=false` |
| 스토리 목록 | 기존 스토리 상세 진입률 | `story_detail_viewed` 수 where `source=story_list` / `story_card_clicked` 수 |
| 스토리 목록 | 추가 제작률 | `story_create_step_viewed` 수 where `step_number=1` / `story_list_viewed` 수 where `story_count > 0` |
| 스토리 제작 | 스토리 제작 완료율 | `story_detail_viewed` 사용자 수 where `source=story_create` / `story_create_step_viewed` 사용자 수 where `step_number=1` |
| 스토리 제작 | 제작 명시 종료율 | `story_create_exit_clicked` 사용자 수 / `story_create_step_viewed` 사용자 수 where `step_number=1` |
| 스토리 제작 | 단계별 이탈율 | `1 - 다음 단계 화면 진입 이벤트 사용자 수 / 현재 단계 화면 진입 이벤트 사용자 수` |
| 스토리 제작 | AI 스토리라인 생성 실패 노출률 | `story_create_error_shown` 수 where `step_number=2` and `feature=storyline_generation` / `story_create_next_clicked` 수 where `step_number=1` |
| 스토리 제작 | AI 스토리 생성 실패 노출률 | `story_create_error_shown` 수 where `step_number=3` and `feature=story_completion` / `story_create_complete_clicked` 수 where `step_number=3` |
| 스토리 제작 | 다시 만들기율 | `story_create_regenerate_clicked` 수 where `step_number=2` / `story_create_step_viewed` 수 where `step_number=2` |
| 스토리 제작 | 커스텀 키워드 사용률 | `story_create_next_clicked` 중 `step_number=1` and `has_custom_keyword=true` 사용자 수 / `story_create_next_clicked` 사용자 수 where `step_number=1` |
| 스토리 상세 | 상세 → 채팅 시작 전환율 | `chat_start_clicked` 수 / `story_detail_viewed` 수 |
| 스토리 상세 | 제작 직후 채팅 전환율 | `chat_start_clicked` 수 / `story_detail_viewed` 수 where `source=story_create` |
| 스토리 상세 | 목록 재진입 후 채팅 전환율 | `chat_start_clicked` 수 / `story_detail_viewed` 수 where `source=story_list` |
| 스토리 상세 | 상세 이탈율 | `1 - (chat_start_clicked 수 / story_detail_viewed 수)` |
| 스토리 상세 | 기존 채팅 보유 스토리 전환율 | `chat_start_clicked` 수 / `story_detail_viewed` 수 where `has_existing_chat=true` |
| 스토리 상세 | 신규 채팅 시작 전환율 | `chat_start_clicked` 수 / `story_detail_viewed` 수 where `has_existing_chat=false` |
| 스토리 상세 | 상세 스크롤률 | `story_detail_scrolled` 수 / `story_detail_viewed` 수 |
| 채팅 목록 | 채팅 빈 목록 CTA 클릭률 | `story_create_cta_clicked` 수 / `chat_list_viewed` 수 where `is_empty=true` |
| 채팅 목록 | 채팅 빈 목록 → 제작 화면 진입률 | `story_create_step_viewed` 수 where `step_number=1` / `story_create_cta_clicked` 수 where `screen_name=chat_list` |
| 채팅 목록 | 채팅 항목 클릭률 | `chat_thread_clicked` 수 / `chat_list_viewed` 수 where `is_empty=false` |
| 채팅 목록 | 채팅방 재진입률 | `chat_room_viewed` 수 / `chat_thread_clicked` 수 |
| 채팅 목록 | 재진입 후 메시지 전송률 | `user_message_sent` 수 / `chat_room_viewed` 수 where `message_count > 0` |
| 채팅 목록 | 채팅 목록 이탈율 | `1 - (chat_thread_clicked 수 / chat_list_viewed 수)` where `is_empty=false` |
| 채팅 | 채팅 시작 → 채팅방 진입률 | `chat_room_viewed` 수 / `chat_start_clicked` 수 |
| 채팅 | 첫 입력 의도율 | `chat_input_focused` 또는 `ai_suggestion_clicked` 수 / `chat_room_viewed` 수 |
| 채팅 | 첫 메시지 전송률 | 첫 `user_message_sent` 사용자 수 / `chat_room_viewed` 사용자 수 |
| 채팅 | 첫 화면 이탈율 | `1 - (첫 user_message_sent(turn_index=1) 사용자 수 / chat_room_viewed 사용자 수)` |
| 채팅 | 2턴 이상 진행률 | `turn_index >= 2` 사용자 수 / 첫 `user_message_sent` 사용자 수 |
| 채팅 | 5턴 이상 진행률 | `turn_index >= 5` 사용자 수 / `chat_room_viewed` 사용자 수 |
| 채팅 | 추천 입력 노출률 | `ai_suggestion_shown` 수 / `chat_room_viewed` 수 |
| 채팅 | 추천 입력 클릭률 | `ai_suggestion_clicked` 수 / `ai_suggestion_shown` 수 |
| 채팅 | 추천 입력 전송 비중 | `user_message_sent` 수 where `input_type=ai_suggestion` / `user_message_sent` 수 |
| 채팅 | 직접 입력 전송 비중 | `user_message_sent` 수 where `input_type=manual` / `user_message_sent` 수 |
| 채팅 | AI 응답 실패율 | `ai_response_failed` 수 / `user_message_sent` 수 |
| 피드백 | 피드백 제출률 | `feedback_submitted` 사용자 수 / `feedback_page_viewed` 사용자 수 |
| 피드백 | 입력 시작률 | `feedback_input_started` 수 / `feedback_page_viewed` 수 |
| 피드백 | 입력 시작 → 제출 성공률 | `feedback_submitted` 수 / `feedback_input_started` 수 |
| 피드백 | 제출 클릭 → 제출 성공률 | `feedback_submitted` 수 / `feedback_submit_clicked` 수 |
| 피드백 | 유효 피드백률 | `feedback_submitted` 중 `content_length >= 10` 비율 |
| 피드백 | 이메일 남김률 | `feedback_submitted` 중 `has_email=true` 비율 |
| 피드백 | 제출 실패율 | `feedback_submit_failed` 수 / `feedback_submit_clicked` 수 |

이탈과 취소는 분리해서 본다.

| 구분 | 정의 |
| --- | --- |
| 이탈 | 현재 단계 이후 다음 단계 이벤트가 30분 안에 발생하지 않은 경우 |
| 취소 | 사용자가 뒤로가기, 나가기, 다시 선택하기 등으로 현재 흐름을 명시적으로 벗어난 경우 |

## AN-1-5 스토리 제작 퍼널

스토리 제작 기본 퍼널은 화면 진입 이벤트를 기준으로 본다. 화면 안에서 발생하는 장르 선택, 키워드 추가, 스토리라인 반응 같은 행동은 세부 퍼널 또는 행동 사용률로 따로 분석한다.

| 순서 | 단계 | 이벤트 조건 | 전환율 |
| --- | --- | --- | --- |
| 1 | Step1 키워드 선택 화면 진입 | `story_create_step_viewed` where `step_number=1` | 기준 모수 |
| 2 | Step2 스토리라인 선택 화면 진입 | `story_create_step_viewed` where `step_number=2` | Step2 진입 / Step1 진입 |
| 3 | Step3 추가 정보 입력 화면 진입 | `story_create_step_viewed` where `step_number=3` | Step3 진입 / Step2 진입 |
| 4 | 완성 버튼 클릭 | `story_create_complete_clicked` where `step_number=3` | 완성 클릭 / Step3 진입 |
| 5 | 생성된 스토리 상세 화면 진입 | `story_detail_viewed` with `source=story_create` | 상세 진입 / 완성 클릭 |
| 6 | 채팅 시작 | `chat_start_clicked` | 채팅 시작 / 생성된 스토리 상세 진입 |

화면 안 세부 행동은 다음 보조 퍼널로 본다.

| 화면 | 분석 질문 | 기준 이벤트 | 세부 이벤트 또는 property |
| --- | --- | --- | --- |
| Step1 | 사용자가 어떤 입력 요소를 많이 쓰는가? | `story_create_step_viewed` where `step_number=1` | `story_create_option_clicked`, `story_create_option_tab_clicked`, `story_create_custom_keyword_add_clicked` |
| Step1 | 선택 상태가 다음 단계 이동에 영향을 주는가? | `story_create_next_clicked` where `step_number=1` | `selected_genre_count`, `selected_keyword_count`, `has_custom_keyword`, `custom_keyword_count` |
| Step2 | 스토리라인 후보가 선택으로 이어지는가? | `story_create_step_viewed` where `step_number=2` | `story_create_storyline_clicked`, `story_create_next_clicked`, `storyline_index`, `storyline_count` |
| Step2 | 재생성 또는 반응 행동이 많은가? | `story_create_step_viewed` where `step_number=2` | `story_create_regenerate_clicked`, `story_create_storyline_reaction_clicked`, `reaction_type` |
| Step3 | 추가 정보 입력이 완성 클릭으로 이어지는가? | `story_create_step_viewed` where `step_number=3` | `story_create_suggestion_clicked`, `story_create_complete_clicked`, `extra_info_count` |

스토리 제작 이벤트에 사용하는 custom properties는 다음과 같다.

| property | 설명 |
| --- | --- |
| `flow_name` | 제작 flow 이름. 값은 `story_create` |
| `step_number` | 제작 단계 번호. 예: `1`, `2`, `3` |
| `step_name` | 제작 단계 의미. 예: `keyword_selection`, `storyline_selection`, `extra_info` |
| `option_group` | 선택 옵션 묶음. 예: `genre`, `main_character`, `supporting_character` |
| `option_id` | 선택하거나 해제한 옵션 ID |
| `selected_genre_ids` | 선택한 장르 ID 목록 |
| `selected_genre_count` | 선택한 장르 수 |
| `selected_main_character_ids` | 선택한 주인공 성격 ID 목록 |
| `selected_main_character_count` | 선택한 주인공 성격 수 |
| `selected_supporting_character_ids` | 선택한 주변 인물 성격 ID 목록 |
| `selected_supporting_character_count` | 선택한 주변 인물 성격 수 |
| `selected_keyword_count` | 현재 선택된 전체 키워드 수 |
| `has_custom_keyword` | 직접 추가한 키워드 존재 여부 |
| `custom_keyword_count` | 직접 추가한 키워드 수 |
| `is_selected_after_click` | 클릭 후 선택 상태 |
| `keyword_length` | 직접 추가한 키워드 길이. 원문은 보내지 않는다. |
| `storyline_index` | 선택한 스토리라인 순서 |
| `storyline_count` | 노출된 스토리라인 후보 수 |
| `previous_storyline_count` | 다시 만들기 전 노출된 스토리라인 후보 수 |
| `reaction_type` | 스토리라인 반응. 예: `like`, `dislike` |
| `suggestion_index` | 선택한 AI 추천 추가 정보 순서 |
| `suggestion_count` | 노출된 AI 추천 추가 정보 수 |
| `feature` | AI 또는 서버 기능 구분. 예: `storyline_generation`, `story_completion` |
| `generation_time_ms` | AI 생성 소요 시간 |
| `error_code` | 생성 실패 코드 |
| `extra_info_count` | 추가 정보 입력 또는 선택 개수 |
| `extra_info_length_bucket` | 추가 정보 길이 구간 |
| `source` | 상세 화면 진입 출처. 스토리 생성 직후에는 `story_create` |
| `exit_step` | 사용자가 명시적으로 제작 흐름을 벗어난 단계 |
| `total_duration_ms` | 제작 시작부터 완료까지 걸린 시간 |

스토리 제작 이벤트별 properties는 다음처럼 매핑한다. 아래 표에는 공통 properties를 제외한 이벤트별 핵심 값만 적는다.

| 우선순위 | 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- | --- |
| P0 | `story_create_step_viewed` | 제작 단계 화면 진입 | `flow_name`, `step_number`, `step_name`, `entry_point`, `storyline_count`, `generation_time_ms` |
| P0 | `story_create_next_clicked` | Step1 또는 Step2에서 다음 버튼 클릭 | `flow_name`, `step_number`, `step_name`, `selected_genre_ids`, `selected_genre_count`, `selected_main_character_ids`, `selected_main_character_count`, `selected_supporting_character_ids`, `selected_supporting_character_count`, `selected_keyword_count`, `has_custom_keyword`, `custom_keyword_count`, `storyline_index`, `storyline_count` |
| P0 | `story_create_storyline_clicked` | Step2에서 스토리라인 후보 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `storyline_count` |
| P0 | `story_create_complete_clicked` | Step3에서 `스토리 완성하기` 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `extra_info_count`, `extra_info_length_bucket`, `total_duration_ms` |
| P0 | `story_detail_viewed` | 생성된 스토리 상세 화면 진입 | `story_id`, `source`, `has_existing_chat` |
| P0 | `chat_start_clicked` | 생성된 스토리 상세에서 채팅 시작 클릭 | `story_id`, `source` |
| P1 | `story_create_option_clicked` | Step1에서 옵션 선택 또는 선택 해제 | `flow_name`, `step_number`, `step_name`, `option_group`, `option_id`, `is_selected_after_click`, `selected_genre_count`, `selected_main_character_count`, `selected_supporting_character_count`, `selected_keyword_count` |
| P1 | `story_create_option_tab_clicked` | Step1에서 옵션 탭 클릭 | `flow_name`, `step_number`, `step_name`, `option_group`, `selected_genre_count`, `selected_keyword_count` |
| P1 | `story_create_custom_keyword_add_clicked` | Step1에서 직접 키워드 추가 클릭 | `flow_name`, `step_number`, `step_name`, `custom_keyword_count`, `keyword_length` |
| P1 | `story_create_loading_shown` | AI 생성 로딩 상태 노출 | `flow_name`, `step_number`, `step_name`, `feature`, `request_id` |
| P1 | `story_create_error_shown` | AI 생성 실패 상태 노출 | `flow_name`, `step_number`, `step_name`, `feature`, `error_code`, `generation_time_ms`, `total_duration_ms` |
| P1 | `story_create_regenerate_clicked` | Step2에서 다시 만들기 클릭 | `flow_name`, `step_number`, `step_name`, `feature`, `storyline_count`, `previous_storyline_count` |
| P1 | `story_create_storyline_reaction_clicked` | Step2에서 스토리라인 좋아요 또는 싫어요 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `reaction_type` |
| P1 | `story_create_suggestion_clicked` | Step3에서 AI 추천 추가 정보 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `suggestion_index`, `suggestion_count`, `extra_info_count` |
| P1 | `story_create_extra_info_focused` | Step3에서 직접 입력창 포커스 | `flow_name`, `step_number`, `step_name`, `storyline_index` |
| P1 | `story_create_exit_clicked` | 제작 중 뒤로가기, 닫기, 나가기 클릭 | `flow_name`, `step_number`, `step_name`, `exit_step`, `total_duration_ms` |

## AN-1-6 채팅 퍼널

채팅 퍼널은 `chat_start_clicked` 또는 `chat_room_viewed`를 기준으로 본다. 스토리 상세에서 채팅으로 잘 이어지는지는 `chat_start_clicked`를 기준으로 보고, 채팅방 안에서의 몰입은 `chat_room_viewed`를 기준으로 본다.

| 순서 | 단계 | 이벤트 | 전환율 |
| --- | --- | --- | --- |
| 1 | 채팅 시작 클릭 | `chat_start_clicked` | 기준 모수 |
| 2 | 채팅방 진입 | `chat_room_viewed` | 채팅방 진입 / 채팅 시작 클릭 |
| 3 | 첫 입력 의도 | `chat_input_focused` 또는 `ai_suggestion_clicked` | 입력 의도 / 채팅방 진입 |
| 4 | 첫 메시지 전송 | `user_message_sent` with `turn_index=1` | 첫 메시지 / 채팅방 진입 |
| 5 | AI 응답 성공 | `ai_response_received` | AI 응답 / 사용자 메시지 |
| 6 | 2턴 진행 | `user_message_sent` with `turn_index=2` | 2턴 진행 / 첫 메시지 |
| 7 | 5턴 진행 | `user_message_sent` with `turn_index=5` | 5턴 진행 / 채팅방 진입 |

채팅 중 공통으로 사용하는 properties는 다음과 같다.

| property | 설명 |
| --- | --- |
| `chat_id` | 채팅 ID |
| `story_id` | 연결된 스토리 ID |
| `turn_index` | 사용자 메시지 기준 턴 번호 |
| `input_type` | 입력 방식. 예: `manual`, `ai_suggestion` |
| `suggestion_index` | 선택한 AI 추천 입력 순서 |
| `suggestion_count` | 노출된 AI 추천 입력 수 |
| `message_count` | 채팅방에 저장된 메시지 수 |
| `message_length_bucket` | 메시지 길이 구간. 예: `1_20`, `21_50`, `51_100`, `101_plus` |
| `response_time_ms` | AI 응답 소요 시간 |
| `error_code` | AI 응답 실패 코드 |
| `exit_after_turn` | 사용자가 나간 시점의 턴 번호 |
| `entry_point` | 채팅방 진입 경로. 예: `story_detail`, `chat_list` |

## AN-1-7 페이지별 이벤트 스펙

### AN-1-7-1 스토리 목록

목적은 스토리 제작 진입과 기존 스토리 재방문을 확인하는 것이다.

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `story_list_viewed` | 스토리 목록 화면 진입 | `is_empty`, `story_count` |
| `story_create_cta_clicked` | `스토리 만들기` 또는 `만들기` 클릭 | `entry_point`, `is_empty`, `story_count`, `chat_count`, `cta_type` |
| `story_card_clicked` | 스토리 카드 클릭 | `story_id`, `story_position`, `genre_tags` |
| `story_menu_clicked` | 스토리 카드의 메뉴 클릭 | `story_id`, `story_position` |

`story_create_cta_clicked`는 스토리 목록과 채팅 목록 양쪽에서 발생한다. 두 화면에서 같은 property 집합(`entry_point`, `is_empty`, `story_count`, `chat_count`, `cta_type`)을 보내고, 진입 화면 구분은 공통 property인 `screen_name`으로 한다.

### AN-1-7-2 스토리 상세

목적은 생성된 스토리가 채팅 시작으로 이어질 만큼 매력적인지 확인하는 것이다.

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `story_detail_viewed` | 스토리 상세 화면 진입 | `story_id`, `source`, `has_existing_chat`, `genre_tags`, `start_situation_count` |
| `story_detail_scrolled` | 상세 설명 또는 시작 상황 영역 스크롤 | `story_id`, `source`, `scroll_depth` |
| `chat_start_clicked` | `채팅 시작하기` 클릭 | `story_id`, `source`, `has_existing_chat` |
| `story_detail_back_clicked` | 뒤로가기 클릭 | `story_id`, `source` |
| `story_detail_menu_clicked` | 상세 화면 메뉴 클릭 | `story_id`, `source` |

`source` 값은 다음 값만 사용한다.

| 값 | 의미 |
| --- | --- |
| `story_list` | 스토리 목록에서 진입 |
| `story_create` | 스토리 생성 직후 진입 |
| `chat_list` | 채팅 목록에서 연결 진입 |

### AN-1-7-3 스토리 제작

목적은 간편 모드 제작 과정에서 사용자가 어디서 막히는지 확인하는 것이다.

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `story_create_step_viewed` | 제작 단계 화면 진입 | `flow_name`, `step_number`, `step_name`, `entry_point`, `storyline_count`, `generation_time_ms` |
| `story_create_option_tab_clicked` | Step1에서 옵션 탭 클릭 | `flow_name`, `step_number`, `step_name`, `option_group`, `selected_genre_count`, `selected_keyword_count` |
| `story_create_option_clicked` | Step1에서 옵션 선택 또는 선택 해제 | `flow_name`, `step_number`, `step_name`, `option_group`, `option_id`, `is_selected_after_click`, `selected_genre_count`, `selected_main_character_count`, `selected_supporting_character_count`, `selected_keyword_count` |
| `story_create_custom_keyword_add_clicked` | Step1에서 직접 키워드 추가 클릭 | `flow_name`, `step_number`, `step_name`, `custom_keyword_count`, `keyword_length` |
| `story_create_next_clicked` | Step1 또는 Step2에서 다음 버튼 클릭 | `flow_name`, `step_number`, `step_name`, `selected_genre_ids`, `selected_genre_count`, `selected_main_character_ids`, `selected_main_character_count`, `selected_supporting_character_ids`, `selected_supporting_character_count`, `selected_keyword_count`, `has_custom_keyword`, `custom_keyword_count`, `storyline_index`, `storyline_count` |
| `story_create_loading_shown` | AI 생성 로딩 상태 노출 | `flow_name`, `step_number`, `step_name`, `feature`, `request_id` |
| `story_create_error_shown` | AI 생성 실패 상태 노출 | `flow_name`, `step_number`, `step_name`, `feature`, `error_code`, `generation_time_ms`, `total_duration_ms` |
| `story_create_regenerate_clicked` | Step2에서 다시 만들기 클릭 | `flow_name`, `step_number`, `step_name`, `feature`, `storyline_count`, `previous_storyline_count` |
| `story_create_storyline_reaction_clicked` | Step2에서 스토리라인 좋아요 또는 싫어요 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `reaction_type` |
| `story_create_storyline_clicked` | Step2에서 스토리라인 후보 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `storyline_count` |
| `story_create_suggestion_clicked` | Step3에서 AI 추천 추가 정보 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `suggestion_index`, `suggestion_count`, `extra_info_count` |
| `story_create_extra_info_focused` | Step3에서 직접 입력창 포커스 | `flow_name`, `step_number`, `step_name`, `storyline_index` |
| `story_create_complete_clicked` | Step3에서 `스토리 완성하기` 클릭 | `flow_name`, `step_number`, `step_name`, `storyline_index`, `extra_info_count`, `extra_info_length_bucket`, `total_duration_ms` |
| `story_create_exit_clicked` | 제작 중 뒤로가기, 닫기, 나가기 클릭 | `flow_name`, `step_number`, `step_name`, `exit_step`, `total_duration_ms` |

제작 단계 값은 다음 값만 사용한다.

| step_number | step_name | screen_name |
| --- | --- | --- |
| `1` | `keyword_selection` | `story_create_keyword_selection` |
| `2` | `storyline_selection` | `story_create_storyline_selection` |
| `3` | `extra_info` | `story_create_extra_info` |

장르와 성격 값은 원문 대신 관리되는 ID만 `option_id`로 보낸다.

| option_group | 의미 |
| --- | --- |
| `genre` | 선택하거나 해제한 장르 |
| `main_character` | 선택하거나 해제한 주인공 성격 |
| `supporting_character` | 선택하거나 해제한 주변 인물 성격 |

### AN-1-7-4 채팅 목록

목적은 사용자가 진행 중인 채팅을 다시 이어가는지 확인하는 것이다.

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `chat_list_viewed` | 채팅 목록 화면 진입 | `is_empty`, `chat_count` |
| `story_create_cta_clicked` | 빈 채팅 목록에서 `스토리 만들기` 클릭 | `entry_point`, `is_empty`, `story_count`, `chat_count`, `cta_type` |
| `story_create_step_viewed` | Step1 키워드 선택 화면 진입 | `entry_point`, `screen_name`, `flow_name`, `step_number`, `step_name` |
| `chat_thread_clicked` | 채팅 항목 클릭 | `chat_id`, `story_id`, `message_count`, `thread_position`, `last_active_at` |
| `chat_thread_menu_clicked` | 채팅 항목 메뉴 클릭 | `chat_id`, `story_id`, `thread_position` |

### AN-1-7-5 채팅

목적은 사용자가 AI 추천 또는 직접 입력으로 이야기를 이어가는지 확인하는 것이다.

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

### AN-1-7-6 피드백

목적은 MVP 개선에 필요한 불편, 니즈, 기능 요청을 수집하는 것이다.

| 이벤트 | 발생 시점 | 핵심 properties |
| --- | --- | --- |
| `feedback_page_viewed` | 피드백 화면 진입 | `entry_point`, `last_screen_name` |
| `feedback_input_started` | 피드백 입력 시작 | `entry_point`, `last_screen_name` |
| `feedback_submit_clicked` | `피드백 보내기` 클릭 | `content_length`, `has_email` |
| `feedback_submitted` | 피드백 제출 성공 | `content_length`, `has_email` |
| `feedback_submit_failed` | 피드백 제출 실패 | `content_length`, `has_email`, `error_code` |

## AN-1-8 개인정보와 원문 수집 원칙

MVP 분석 이벤트에는 사용자가 입력한 원문을 직접 넣지 않는다.

| 데이터 | 이벤트 property 포함 여부 | 처리 방식 |
| --- | --- | --- |
| 피드백 본문 | 포함하지 않음 | 별도 저장소에 저장한다. 이벤트에는 `content_length`만 남긴다. |
| 이메일 | 포함하지 않음 | 별도 저장소에 저장한다. 이벤트에는 `has_email`만 남긴다. |
| 채팅 메시지 원문 | 포함하지 않음 | 이벤트에는 `message_length_bucket`과 `input_type`만 남긴다. |
| 직접 추가 키워드 원문 | 원칙적으로 포함하지 않음 | 필요하면 별도 정책을 정한 뒤 저장한다. 이벤트에는 `keyword_length`만 남긴다. |

## AN-1-9 MVP 우선 적용 이벤트

처음부터 모든 이벤트를 심기 어렵다면 아래 이벤트를 우선 적용한다.

| 우선순위 | 이벤트 |
| --- | --- |
| P0 | `story_list_viewed` |
| P0 | `story_create_cta_clicked` |
| P0 | `story_create_step_viewed` |
| P0 | `story_create_next_clicked` |
| P0 | `story_create_storyline_clicked` |
| P0 | `story_create_complete_clicked` |
| P0 | `story_card_clicked` |
| P0 | `story_detail_viewed` |
| P0 | `chat_start_clicked` |
| P0 | `chat_list_viewed` |
| P0 | `chat_thread_clicked` |
| P0 | `chat_room_viewed` |
| P0 | `user_message_sent` |
| P0 | `ai_response_received` |
| P0 | `feedback_page_viewed` |
| P0 | `feedback_submitted` |
| P1 | `story_menu_clicked` |
| P1 | `story_detail_scrolled` |
| P1 | `story_detail_back_clicked` |
| P1 | `story_detail_menu_clicked` |
| P1 | `chat_thread_menu_clicked` |
| P1 | `story_create_option_clicked` |
| P1 | `story_create_option_tab_clicked` |
| P1 | `story_create_custom_keyword_add_clicked` |
| P1 | `story_create_loading_shown` |
| P1 | `story_create_error_shown` |
| P1 | `story_create_regenerate_clicked` |
| P1 | `story_create_storyline_reaction_clicked` |
| P1 | `story_create_suggestion_clicked` |
| P1 | `story_create_extra_info_focused` |
| P1 | `story_create_exit_clicked` |
| P1 | `ai_suggestion_shown` |
| P1 | `ai_suggestion_clicked` |
| P1 | `chat_input_focused` |
| P1 | `ai_response_failed` |
| P1 | `chat_room_exited` |
| P1 | `feedback_input_started` |
| P1 | `feedback_submit_clicked` |
| P1 | `feedback_submit_failed` |

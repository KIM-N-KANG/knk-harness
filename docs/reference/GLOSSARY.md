# 용어집

이 문서는 **마냑 서비스의 모든 레포지토리와 문서에서 통일해 사용할 용어**를 정의하는 용어 스펙이다. 같은 개념에 서로 다른 단어를 쓰지 않도록 공식 한국어 용어, 영문 식별자, 지양 표기를 확정한다. 새 코드, 새 문서, 새 이벤트를 작성할 때 이 문서의 용어를 기준으로 삼는다.

<br>

### 1 목적과 적용 범위

이 문서는 다음 범위에 적용한다.

1. **제품, 문서 용어(한국어)**, 스펙 문서, 커밋 메시지, PR, UI 카피에서 쓰는 도메인 단어.
2. **코드 식별자(영문)**, API 필드, DB 테이블, 컬럼, 로그 필드, 분석 이벤트, 프로퍼티, 모듈, 타입 이름.

적용 규칙은 다음과 같다.

- **신규 작성 강제, 기존 코드 점진 적용.** 새로 만드는 이름은 이 문서를 따른다. 이미 배포된 계약(API 필드, DB 컬럼, 적재된 이벤트)은 마이그레이션 비용을 고려해 별도 과제로 정리하고, 이 문서는 대응 관계만 고정한다.
- **확정된 용어만 정의한다.** 의사결정 대기 상태의 초안 용어는 편입하지 않고, 명세가 확정된 뒤 반영한다.

<br>

### 2 용어 결정 원칙

여러 후보 중 공식 용어를 고를 때 다음 순서로 판단했다. 새 용어를 추가할 때도 같은 순서를 적용한다.

1. **개념이 다르면 단어도 다르게.** 서로 다른 개념(예: 추천 입력 vs 선택지)이 같은 단어를 공유하지 않는다.
2. **데이터 계층의 현행 표기를 우선.** DB, API, 이벤트에 이미 넓게 자리 잡은 표기를 UI 카피보다 우선한다.
3. **업계 표준과 정합.** 대응하는 업계 표준 용어(chat, turn, choice, lorebook, tag, anonymous user 등)가 있으면 따른다. 근거는 §7에 정리한다.
4. **미래 용어와 충돌 예방.** 로드맵에 예약된 이름(예: 트리거형 `keyword_notes`)과 겹치는 표기를 피한다.

<br>

### 3 핵심 도메인 용어

각 표의 `지양 표기`는 같은 개념에 쓰지 않을 단어이다. 문학적 서술이나 UI 감성 카피에서의 예외는 각 항목에 명시한다. 과거 구조나 예약된 이름은 해당 항목에서 구분한다. 현재 사용자 계약과 구현 범위는 도메인 명세를 따른다.

<br>

### 3-1 콘텐츠 단위

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 스토리 | `story`, `story_id` | 사용자가 제작, 플레이하는 세계관, 설정 콘텐츠 단위. 외부 노출 식별자는 UUID `story_id` | "이야기"(API 문서, 식별자, 오류 메시지), "세계관"(스토리 전체를 가리킬 때) |
| 오리지널 스토리 | original story | 마냑 공식 계정이 소유한 공개(`PUBLISHED`, `PUBLIC`) 스토리. 제작 없이도 플레이할 거리를 주려고 홈(`/`)에 노출한다. 홈은 공개 스토리 목록의 "오리지널" 필터로 오리지널만 모아 보고, 내가 만든 스토리는 제작 탭(`/studio`)이 담당한다(KNK-988 화면 분리, KNK-994 URL 변경, KNK-1421 필터, [3-1 화면 구성](../domain/STORY/CLIENT/3-1-INFORMATION-ARCHITECTURE.md)). 조회는 `GET /stories?filter=original`이며 인증이 필요 없다(`GET /stories/originals`는 폐기 예정) | "공식 스토리", "추천 스토리"(추천 로직이 없음), "마냑 스토리" |
| 스토리라인 | `storyline`, `storyline_id` | 간편 제작에서 AI가 생성하는 이야기 전개 방향 후보(3개 중 택1). 스토리가 되기 전 단계의 산출물 | `example`(레거시 표기), 스토리라인 본문을 담는 `story` 필드 |
| 스토리 설정 | `story_settings` | 통글 4필드 묶음: `world_setting`(세계관), `character_setting`(등장인물), `user_role_setting`(주인공), `rule_setting`(규칙) | `prompt_settings`(컴파일 내부 세분 스키마 전용, §6) |
| 통글 | (한국어 고유 조어) | 섹션 헤더로 구분한 단일 마크다운 필드. 스토리 설정의 저장, 전달 단위 | 없음 |
| 시작 설정 | `start_settings` | 채팅 시작 장면 3필드: `name`(상황 이름), `start_situation`(시작 상황), `prologue`(프롤로그) | 단수, 복수, 접두어가 다른 변형 신설 금지 |
| 프롤로그 | `prologue` | 채팅 시작 시 먼저 보여주는 도입 서사 텍스트 | "채팅 첫 메시지", "도입부 내레이션", first message, greeting |
| 추천 입력 | `suggested_inputs` | 채팅 시작 화면에서 제안하는 첫 입력 후보 문구(3개). 선택지(§3-3)와 다른 개념 | `recommendedInputs`, 선택지를 "추천 입력"으로 부르는 것 |
| 태그 | `tag`, `tag_id` | 간편 제작에서 선택하거나 직접 추가하는 스토리 속성. `PREDEFINED`(제공)와 `CUSTOM`(직접 추가)으로 나뉨. 직접 추가 태그의 동일성은 정규화 키(trim → 내부 공백 제거 → lowercase)로 판정하고 표시명은 최초 입력의 trim본 유지([간편 제작 계약](../domain/STORY/BACKEND/4-2-CONTRACT.md#4-2-11-간편-제작-스토리라인-생성)) | "키워드"(코드, 데이터, 이벤트, 문서. UI 카피 전환은 별도 논의) |
| 태그 카테고리 | `category`: `GENRE`, `PROTAGONIST`, `SUPPORTING_CHARACTER` | 태그 분류 3종: 장르, 주인공 특징, 주변 인물 특징. 주인공, 주변 인물은 특징 태그 묶음이 아니라 인물 단위(이름, 성별, 특징)로 입력받는다. 직접 추가 태그는 카테고리별 배열이 아니라 인물별 `customTags`로 전송된다. 장르는 제공 장르만 고르며 `customGenreTags`는 제공 장르 전환 전 요청의 호환 필드로만 남는다([2-2-5 장르 검색](../domain/STORY/CLIENT/2-2-REQUIREMENTS.md#2-2-5-장르-검색)). 과거 확장 계획(KNK-621)의 `BACKGROUND`(배경)를 추가해 4종으로 확장하고 장르, 배경을 UI에서 "세계관" 탭으로 묶는 것은 미구현([간편 제작 계약](../domain/STORY/BACKEND/4-2-CONTRACT.md#4-2-11-간편-제작-스토리라인-생성)) | `tag_type` |
| 제공 장르 | `genres`(`GET /stories/genres`), `genreTagIds` | 서버가 관리하는 활성 장르 목록(KNK-1537). 클라이언트는 직접 입력 대신 이 목록에서 검색해 고르며, id는 장르 태그 id와 같다([4-2-4 제공 장르](../domain/STORY/BACKEND/4-2-CONTRACT.md#4-2-4-제공-장르)) | 없음 |
| 대표 장르 | `featuredGenres` | 제공 장르 중 칩으로 먼저 보이는 15개. 검색어와 관계없이 대표 순서로 받는다 | 없음 |
| 추가 정보 | `additional_infos` | 사용자가 스토리라인에 첨부하는 보강 정보(추천 채택분 포함, 총 13개 상한) | `extra_info` |
| 추천 추가 정보 | `recommended_infos` | 스토리라인마다 AI가 제안하는 추가 정보 후보 3개 | "추천 질문"(`questions`, 레거시) |
| 로어북 | `lorebook` | 장르 공용 용어 사전. 트리거 키워드 없는 카탈로그 | world info |
| 화풍 | `art_style` / `ArtStyle` | 간편 제작의 인물 이미지와 표지에 함께 적용하는 그림체. `NONE`은 이미지 생성 생략이며 표시 목록은 [서버 카탈로그](../domain/STORY/BACKEND/4-2-CONTRACT.md#4-2-10-화풍-목록)가 정한다 | 그림체는 설명문에서 허용 |
| 키워드북 | `keyword_notes` | 특정 키워드가 입력되면 반응, 사건을 트리거하는 키워드-반응 저장소. 트리거 없는 로어북과 구분 | 로어북 |
| 주요 사건 | `main_event` | 스토리 전개의 방향을 제시하는 사건 후보. 이름, 설명과 키 문장을 포함하며 AI가 본문과 선택지 생성에 참고한다. 서비스가 사건 진행이나 완결을 판정하지 않는다. ([채팅 태스크](../domain/CHAT/AI/3-TASK-DEFINITION.md#3-2-채팅-응답-생성)) | "메인 이벤트" |
| 키 문장 | `key_sentence` | 주요 사건의 의미를 설명하는 입력 문장. 현재 채팅 생성의 참고 정보이며 별도 사건 관련성 판정의 실행 조건이 아니다. ([채팅 계약](../domain/CHAT/AI/5-CONTRACT.md#5-2-채팅-턴-요청과-결과)) | "트리거 문장"(키워드북 트리거와 혼동) |
| 목표 사건 | `target_main_event` | 과거 사건 진행 판정에서 사용한 호환 필드. AI는 요청에 이 값이 있어도 사용하지 않으며 사건 진행 상태를 새로 판정하지 않는다. ([KNK-1626 결정](../domain/CHAT/AI/DECISIONS.md)) | "진행 중 사건", "현재 사건" |
| 엔딩 | `ending` | 스토리의 결말 후보와 서술 가이드. 현재 AI가 본문 생성에 참고하며 서비스는 엔딩 도달을 별도로 판정하지 않는다. 입력의 스키마와 개수는 STORY 계약을 따른다. ([스토리 계약](../domain/STORY/BACKEND/4-2-CONTRACT.md), [채팅 태스크](../domain/CHAT/AI/3-TASK-DEFINITION.md)) | 없음 |
| 엔딩 조건 | `ending_requirement` | 엔딩 후보의 조건을 설명하는 입력. 최소 턴 수와 달성 조건을 조합한 과거 판정은 KNK-1626으로 폐기됐다. 현재 엔딩 도달을 기록하는 활성 판정 규칙으로 사용하지 않는다. ([채팅 결정](../domain/CHAT/AI/DECISIONS.md)) | `condition_text`(현행 구현 표기), `goal`, `main_event_names`(분리 구조, 폐기) |
| 엔딩 에필로그 | `ending_epilogue` | 엔딩 후보의 서술 방향을 설명하는 입력 가이드. 현재 본문 생성의 참고 정보이며 별도 도달 판정 이후 실행하는 단계가 아니다. ([채팅 태스크](../domain/CHAT/AI/3-TASK-DEFINITION.md)) | "엔딩 출력 가이드"는 설명문에서 허용 |
| 엔딩 도달 | ending reached | 과거 채팅 판정에서 엔딩을 달성했다고 기록한 상태. 현재 AI는 사건과 엔딩을 판정하지 않는다. 기존 데이터의 표시와 현재 본문의 결말 서술을 구분한다. ([채팅 결정](../domain/CHAT/AI/DECISIONS.md)) | "엔딩 완료", "클리어" |
| 썸네일 | thumbnail | 스토리의 대표 이미지. 등록 시 팀 프리셋을 자동 연결하지 않는다. 간편 제작은 AI 생성 표지를 사용하고 생성에 실패하면 표지는 null이다. 소유자가 업로드한 이미지는 생성 이미지를 대체한다. URL이 있고 검수 승인 상태이면 URL, 아니면 기존 프리셋 키의 표지를 사용하며 둘 다 없으면 null이다. 표지를 삭제하면 URL과 프리셋 키를 모두 지운다. null이면 프론트엔드가 라이트 모드와 다크 모드에 맞는 기본 이미지를 표시한다 | "커버". 와이어는 `thumbnailUrl`과 `thumbnailUrlSm`을 사용한다 |
| 스토리 이미지 | `story_images`, `trigger_text`(과거 표기) | 과거 일반 제작의 이미지와 트리거 구조를 나타내던 용어. 현재 저장과 채팅 전달은 인물별 `story_character_images`와 `character_images`를 따른다. ([인물과 이미지](../domain/STORY/BACKEND/3-2-DB-SCHEMA.md#3-2-5-인물과-이미지)) | 현재 인물 이미지와 과거 트리거 구조의 혼용 |
| 인물 이미지 이름 | `image_name`(AI 요청), `imageName`(SSE, 응답) | 인물의 이미지 한 장을 구분하는 이름. 스토리라인 컴파일 출력의 `character_images[].image_name`과 채팅 이미지 식별에 사용한다. 요청, 응답과 저장 위치는 각 계약을 따른다. ([컴파일 계약](../domain/STORY/AI/5-CONTRACT.md#5-3-컴파일-요청과-결과), [채팅 계약](../domain/CHAT/AI/5-CONTRACT.md#5-2-채팅-턴-요청과-결과)) | "표정"(이름의 일부일 뿐 이름 자체가 아님) |

<br>

### 3-2 제작 흐름

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 제작 | creation | **사용자가** 스토리를 만드는 행위와 퍼널 전체. 예: 스토리 제작 완료율 | 사용자 행위에 "생성" 사용. UI 버튼 카피 "만들기"는 허용 |
| 생성 | generation | **AI가** 산출물을 만드는 행위. 예: 스토리라인 생성, 응답 생성 | AI 행위 식별자에 `create` 사용(`generate` 계열로 통일) |
| 간편 제작 | simple creation | 태그 선택 → 스토리라인 선택 → 추가 정보의 3단계 제작 방식 | "간편 모드"(레거시) |
| 일반 제작 | general creation | 스토리 구성 항목을 폼에 직접 입력하는 제작 방식. 신규 등록, 저장, 수정과 재제출의 범위는 STORY 요구사항을 따른다. ([일반 제작과 수정](../domain/STORY/CLIENT/3-2-INTERACTION-FLOWS.md#3-2-3-일반-제작과-수정)) | "일반 모드", "일반 모드 제작". 채팅 입력 모드 "일반 입력"(`NORMAL`)과 다른 개념(§5) |
| 스토리 수정 | edit | 사용자가 이미 등록된 스토리의 설정을 고치는 행위 | "스토리 편집"("편집"은 채팅 산출물, AI 응답, 메모리, 전용) |
| 제품 분석 제작 진행 ID | `analytics_creation_id` | 간편 제작 1회 진행(세션) 단위의 식별자. 원본은 DB PK `story_creation_sessions.id`(Long), 와이어는 `simpleCreationId`, 분석 이벤트에는 문자열로 변환해 싣는다. **분석 이벤트의 와이어 키 이름이 `creation_id`이므로 아래 항목과 혼동 금지, 서로 다른 값이며 직접 조인할 수 없다**([분석과 관측 기준](ANALYTICS.md)) | 로그 필드 `simple_creation_id`. 개념 이름 없이 `creation_id`로만 쓰지 않기 |
| AI 트레이스 연결 ID | `trace_creation_id` | 간편 제작 **스토리라인 생성 요청**의 클라이언트 생성 UUID(`story_creation_requests.request_id`). Langfuse 트레이스를 진행 단위로 묶는 열쇠이며 전달 헤더는 `X-Manyak-Creation-Id`이고 Langfuse metadata 키는 `creation_id`이다. `ai_call_logs.creation_id`는 계획 컬럼이며 현재 DB 스키마에는 없다([제작 추적 헤더](../domain/STORY/BACKEND/5-4-OBSERVABILITY.md#5-4-3-ai-서버로-전달하는-헤더)). 위 진행(세션) ID와 **다른 값**이다. 세션 PK는 스토리라인 AI 호출이 성공해야 생겨 그 최초 호출 시점에는 전달할 수 없다 | 위 제품 분석 ID와 혼동 금지. 두 값을 직접 조인하지 않기 |
| 제작 단계 | `step_name`: `keyword`, `storylineSelect`, `additionalInfo`, `complete` | 간편 제작 퍼널의 4단계. 분석 표기 기준이며 라우팅 슬러그(kebab-case)와의 매핑은 §4 | 없음 |
| 컴파일 | compile | 선택한 스토리라인 + 추가 정보 + 태그를 스토리 명세로 확장하는 AI 호출. 간편 제작의 완성 단계에서 실행 | 관측 feature 값 `story_completion`은 이 호출의 역사적 명칭, 적재 데이터 연속성을 위해 유지하되 새 이름에 쓰지 않음 |
| 완성 | completion | **사용자 관점**에서 스토리 제작을 끝내는 퍼널 단계 | 컴파일(AI 호출)과 혼용 금지 |
| 스토리라인 평가 | `rating`: `GOOD`, `BAD` | 스토리라인에 남기는 좋아요/싫어요 평가 | "좋아요"(스토리 `like`와 혼동) |
| 좋아요 | `like_count` | 스토리에 대한 좋아요 수. 실 집계 전환, 등록/취소 API는 KNK-1024([스토리 좋아요 계약](../domain/STORY/BACKEND/4-2-CONTRACT.md#4-2-21-좋아요)) | 없음 |
| 싫어요 | `dislike` | 스토리에 대한 부정 반응. **도입하지 않기로 결정(2026-08-28)**, 스토리 반응은 좋아요(like)만 둔다(KNK-1024) | 스토리라인 평가(GOOD/BAD)와 혼동 |
| 찜 | `wishlist` | 스토리를 찜 목록(위시리스트)에 담는 행위 | "북마크", "즐겨찾기" |

<br>

### 3-3 플레이(채팅) 단위

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 페르소나 | `persona`, `personaId` | 회원 계정에 저장한 플레이용 이름과 설명. 채팅 시작 시 선택하면 기본 주인공 이름과 설명을 통째로 대체하며 시작 시 스냅샷은 원본 수정, 삭제 뒤에도 유지한다 | 닉네임이나 계정 프로필과 혼용 |
| 기본 주인공 이름 | `protagonistName`(클라이언트), `protagonist_name`(DB, AI) | 스토리에 저장한 주인공 이름. 페르소나를 선택하지 않은 채팅과 채팅 밖의 이름 토큰 치환에 사용한다. 기존 스토리는 null | 페르소나 이름과 혼용 |
| 플레이 이름 | 없음 | 채팅에서 주인공을 부르는 이름. 페르소나를 선택했으면 페르소나 이름, 아니면 기본 주인공 이름 | "채팅 이름", 기본 주인공 이름과 혼용 |
| 이름 토큰 | `{username}` | 스토리 원문에서 주인공 이름을 나타내는 문자열. 백엔드가 표시, AI 채팅 요청 시 이름과 조사를 치환한다. 편집, 검수는 원문을 유지한다 | 클라이언트 템플릿 변수나 회원 닉네임으로 해석 |
| 채팅 | `chat`, `chat_id` | 스토리를 기반으로 진행하는 플레이 세션. 저장, 이어쓰기, 삭제의 단위. 외부 노출 식별자는 UUID `chat_id` | "대화"(식별자, 계약. 설명문에서는 허용), play session(레거시 표기), "스토리 플레이", "채팅 플레이", "체험 플레이", "세션" |
| 채팅 화면 | 없음 | 개별 채팅을 플레이하는 화면(`/chats/[id]`) | "채팅방"(구어. 코드 `room` 계열 식별자 신설 금지) |
| 턴 | `turn`, `turn_number` | 사용자 입력 한 번과 그에 대한 AI 출력 한 번의 단위. 선택지는 별도 요청으로 생성하며 표시 여부는 설정에 따른다. `turn_number`는 사용자 입력 기준 1부터 센다 | 메시지와 혼용 금지 |
| 메시지 | `message` | 턴을 구성하는 개별 발화 저장 행. `role`: `USER`, `ASSISTANT`, `SYSTEM` | 없음 |
| 사용자 입력 | `userInput` | 턴에서 사용자가 보낸 텍스트(최대 3,000자) | 없음 |
| 입력 모드 | `input_mode`: `NORMAL`, `BLOCK` | 채팅 사용자 입력 방식 2종. **일반 입력**은 한 칸에 자유 텍스트로 쓰고 강조 마크업(`*...*`)으로 상황, 행동을 표기한다. **블럭 입력**은 상황, 대사 추가 버튼으로 입력 칸을 하나씩 늘려 각 칸을 채우면 프론트엔드가 조합해 하나의 `userInput`으로 보낸다(마크업이 익숙지 않은 사용자용) | "인풋 모드" |
| AI 출력(본문) | `aiOutput` | 선택지를 제외한 AI 생성 본문(상황 묘사 + 인물 대사) | "답변", "응답" 단독 표기(HTTP 응답과 혼동, "AI 응답", "엔딩 응답"처럼 수식어를 붙인 설명문 표기는 허용), `output` 단독 표기 |
| 선택지 | `choice`, `choices` | AI가 제안하는 다음 행동 후보 3개. 사건 진행 방향, 다른 사건 방향과 자유 맥락의 후보를 구성한다. 본문 생성과 별도 API이며 선택된 행동만 다음 사용자 입력에 사용한다. ([선택지 태스크](../domain/CHAT/AI/3-TASK-DEFINITION.md#3-4-선택지-생성)) | next actions(AI 내부 잔존 표기), "다음 행동 선택지", "AI 추천 선택지", "추천 입력"(다른 개념, §3-1) |
| 이어쓰기 | continue | 기존 채팅에 턴을 추가하는 행위 | UI 카피 "이어가기"는 허용 |
| 재생성 | regenerate | 마음에 들지 않는 AI 출력(본문)을 같은 턴에서 다시 생성하는 행위. 스토리라인 재생성과 대상이 다르므로 "응답 재생성", "스토리라인 재생성"처럼 대상을 명시 | "리롤"(구어) |
| 생성 ID | `generationId` | 이어쓰기나 재생성으로 시작한 생성 하나를 가리키는 UUID. `started` 이벤트와 채팅 상세의 `generatingTurn`으로 받고 재연결에 쓴다 | 스토리 생성의 요청 ID(`requestId`)와 혼용 |
| 생성 이어받기 | 없음 | 연결이 끊기거나 채팅 화면에 다시 들어왔을 때 같은 생성의 이벤트를 처음부터 다시 받아 생성 중 화면을 이어 가는 클라이언트 동작. 생성과 과금은 반복하지 않는다 | "재시도"(생성을 다시 하는 것으로 오해) |
| 채팅 이미지 | chat image | 채팅 본문과 함께 표시하는 이미지. 저장 이미지와 실시간 생성 이미지를 구분하며 설정과 결과에 따른 표시는 CHAT 계약을 따른다. ([이미지 계약](../domain/CHAT/CLIENT/2-2-REQUIREMENTS.md)) | "이미지 생성"(Phase 3 개념과 혼동) |
| 실시간 이미지 | `realtimeImage` | 채팅 턴 진행 중 AI가 그 장면에 맞춰 새로 생성하는 이미지. [AI 스펙](../domain/CHAT/AI/6-1-AI-EXECUTION.md#6-1-2-실시간-이미지)의 “자식 이미지”와 같은 대상이며 클라이언트, 백엔드 계약에서는 실시간 이미지(`realtimeImage`)를 쓴다. 인물의 기본 이미지(AI 스펙의 “부모 이미지”)와 구분한다 | 클라이언트, 백엔드 계약에서 “자식 이미지” 표기 |
| 채팅 모델 | `model`: `LITE`, `AURORA` | 채팅 AI 출력(본문)을 생성할 모델. 서버가 채팅마다 저장하고 채팅 화면 헤더 모델 버튼이 여는 채팅 응답 시트에서 고른다. 사용자 표기는 서버 모델 목록의 이름(라이트, 오로라)이다([모델 목록](../domain/CHAT/BACKEND/4-2-CONTRACT.md#4-2-14-모델-목록)). AI 요청에서는 `model_tier`로 전달하고 실제 모델은 AI 서버가 정한다([AI 실행 명세](../domain/CHAT/AI/6-1-AI-EXECUTION.md#6-1-1-채팅-응답-생성)) | 실제 모델 이름을 사용자 표기로 노출, "모델 등급" |
| 긴 응답 | `longResponse` | 채팅 AI 출력(본문)의 분량 설정. 켜면 한 번에 더 많은 장면을 쓴다. 서버가 채팅마다 저장하고(새 채팅은 꺼짐) 채팅 응답 시트의 스위치로 바꾼다. 게스트 턴에도 그대로 적용되고 비용은 바뀌지 않는다([채팅 설정 변경](../domain/CHAT/BACKEND/4-2-CONTRACT.md#4-2-15-채팅-설정-변경)) | "응답 길이 모드", 기기 설정처럼 다루기 |
| 장면 이미지 | scene image | 오리지널 스토리의 프롤로그(`prologue`)와 시작 상황(`startSituation`) 문자열 사이에 `[[URL]]` 마커로 넣은 팀 제작 장면 그림. 인물 이미지와 달리 마커 다음 줄에 인물명 라벨이 없다 | 없음 |
| 강조 마크업 | emphasis | `*...*`로 감싼 상황, 행동 묘사 표기. 사용자 입력과 AI 출력 양방향 공통 규약 | UI 버튼 카피 "상황 묘사 추가"는 허용. "지문"은 프롬프트의 서사 문맥 전용 |
| 요약 | `summary` | 백엔드가 AI 요청의 `summary`로 전달하는 대화 요약 문자열. 없는 경우 빈 문자열을 전달한다. 현재 단일 채팅 프롬프트의 입력이며, 이 필드가 있다는 사실로 사용자 메모리 조회나 편집 기능을 제공한다고 해석하지 않는다. ([채팅 계약](../domain/CHAT/AI/5-CONTRACT.md#5-2-채팅-턴-요청과-결과)) | "세션 상태"(session 예약어와 충돌, §5), "메모리 TEXT" |

<br>

### 3-4 사용자와 식별자

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 게스트 | guest | 로그인 없이 서비스를 쓰는 사용자. 웹은 공개 콘텐츠 열람과 이용 동의 후 체험을 제공한다. Android는 로그인 후 사용한다. ([웹 게스트 요구사항](../domain/ACCOUNT/CLIENT/WEB/2-2-REQUIREMENTS.md#2-2-1-게스트와-회원)) | "비로그인 사용자"는 설명문에서 허용 |
| 익명 사용자 | anonymous user | 분석에서 로그인 계정과 연결되지 않은 사용자 단위. `device_id`로 식별하며 제품의 이용 권한은 플랫폼별 게스트 계약을 따른다 | 없음 |
| 디바이스 ID | `device_id` / `device_id_hash` | 기기 또는 브라우저 단위 식별자. 웹은 Amplitude Browser SDK 값, Android는 앱이 생성하고 영속화한 UUID를 SDK에 주입한다. API 헤더와 SDK가 같은 값을 사용하고 서버 저장에는 해시를 사용한다. ([식별자 정책](ANALYTICS.md#2-식별자-정책)) | `anonymous_id`(레거시, V17에서 정리 완료) |
| 세션 | `session_id` | **분석 세션 전용 예약어**(Amplitude). 한 번의 방문 단위 | 채팅, 간편 제작 진행 단위를 "세션"으로 부르는 것(§5) |
| 요청 ID | `request_id` | API 요청 1건의 상관 ID(`req_` + UUID). 헤더 `X-Manyak-Request-Id` | 없음 |
| 사용자 | `user` | 로그인한 사용자 계정. 외부 식별자는 UUID `public_id` | 없음 |
| 소셜 제공자 | `provider` / `SocialProvider` | 로그인을 위임하는 외부 신원 제공자. 현재 지원은 `GOOGLE`, `KAKAO`이며 예약 값과 지원 값은 ACCOUNT 계약을 따른다 | 없음 |
| 소셜 연동 | `social_accounts` | 사용자 계정과 소셜 제공자 계정의 연결. 제공자 신원이 다르면 기본적으로 별개 계정이며 계정 연동으로 기존 계정에 다른 로그인 수단을 추가한다. 계정 병합과 구분한다. ([ACCOUNT 요구사항](../domain/ACCOUNT/CLIENT/2-2-REQUIREMENTS.md)) | "계정 연결"(연동으로 통일, KNK-737), "SNS 계정" |
| 닉네임 | `nickname` | 사용자 표시 이름. 가입 시 부여하며 프로필 변경 규칙은 ACCOUNT 계약을 따른다 | 없음 |
| 프로필 이미지 | `profileImageUrl`(와이어) | 사용자 대표 이미지. 닉네임에 대응하는 프리셋과 프로필 변경 범위는 ACCOUNT 계약을 따른다 | "아바타" |
| 알림함 | notification inbox, `user_notifications` | 회원이 받은 알림의 서버 사본 목록. 분류는 소식(`NEWS`: 공지, 이벤트)과 활동(`ACTIVITY`: 스토리 완성, 검토 결과, 출석 체크)이며 읽음(`readAt`)은 서버에 기록한다. 웹 `/notifications` | "알림 내역"(화면 이름으로는 "알림"), "알림 센터" |
| 데이터 마이그레이션 | migration | 웹 게스트의 스토리와 채팅 소유권을 로그인 계정으로 이관하는 것. 회원 필수 동의 완료 뒤 서버가 평가한 결과에 따라 로컬 ID를 정리한다. ([로그인과 이관](../domain/ACCOUNT/CLIENT/WEB/2-2-REQUIREMENTS.md#2-2-3-로그인과-이관)) | "동기화"(양방향 유지로 오해) |

<br>

### 3-5 이프

이프는 회원 전용 재화다. 웹 게스트 체험은 이프 잔액과 별도로 판정한다. 계약과 수치는 PAYMENT에서 관리한다. ([PAYMENT 계약](../domain/PAYMENT/BACKEND/4-2-CONTRACT.md))

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 이프 | credit | AI 기능(스토리 제작, 채팅) 사용에 소모하는 서비스 내 재화 | "포인트", "코인" |
| 이프 지갑 | `credit_wallets` | 사용자별 이프 잔액 보관 단위. `balance`는 원장 합계의 캐시 | 없음 |
| 원장 | `credit_transactions` | 이프 증감의 불변(append-only) 기록. 환불은 행 수정이 아니라 `REFUND` 행 추가 | "거래 내역"(사용자 노출 화면 명칭으로만 허용) |
| 적립 | earn / `reason` 적립 계열: `SIGNUP_REWARD`, `INVITE_REWARD`, `ATTENDANCE_REWARD`, `PURCHASE` | 보상 또는 구매로 이프가 늘어나는 것. 보상액, 초대자 월 한도와 상품 총량은 서버 정책과 상품 응답을 사용한다. 고정 수치를 용어집에 중복 정의하지 않는다. ([정책값](../domain/PAYMENT/BACKEND/4-2-CONTRACT.md#4-2-3-정책값-조회), [상품 목록](../domain/PAYMENT/BACKEND/4-2-CONTRACT.md#4-2-2-상품-목록-조회)) | "충전"(Phase 3 유료 결제 `PURCHASE` 전용) |
| 소모 | spend / `reason` 소모 계열: `STORY_CREATION`, `CHAT_TURN` | 기능 사용으로 이프가 줄어드는 것. 간편 제작 완성, 채팅 턴과 응답 재생성의 적용 비용은 서버 정책, 선택 모델과 체험 상태로 결정한다. 스토리라인 생성과 재생성은 무료다. 요청 전에 소모하는 방식은 선차감이라고 부른다. ([잔액과 비용](../domain/PAYMENT/CLIENT/2-2-REQUIREMENTS.md#2-2-2-잔액과-비용)) | "차감" 단독 표기(회수, 정산과 혼동, "선차감"은 예외), "사용" 단독 표기 |
| 환불 | refund / `REFUND` | 선차감 후 AI 실패 시 자동으로 이프를 되돌리는 것 | "취소" |
| 구매 | `PURCHASE` | 웹 결제창으로 상품을 구매해 이프를 적립하는 것. Android에는 구매 탭과 인앱 결제가 없다. 구매 로트와 만료 규칙은 PAYMENT 계약을 따른다. ([유료 구매 범위](../domain/PAYMENT/CLIENT/2-2-REQUIREMENTS.md#2-2-1-적용-범위)) | 보상과 혼용 금지 |
| 주문 | `credit_orders` | 결제 상품, 금액, 상태와 적립 원장을 연결하는 단위. 외부 식별자는 UUID `public_id`이다. ([주문 조회](../domain/PAYMENT/BACKEND/4-2-CONTRACT.md#4-2-9-주문-조회)) | 순차 PK 외부 노출 금지 |
| 회수 | `PURCHASE_REVERSAL` | 결제 환불에 따라 구매 로트 잔여를 줄이는 음수 원장 사유. AI 실패에 따른 재적립인 `REFUND`와 구분한다. 잔액과 이용내역 분류는 PAYMENT 계약을 따른다. ([그로블 웹훅](../domain/PAYMENT/BACKEND/4-2-CONTRACT.md#4-2-10-그로블-웹훅-수신)) | AI 실패 후 재적립인 `REFUND`와 혼용 금지 |
| 출석체크 | attendance | KST 자정 기준 하루 1회 접속 보상을 받는 행위 | "데일리 체크인" |
| 초대 코드 | invite code, `invite_code` | 다른 회원의 초대 관계와 보상을 등록하는 코드. 등록 자격은 ACCOUNT, 보상액과 초대자 월 상한은 PAYMENT에서 정의한다. ([계정 요구사항](../domain/ACCOUNT/CLIENT/2-2-REQUIREMENTS.md#2-2-4-연동과-초대), [보상과 내역](../domain/PAYMENT/CLIENT/2-2-REQUIREMENTS.md#2-2-4-보상과-내역)) | "초대 링크"(링크 어트리뷰션 방식은 KNK-567로 폐기), "추천인 코드" |
| 체험 한도 | trial limit | 이프 없이 사용할 수 있는 기능별 사용량 상한. 웹 게스트 체험과 회원의 적용 비용 표시를 구분하며 실제 한도와 사용량은 서버 응답을 따른다. Android에는 게스트 체험이 없다. ([체험 사용량](../domain/PAYMENT/BACKEND/4-2-CONTRACT.md#4-2-4-체험-사용량-조회), [플랫폼 범위](../domain/PAYMENT/CLIENT/2-2-REQUIREMENTS.md#2-2-1-적용-범위)) | "무료 이프"(게스트는 이프가 없음) |

<br>

### 4 계층별 표기 컨벤션

같은 개념이라도 계층에 따라 표기(casing)가 다르다. 다음 표가 기준이며, 계층 간 이름 자체(단어)는 §3의 공식 용어를 따른다.

| 계층 | 표기 | 예시 |
| --- | --- | --- |
| 클라이언트 REST 와이어(JSON) | camelCase | `storyId`, `aiOutput`, `suggestedInputs` |
| DB 테이블, 컬럼 | snake_case | `story_chats`, `turn_number` |
| 구조화 로그, MDC, Sentry | snake_case | `event_name`, `chat_id`, `error_code` |
| 분석 이벤트명 | `client_{screenName}_{object}_{action}`, 세그먼트 구분 `_`, 세그먼트 내부 camelCase, 동사 과거형 | `client_chat_choiceOption_selected` |
| 분석 프로퍼티 | snake_case | `turn_number`, `creation_id`, `step_name` |
| HTTP 헤더 | `X-Manyak-` 접두 Train-Case | `X-Manyak-Device-Id` |
| enum 값 | UPPER_SNAKE_CASE | `USER`, `ASSISTANT`, `GOOD`, `SUPPORTING_CHARACTER` |
| 프롬프트 버전 키 | UPPER_SNAKE_CASE | `CHAT`, `STORYLINES`, `NEXT_ACTIONS` |

추가 규칙:

- **AI 계약의 이원 표기는 공식화된 예외이다.** story 계열 계약(`/story/*`)은 snake_case, chat SSE `completed` 페이로드는 camelCase이다. 각 엔드포인트에 필드를 추가할 때 해당 엔드포인트의 기존 규칙을 따른다.
- **외부 식별자는 각 API 계약의 타입을 따른다.** 사용자와 콘텐츠의 공개 ID, 제작 진행과 턴의 숫자 식별자를 구분한다. 내부 PK를 임의로 새 외부 계약에 노출하지 않는다.
- **제작 단계 표기.** 분석의 `step_name`은 `keyword`, `storylineSelect`, `additionalInfo`, `complete`를 사용한다. 화면의 URL과 내비게이션은 각 플랫폼의 STORY 문서에서 정의한다.
- **role 변환.** 계약과 저장은 대문자(`USER`/`ASSISTANT`), LLM 호출 직전 소문자 변환은 AI 서버 내부 구현이다.

<br>

### 5 동명이의, 예약어 규칙

한 단어가 여러 개념을 가리켜 혼동을 만드는 사례이다. 다음 규칙으로 의미를 고정한다.

| 단어 | 규칙 |
| --- | --- |
| 세션(session) | 분석 세션(`session_id`) 전용 예약어. 채팅은 `chat`, 간편 제작 진행은 `analytics_creation_id`(와이어 `creation_id`) 계열로 부른다 |
| 스토리(story) | 제품 콘텐츠, Jira 이슈 유형과 과거 프롬프트 레이어 이름을 구분한다. 제품 외의 의미에는 Jira 스토리, 과거 STORY 레이어처럼 수식어를 붙인다 |
| USER | 대화 이력의 역할과 사용자 입력을 구분한다. 과거 USER 레이어나 템플릿 블록을 설명할 때는 과거 구조임을 명시한다 |
| meta | 컴파일 응답에서 노출 메타(제목 등)는 `stories` 키, 로깅 메타(model, 토큰)는 `meta` 키. "메타"라고만 쓰지 않는다 |
| chatCount | 스토리의 채팅 수 전용. 채팅 안의 턴 수는 `turn_count`(개념명 "턴 수")로 부른다 |
| 좋아요/싫어요 | 스토리 반응(`like`/`dislike`) 전용. 스토리라인 GOOD/BAD는 "평가(rating)"로 구분 |
| 추천 입력 | `suggested_inputs`(첫 입력 후보) 전용. 선택지(`choices`)에 쓰지 않는다 |
| 시드(seed) | 대화 이력의 오프닝 시드와 과거 MEMORY의 Seed State를 구분한다. 단독 시드 표기를 피한다 |
| 트리거(trigger) | 키워드북 트리거(`keyword_notes`, 백로그)와 이미지 트리거(`trigger_text`, 스토리 이미지 표시 조건)는 다른 개념. "이미지 트리거", "키워드 트리거"처럼 대상을 명시한다 |
| 온보딩(onboarding) | 처음 이용하는 기능을 안내하는 흐름. 신규 가입 스토리 온보딩, 초대 코드 안내와 첫 진입 안내를 구분해 대상 이름을 함께 쓴다 |
| 첫 진입 안내 | 화면을 처음 쓰는 사용자에게 기기마다 한 번 보이는 안내. 채팅 첫 진입 안내(입력 영역 하이라이트 투어)와 간편 제작 첫 진입 안내(마냑 캐릭터가 말하는 하단 대화창, 분석 이벤트 `client_storyCreate_tutorial*`)가 있다. "튜토리얼"은 코드 식별자에만 쓴다 |
| 일반 | "일반 입력"은 채팅 입력 모드(`NORMAL`), "일반 제작"은 제작 방식. 어느 쪽도 "일반 모드"라고만 쓰지 않는다 |
| NORMAL | enum 값 `NORMAL`은 `input_mode`(일반 입력)에 쓰인다. 단독 표기하지 않고 필드명과 함께 쓴다 |
| 수정/편집 | 스토리 설정을 고치는 것은 "수정(edit)", 채팅 산출물(AI 응답, 메모리)을 고치는 것은 "편집" |
| user_id | 분석 프로퍼티 `user_id`는 외부 식별자(`public_id` UUID 문자열), DB `user_id`(`stories`, `story_chats` 등)는 내부 Long FK. 계층이 달라 값이 다르며 계약, 로그, 이벤트에는 `public_id`만 싣는다(§4 외부 노출 규칙) |

<br>

### 6 AI 서버 내부 용어

AI 서버와 프롬프트 스펙에서만 쓰는 용어이다. 현재 정의는 도메인의 AI 세트에서 관리한다. 폐기된 프롬프트 구조의 용어는 과거 결정 해석에만 사용한다.

| 용어 | 정의 |
| --- | --- |
| 6레이어 | 과거 채팅 프롬프트 구조. SAFETY, CORE, STORY, CHARACTER, USER, MEMORY로 나눴으며 2026-10-21 단일 채팅 프롬프트 결정으로 폐기됐다. ([채팅 결정](../domain/CHAT/AI/DECISIONS.md)) |
| PHI (Post-History Instructions) | 과거 생성 직전에 재주입하던 지시 블록. 현재 단일 채팅 프롬프트에는 이 구조를 적용하지 않는다 |
| Depth | 과거 대화 이력 끝 근처에 MEMORY를 넣던 슬롯. 현재 채팅 프롬프트의 적용 구조가 아니다 |
| 희소 입력 | 컴파일의 입력(선택 스토리라인 + 추가 정보 + 태그)을 가리키는 표현 |
| 시점 A-1 / 시점 B | 컴파일 시점(스토리당 1회) / 채팅 턴 런타임 시점. A-2(세션 초기화)는 stateless 확정으로 폐기되어 B에 흡수 |
| 오프닝 시드 | 백엔드가 프롤로그 + 시작 상황을 History 첫 ASSISTANT 항목으로 래핑해 전달하는 것 |
| 부분 재호출(refill) | 컴파일, 선택지 생성에서 빈 필수 블록만 다시 채우는 재호출(최대 2회). 관측 필드 `retry_count`가 이 횟수를 담는다 |
| 화자 라벨(인물명 라벨) / 지문 | `인물명: 대사`와 `*별표*` 행동 묘사 표기. 저장 이미지 선택과 대사별 연결은 현재 채팅 AI 실행 계약을 따른다. ([채팅 실행](../domain/CHAT/AI/6-1-AI-EXECUTION.md)) |
| 스토리 명세(StorySpec) | 컴파일의 내부 세분 JSON 산출물. 통글로 렌더링되어 `story_settings`가 된다 |

<br>

### 7 참고 근거

공식 용어 선정에 참고한 업계 표준 근거이다.

| 용어 | 근거 |
| --- | --- |
| 채팅(chat) | Character.AI, SillyTavern, Janitor AI 등 AI 챗 제품군의 공통 명칭. AI Dungeon만 adventure를 사용 |
| 턴(turn) | 대화형 AI 업계 표준(multi-turn conversation) |
| 선택지(choice) | 비주얼 노벨 도메인 표준. 챗봇 UI 관행(suggested reply)보다 서사 제품 성격에 부합 |
| 프롤로그(prologue) | AI 챗 제품군은 first message/greeting을 쓰지만, 시작 장면 서사 텍스트라는 성격은 웹소설, 비주얼 노벨 관행인 프롤로그가 더 정확 |
| 태그(tag) | Character.AI, Janitor AI, 제타, 크랙의 분류 명칭. 트리거형 `keyword_notes` 로드맵과의 충돌 예방 |
| 로어북(lorebook) | SillyTavern, Character Card V2 스펙, NovelAI로 이어지는 사실상 표준 |
| 익명 사용자(anonymous user) | Segment(`anonymousId`), Amplitude(`device_id`) 표준 개념 |
| 이벤트 네이밍 | Segment, Amplitude 공통 권장인 Object-Action 프레임워크(동사 과거형) |

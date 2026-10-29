# 4-1 연동 계약

기준: [요구사항](2-2-REQUIREMENTS.md), [화면 흐름](3-2-INTERACTION-FLOWS.md).

<br>

### 4-1-1 제공자 경계

API 경로는 `/api/v1` 기준이다. 인증, 응답 전체 필드와 서버 제약은 제공자 계약을 따른다.

| 용도 | 제공자 계약 | 클라이언트 사용 |
|---|---|---|
| 탐색 | [공개 목록](../BACKEND/4-2-CONTRACT.md#4-2-2-공개-목록) | `GET /stories`, filter와 sort, 커서. 기본 all과 popular. 서버 순서 유지 |
| 장르와 태그 | [제공 장르](../BACKEND/4-2-CONTRACT.md#4-2-4-제공-장르), [간편 태그](../BACKEND/4-2-CONTRACT.md#4-2-9-간편-제작-태그-목록) | 전체와 대표 목록, 질의 결과 및 인물 특징 |
| 상세와 소유 목록 | [상세](../BACKEND/4-2-CONTRACT.md#4-2-7-상세), [일괄 조회](../BACKEND/4-2-CONTRACT.md#4-2-6-일괄-조회) | 회원 내 스토리는 `GET /users/me/stories`, 게스트 소유 ID는 ACCOUNT에서 관리 |
| 삭제와 좋아요 | [삭제](../BACKEND/4-2-CONTRACT.md#4-2-8-삭제), [좋아요](../BACKEND/4-2-CONTRACT.md#4-2-21-좋아요) | 서버 소유권과 좋아요 결과 사용 |
| 간편 제작 | [스토리라인 생성](../BACKEND/4-2-CONTRACT.md#4-2-11-간편-제작-스토리라인-생성), [완성](../BACKEND/4-2-CONTRACT.md#4-2-12-간편-제작-완성), [복구](../BACKEND/4-2-CONTRACT.md#4-2-13-간편-제작-복구-조회), [평가](../BACKEND/4-2-CONTRACT.md#4-2-14-간편-제작-스토리라인-평가) | 입력, requestId, 결과와 상태를 구분 |
| 이미지 스타일 | [화풍 목록](../BACKEND/4-2-CONTRACT.md#4-2-10-화풍-목록) | 제공 순서, 미리보기와 code |
| 일반 제작과 수정 | [등록](../BACKEND/4-2-CONTRACT.md#4-2-15-일반-제작-등록), [편집 조회](../BACKEND/4-2-CONTRACT.md#4-2-16-수정-폼), [수정](../BACKEND/4-2-CONTRACT.md#4-2-17-스토리-수정) | 전체 등록, baseline 대비 변경 필드 및 미승인 제출본 |
| 이미지 | [presign](../BACKEND/4-2-CONTRACT.md#4-2-18-이미지-presign), [표지 삭제](../BACKEND/4-2-CONTRACT.md#4-2-19-표지-삭제) | 등록 전에 업로드한 objectKey, 기존 이미지 ID |
| 초안 | [목록](../BACKEND/4-2-CONTRACT.md#4-2-23-초안-목록), [상세](../BACKEND/4-2-CONTRACT.md#4-2-24-초안-상세), [저장](../BACKEND/4-2-CONTRACT.md#4-2-25-초안-저장), [삭제](../BACKEND/4-2-CONTRACT.md#4-2-26-초안-삭제) | `/users/me/story-drafts`, 클라이언트 payload v1 |
| 제출본 | [MODERATION 계약](../../MODERATION/BACKEND/4-2-CONTRACT.md) | `/stories/submissions`, 신규 CREATE와 UPDATE 구분, 상세와 재제출 및 취소 |
| 채팅 시작 | [CHAT 계약](../../CHAT/CLIENT/4-1-CONTRACT.md) | storyId, startSettingId와 선택 personaId. 기본 주인공은 personaId 생략 또는 null |

사용하지 않는 `GET /stories/originals`로 홈 목록을 대체하지 않는다. 별도 클라이언트 인기 점수를 계산하지 않는다.

<br>

### 4-1-2 간편 제작 요청

| 값 | 변환 |
|---|---|
| 스토리라인 생성 | `genreTagIds`, `protagonist`, `supportingCharacters`와 requestId. 장르 ID는 선택 순서 |
| 인물 | `name`, `gender`, `featureTagIds`, `customTags`. 비운 이름과 성별은 null이며 선택한 특징만 보낸다 |
| 직접 입력 장르 | 새 요청에 `customGenreTags`를 넣지 않는다. 같은 requestId의 재시도는 당시 저장한 요청을 바꾸지 않는다 |
| 생성 연결 | 새 재생성의 parentCreationId는 바로 직전 요청의 requestId이며 최초는 null이다. 같은 실패 요청의 재시도는 requestId를 유지한다 |
| 생성 응답 | 스토리라인 세 개와 `simpleCreationId`. 재생성이 실패해 이전 결과가 남으면 그 결과를 만든 요청도 함께 유지한다 |
| 평가 | PUT 또는 DELETE. 생성과 완성의 입력에는 합치지 않는다 |
| 추가 정보 | 추천과 자유 입력의 앞뒤 공백을 제거하고 비어 있지 않은 값만 `additionalInfos`로 합친다. 전체 최대 13개 |
| 완성 | 고른 스토리라인, 추가 정보, 화풍 `artStyle`, `visibility`, 세션 `draftId`와 requestId |
| 같은 명령 | 화풍이나 공개 범위가 달라지면 다른 명령이다. 이전 요청의 공개 범위 생략은 PRIVATE와 같은 명령으로 해석한다 |
| 내용 거절 | HTTP 422와 `CONTENT_REJECTED`로 구분한다. 응답 문구로 추측하지 않는다. 복구 조회 FAILED 뒤 같은 명령 재전송에서도 원 거절이 돌아올 수 있다 |

<br>

### 4-1-3 일반 제작 입력 변환

| 입력 | 요청 표현 |
|---|---|
| 기본 정보 | title, oneLineIntro, thumbnailObjectKey. 글 앞뒤 공백을 제거한다 |
| 세계관 | `storySettings.worldSetting`에 `# 세계관` 다음 본문 |
| 전개 방식과 배분 | `ruleSetting`에 `# 전개 규칙`과 `# 분량 배분` 순서. 절 사이 빈 줄 하나 |
| 기본 주인공 이름 | `protagonistName`. 등록의 생략과 null은 이름 없음, 수정의 생략과 null은 유지 |
| 주인공 설명 | `userRoleSetting`에 `# 주인공`, `## 성별`, 특징 본문. 이름은 합치지 않는다 |
| 주변 인물 설명 | `characterSetting`에 `# 등장인물`, 인물별 `## {이름}`, `### 성별`과 특징 |
| 인물 객체 | characters에는 주변 인물만 넣는다. UI 5명이며 서버 상한 6명. 이름은 설정 글과 같은 입력을 사용한다 |
| 인물 소개 | description은 탭과 줄바꿈을 공백으로 바꾸고 trim한다. 등록에서 비면 생략하며 설정 글에 합치지 않는다 |
| 대표 이미지 | 인물당 UI 1장, `images`에 objectKey와 `imageName: "{이름}_기본"`. 서버 계약은 인물당 최대 10장이므로 수정 시 나머지를 보존한다 |
| 이미지 이름 | `{인물이름}_{접미}`. 접미는 1~20자의 한글, 영문, 숫자이며 같은 인물에서 유일 |
| 시작 상황 | `startSettings`의 name, prologue, startSituation, suggestedInputs, endings |
| 엔딩과 사건 | endings는 해당 시작 상황에, mainEvents는 스토리 범위에 둔다. 폼 전용 ID는 등록 입력에서 제외 |
| 장르와 주요 내용 | genres는 선택 순서의 이름. 첫 장르가 기본 커버 기준이다. 비어 있는 주요 내용은 생략 |

편집 조회를 폼으로 바꿀 때는 다음을 보존한다.

| 대상 | 읽기와 수정 규칙 |
|---|---|
| 설정 절 | 정해진 제목이 정해진 순서에 나올 때만 분리한다. 알 수 없는 제목은 앞 칸 본문에 남기고 제목 없는 글은 통째로 넣는다 |
| 배분 | 해석할 수 없으면 5:5. 빈 칸은 다시 만들 때 제목도 제외 |
| 인물 설정 | 주인공 이름은 protagonistName에서 읽는다. 주인공 성별과 주변 인물 이름 절만 분리하고 역할, 성격, 이전 호칭 절은 특징에 남긴다. 남성과 여성이 아닌 성별 절도 본문에 유지 |
| 기존 인물 | 시작 상황과 인물은 서버 ID로 대응한다. 인물은 이름으로 찾아 첫 이미지와 소개를 채우고 대응하지 않으면 비운다 |
| 제출본 인물 | 이름으로 대응하고 없으면 같은 순서의 인물을 사용한다 |
| 부분 수정 | 폼을 연 시점의 baseline과 현재 요청 표현이 다른 필드만 PATCH한다. 설정 분해와 재조합만으로 미수정 필드가 전송되지 않게 한다 |
| characters 변경 | 폼 밖 서버 인물과 바꾸지 않은 이미지도 ID로 함께 보낸다. 폼 안의 비운 소개는 빈 문자열로 삭제하고 폼 밖의 소개는 생략해 유지한다 |
| 이미지 변경과 삭제 | 대표 이미지 변경은 새 이미지를 맨 앞에 두고 나머지 유지. 대표 삭제는 첫 이미지만 제외 |
| 표지 삭제 | PATCH에 null로 싣지 않고 별도 DELETE 후 나머지 변경을 PATCH한다. 표지만 삭제하면 검수 없이 완료 |
| 반려와 실패 수정 | 미승인 제출본 입력을 폼에 합친다. 다음 PATCH가 그 제출본을 덮어쓰므로 변경되지 않은 필드도 모두 보낸다 |

<br>

### 4-1-4 공통 초안 봉투와 버전

| 필드 | 계약 |
|---|---|
| 초안 ID | 제작 세션마다 고정한 UUID. 재개와 단계 이동 및 재생성에도 유지 |
| mode와 stage | SIMPLE의 KEYWORD_DRAFT 또는 STORY_DRAFT, GENERAL의 GENERAL_DRAFT |
| schemaVersion | 1. 다른 버전은 읽기 실패로 처리하며 알 수 없는 필드를 지운 채 다시 쓰지 않는다 |
| baseVersion | 마지막 저장 응답의 version. 새 초안은 기준 버전 없이 저장 |
| payload | 클라이언트 공용 JSON 형식. 서버는 내부 의미를 해석하지 않는다 |
| 일반 제작 요약 | title과 oneLineIntro는 trim 후 비면 null, thumbnailObjectKey는 표지 키 |
| 간편 제작 요약 | title과 thumbnailObjectKey는 null. 키워드 oneLineIntro는 null, 추가 정보 단계는 선택한 스토리라인 본문, 그 밖은 null |
| generationRequestId | 키워드 초안은 null. 스토리라인 초안은 표시 중 결과를 만든 generationRequest.requestId |
| 미리보기 | 상세 응답 imageUrls를 사용한다. 서버 payload에는 이미지 파일과 Blob을 넣지 않는다 |

<br>

### 4-1-5 간편 제작 payload v1

| stage | payload |
|---|---|
| KEYWORD_DRAFT | selectedGenreTagIds, addedGenreTagIds, customGenreTags의 name과 selected, protagonist, supportingCharacters 배열 |
| 키워드 인물 | name, gender, selectedTagIds, customTags의 name과 selected |
| STORY_DRAFT | step, generationRequest, activeStorylineIndex, selectedStorylineId, additionalInfos, selectedRecommendations, artStyle, visibility, createdStoryId, completionRequest |

- step은 `storyline-select` 또는 `additional-info`다. generationRequest는 표시 중인 결과를 만든 요청 전체이며 재생성과 선택한 키워드 표시에 쓴다.
- selectedStorylineId는 고른 ID 또는 null이다. artStyle, visibility, createdStoryId와 completionRequest는 없으면 null이다. visibility는 PUBLIC 또는 PRIVATE이며 없는 초안은 공개로 연다.
- 생성 결과 원문은 payload에 넣지 않고 상세의 generation으로 받는다. COMPLETED 상태와 결과가 있어야 이어서 연다.
- 결과에서 선택 ID를 찾지 못하면 스토리라인 선택 단계로 연다. 빠졌거나 null인 선택 필드는 빈 배열, 0과 없음으로 채운다. step, generationRequest와 키워드 입력 형태를 해석하지 못하면 불러오기 실패다.
- 생성 결과가 없을 때의 빈 초안 복귀와 안내 차이는 플랫폼 적용 범위를 따른다.

<br>

### 4-1-6 일반 제작 payload v1

| 필드 | 형식 |
|---|---|
| texts | 폼 글 칸 이름을 키로 한 문자열 객체 |
| cover | objectKey를 가진 객체 또는 null |
| descriptionRatio | 묘사 비율 숫자 |
| protagonist | name, gender, feature |
| supporting | id, name, gender, feature, description과 image를 가진 배열. image는 objectKey 객체 또는 null |
| startSettings | id, name, prologue, situation, 문자열 세 개의 suggestedInputs, endings 배열 |
| endings | id, name, minTurns, condition, epilogue. minTurns는 빈 입력을 보존하는 문자열 |
| mainEvents | id, name, description, keySentence 배열 |
| genres | 선택 순서 selected, 이름을 보관하는 customTags, 대표 밖 칩 순서 addedTagIds |
| description와 visibility | 주요 내용 문자열과 PUBLIC 또는 PRIVATE |

selected는 tag의 숫자 ID 또는 custom의 ID를 구분하고 customTags는 ID와 이름을 보관한다. Android가 이름으로 저장한 값과 웹이 제공 ID로 저장한 값을 모두 읽는다. 제공 ID를 이름으로 변환하는 데 필요한 카탈로그를 받지 못하면 이름을 잃은 채 다시 저장하지 않는다.

최상위 필드의 타입이 다르거나 필드가 없으면 새 폼 기본값을 채운다. 항목 안의 빠진 필드도 기본값을 사용한다. 이전 초안에 없는 인물 소개는 빈 문자열로 읽는다.

<br>

### 4-1-7 검수 결과의 화면 대응

| 응답 | 사용 |
|---|---|
| 일반 등록 202 | submissionId와 PENDING. 아직 storyId가 없으므로 상세나 채팅으로 이동하지 않는다 |
| 승인 | 반환된 storyId로 후속 화면을 연다 |
| issues와 imageErrors | 제출한 폼의 배열 순번을 안정적인 항목 ID로 대응해 삭제와 추가 뒤에도 같은 칸을 가리킨다 |
| reason 없음 | 기본 금지 내용 문구로 표시 |
| IMAGE_INVALID와 IMAGE_UNREADABLE | 형식 및 크기, 읽기 실패를 구분하고 그 외 이미지 실패도 별도 기본 문구로 표시 |
| 경로가 여러 칸에 걸침 | 해당 탭과 폼 위 사유. 알 수 없는 경로도 사유 목록에서 누락하지 않는다 |
| IMAGES_TOO_LARGE와 UPLOAD_NOT_FOUND | 등록과 수정에서 이미지 크기 및 장수, 업로드 원본 없음으로 안내 |
| 400 검증 실패 | 클라이언트 선검증이 더 엄격한 기존 계약에 따라 details를 칸별 오류로 다시 해석하지 않고 등록 또는 수정 실패로 표시 |
| 수정 200 | 검수 없이 반영된 결과. 일반 공개 범위 변경 또는 표지 삭제만인 경우 |
| 수정 202 | 검수 제출본. 관리자가 공개 중단한 스토리의 공개 변경도 포함 |
| 수정 409 | 아직 검토 중임을 알리고 입력 보존 |

# WEB 결정 기록

확정된 결정의 ID, 당시 상태와 본문을 보존한다. 현재 적용 기준과 후속 결정은 해당 문서에서 확인한다.


<br>

<a id="w-035"></a>

## W-035. 겹치는 operationId는 메서드와 경로로 생성 이름을 고정

- 결정일: 2026-10-15, 기록 확정 상태: Accepted
- 근거: [요청 흐름](COMPONENT-ARCHITECTURE.md#구성과-의존), [KNK-1655](https://kimandkang.atlassian.net/browse/KNK-1655)
- **맥락:** 백엔드(Springdoc)는 Java 메서드 이름으로 operationId를 만들고, 이름이 겹치면 스캔 순서대로 `get`, `get_1`, `get_2`처럼 순번을 붙입니다. Orval은 이 값으로 훅 이름(`useGet1`)을 만듭니다. 임시 저장 API(`story-draft-controller`)가 추가되자 순번이 하나씩 밀려 `useList1` 같은 import가 깨졌고, `useGet3`은 이름이 남은 채 화풍 목록 대신 장르 목록을 가리켰습니다.
- **결정:** Orval 입력 변환기(`input.override.transformer`)로 스펙을 생성 전에 고칩니다. 순번 접미사(`_숫자`)를 뗀 기본 이름이 둘 이상인 operationId는 모두 HTTP 메서드와 경로 이름으로 바꾸고(`GET /api/v1/stories/submissions/{id}` → `getStoriesSubmissionsById`), 겹치지 않는 이름은 그대로 둡니다. API와 Zod 생성에 같은 변환기를 씁니다.
- **이유:** 메서드와 경로는 API 계약 자체라 백엔드 메서드가 늘거나 스캔 순서가 바뀌어도 변하지 않습니다. 같은 이름이 다른 API를 가리키는 일은 없어집니다. 모든 이름을 경로로 바꾸면 이미 쓰는 고유 이름(`getStoryDetail` 등)까지 바뀌어, 겹치는 이름만 바꿉니다. 근본 해결은 백엔드가 `@Operation(operationId = ...)`로 고유 이름을 다는 것이지만 백엔드 코드라 웹에서 정하지 않습니다.
- **주요 영향:** 지금 고유한 이름도 나중에 백엔드에 같은 이름의 메서드가 생기면 경로 이름으로 바뀌어 import가 깨집니다. 다만 다른 API를 가리키지 않고 typecheck에서 드러납니다. 경로가 바뀌면 이름도 바뀝니다. 생성 훅 이름은 길어집니다.

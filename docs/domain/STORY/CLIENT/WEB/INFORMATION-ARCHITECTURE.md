# 웹 STORY 화면 구성

기준: [공통 화면](../INFORMATION-ARCHITECTURE.md), [웹 요구사항](REQUIREMENTS.md).

<br>

### URL과 접근

| 화면 | URL | 접근 |
|---|---|---|
| 홈 | `/` | 게스트와 회원. filter와 sort 쿼리 |
| 제작 | `/studio` | 게스트와 회원 |
| 방식 선택 | `/studio/story` | 게스트와 회원 |
| 간편 제작 | `/studio/story/simple` | 회원 또는 게스트. 게스트 동의는 생성 직전 |
| 일반 제작 | `/studio/story/general` | 동의를 마친 회원 |
| 재제출 | `/studio/story/general?submissionId=...` | 해당 제출본 소유 회원 |
| 상세 | `/stories/[id]` | 서버 권한 판정 |
| 수정 | `/stories/[id]/edit` | 회원 소유자 |

필터는 all과 original, 정렬은 popular와 latest 및 likes와 chats다. 기본값은 URL에서 생략하며 잘못된 값은 기본값으로 읽는다. 기존 `/create`는 제작 탭으로, `/create/story`와 `/stories/new`는 간편 제작으로 영구 이동한다. `/studio/story`는 현재 제작 방식 선택 화면이다.

<br>

### 첫 HTML과 메타데이터

| 화면 | 공개 정보 |
|---|---|
| 홈 | 제목이 실제 텍스트인 상세 링크와 카드. canonical은 `https://manyak.app/` |
| 공개 오리지널 상세 | 제목, 한 줄 소개, 주요 내용, 장르, 공개 시작 상황과 인물 소개. 문서 제목과 description, Open Graph와 Twitter는 같은 작품을 사용하고 canonical은 상세 URL |
| 조회 불가 상세 | 공개 본문을 넣지 않고 클라이언트 조회. noindex, nofollow |

홈 검색 설명과 Open Graph 및 Twitter 설명은 다음 문구를 사용한다.

> 키워드를 골라 스토리를 만들면 주변 인물 이미지까지 한 번에 완성되는 AI 스토리챗, 마냑. 채팅으로 스토리를 이어가 보세요. 실시간 이미지를 켜면 대화에 따라 인물의 표정과 행동, 스토리 속 장소가 달라져요. 생생한 장면을 보며 스토리에 푹 빠져보세요.

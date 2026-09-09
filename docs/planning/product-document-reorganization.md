# product-document-reorganization

| 항목 | 내용 |
| --- | --- |
| 작성일·수정일 | 2026-09-09 |
| 대상 | knk-harness 제품 문서와 저장소 내 참조 |
| 목적 | 파일명 변경·본문 이관·Android 통합 결과와 남은 정리·검증·복구를 연결합니다. |
| 이전 기준 | `f075a236ce7eb0c36ccb547471927e57954bd92f` |
| 결정 | [C-007](../adr/1-1-client-adr.md#c-007), 이전 배치 결정 [C-006](../adr/1-1-client-adr.md#c-006) |

## 1. 목표와 적용 범위

배경·요구·계약은 `docs/spec/`, 현재 내부 구조는 `docs/design/`, 누적 결정은 `docs/adr/`에 둡니다. 세 폴더는 `docs/` 바로 아래이며 `product-specs/`로 감싸지 않습니다. 번호는 폴더마다 독립적으로 배정하고 사용자가 바꾼 현재 파일명을 기준으로 본문·안내·참조를 맞춥니다.

이번에는 빈 백엔드 Design·ADR, AI Design을 기존 문서에서 분리해 채웠습니다. Android 모듈 파일은 Android Design에 합치고 반복된 화면·계약 설명을 줄였습니다. 제품 정책 승인이나 코드·운영·배포 상태 변경은 포함하지 않습니다.

## 2. 현재 구조와 본문 소유권

| 영역 | Spec | Design | ADR |
| --- | --- | --- | --- |
| 용어·배경·요구 | `0-glossary.md`, `1-background.md`, `2-user-stories.md` | — | — |
| 공통 클라이언트 | `3-1-client-spec.md` | 플랫폼 설계에서 구체화 | `1-1-client-adr.md` |
| 웹 | `3-2-web-spec.md` | `1-1-web-design.md` | `1-2-web-adr.md` |
| Android | `3-3-android-spec.md` | `1-2-android-design.md` — 모듈 포함 | `1-3-android-adr.md` |
| 백엔드 | `4-backend-server-spec.md` | `2-backend-server-design.md` | `2-backend-server-adr.md` |
| AI | `5-ai-server-spec.md` | `3-ai-server-design.md` | `3-ai-server-adr.md` |
| 분석 | `6-analytics.md` | 각 서비스의 관측 구현 | — |
| 배포 | 현재 배포 Design의 계약 절 참조 | `4-deployment.md` | — |

각 열의 파일은 해당 폴더 바로 아래에 있습니다. 제품 문서는 총 19개이며 빈 문서와 별도 Android 모듈 문서는 없습니다. 새 역할이 생길 때만 파일을 추가하며 다른 폴더의 번호에 맞춰 빈 파일을 만들지 않습니다.

## 3. 이번 본문 이관

| 출처 | 현재 소유자 | 처리 |
| --- | --- | --- |
| 백엔드 Spec §4-2 | [백엔드 Design §2-1](../design/2-backend-server-design.md#2-1-기술-환경과-요청-흐름) | 기술 환경·요청 흐름·도메인 책임 이동. Spec은 링크 유지 |
| 백엔드 Spec §4-4 저장소 표 | [백엔드 Design §2-2](../design/2-backend-server-design.md#2-2-저장소와-데이터-수명) | 현재 저장 구조 이동. 계획·혼재 원문은 아래 별도 보존 |
| 백엔드 Spec §4-3-7 원장·동시성 | [백엔드 Design §2-3](../design/2-backend-server-design.md#2-3-원장과-동시성) | 잠금·멱등·대사 구현 이동. reason enum은 Spec 유지 |
| 백엔드 Spec §4-7 메트릭·환경 변수 | [백엔드 Design §2-4~2-5](../design/2-backend-server-design.md#2-4-메트릭과-운영-연동) | 배선·설정 이동. 공개 관측·수집 계약은 Spec 유지 |
| 백엔드의 명시적 결정 기록 27개 | [백엔드 ADR BE-001~027](../adr/2-backend-server-adr.md#결정-목록) | 당시 원문 보존, 출처는 결정 링크로 교체 |
| AI Spec §5-2·5-4 | [AI Design §3-1~3-2](../design/3-ai-server-design.md#3-1-호출-경계와-요청-흐름) | 호출·어댑터·모델·프롬프트 설정 이동 |
| AI Spec §5-6 관측 SDK·환경 설정 | [AI Design §3-3](../design/3-ai-server-design.md#3-3-관측과-런타임-설정) | 활성화·실패 격리·flush·설정 이동. 응답 meta·trace 허용 키는 Spec 유지 |
| 이전 별도 Android 모듈 파일과 Android Design | [Android Design](../design/1-2-android-design.md) | 단일 문서로 통합. 책임·의존·상태 수명·실패/복구를 남기고 화면별 반복 계약과 상세 QA는 기존 정본으로 연결 |

### 미결 저장 구조

아래는 출처에 계획 또는 현재 구조와 혼재해 있던 행의 원문입니다. 구현 완료로 승격하지 않습니다. `story_messages`·`credit_lots`·`story_characters`의 확인된 현재 부분은 Design에 남겼습니다. `story_likes`·`story_reports`는 API 절의 후속 기록과 상태가 충돌할 수 있어 코드 확인이 필요합니다. 결제 테이블과 레거시 컬럼 제거도 구현 근거 확인 뒤 Design을 갱신합니다.

| 그룹 | 테이블 | 이관한 원문·당시 상태 |
| --- | --- | --- |
| 채팅 | `story_messages` | 메시지 행. `role`: `USER` · `ASSISTANT` · `SYSTEM`. `Phase 1 · 계획` 컬럼 — 본문 확정 시각(최초 생성 시 `created_at`과 동값, 재생성 성공 시 갱신 — 이미지 `images[]` 재구성 컷오프 앵커, [§4-3-9](../spec/4-backend-server-spec.md#4-3-api-계약)). 현행은 `created_at`뿐이고 재생성이 타임스탬프를 갱신하지 않아 이미지 마이그레이션과 함께 추가 |
| 스토리 | `story_likes` | `Phase 2 · 계획`(KNK-1024) 스토리 좋아요. `user_id` · `story_id` · `created_at`, `(user_id, story_id)` UNIQUE — 등록·취소 멱등과 `likeCount` 실 집계·`isLiked` 판정의 앵커([§4-3-1](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| 스토리 | `story_reports` | `Phase 2 · 계획`(KNK-1024) 스토리 신고. `user_id` · `story_id` · `created_at` 골격 — 사유 분류·중복 정책 컬럼은 구현 시 확정([§4-3-1](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| 이프 | `credit_lots` | `Phase 1 · 구현` 적립 로트(V39). `user_id` · `transaction_id`(적립·환불 원장 행, 레거시 승계는 NULL) · `original_amount`(> 0) · `remaining`(0~원금) · `expires_at`(NULL=무기한) · 보상·환불 30일 만료·FIFO 차감의 잔여 추적. `Phase 3 · 계획` 구매 로트는 웹·앱 모두 적립 후 5년 만료이며 구매당 기본·보너스 총량을 한 로트에 저장. 이용내역 만료일 배치 해석용 `transaction_id` 인덱스는 V64(KNK-1044) |
| 이프 | `credit_orders` | `Phase 3 · 계획`(KNK-1155, V번호 구현 시 확정). `id` · `public_id`(UUID, 외부 노출) · `user_id` · `product_id`(varchar) · `provider`(`GROBLE`·`GOOGLE_PLAY`) · `status`(`PENDING`·`COMPLETED`·`REFUNDED`) · `price_krw` · `credit_amount`(기본+보너스 총량) · `provider_ref`(그로블 `merchantUid` 또는 Google 구매 토큰 SHA-256, UNIQUE·NULL 허용) · `credit_transaction_id`(적립 원장 행) · `created_at` · `completed_at` · `refunded_at`(환불 회수 시각, NULL 허용) · `reversal_shortfall`(BIGINT NULL, 회수 시 소진돼 못 돌려받은 수량, 0이면 전량 회수). 인덱스 `(user_id, created_at DESC)` |
| 이프 | `groble_refund_marks` | `merchant_uid`(VARCHAR(255), PK) · `created_at`(TIMESTAMPTZ, NOT NULL, 기본 now()). `refund_amount`(BIGINT NULL, 선도착 환불 금액, NULL은 잠금용). merchantUid 단위 직렬화 표식. 완료 시 금액 대조 후 삭제 |
| 이미지 | `story_images` | `Phase 1 · 계획` 스토리↔배경 후보 연결. 등록 시 장르 매칭으로 5~8장 확정하고 매 턴 AI 요청에 동일 목록 전달([§4-3-9](../spec/4-backend-server-spec.md#4-3-api-계약)). 썸네일 확정값은 별도로 `stories` 썸네일 컬럼에 저장 |
| 이미지 | `story_characters` | `Phase 2 · 구현`(KNK-414·KNK-966) 인물↔이미지 저장(컴파일 산출물). `story_id` · `name`(인물 이름) · `image_url`(nullable — 생성 실패 시 NULL). 컴파일 응답의 `character_images[]`에서 base64를 디코딩해 S3에 올린 뒤 URL을 저장. 이미지 이름 컬럼은 이 표에 만들지 않았고 `story_character_images.image_name`이 대신합니다(KNK-1126, AI 컴파일 응답은 KNK-1027로 `image_name`을 보냄 — [§4-3-9](../spec/4-backend-server-spec.md#4-3-api-계약)). 같은 인물=같은 이미지를 DB 고정으로 보장([§4-3-9](../spec/4-backend-server-spec.md#4-3-api-계약)). 스토리 상세 `characters[]`(이름·이미지)의 소스이기도 합니다(KNK-1058, [§4-3-1](../spec/4-backend-server-spec.md#4-3-api-계약)). `Phase 3 · 구현`(KNK-1126, V76) — 이미지 정본이 `story_character_images`로 옮겨가며 `image_url`·`image_name`은 읽지 않는 릴리스 다음에 제거 예정 |

### 미결 설정

계획으로 적힌 설정·릴리스 게이트를 이관했습니다. Kakao client ID의 현재 사용법은 Design에 남기고 추가 게이트의 적용 여부는 아래 원문으로 구분합니다.

| 환경 변수 | 필수·당시 상태 | 원문 |
| --- | --- | --- |
| `MANYAK_KAKAO_CLIENT_IDS` | 카카오 로그인 사용 시 예 | **같은 카카오 디벨로퍼스 앱의** REST API 키(웹 `aud`)와 네이티브 앱 키(Android `aud`) 목록(콤마 구분). 사용하는 플랫폼의 키가 빠지면 그 플랫폼 로그인만 401이고, 변수 전체가 비면 모든 Kakao 로그인을 거부합니다(fail-closed). Google에는 영향이 없습니다. 다른 카카오 앱의 키 혼입 금지와 앱 ID 대조 릴리스 게이트는 [§4-5](../spec/4-backend-server-spec.md#4-5-인증과-권한)를 따릅니다(`Phase 1 · 계획`) |
| `MANYAK_GROBLE_WEBHOOK_SECRET` | 결제 사용 시 예(`Phase 3 · 계획`) | 그로블 웹훅 HMAC 시크릿. FCM의 미설정 관례에 따라 빈 값으로 기동할 수 있지만, 비어 있으면 웹훅·주문 생성은 503입니다. 상품 5종·결제창 링크는 `manyak.payment.groble.products[]` yml 설정으로 관리합니다([§4-3-7](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| `MANYAK_GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | 앱 결제 사용 시 예(`Phase 3 · 계획`) | androidpublisher 구매 검증·Voided Purchases API 대사용 서비스 계정 JSON |
| `MANYAK_GOOGLE_PLAY_PACKAGE_NAME` | 앱 결제 사용 시 예(`Phase 3 · 계획`) | Google Play 구매 검증 대상 앱 패키지 이름 |

## 4. 남은 본문 분리 계획

| 대상 | 유지할 정본 | 남은 작업 |
| --- | --- | --- |
| 용어·배경·유저 스토리 | 정의·서비스 맥락·승인된 요구·US ID | Phase·상태·Jira는 로드맵·추적, 화면·API 상세는 Spec 링크로 축소 |
| 공통·웹·Android Spec | 공통 계약과 승인된 플랫폼 예외 | 남은 내부 구조·저장 상세는 해당 Design, 미승인 목표는 추적·기능 계획으로 구분 |
| 웹 Design | 현재 요청·라우팅·인증·관측 구조 | 반복 사용자 계약은 Spec으로 연결. 일회성 변경·검증 이력은 추적에 연결 |
| 백엔드 Spec §4-3~4-7 | API 필드·권한·식별자·외부 상태·실패·관측 의미 | API 설명 안에 남은 질의·Redis·필터·예외 처리 구현을 Design과 대조해 통합. 미래 score outbox 등은 기능 계획으로 이동 |
| 백엔드 Spec §4-8 | 수용 기준·US↔API | B 계열 간극·Jira·검증 근거를 제품 추적으로 확장. 기존 HTTP·테스트·QA 절차 재사용 |
| AI Spec §5-3·5-9 | 온라인 API 계약 | 필드 정의를 §5-9에 모으고 알고리즘 상세는 Design으로 연결. 서비스별 refill 설명의 계약·구현 경계 추가 정리 |
| AI Spec §5-7~5-8 | 평가 대상·입력 조건·판정·합격 기준 | 온라인 API와 평가 문서 분리 필요성 확인. 연구 실행기는 연구 저장소 정본을 사용하고 새 번호는 실제 분리 시 배정 |
| AI ADR | D1~D13·기능·평가 결정 | A1~A22의 제약·후속 이력은 제품 추적과 연결. 기존 결정 원문·ID 유지 |
| 분석 Spec | 이벤트·지표·수집 제한·수용 기준 | 구현 개수·누락·Jira는 추적, SDK·저장 배선은 서비스 Design. 별도 관측 문서는 독립 책임이 확인될 때만 추가 |
| 배포 Design §4-1~4-9 | 현재 환경·책임·CI/CD·설정·복구 | 필수 격리·승격·롤백 조건과 현재 구조를 구분. 미래 전환은 기능 계획, 실행 결과는 추적 |
| 배포 Design §4-10~4-11 | 현재 제약 | Jira·PR·배포 이력·미결을 추적으로 연결하고 과거 활성화를 현재 운영 증거로 쓰지 않음 |

추적 문서는 지금은 `client-tracking.md`를 유지합니다. 서버·AI·분석 간극을 실제로 이관할 때 제품 전체 추적으로 확장하고 영역별 ID를 함께 표기합니다. 이름 변경만을 위해 빈 추적 파일을 추가하지 않습니다.

## 5. 진행 순서와 작성 규칙

1. 남은 각 절을 계약·현재 구조·결정·미래 계획·실행 근거로 분류합니다. 상충 기록은 승인·구현 근거를 확인하기 전 한쪽으로 단정하지 않습니다.
2. API 필드·이벤트·지표·수용 기준의 정본을 한 곳으로 정하고 소비 문서는 링크합니다. 공통 계약은 공통 Spec, 플랫폼 예외는 플랫폼 Spec에 둡니다.
3. 현재 Design에 미래 구조를 먼저 덮어쓰지 않습니다. 구체적 실행 계획은 웹 `docs/superpowers/plans/`, Android `docs/plans/` 등 기존 구현 저장소 계획을 재사용합니다.
4. ADR은 영역별 한 파일에 누적하며 확정된 결정 ID·본문을 보존합니다. 바꾸는 경우 새 결정에 이전 ID와 대체 범위를 기록합니다.
5. 각 파일의 제목·목차·읽는 순서·정보 표를 본문과 맞춥니다. 일반 절 번호는 해당 파일 접두어 아래에서 배정하며 US·FE-SCREEN·FLOW·ADR ID는 재번호하지 않습니다.
6. Phase·마일스톤은 roadmap, 담당·일정·진행은 Jira, 적용·간극·검증·배포 증거는 추적이 소유합니다. 코드 관측이나 문서 이동만으로 제품 정책·릴리스 완료를 선언하지 않습니다.

## 6. 검증과 복구

- 파일 수·빈 파일·제목/번호·본문 목차·로컬 링크/절 참조를 검사합니다. README·AGENTS·계획·QA·템플릿을 포함하고 CLAUDE→AGENTS 심볼릭 링크를 유지합니다.
- 백엔드 결정 원문 27개와 기존 ADR 확정 본문은 로컬 링크 수선을 제외하고 보존합니다. API 계약은 이동 범위 밖의 원문과 대조합니다.
- Android는 축약 전 설계·모듈 문서와 비교해 모듈 책임, 저장 호환, 토큰·세션 종료 순서, 제작 복구, 알림 계정 격리를 확인합니다. 화면별 문구·치수·QA의 상세 원문은 아래 기준 커밋에서 확인할 수 있습니다.
- 새로 끊긴 파일·절 링크가 없어야 합니다. 이전부터 로컬에 없는 `manyak-autoresearch` 대상 12개는 별도 미확인으로 구분하며 정상으로 판정하지 않습니다.
- 공백 검사는 `git diff --check`와 신규 Markdown을 함께 확인합니다. 코드·브라우저·기기 테스트는 이번 문서 변경의 실행 범위가 아닙니다. 구현 저장소에서 하네스로 들어오는 참조는 해당 저장소의 후속 검사 대상입니다.

### 축약 전 근거

- [Android 설계 원문](https://github.com/KIM-N-KANG/knk-harness/blob/f075a236ce7eb0c36ccb547471927e57954bd92f/docs/product-specs/3-7-android-design.md)
- [Android 모듈 설계 원문](https://github.com/KIM-N-KANG/knk-harness/blob/f075a236ce7eb0c36ccb547471927e57954bd92f/docs/planning/android-module-architecture.md)
- [백엔드 원문](https://github.com/KIM-N-KANG/knk-harness/blob/f075a236ce7eb0c36ccb547471927e57954bd92f/docs/product-specs/4-backend.md)
- [AI 원문](https://github.com/KIM-N-KANG/knk-harness/blob/f075a236ce7eb0c36ccb547471927e57954bd92f/docs/product-specs/5-1-ai-server-spec.md)

### 복구

문제가 생기면 이번 본문 이관과 관련 참조만 함께 되돌립니다. 기준 커밋을 원문 비교에 사용하되 사용자가 변경한 파일명과 다른 미커밋 변경을 덮어쓰는 전체 초기화는 하지 않습니다. 커밋 뒤에는 해당 문서 변경 커밋 단위로 복구합니다.

### 이번 검증 결과

- 제품 문서 19개, 빈 파일 0개. 별도 Android 모듈 파일은 제거했습니다.
- Android 설계·모듈 문서 합계 1,469줄을 통합 설계 270줄로 정리했습니다.
- 로컬 Markdown 링크 1,307개를 검사해 끊긴 절 참조 0개를 확인했습니다. 없는 경로는 기존 연구 저장소 대상 12개뿐입니다.
- 백엔드 결정 27개와 기존 공통·웹·Android·AI ADR의 확정 본문을 대조했습니다. 파일명·로컬 링크·절 번호 수선을 제외한 원문을 보존했습니다.
- 백엔드 엔드포인트 카탈로그·식별자·삭제·오류 계약과 AI API 명세의 원문 보존, 기존 외부 URL의 잔존, 축약 전 근거 커밋의 파일 존재를 확인했습니다.
- 제목 접두어·구 파일명 잔존·새 공백 오류·CLAUDE 심볼릭 링크·`git diff --check` 검사를 통과했습니다. 앱·서버 실행 테스트는 수행하지 않았습니다.

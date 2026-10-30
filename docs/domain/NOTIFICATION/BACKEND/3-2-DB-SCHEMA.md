# 3-2 DB 스키마

이 문서는 NOTIFICATION 도메인이 관리하는 PostgreSQL 테이블의 컬럼, 제약, 인덱스, Redis 키, 메시지 큐와 데이터 수명을 정한다.

다른 도메인의 테이블에서는 NOTIFICATION 도메인이 관리하거나 참조하는 컬럼만 설명한다.

입력값의 검증 규칙은 보안에, 잠금 순서와 멱등 규칙은 동시성에, 수명과 주기는 오류 처리에 있다. ([5-1-5 입력 검증](5-1-SECURITY.md#5-1-5-입력-검증), [5-2 동시성](5-2-CONCURRENCY.md), [5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도))

<br>

### 3-2-1 공통 규칙

| 규칙 | 내용 |
|---|---|
| 식별자 | 내부 PK는 `bigint` 자동 증가<br>캠페인과 알림 내역은 외부 노출용 `public_id uuid`를 따로 둠<br>토큰 행 ID는 노출하지 않음 |
| 시각 | `timestamp with time zone`<br>`created_at`은 아래 표에 표시하지 않으며 기본값은 `now()`<br>아웃박스의 `created_at`만 기본값 없이 기록 시점을 넣음 |
| 삭제 | 토큰과 알림 내역은 물리 삭제<br>템플릿, 캠페인, 아웃박스, 발송 결과는 삭제 경로 없음<br>템플릿은 종료 시각만 갱신 |
| FK | 토큰과 알림 내역은 회원 삭제 시 함께 삭제(`ON DELETE CASCADE`)<br>알림 내역의 스토리와 공지는 공개 식별자 사본이라 FK 없음<br>발송 결과의 회원과 캠페인은 연쇄 삭제 없음<br>회원 행은 탈퇴해도 남으므로 실제 연쇄 삭제는 일어나지 않음 |

<br>

### 3-2-2 관계도

관계도는 데이터 묶음별 소유 관계를 보여준다. 각 상자에는 식별과 연결에 쓰는 컬럼만 표시한다. 전체 컬럼은 아래 표에서 정의한다. 다른 도메인의 테이블은 관계 라벨에 도메인을 적고 컬럼을 생략한다.

```mermaid
erDiagram
    users ||--o{ device_push_tokens : "ACCOUNT, 기기"
    device_push_tokens {
        bigint id PK
        bigint user_id FK
        varchar token
        varchar platform
    }
    users ||--o{ user_notifications : "ACCOUNT, 받는 회원"
    user_notifications {
        bigint id PK
        uuid public_id
        bigint user_id FK
        varchar message_key
        varchar category
    }
    push_message_templates {
        bigint id PK
        varchar template_key
    }
    notices |o--o{ push_campaigns : "NOTICE, 공지 알림"
    push_campaigns {
        bigint id PK
        uuid public_id
        varchar kind
        varchar status
        bigint notice_id FK
    }
    push_outbox {
        bigint id PK
        varchar message_id
        varchar status
    }
    push_campaigns |o--o{ push_delivery_results : "캠페인 메시지"
    users |o--o{ push_delivery_results : "ACCOUNT, 수신 회원"
    push_delivery_results {
        bigint id PK
        varchar message_id
        varchar type
        bigint campaign_id FK
        bigint user_id FK
        varchar outcome
    }
```

<br>

### 3-2-3 푸시 토큰

**`device_push_tokens`**

회원 기기의 설치본 하나가 한 행이다. 게스트 기기는 저장하지 않는다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | |
| `user_id` | bigint | NOT NULL, FK `users.id` CASCADE | 소유 회원<br>같은 기기에서 계정이 바뀌면 소유 회원 변경 |
| `token` | varchar(512) | NOT NULL, UNIQUE | FCM 등록 토큰 |
| `platform` | varchar(16) | NOT NULL, CHECK `ANDROID` `WEB` | |
| `updated_at` | timestamptz | NOT NULL, 기본 `now()` | 마지막 등록 시각<br>값이 같아도 재등록마다 갱신 |

| 인덱스 | 컬럼 |
|---|---|
| `idx_device_push_tokens_user` | `user_id` |

<br>

### 3-2-4 수신 동의

**`users`**

회원 행의 세 컬럼은 이 도메인이 관리한다. 다른 컬럼은 계정 도메인이 정한다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `service_push_enabled` | boolean | NOT NULL, 기본 `true` | 서비스 알림 수신 여부 |
| `marketing_push_agreed_at` | timestamptz | | 광고 알림 최초 동의 시각<br>`NULL`이면 미동의 또는 철회 |
| `marketing_push_night_agreed_at` | timestamptz | | 야간 광고 알림 최초 동의 시각<br>광고 동의 없이 단독으로 값이 있을 수 없음 |

<br>

### 3-2-5 문구 템플릿

**`push_message_templates`**

출석 리마인드와 이프 만료 예정 알림 문구의 오버라이드 1건이 한 행이다. 행이 없으면 기본 문구를 쓴다. 관리자 API가 행을 추가한다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | |
| `template_key` | varchar(64) | NOT NULL | 템플릿 키<br>값은 `attendance_reminder`, `credit_expiry_reminder` |
| `title` | varchar(100) | NOT NULL | 광고 표기 없는 제목 |
| `body` | varchar(300) | NOT NULL | 수신거부 안내 없는 본문 |
| `effective_from` | timestamptz | NOT NULL, 기본 `now()` | 적용 시작<br>유효한 행이 여럿이면 가장 늦게 시작한 행, 같으면 `id`가 큰 행 |
| `effective_until` | timestamptz | | 적용 종료<br>`NULL`은 상시 적용<br>기본 문구로 복귀할 때 현재 시각으로 갱신 |

| 인덱스 | 컬럼 |
|---|---|
| `idx_push_message_templates_key` | `template_key` |

<br>

### 3-2-6 캠페인

**`push_campaigns`**

캠페인 1건의 예약과 결과가 한 행이다. 관리자 API가 예약 행을 추가하고 스케줄러가 결과를 기록한다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | |
| `public_id` | uuid | NOT NULL, UNIQUE | 푸시 데이터의 캠페인 식별자 |
| `kind` | varchar(16) | NOT NULL, 기본 `MARKETING`, CHECK `SERVICE` `MARKETING` | 대상 조건과 시나리오를 정함<br>공지 알림은 공지 태그에서 정한 값 |
| `notice_id` | bigint | FK `notices.id` | 공지 알림이면 연결한 공지<br>한 공지에 여러 행<br>프로모션은 NULL |
| `notice_tag` | varchar(16) | CHECK `SERVICE` `UPDATE` `MAINTENANCE` `EVENT` `PROMOTION` | 공지 알림이면 연결할 때의 공지 태그<br>프로모션은 NULL |
| `story_id` | bigint | FK `stories.id` | 이동 대상 스토리<br>없으면 NULL |
| `title` | varchar(100) | NOT NULL | 광고 표기 없는 제목 |
| `body` | varchar(300) | NOT NULL | 수신거부 안내 없는 본문 |
| `scheduled_at` | timestamptz | NOT NULL | 발송 예약 시각 |
| `status` | varchar(20) | NOT NULL, CHECK `SCHEDULED` `SENDING` `SENT` `CANCELED` `FAILED` | |
| `target_count` | integer | | 마지막 회차에서 조회된 대상 수 |
| `sent_count` | integer | | 마지막 회차의 결과<br>원격 모드는 기록한 발송 요청 수, 로컬 모드는 발송기 호출 수 |
| `skipped_count` | integer | | 사용하지 않음 |
| `started_at` | timestamptz | | 선점 시각<br>전송 중 시간 초과 판정의 기준 |
| `deep_link_included` | boolean | | 기록한 발송 요청 가운데 딥링크를 넣은 요청이 있는지<br>회차가 발송 요청을 기록하는 트랜잭션에서 갱신<br>한 번 참이면 재실행해도 거짓으로 바꾸지 않음<br>발송 요청을 기록한 적 없으면 NULL |
| `finished_at` | timestamptz | | 회차 종료 시각 |

| 인덱스 | 컬럼 |
|---|---|
| `idx_push_campaigns_status_scheduled_at` | `status`, `scheduled_at` |

- 공지 참조에는 인덱스를 두지 않는다. 공지로 캠페인을 찾는 조회가 없고 공지 삭제의 참조 확인은 캠페인 수가 적어 전체 읽기로 끝난다.

<br>

### 3-2-7 아웃박스

**`push_outbox`**

원격 모드에서 발송 요청 1건이 한 행이다. 도메인 커밋과 같은 트랜잭션에 기록한다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | 선점 순서 |
| `message_id` | varchar(255) | NOT NULL, UNIQUE | 메시지 식별자 |
| `payload` | jsonb | NOT NULL | 큐 메시지 본문 |
| `status` | varchar(16) | NOT NULL, 기본 `PENDING`, CHECK `PENDING` `PUBLISHED` `FAILED` | |
| `attempts` | integer | NOT NULL, 기본 0 | 발행 실패 횟수<br>관찰용이며 포기 판정에 쓰지 않음 |
| `next_attempt_at` | timestamptz | NOT NULL | 다음 선점 가능 시각<br>선점 중에는 임대 만료 시각 |
| `published_at` | timestamptz | | |

| 인덱스 | 컬럼 |
|---|---|
| `idx_push_outbox_pending` | `next_attempt_at` WHERE `status = 'PENDING'` |

<br>

### 3-2-8 참조하는 다른 도메인의 컬럼

| 테이블 | 컬럼 | NOTIFICATION이 하는 일 |
|---|---|---|
| `users` | `status` | 발송 자격 판정<br>알림 내역 대상과 요청자 상태 판정 |
| `users` | `public_id` | 수신자 식별자<br>발송 결과의 수신 회원 해석 |
| `users` | `reward_identity_user_id` | 출석 미수령 판정 |
| `users` | `service_push_enabled`, `marketing_push_agreed_at`, `marketing_push_night_agreed_at` | 이 도메인이 관리하는 컬럼<br>캠페인 대상 조회와 대상 수 미리보기 |
| `credit_transactions` | `idempotency_key` | 당일 출석 보상 키의 존재 여부로 미수령 판정 |
| `credit_lots` | `remaining` | 잔여가 있는 로트만 만료 예정 판정 |
| `credit_lots` | `expires_at` | 만료 예정 판정과 발송 요청의 유효 기한 |
| `notices` | `id`<br>`public_id` | 공지 알림 캠페인의 참조와 딥링크 경로값 |

<br>

### 3-2-9 Redis 키

`push:` 키는 서버가 쓴다. `notification:` 키는 알림 서비스가 쓴다.

| 키 | 값 | 삭제 |
|---|---|---|
| `push:attendance-reminder:{KST 날짜}` | `1` | 선점 키 수명 만료 |
| `push:credit-expiry-reminder:{KST 날짜}` | `1` | 선점 키 수명 만료 |
| `push:credit-expiry-reminder:cooldown:{회원 내부 ID}` | `1` | 쿨다운 수명 만료 |
| `notification:processed:{메시지 식별자}` | 처리 중이면 소유자 값, 완료면 `done` | 처리 중 선점 수명 만료<br>완료 후 멱등 기록 수명 만료 |
| `notification:sent:{메시지 식별자}` | 성공한 토큰의 SHA-256 해시 집합 | 멱등 기록 수명 만료 |

<br>

### 3-2-10 메시지 큐

| 큐 | 내용 | 설정 |
|---|---|---|
| `push-requested` | 발송 요청 | SQS 표준 큐<br>실제 이름에는 프로젝트와 환경 접두를 붙임<br>수신 상한을 넘기면 실패 메시지 큐로 이동 |
| `push-requested-dlq` | 재전달 상한을 넘긴 메시지 | 보존 기간 만료 시 삭제 |

<br>

### 3-2-11 데이터 수명

| 데이터 | 삭제 |
|---|---|
| 푸시 토큰 | 삭제 요청, 탈퇴, 무효 통지, 기기 상한 초과 삭제 |
| 수신 동의 | 없음<br>철회는 값을 비움 |
| 문구 템플릿, 캠페인, 아웃박스, 발송 결과 | 없음 |
| 알림 내역 | 탈퇴, 회원 행 삭제 시 연쇄 삭제<br>보관 기간과 정리 작업 없음 |

<br>

### 3-2-12 알림 내역과 발송 결과

**`user_notifications`**

회원이 받은 알림의 사본 1건이 한 행이다. 알림함이 읽는다. 시나리오별 기록 시점에 서버가 추가하고 푸시 설정이나 토큰 보유와 무관하게 남긴다. 이프 만료 예정 알림은 회차 트랜잭션에서 대상 회원마다 기록한다. ([4-1-19 알림 내역 기록](4-1-PIPELINES.md#4-1-19-알림-내역-기록))

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | 같은 생성 시각 안의 정렬 기준 |
| `public_id` | uuid | NOT NULL, UNIQUE | 알림함 API의 식별자<br>읽음 처리 경로값과 목록 커서 |
| `user_id` | bigint | NOT NULL, FK `users.id` CASCADE | 받는 회원 |
| `message_key` | varchar(255) | NOT NULL | 메시지 식별자와 같은 값<br>발송 모드와 무관하게 같은 값 |
| `type` | varchar(40) | NOT NULL, CHECK `STORY_COMPLETED` `STORY_MODERATION_COMPLETED` `STORY_TAKEN_DOWN` `NOTICE` `ATTENDANCE_REMINDER` `CREDIT_EXPIRY_REMINDER` `PROMOTION` | 시나리오 식별자<br>`CREDIT_EXPIRY_REMINDER`는 CHECK 확장 마이그레이션이 필요 |
| `category` | varchar(16) | NOT NULL, CHECK `NEWS` `ACTIVITY` | 알림 분류<br>기록 시 종류에서 정함<br>`CREDIT_EXPIRY_REMINDER`는 `ACTIVITY` |
| `title` | varchar(120) | NOT NULL | 표시 제목<br>광고 알림도 광고 표기 없는 원문 |
| `body` | varchar(300) | NOT NULL | 표시 본문<br>광고 알림도 수신거부 안내 없는 원문 |
| `deep_link` | varchar(512) | | 눌렀을 때 열 절대 URL<br>딥링크가 없는 프로모션은 NULL |
| `story_public_id` | uuid | | 관련 스토리 공개 식별자<br>FK 없음<br>이프 만료 예정 알림은 NULL |
| `notice_public_id` | uuid | | 관련 공지 공개 식별자<br>FK 없음<br>이프 만료 예정 알림은 NULL |
| `notice_tag` | varchar(16) | CHECK `SERVICE` `UPDATE` `MAINTENANCE` `EVENT` `PROMOTION` | 공지 알림이면 캠페인의 공지 태그<br>그 외 NULL |
| `read_at` | timestamptz | | 읽음 시각<br>`NULL`이면 안 읽음 |

| 제약과 인덱스 | 컬럼 | 쓰임 |
|---|---|---|
| `uk_user_notifications_user_message` | `user_id`, `message_key` UNIQUE | 같은 알림의 중복 기록 방지 |
| `idx_user_notifications_user_created` | `user_id`, `created_at DESC`, `id DESC` | 전체 목록 |
| `idx_user_notifications_user_category_created` | `user_id`, `category`, `created_at DESC`, `id DESC` | 분류별 목록 |
| `idx_user_notifications_unread` | `user_id`, `category` WHERE `read_at IS NULL` | 분류별 안 읽은 수와 모두 읽음 |

- 행은 기록 시점의 사본이다. 원본 스토리나 공지가 바뀌거나 사라져도 고치지 않는다.
- 같은 회차의 행은 생성 시각이 같아 `id`로 순서를 정한다. 정렬 방향을 목록과 같게 두어 커서 조회가 인덱스 범위 조회로 끝난다.

<br>

**`push_delivery_results`**

메시지 식별자별 최종 발송 결과 1건이 한 행이다. 알림 서비스의 보고와 로컬 모드 발송기가 기록한다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | |
| `message_id` | varchar(255) | NOT NULL, UNIQUE | 메시지 식별자 |
| `type` | varchar(40) | NOT NULL | 시나리오 식별자<br>허용 값은 발송 결과 보고의 `type`과 같음 |
| `kind` | varchar(16) | NOT NULL, CHECK `SERVICE` `MARKETING` | |
| `campaign_id` | bigint | FK `push_campaigns.id` | 캠페인 발송만<br>그 외 NULL |
| `user_id` | bigint | FK `users.id` | 수신 회원<br>보고 시점에 존재한 회원만<br>공개 식별자에 해당하는 회원이 없으면 NULL |
| `outcome` | varchar(16) | NOT NULL, CHECK `DELIVERED` `UNDELIVERED` `DISCARDED` | |
| `reason` | varchar(40) | NOT NULL | 발송 응답의 `reason` 값 |
| `delivered_devices` | integer | NOT NULL, CHECK `>= 0` | 재전달을 포함해 FCM이 받아들인 기기 수 |
| `failed_devices` | integer | NOT NULL, CHECK `>= 0` | 마지막 처리에서 영구 실패한 기기 수<br>무효 토큰은 포함하지 않음 |
| `completed_at` | timestamptz | NOT NULL | 처리가 끝난 시각<br>통계의 날짜 기준 |

| 인덱스 | 컬럼 |
|---|---|
| `idx_push_delivery_results_campaign` | `campaign_id` WHERE `campaign_id IS NOT NULL` |
| `idx_push_delivery_results_type_completed` | `type`, `completed_at` |

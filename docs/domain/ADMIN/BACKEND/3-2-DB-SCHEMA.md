# 3-2 DB 스키마

이 문서는 ADMIN 도메인이 관리하는 PostgreSQL 테이블의 컬럼, 제약, 인덱스와 데이터 수명을 정한다.

다른 도메인의 테이블에서는 ADMIN 도메인이 참조하는 컬럼만 설명한다.

입력값의 검증 규칙은 보안에 있으며 감사 기록의 트랜잭션 규칙은 동시성에 있다. ([5-1-5 입력 검증](5-1-SECURITY.md#5-1-5-입력-검증), [5-2 동시성](5-2-CONCURRENCY.md))

<br>

### 3-2-1 공통 규칙

| 규칙 | 내용 |
|---|---|
| 식별자 | 내부 PK는 `bigint` 자동 증가<br>감사 로그는 외부 노출용 `public_id uuid`를 따로 둠<br>감사 로그의 대상은 그 도메인의 외부 식별자 문자열로 기록 |
| 시각 | `timestamp with time zone`<br>`created_at`의 기본값은 `now()`이며 아래 표에서는 표시하지 않음 |
| 삭제 | 감사 로그는 삭제 경로 없음<br>관리자 역할은 운영자가 행을 삭제 |
| FK | 관리자 역할은 회원 삭제 시 함께 삭제(`ON DELETE CASCADE`)<br>감사 로그의 처리자는 연쇄 삭제 없음<br>회원 행은 탈퇴해도 남으므로 실제 연쇄 삭제는 일어나지 않음 |

<br>

### 3-2-2 관계도

관계도는 데이터 묶음별 소유 관계를 보여준다. 각 상자에는 식별과 연결에 쓰는 컬럼만 표시한다. 전체 컬럼은 아래 표에서 정의한다. 다른 도메인의 테이블은 관계 라벨에 도메인을 적고 컬럼을 생략한다.

```mermaid
erDiagram
    users ||--o| admin_accounts : "ACCOUNT, 관리자 역할"
    users ||--o{ admin_audit_logs : "ACCOUNT, 처리자"
    admin_accounts {
        bigint user_id PK
        timestamptz granted_at
    }
    admin_audit_logs {
        bigint id PK
        uuid public_id
        bigint admin_user_id FK
        varchar action
        varchar target_type
        varchar target_id
    }
```

<br>

### 3-2-3 관리자 역할

**`admin_accounts`**

관리자 역할을 가진 회원 1명이 1행이다. 운영자가 직접 기록하고 삭제한다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `user_id` | bigint | PK, FK `users.id` CASCADE | |
| `granted_at` | timestamptz | NOT NULL, 기본 `now()` | 부여 시각 |

<br>

### 3-2-4 감사 로그

**`admin_audit_logs`**

관리자의 변경 작업 1건 또는 개인정보 조회 1건이 한 행이다. 추가만 하고 수정하지 않는다.

| 컬럼 | 타입 | 제약 | 의미 |
|---|---|---|---|
| `id` | bigint | PK | |
| `public_id` | uuid | NOT NULL, UNIQUE | 외부 노출 식별자 |
| `admin_user_id` | bigint | NOT NULL, FK `users.id` | 처리자 |
| `category` | varchar(10) | NOT NULL, CHECK `CHANGE` `ACCESS` | 변경 작업 또는 개인정보 조회 |
| `action` | varchar(50) | NOT NULL | 작업 이름<br>목록은 아래 |
| `target_type` | varchar(30) | NOT NULL | 대상 종류<br>목록은 아래 |
| `target_id` | varchar(255) | NOT NULL | 대상의 외부 식별자<br>회원, 공지, 캠페인, 제출본, 스토리는 공개 식별자<br>정책값은 정책 키<br>검색은 검색어 |
| `reason` | varchar(500) | | 사유<br>변경 작업은 NOT NULL, 조회는 NULL |
| `before_state` | jsonb | | 변경 전 값<br>조회와 생성은 NULL<br>필드는 아래 기록 허용 목록만 |
| `after_state` | jsonb | | 변경 후 값<br>조회와 삭제는 NULL<br>필드는 아래 기록 허용 목록만 |
| `request_id` | varchar(64) | NOT NULL | 상관관계 필터가 확정한 요청 ID<br>헤더 값이 조건에 어긋나면 서버 생성 값 |

| 인덱스 | 컬럼 |
|---|---|
| `idx_admin_audit_logs_created` | `created_at DESC`<br>`public_id` |
| `idx_admin_audit_logs_admin` | `admin_user_id`<br>`created_at DESC` |
| `idx_admin_audit_logs_target` | `target_type`, `target_id`, `created_at DESC` |

| `action` | `category` | `target_type` | 기록하는 도메인 |
|---|---|---|---|
| `MEMBER_SEARCHED` | `ACCESS` | `MEMBER_QUERY` | ADMIN |
| `MEMBER_VIEWED` | `ACCESS` | `MEMBER` | ADMIN |
| `MEMBER_SUSPENDED` | `CHANGE` | `MEMBER` | ACCOUNT |
| `MEMBER_UNSUSPENDED` | `CHANGE` | `MEMBER` | ACCOUNT |
| `CREDIT_GRANTED` | `CHANGE` | `MEMBER` | PAYMENT |
| `CREDIT_REVOKED` | `CHANGE` | `MEMBER` | PAYMENT |
| `CREDIT_POLICY_UPSERTED` | `CHANGE` | `CREDIT_POLICY` | PAYMENT |
| `CREDIT_POLICY_DELETED` | `CHANGE` | `CREDIT_POLICY` | PAYMENT |
| `PUSH_CAMPAIGN_CREATED` | `CHANGE` | `PUSH_CAMPAIGN` | NOTIFICATION |
| `PUSH_CAMPAIGN_CANCELED` | `CHANGE` | `PUSH_CAMPAIGN` | NOTIFICATION |
| `PUSH_CAMPAIGN_RETRIED` | `CHANGE` | `PUSH_CAMPAIGN` | NOTIFICATION |
| `PUSH_TEMPLATE_UPSERTED` | `CHANGE` | `PUSH_TEMPLATE` | NOTIFICATION |
| `PUSH_TEMPLATE_RESET` | `CHANGE` | `PUSH_TEMPLATE` | NOTIFICATION |
| `NOTICE_CREATED` | `CHANGE` | `NOTICE` | NOTICE |
| `NOTICE_UPDATED` | `CHANGE` | `NOTICE` | NOTICE |
| `NOTICE_PUBLISHED` | `CHANGE` | `NOTICE` | NOTICE |
| `NOTICE_UNPUBLISHED` | `CHANGE` | `NOTICE` | NOTICE |
| `NOTICE_DELETED` | `CHANGE` | `NOTICE` | NOTICE |
| `SUBMISSION_HOLD_RELEASED` | `CHANGE` | `SUBMISSION` | MODERATION |
| `ORIGINAL_CREATED` | `CHANGE` | `STORY` | STORY |
| `ORIGINAL_UPDATED` | `CHANGE` | `STORY` | STORY |
| `ORIGINAL_THUMBNAIL_DELETED` | `CHANGE` | `STORY` | STORY |

변경 전후 값에 넣을 수 있는 필드는 작업마다 다음으로 한정한다. 목록에 없는 필드는 넣지 않는다. 회원의 이메일, 닉네임, 소셜 식별자, 프로필 이미지, 채팅 메시지 원문은 어떤 작업에서도 넣지 않는다.

| `action` | `before_state` | `after_state` |
|---|---|---|
| `MEMBER_SUSPENDED`, `MEMBER_UNSUSPENDED` | `status` | `status` |
| `CREDIT_GRANTED` | `balance` | `balance`, `amount`, `expiresInDays`, `expiresAt` |
| `CREDIT_REVOKED` | `balance` | `balance`, `amount`, `shortfall` |
| `CREDIT_POLICY_UPSERTED` | `policyKey`, `value`, `endsAt` | `policyKey`, `value`, `endsAt` |
| `CREDIT_POLICY_DELETED` | `policyKey`, `value`, `endsAt` | 없음 |
| `PUSH_CAMPAIGN_CREATED` | 없음 | `kind`, `title`, `body`, `scheduledAt`, `status`, `storyId` |
| `PUSH_CAMPAIGN_CANCELED`, `PUSH_CAMPAIGN_RETRIED` | `status`, `scheduledAt` | `status`, `scheduledAt` |
| `PUSH_TEMPLATE_UPSERTED` | 없음 | `templateKey`, `title`, `body`, `effectiveFrom`, `effectiveUntil` |
| `PUSH_TEMPLATE_RESET` | `templateKey`와 종료한 행마다 `title`, `body`, `effectiveFrom`, `effectiveUntil` | 없음 |
| `NOTICE_CREATED` | 없음 | `title`, `status` |
| `NOTICE_UPDATED` | `title`, `status` | `title`, `status` |
| `NOTICE_PUBLISHED`, `NOTICE_UNPUBLISHED` | `status`, `publishedAt`, `notifiedAt` | `status`, `publishedAt`, `notifiedAt` |
| `NOTICE_DELETED` | `title`, `status` | 없음 |
| `SUBMISSION_HOLD_RELEASED` | `holdReason`, `attempt` | 없음 |
| `ORIGINAL_CREATED` | 없음 | `status`, `visibility`, `title`, `genres` |
| `ORIGINAL_UPDATED` | `status`, `visibility`, `title`, `genres` | `status`, `visibility`, `title`, `genres` |
| `ORIGINAL_THUMBNAIL_DELETED` | `thumbnailUrl` | 없음 |

공지 본문은 5,000자까지라 변경 전후 값의 상한을 넘으므로 넣지 않는다. 변경 내용은 공지 상세로 확인한다.

<br>

### 3-2-5 참조하는 다른 도메인의 컬럼

| 테이블 | 컬럼 | ADMIN이 하는 일 |
|---|---|---|
| `users` | `id`, `public_id`, `nickname`, `status`, `created_at`, `deleted_at` | 관리자 판정, 회원 목록과 상세, 회원 수 집계, 팀 계정 제외 판정, 소유자 요약 |
| `social_accounts` | `user_id`, `email`, `deleted_at` | 회원 목록의 이메일 정확 일치 검색 |
| `story_chats` | `id`, `public_id`, `story_id`, `user_id`, `current_turn`, `created_at`, `updated_at`, `deleted_at` | 채팅 시작 수, 채팅방 목록과 상세, 턴 분포, 유지율, 회원의 채팅방 수와 최근 활동 |
| `story_messages` | `chat_id`, `role`, `created_at` | 채팅 턴 수, 첫 사용자 메시지 시각, 턴 날짜 필터<br>`content`는 읽지 않음 |
| `stories` | `id`, `public_id`, `user_id`, `title`, `description`, `genre`, `visibility`, `created_at`, `deleted_at` | 스토리 수, 스토리 목록과 상세, 장르 필터, 범위 판정 |
| `story_creation_sessions` | `id`, `user_id`, `story_id`, `created_at` | 제작 세션 차트, 스토리의 태그와 주변 인물 수 |
| `story_creation_characters` | `id`, `creation_session_id`, `role`, `name`, `gender` | 입력한 주변 인물 수 |
| `story_creation_session_tags` | `creation_session_id`, `character_id`, `tag_id` | 스토리의 태그<br>인물에 연결된 특징 태그로 입력 여부 판정 |
| `story_creation_tags` | `id`, `name`, `tag_type` | 태그 이름 |
| `ai_call_logs` | `feature`, `status`, `latency_ms`, `story_id`, `chat_id`, `created_at` | AI 호출 차트, 스토리와 채팅방의 AI 호출 필터 |
| `credit_transactions` | `id`, `user_id`, `amount`, `reason`, `ref_type`, `ref_id`, `created_at` | 이프 지급과 소진, 출석, 회원 거래 내역과 소모, 채팅방 소모, 결제 전후 비교 |
| `credit_orders` | `id`, `public_id`, `user_id`, `product_id`, `status`, `price_krw`, `credit_amount`, `completed_at`, `refunded_at`, `reversal_shortfall` | 결제 건수와 금액, 결제 내역과 상세, 회원 결제액 |
| `story_submissions` | `story_id`, `status`, `held_at` | 스토리의 보류 상태 |

<br>

### 3-2-6 데이터 수명

| 데이터 | 삭제 |
|---|---|
| 관리자 역할 | 운영자가 삭제 |
| 감사 로그 | 없음 |

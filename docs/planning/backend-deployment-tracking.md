# backend-deployment-tracking

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | v1.0 |
| 작성일 | 2026-09-12 |
| 수정일 | 2026-09-13 |
| 대상 | 백엔드·배포 문서 |
| 작성 목적 | 현재 계약과 구현 차이·문서 복원 범위를 추적합니다. |

## 읽는 순서

- 조사 범위와 현재 차이를 확인하고 연결한 Spec·ADR·코드로 이동합니다.

## 목차

- [백엔드 구현 차이](#백엔드-구현-차이)
- [배포 구현 차이](#배포-구현-차이)
- [복원과 검증 근거](#복원과-검증-근거)
- [후속 계약 검토](#후속-계약-검토)

## 백엔드 구현 차이

| ID | 합의·관측 차이 | 근거·처리 |
| --- | --- | --- |
| IMG-01 | 합의된 SSE `imageName`·`completed.characterImages[]`가 현재 서버 출력 DTO에 없음. `character_image` 중계 자체는 구현됨 | `ChatDtos.kt`의 `ChatStreamCharacterImageEvent`·`ChatStreamCompletedEvent`, `ChatService` 중계. 합의는 BE-028·Spec에 유지하고 누락 구현으로 추적. 상세·공유 배열 복원은 2026-08-28 결정에 따라 제외 |
| IMG-02 | 배경 후보 연결·AI 전달·`completed.images[]` 트랙은 인물 이미지와 별도 미구현 | 인물 이미지 완성을 근거로 배경 완성을 표시하지 않음. 현재 합의된 후보·마커 계약은 Spec에 유지 |
| CREDIT-01 | 런타임 정책 변경 전후 혼합 단가에 그룹 대사 금액 부족 가능 | BE-033. 기존 개수 기반 대사와 경고를 현재 한계로 기록. 정확한 차감 행 단위 대사는 새 설계 필요 |
| CREDIT-02 | 재가입 전후 다른 지갑이 같은 보상 신원의 초대 월 한도를 동시에 판정하면 1회 초과 가능 | BE-029. 지갑 락을 전역 신원 잠금으로 오해하지 않음 |
| PLAN-01 | 키워드 단계 개편·선호 score·검수 완료 푸시 등 기존 합의의 미완료 범위 | 각 Spec 상세 계약과 기존 planning의 미결 항목을 유지. 이번 문서 작업으로 구현·외부 활성화 완료 처리하지 않음 |
| LEGACY-01 | 과거 B번호 목록에는 완료·미완료가 혼재 | B10의 생성 표지·인물 S3 저장, 결제 API·V78~79는 코드 존재 확인. 옛 B표는 Git 스냅샷에 보존하고 현재 표와 중복 관리하지 않음 |
| RISK-01 | 게스트 체험 한도는 디바이스 헤더 변조·기기 교체·게스트↔게스트 접근으로 우회 가능. 카운터에 TTL·총량 상한 없음 | 옛 B8. 서버가 게스트를 식별할 수 없어 수용하고 관측으로 추적. 키 TTL·총량 상한은 후속 강화([Spec §4-3-7](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| RISK-02 | 피드백 등 무인증 쓰기 경로에 rate limit 없음 | 옛 B18. 등록량 급증을 관측으로 추적([Spec §4-3-4](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| RISK-03 | 게스트 이관은 UUID 소유를 증명할 수 없고 `status` 4종이 열거 오라클이 될 수 있음 | 옛 B19. 시도 상한 5회(`migration_attempts`)로 열거 규모를 제한하고 잔여는 수용([Spec §4-3-5](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| RISK-04 | 새 소셜 계정을 계속 만드는 Sybil 보상 파밍 | 옛 B21. 탈퇴·재가입 축은 KNK-1053으로 닫힘. 기존 계정 쌍의 상호 코드 입력(쌍당 최대 2,000 이프)도 수용 |
| RISK-05 | 선택 기록의 세대 가드는 요청 전에 끝난 재생성을 막지 못함 | 옛 B25. 클라이언트가 본 선택지의 `choiceId`를 보내는 KNK-762 계약에서 해결 예정([Spec §4-3-3](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| OBS-01 | 운영 readiness의 Redis 검사가 비활성(`management.health.redis.enabled=false`) | 재활성 시점 미정. 활성화 시 Redis 장애가 readiness 실패로 이어지는 영향 범위를 먼저 확인 |
| OBS-02 | Langfuse 선호 행동 저장·score 발행(KNK-762) 미구현 | 트레이스 연결 식별자 전달(KNK-707·751·755)과 직접 입력 장르 관측은 구현됨. 미결: 상호작용 API 경로·와이어 형식, 공개 ID 자료형, 생성 버전 연결 테이블, `request_id`→trace ID 조회·보관, outbox 상태·재시도, Langfuse 클라이언트 환경 변수·가드, `selectionAttemptId`·`inputAttemptId` 규약(manyak-web과 합의), 부모 요청의 스토리라인 단계 검증 |
| OBS-03 | 재생성은 AI 판정 메타(사건 완결·목표·엔딩)를 다시 쓰지 않음 | 폐기·재기록 정합 문제로 현재 범위에서 제외. 엔딩 도달 턴 재생성은 409로 차단([Spec §4-3-10](../spec/4-backend-server-spec.md#4-3-api-계약)) |
| SCHEMA-01 | `creation_session_id` FK 컬럼명이 용어집 `creation_id` 계열과 다름 | 2026-07-07 결정으로 Flyway 개명 예정, 미실행([Spec §4-4](../spec/4-backend-server-spec.md#4-4-데이터-모델)) |
| SCHEMA-02 | `story_characters.image_url` 잔존 컬럼 | V76이 정본을 `story_character_images`로 옮김. 읽는 코드가 사라진 릴리스 다음 릴리스에서 DROP(expand/contract) |
| PLAN-02 | 프리셋 배정 도입 전 가입한 회원의 Google `name`·`picture` 백필 여부 미결 | 신규 가입분만 프리셋 배정 적용 |
| PLAN-03 | `story_creation_requests` 행 보존 기간·정리 정책 미정 | 현재 무기한 보존 |
| PLAN-04 | 스토리 신고의 사유 enum·중복 정책·접수 후 처리 미확정 | Spec은 엔드포인트 골격만 고정. Slack 신고 webhook 배선은 DEP-035 |
| PLAN-05 | 공개 스토리 목록 정렬 인덱스 미추가 | 목록이 커지면 `latest` 부분 인덱스·`popular` 비정규화 검토 |

## 배포 구현 차이

| ID | 확인 범위 | 후속 확인 |
| --- | --- | --- |
| DPL-01 | Terraform dev 현재 코드의 ECS·RDS·Redis·IAM·설정 참조 확인 | 실제 AWS state·태스크 revision·digest·활성 설정은 배포 실행 기록으로 확인. 이번 작업에서 apply·배포하지 않음 |
| DPL-02 | prod FCM·결제 참조가 코드에 존재 | 시크릿 값 등록·태스크 참조·재배포·기능 성공을 구분. PR의 예정 작업을 활성화 완료로 간주하지 않음 |
| DPL-03 | 운영 AI 모델 Parameter는 ignore_changes | Terraform 기본값 변경으로 기존 운영값이 변경됐다고 쓰지 않음. 모델 설정과 AI 이미지 호환성을 같은 배포에서 확인 |
| DPL-04 | 로컬 Compose 모델 기본값과 AWS 모델 선언이 다름 | 사용 이미지의 모델 등록부와 실행값 대조. manyak-infra 코드는 이번 문서 작업에서 변경하지 않음 |
| DPL-05 | server·ai workflow의 concurrency는 레포별 | 공유 ECS 태스크의 레포 간 동시 배포는 전역 직렬화로 표현하지 않음 |

## 복원과 검증 근거

복원 근거는 네 레포의 로컬 Git 이력과 GitHub PR입니다. 백엔드 ADR은 BE-001~027을 보존하고 BE-028~043을 추가했으며, 배포 ADR은 Terraform PR #1~46을 DEP-001~046으로 연결했습니다. 2026-09-12는 복원일이며 결정일·병합일·실배포일과 다릅니다. 기존 [재구성 계획](product-document-reorganization.md)은 당시 기록으로 보존합니다.

## 후속 계약 검토

- 현재 상태: 인물 단위 입력과 `customGenreTags`를 사용하며 배경 카테고리는 API에 없습니다.
- 검토 항목: 장르·배경 각 1~2개 선택, 제공 태그만 허용, 인물 특징 직접 입력 유지, 40종 마스터·이미지·로어북 시드 동시 변경.
- 제외 근거: 2026-07-20의 8개 장르·11개 배경은 V57 이전 초안입니다. 폐기 결정이 확인되지 않아 현재 목록으로 옮기지 않습니다.

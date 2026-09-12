# 4-deployment

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | v1.1 |
| 작성일 | 2026-07-03 |
| 수정일 | 2026-09-13 |
| 대상 | 마냑 운영·개발·통합 배포 |
| 작성 목적 | 현재 배포 구성·설정·실행·검수·복구 구조를 설명합니다. 코드와 함께 갱신합니다. |
| 기준 코드 | `manyak-terraform` dev `4c9921970160`. 실제 AWS 활성 상태와 구분합니다. |

## 읽는 순서

- 이 문서에서 현재 구성을 확인한 뒤, 변경 이유와 전환 이력은 [배포 ADR](../adr/4-deployment-adr.md)을 봅니다. 이전 종합 문서 원문은 [Git 스냅샷](https://github.com/KIM-N-KANG/knk-harness/blob/56333a3/docs/design/4-deployment.md)에 있습니다.

## 목차

- [4-1. 목적과 범위](#4-1-목적과-범위)
- [4-2. 기준 레포지토리와 책임 경계](#4-2-기준-레포지토리와-책임-경계)
- [4-3. 환경 구분과 배포 단위](#4-3-환경-구분과-배포-단위)
- [4-4. 인프라 아키텍처](#4-4-인프라-아키텍처)
- [4-5. 이미지 빌드와 CI/CD](#4-5-이미지-빌드와-cicd)
- [4-6. 런타임 설정과 시크릿](#4-6-런타임-설정과-시크릿)
- [4-7. 배포 절차](#4-7-배포-절차)
- [4-8. 로컬·통합 실행](#4-8-로컬통합-실행)
- [4-9. 검수, 관측, 롤백](#4-9-검수-관측-롤백)

## 4-1. 목적과 범위

이 문서는 현재 배포 구조와 실행 방법을 설명합니다. 기준은 2026-09-12에 확인한 `manyak-terraform`의 로컬 dev 코드입니다. Terraform 선언, 실제 AWS 리소스, 실행 중인 이미지 다이제스트는 따로 확인합니다. 실제 활성값은 배포 기록을 따릅니다.

## 4-2. 기준 레포지토리와 책임 경계

| 레포지토리 | 책임 | 코드 위치 |
| --- | --- | --- |
| manyak-terraform | AWS 리소스·IAM·태스크 정의·설정 참조·Terraform 검증 | `terraform/envs/dev`, `terraform/envs/prod`, `terraform/modules`, `scripts/tf-apply.sh` |
| manyak-server·manyak-ai | 이미지 빌드·태그 승격·ECS 배포·서비스 검수 | 각 `.github/workflows/docker-image.yml` |
| manyak-infra | 로컬 통합 Docker Compose | `docker-compose.yml` |
| manyak-web·manyak-android | 플랫폼별 빌드·배포 | 각 플랫폼 레포 및 [웹 Spec](../spec/3-2-web-spec.md)·[Android Spec](../spec/3-3-android-spec.md) |
| knk-harness | 현재 구조·결정 이력 | 이 Design, 배포 ADR |

Terraform에서 관리하지 않는 웹 호스팅 설정이나 Play 배포 트랙을 AWS 코드에서 추정하지 않습니다. 애플리케이션 도메인 계약은 [백엔드 Spec](../spec/4-backend-server-spec.md)과 [AI Spec](../spec/5-ai-server-spec.md)이 소유합니다.

## 4-3. 환경 구분과 배포 단위

| 항목 | 개발 AWS | 운영 AWS | 로컬 통합 |
| --- | --- | --- | --- |
| 선언 위치 | `terraform/envs/dev` | `terraform/envs/prod` | manyak-infra Compose |
| 컴퓨트 | ECS Fargate Spot, 단일 태스크 | ECS Fargate, 단일 서비스·태스크 수 선언 1 | Docker Compose |
| 태스크 구성 | server·ai·postgres·redis·FireLens | server·ai·FireLens | 독립 Compose 서비스 |
| DB | PostgreSQL 컨테이너, EFS 영속 | RDS PostgreSQL | PostgreSQL 컨테이너 |
| Redis | 태스크 내 비영속 Redis | ElastiCache Redis | 비영속 Redis 컨테이너 |
| 서버 프로파일 | 독립 `dev` | `prod` | `local` |
| 외부 API | `https://dev-api.manyak.app` | `https://api.manyak.app` | Compose 포트 매핑 |
| 자산 | dev S3·`dev-cdn.manyak.app` | prod S3·`cdn.manyak.app` | 실행 설정에 따른 URL |
| 이미지 기본 좌표 | GHCR `dev` | ECR `latest` | Compose의 이미지·빌드 선언 |

서버와 AI는 같은 ECS 태스크의 네트워크를 공유합니다. AI 호출은 태스크 내부 주소를 사용하며 Compose 서비스명 DNS는 ECS에서 쓰지 않습니다. AI 컨테이너는 독립적으로 실패할 수 있으므로 서버 상태 검사만으로 AI 기능 성공을 판정하지 않습니다. 개발 태스크 교체는 PostgreSQL·Redis에도 영향을 주며 교체 중 중단을 허용합니다. 개발 검수는 운영 RDS·ElastiCache·NAT·롤링 배포를 검증하지 않습니다.

## 4-4. 인프라 아키텍처

### 네트워크와 트래픽

운영 VPC는 `10.0.0.0/16`, 개발은 `10.1.0.0/16`으로 분리합니다. 운영 태스크는 사설 app subnet에서 NAT를 통해 외부로 나가며 공인 IP를 받지 않습니다. 개발은 NAT 없이 공인 IP를 가진 태스크를 사용합니다. 운영의 다중 AZ subnet 구성은 애플리케이션 태스크 여러 개나 DB Multi-AZ를 뜻하지 않습니다.

HTTPS ALB는 IP target group의 서버 8080으로 전달합니다. 운영 상태 검사 경로는 `/actuator/health`, 성공 코드는 200입니다. ALB에서 태스크 보안 그룹으로 가는 8080 egress가 필요합니다. 태스크 보안 그룹의 DB·Redis egress는 대상 보안 그룹으로 제한합니다. 현재 Terraform에는 운영 EC2, 운영 Compose, EC2 `deploy.sh`·SSM 배포 경로가 없습니다.

### 배포와 데이터의 현재 선언값

아래 값은 기준 커밋의 Terraform 입력·리소스 선언이며 AWS 실측값이 아닙니다. 복구 판단 시 기본값만 읽지 않고 환경별 override도 함께 확인합니다.

| 항목 | 현재 선언 | 근거 |
| --- | --- | --- |
| ALB idle timeout | dev·prod 200초 | `modules/edge/variables.tf`의 `idle_timeout`, 환경 호출부에 override 없음 |
| ECS 배포 중 태스크 비율 | dev 최소 0%·최대 100%, prod 최소 100%·최대 200% | `modules/compute-ecs/main.tf`, `modules/compute-ecs-app/main.tf` |
| 개발 target draining | 30초 | `envs/dev/main.tf`의 `deregistration_delay` |
| 운영 RDS | PostgreSQL 16, db.t3.micro, 20GB, Single-AZ | `modules/data/variables.tf`·`main.tf`, `envs/prod/main.tf` |
| RDS 자동 백업 | 7일 | `db_backup_retention_days` |
| RDS 삭제 관련 설정 | `deletion_protection=false`, `skip_final_snapshot=true` | data 모듈 기본값, prod 호출부 override 없음. 삭제 시 자동으로 최종 스냅샷이 생긴다고 가정하지 않음 |

### 저장소와 자산

PostgreSQL이 업무 데이터 정본이며 OpenSearch 인덱스는 파생 데이터입니다. 운영 DB와 Redis는 태스크 수명과 분리됩니다. 개발 PostgreSQL의 EFS는 태스크 교체 후 데이터를 유지하지만 Redis는 교체 시 유실됩니다. 운영 Redis는 `volatile-ttl` 축출 정책으로 짧은 TTL 키부터 축출합니다. TTL 없는 카운터와 TTL 있는 세션·핸드오프의 수명은 백엔드 Spec을 따릅니다.

이미지는 비공개 S3에서 CloudFront OAC로 서빙합니다. 프리셋 키는 불변이며 변경은 새 키로 만듭니다. 썸네일 원본과 `_sm` 파생은 `scripts/upload-image-presets.sh`가 재현합니다. 생성 이미지와 사용자 업로드는 서버 태스크 역할에 허용된 prefix 안에서 저장합니다. `characters/generated/*`와 `thumbnails/generated/*` 권한을 구분하며 업로드 prefix도 별도로 제한합니다. S3 PUT·HEAD CORS는 브라우저 업로드용이며 CDN GET 서빙 정책과 별개입니다.

### 로그와 검색

공유 OpenSearch 도메인 `manyak-logs`는 dev state가 소유합니다. prod는 도메인 이름으로 조회하며 같은 리소스를 중복 소유하지 않습니다. FireLens 로그는 `manyak-logs-dev-*`·`manyak-logs-prod-*`, 검색은 `stories-dev`·`stories-prod`로 분리합니다. 한국어 분석용 `analysis-nori` 연결은 공유 도메인에서 한 번 관리하며 엔진 버전과 맞는 패키지를 사용합니다.

태스크 IAM의 `es:ESHttp*`만으로 검색 접근이 완성되지 않습니다. 서버의 `opensearch/setup-search.sh`가 관리하는 세분 접근 제어 역할과 backend role 매핑도 필요합니다. `MANYAK_OPENSEARCH_REINDEX_ON_STARTUP`은 초기 적재·복구 때 일시적으로 켠 뒤 되돌립니다. 서버의 재색인 대상과 검색 가시성은 백엔드 Spec을 따릅니다.

## 4-5. 이미지 빌드와 CI/CD

서비스 워크플로는 SHA 이미지를 빌드하고 환경 태그를 갱신한 뒤 ECS `force-new-deployment`를 실행합니다. ECS는 기존 태스크 정의로 새 태스크를 띄워 갱신된 환경 태그를 다시 받습니다. Terraform은 태스크 정의와 서비스 설정을 관리합니다. 개발 역할은 각 서비스 저장소의 dev 브랜치, 운영 역할은 운영 워크플로만 맡습니다. AWS 인증은 GitHub OIDC를 사용합니다.

배포 작업은 최신 브랜치 SHA를 확인하고 같은 저장소·환경의 배포를 직렬화합니다. GitHub concurrency는 저장소마다 동작하므로 server와 ai가 공유 태스크를 동시에 배포할 수 있습니다. 성공 여부는 deployment ID의 완료 상태, 실행 태스크의 이미지 digest, 각 컨테이너와 외부 API의 상태를 함께 확인합니다. 가변 태그 이름만 같다고 같은 이미지로 판단하지 않습니다.

Terraform PR 검증과 drift 검사는 자격증명과 권한을 분리합니다. 비밀이 아닌 운영값은 `dev.auto.tfvars`와 `prod.auto.tfvars`에 보관합니다. `desired_count`의 기본값 0만 보고 현재 서비스의 목표 수를 판단하지 않습니다. 커밋된 값은 환경별 1이며 일시 변경은 실행 기록에 남깁니다.

## 4-6. 런타임 설정과 시크릿

Terraform은 Secrets Manager 리소스와 태스크의 참조를 관리합니다. 실제 앱 시크릿 값은 Terraform state에 저장하지 않습니다. `ignore_changes`만으로 secret_version refresh를 차단할 수 없으므로 해당 리소스를 다시 도입하지 않습니다. 태스크 실행 역할의 비밀 읽기와 애플리케이션 태스크 역할의 AWS 접근을 구분합니다. 시크릿 값 등록, 태스크 참조, 재배포의 세 단계가 모두 있어야 실행 중 컨테이너에 반영됩니다.

| 설정 묶음 | 주입 대상·경계 |
| --- | --- |
| JWT·Google·Kakao | server 인증 설정. 허용 client ID와 서명 설정은 백엔드 계약에 맞춰 공급 |
| RDS 비밀번호 | 운영 server에 시작 시 주입. 회전 후 새 태스크로 갱신 |
| LLM 공급자 키·Langfuse | AI 컨테이너. AI가 선택 모델의 공급자와 관측 설정을 검사 |
| 이미지 bucket·region·base URL | server 생성 이미지 저장. 필요한 값과 IAM을 함께 공급 |
| OpenSearch endpoint·index·재색인 | server 검색·색인. IAM과 검색 역할 매핑을 별도로 확인 |
| OTLP | server에 endpoint·인증 참조와 활성 토글을 함께 공급. prod 선언은 `enable_otlp_metrics=true` |
| 신고·피드백 webhook | server에 목적별 참조. 값이 없을 때 저장과 알림의 실패 경계는 백엔드 계약을 따름 |
| FCM | dev·prod server에 `MANYAK_FCM_SERVICE_ACCOUNT_JSON` 참조 |
| Groble·Google Play | dev·prod server에 HMAC, 서비스 계정 JSON, 패키지명 참조. 비어 있으면 구매는 503, 대사는 실행하지 않음 |

운영 AI 모델은 SSM Parameter Store의 컴파일·스토리라인·채팅 값 세 개로 관리합니다. 이미 존재하는 Parameter의 값은 `ignore_changes`이므로 Terraform 기본값 수정만으로 바뀌지 않습니다. Parameter 변경 후 새 태스크가 읽게 해야 합니다. 개발은 태스크 정의 환경변수이므로 apply가 필요합니다. 확인한 개발 선언은 컴파일 `gemini-3.7-flash`, 스토리라인·채팅 `deepseek-flash`입니다. 운영 Parameter 실값은 이번 문서 작업에서 조회하지 않았습니다. 옛 모델 이름과 새 AI 등록부가 호환되지 않는 전환은 모델 설정과 이미지를 같은 배포 단위로 맞춥니다.

## 4-7. 배포 절차

1. 작업 코드·현재 Design·ADR과 대상 환경을 확인합니다. 새 설정은 시크릿 키 존재, IAM, 태스크 참조, 공급자 모델 호환성을 먼저 점검합니다.
2. Terraform 변경은 저장소의 `scripts/tf-apply.sh`가 요구하는 최신 dev·작업트리·plan 검사를 통과한 뒤 적용합니다. 오래된 브랜치의 plan을 현재 운영 변경으로 사용하지 않습니다. plan의 replace·destroy 범위를 개별 리소스로 검토합니다.
3. 설정이 준비된 환경에 호환되는 서비스 이미지를 배포합니다. 태스크 정의 변경과 서비스 이미지 배포가 서로 다른 SHA·설정을 덮지 않는지 확인합니다.
4. 새 deployment ID, 태스크 정의 revision, 이미지 digest, 컨테이너·ALB target·API 상태를 확인합니다. AI 변경은 실제 생성·채팅 검수 결과를 따로 남깁니다.
5. 실행 시각(KST), 코드 SHA, 이미지 digest, 설정 변경 범위, 검수·복구 결과를 배포 기록에 남깁니다. 합의된 현재 구성은 이 Design에 반영합니다.

DB 변경은 expand/contract로 진행합니다. 신규 컬럼·테이블을 먼저 추가하고 구버전 태스크가 더 이상 해당 컬럼을 읽지 않는 릴리스 이후에 제거합니다. 새 태스크의 Flyway 실행 중에도 이전 태스크가 요청을 받을 수 있습니다. 이미지 롤백은 파괴적 DB 변경을 자동 복구하지 않습니다.

## 4-8. 로컬·통합 실행

`manyak-infra`의 Compose가 로컬 실행 정본입니다. 서버·AI·웹·PostgreSQL·Redis와 Prometheus 설정을 함께 확인합니다. 서비스명 DNS는 Compose 네트워크 안에서 사용합니다. AI stub과 실제 AI 호출 여부는 명시적인 실행 설정으로 확인합니다.

현재 Compose의 모델 기본값과 AWS 태스크 선언은 같다고 가정하지 않습니다. 통합 레포의 모델 기본값에는 과거 이름이 남아 있으므로 선택한 AI 이미지의 등록부와 맞는 값을 공급해야 합니다. 로컬 통합 성공은 AWS IAM·Secrets Manager 주입·CloudFront 업로드 CORS·ECS 롤링 성공의 증거가 아닙니다.

## 4-9. 검수, 관측, 롤백

- 서버와 AI 컨테이너의 상태, 실제 AI 기능을 각각 확인합니다.
- FireLens 로그의 환경 인덱스와 OTLP 수집을 각각 확인합니다. 로그 수집 성공으로 메트릭 export를 판정하지 않습니다.
- DB 회전은 EventBridge 5분 주기 Lambda가 시크릿 `LastChangedDate`와 태스크 `createdAt`을 비교합니다. 필요할 때만 운영 서비스를 재배포하며 시크릿 원문 읽기 권한은 갖지 않습니다. 이 감지 간격은 무중단 보장이 아니므로 실제 재배포와 DB 연결 결과를 확인합니다.
- 이미지 장애는 이전 정상 digest로 환경 태그를 복원한 뒤 새 ECS 배포를 실행하고 같은 검수를 반복합니다. 같은 태스크 정의·가변 태그를 쓰므로 circuit breaker만으로 이전 이미지 복귀가 보장되지 않습니다.
- 모델 설정 장애는 이전 모델 설정과 호환 이미지의 조합으로 복원합니다. Terraform 기본값을 되돌리는 것만으로 기존 운영 Parameter가 바뀌지 않습니다.
- EC2는 현재 복구 대상이 아닙니다. 과거 EC2 가중치 전환·SSM 재실행은 [배포 ADR DEP-023·030](../adr/4-deployment-adr.md#전환-단계-기록)의 역사 기록입니다.

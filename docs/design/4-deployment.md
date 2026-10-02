# 4-deployment

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | v1.1 |
| 작성일 | 2026-07-03 |
| 수정일 | 2026-09-30 |
| 대상 | 마냑 운영·개발·통합 배포 |
| 작성 목적 | 현재 배포 구성·설정·실행·검수·복구 구조를 설명합니다. 코드와 함께 갱신합니다. |
| 알림 구성 기준 | 2026-09-30 확인한 Terraform `ae315c3`과 알림 서비스 `ac51603`. prod 알림 구성은 BE-051의 미적용 목표로 구분합니다. |
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
| manyak-notification | 알림 이미지 빌드와 dev ECS 배포. prod ECR 및 별도 ECS 서비스 배포는 목표 구성 | `.github/workflows/docker-image.yml` |
| manyak-infra | 로컬 통합 Docker Compose | `docker-compose.yml` |
| manyak-web·manyak-android | 플랫폼별 빌드·배포 | 각 플랫폼 레포 및 [웹 Spec](../spec/3-2-web-spec.md)·[Android Spec](../spec/3-3-android-spec.md) |
| knk-harness | 현재 구조·결정 이력 | 이 Design, 배포 ADR |

Terraform에서 관리하지 않는 웹 호스팅 설정이나 Play 배포 트랙을 AWS 코드에서 추정하지 않습니다. 애플리케이션 도메인 계약은 [백엔드 Spec](../spec/4-backend-server-spec.md)과 [AI Spec](../spec/5-ai-server-spec.md)이 소유합니다.

## 4-3. 환경 구분과 배포 단위

| 항목 | 개발 AWS | 운영 AWS | 로컬 통합 |
| --- | --- | --- | --- |
| 선언 위치 | `terraform/envs/dev` | `terraform/envs/prod` | manyak-infra Compose |
| 컴퓨트 | ECS Fargate Spot, 단일 태스크 | ECS Fargate, 단일 서비스·태스크 수 선언 1 | Docker Compose |
| 태스크 구성 | server, ai, notification, postgres, redis, FireLens | server·ai·FireLens | 독립 Compose 서비스 |
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

dev 알림은 서버와 같은 태스크에서 `http://localhost:8080`으로 내부 API를 호출합니다. 아래 prod 알림 구성은 결정된 목표이며 현재 Terraform에 적용되지 않았습니다. ([BE-051](../adr/2-backend-server-adr.md#be-051))

| 항목 | prod 목표 구성 |
| --- | --- |
| 배포 단위 | prod ECS 클러스터의 별도 알림 서비스. FireLens 사이드카를 포함해 0.25 vCPU, 1GB |
| 내부 호출 | 서버 ECS 서비스를 AWS Cloud Map private DNS에 등록하고 `http://server.manyak-prod.local:8080`으로 호출. 레코드 TTL 10초 |
| 공개 경로 차단 | 공개 ALB의 `/internal/*`는 404 고정 응답. 서버 공유 시크릿 주입 전이나 같은 적용에서 차단 |
| 큐와 역할 | SQS 표준 본 큐와 DLQ. 서버 태스크 역할은 `SendMessage`, 알림 태스크 역할은 `ReceiveMessage`와 `DeleteMessage`로 메시지 권한 분리 |

오래된 DNS 레코드로 자격 조회가 실패하면 소비자는 `ELIGIBILITY_UNAVAILABLE`을 `RETRY`로 처리합니다. SQS는 메시지를 삭제하지 않고 가시성 60초 뒤 재전달하며 재시도 한도 이후에는 DLQ에 보존합니다. dev의 큐와 DLQ는 `envs/dev/sqs.tf`, 알림 컨테이너는 `modules/compute-ecs/main.tf`에 구현되어 있습니다. dev DLQ 경보는 가시 메시지 수가 0보다 크면 SNS 이메일로 알리며 구독 확인이 필요합니다. prod에도 같은 경보를 두는 것이 목표입니다. 본 큐 적체 경보는 임계값 근거가 부족해 보류한 결정을 유지합니다. ([KNK-1381](https://kimandkang.atlassian.net/browse/KNK-1381))

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

### 이중화 계획

[DEP-047](../adr/4-deployment-adr.md#dep-047-운영-가용성-이중화)에 따른 운영 전용 계획입니다. 아래 현재 선언은 `manyak-terraform`의 `origin/dev`를 읽어 확인한 값이며 AWS 실측이나 적용 완료 기록이 아닙니다. 앞 절의 기존 배포 기준과 구분하며, HA 적용 전에는 서비스 분리와 실제 실행 상태부터 대조합니다. 기존 RDS 선언값 표를 목표값으로 바꾸지 않습니다.

| 대상 | 확인한 현재 Terraform 선언 | 이중화 목표 | 근거 경로 (`terraform/` 아래) |
| --- | --- | --- | --- |
| NAT와 app 라우팅 | `single_nat_gateway=true` 기본값, 첫 AZ인 2a NAT 한 개를 두 app subnet이 공유합니다. | 2a와 2c에 각각 NAT를 두고 같은 AZ로 라우팅합니다. | `modules/network/main.tf`, `variables.tf`, `envs/prod/main.tf` |
| RDS | `multi_az=false`, 2a 고정, `apply_immediately=false`입니다. | 기존 DB 인스턴스를 Multi-AZ로 전환하고 다른 AZ에 대기본을 둡니다. | `modules/data/main.tf`, `envs/prod/main.tf` |
| server와 notification | `ecs_desired_count=1`, `notification_desired_count=1`이며 두 app subnet을 사용합니다. `push_mode=local` 선언입니다. | 각각 2개로 시작하고 자동 확장 범위를 2~4개로 둡니다. 알림 remote 전환은 별도 릴리스 조건을 따릅니다. | `envs/prod/prod.auto.tfvars`, `ecs.tf`, `notification.tf`, `modules/compute-ecs-app/main.tf` |
| ai와 PDC | AI의 `desired_count=1`, PDC는 `pdc_enabled=true`로 1개이며 두 app subnet을 사용합니다. | AI는 2개로 시작해 2~4개로 자동 확장하고 PDC는 2개로 고정합니다. | `envs/prod/ai.tf`, `pdc-agent.tf`, `prod.auto.tfvars` |
| Redis | `aws_elasticache_cluster.redis`의 노드 1개이며 AZ를 명시하지 않습니다. 앱은 단일 노드 주소를 참조합니다. | 클러스터 모드 비활성 복제 그룹에 초기 Primary 2a와 Replica 2c를 두고 Multi-AZ 및 자동 장애 조치를 켭니다. 앱은 Primary endpoint를 사용합니다. | `modules/data/main.tf`, `outputs.tf`, `envs/prod/ecs.tf`, `notification.tf` |

두 서브넷을 지정하거나 desired count를 2로 올리는 것만으로 완료로 판정하지 않습니다. ECS의 AZ 분산과 재균형 설정을 확인하고 정상 상태에서 서비스마다 두 AZ에 실행 태스크가 있는지 검증합니다. ALB는 server만 공개하며 AI와 알림의 내부 호출은 기존 Cloud Map 및 보안 그룹 경계를 유지합니다. PDC 두 태스크의 터널과 데이터 소스 조회도 각각 검증합니다.

#### 단계별 변경과 적용 시점

각 단계는 별도 plan으로 변경 범위를 확인하고 이전 단계의 검증 후 진행합니다. 공유 환경 변경은 PR 병합 후 최신 `origin/dev`에서 `scripts/tf-apply.sh prod`로 적용합니다. 설명되지 않는 교체나 삭제가 있으면 진행하지 않습니다. 아래는 실행 계획이며 이 문서 작성으로 apply를 수행하지 않습니다.

| 순서와 작업 | Terraform 변경 범위 | 위험과 확인 사항 | apply 시점 |
| --- | --- | --- | --- |
| 1. 2c NAT, [KNK-1494](https://kimandkang.atlassian.net/browse/KNK-1494) 일부 | prod network 호출의 `single_nat_gateway=false`, 2c EIP와 NAT 생성, app route table의 AZ별 NAT 연결을 사용합니다. | 서비스 중단 없이 전환하는 목표입니다. 2a NAT를 유지하고 새 NAT가 준비된 뒤 2c 라우트를 전환합니다. 기존 외부 연결은 경로 변경으로 끊길 수 있어 재시도를 검증합니다. | 2c 태스크의 외부 통신을 의존시키기 전에 적용합니다. 두 AZ에서 이미지 pull과 외부 API 연결을 확인합니다. |
| 2. RDS Multi-AZ, [KNK-1492](https://kimandkang.atlassian.net/browse/KNK-1492) | data 모듈의 `multi_az` 하드코딩을 환경 입력으로 바꾸고 prod에서 활성화합니다. Multi-AZ에서 고정 `availability_zone`을 제거하며 DB와 엔드포인트를 유지하는 변경인지 plan으로 확인합니다. | 무중단 전환을 목표로 하지만 대기본 생성 중 스냅샷과 복제로 I/O 지연이 생길 수 있습니다. DB 교체는 허용하지 않습니다. | 한산한 시간에 진행합니다. `apply_immediately=false`와 pending modification을 확인해 실제 반영 창을 정하고 대기본 준비 완료까지 기다립니다. |
| 3. 서비스별 desired 2, [KNK-1491](https://kimandkang.atlassian.net/browse/KNK-1491) | prod server와 notification 운영값, AI 서비스의 고정값, PDC 활성 시 개수를 각각 2로 변경합니다. 각 서비스의 두 subnet 지정과 배포 설정을 검증합니다. | DB 연결 수와 외부 API 동시 요청이 증가합니다. 아래 다중 인스턴스 전제 및 실제 AZ 분산을 확인합니다. | NAT와 RDS 검증 후 서비스별로 순차 적용합니다. 앞 서비스가 안정화된 뒤 다음 서비스로 진행합니다. |
| 4. Redis 복제 그룹, [KNK-1493](https://kimandkang.atlassian.net/browse/KNK-1493) | 기존 cluster를 보존하며 새 replication group, AZ 배치, 자동 장애 조치, snapshot 복원 입력을 추가합니다. `redis_endpoint` 출력과 소비 태스크 정의를 전환하고 노드별 경보 dimension을 갱신합니다. | 토큰과 멱등 상태의 유실, 신구 저장소 동시 쓰기 위험이 있습니다. 기존 TTL과 `volatile-ttl`을 보존하며 아래 이전 절차를 따릅니다. | 복원 리허설로 전환 창을 정한 뒤 저부하 시간에 생성, 앱 전환, 구 클러스터 삭제를 분리 적용합니다. |
| 5. 자동 확장, [KNK-1494](https://kimandkang.atlassian.net/browse/KNK-1494) | server, ai, notification별 `aws_appautoscaling_target`과 목표 추적 policy를 추가하고 최소 2, 최대 4로 둡니다. Terraform과 CD가 자동 조절된 `desired_count`를 덮어쓰지 않게 소유권을 분리합니다. PDC는 제외합니다. | CPU만으로 외부 API 대기나 큐 적체를 설명하지 못합니다. 세 서비스 모두 ALB 요청 지표를 쓰는 구성은 피합니다. 축소 때 처리 중 요청과 메시지 재전달을 검증합니다. | 데이터 계층 전환과 고정 2개 검증 후 적용합니다. 잠정값을 명시한 PR로 시작하고 [KNK-1498](https://kimandkang.atlassian.net/browse/KNK-1498)의 결과로 지표, 임계값과 cooldown을 확정합니다. |

server의 `@Scheduled` 다중 인스턴스 안전성은 출석의 `SET NX`, 프로모션의 조건부 `UPDATE`, 대사와 회수의 행 락, 아웃박스와 검수 폴러의 임대 및 `SKIP LOCKED`를 전제로 확인한 결정입니다. 증설 검수에서는 같은 작업을 두 태스크가 수행해도 보상, 회수, 발송이 중복되지 않는지 재확인합니다. 정책과 템플릿 캐시는 태스크별이므로 갱신 직후 잠시 불일치할 수 있습니다. 전역 캐시 일관성을 증설이 해결한다고 보지 않습니다.

자동 확장의 잠정 기본값은 최소 2개를 유지하고 빠른 확장과 신중한 축소를 우선합니다. 지표, 목표값, 확장 및 축소 cooldown의 수치는 아직 확정하지 않습니다. 활성화 PR에는 서비스별 잠정 수치와 선정 근거를 반드시 기록하며 값이 비어 있는 상태로 적용하지 않습니다. 부하 테스트에서는 server의 요청 지연, AI 동시 처리와 공급자 제한, notification의 태스크당 큐 적체 및 처리 시간을 함께 측정합니다. 목표 추적의 동작과 배포 중 축소 제한은 [ECS 공식 문서](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-autoscaling-targettracking.html)를 따릅니다.

#### Redis 데이터 이전

1. 구 클러스터의 스냅샷 복원 가능 여부, 엔진과 파라미터 호환성, TTL 및 핵심 키의 검증 방법을 리허설합니다. 토큰 원문은 출력하지 않습니다. 복원과 재배포에 필요한 시간으로 쓰기 중지 창을 산정합니다.
2. 최종 스냅샷 전에 Redis를 쓰는 요청과 백그라운드 작업, 알림 소비를 멈추고 진행 중 쓰기를 소진합니다. 로그인과 토큰 갱신도 쓰기에 포함합니다. 스냅샷 이후 쓰기를 계속하면 그 변경은 복원본에 없으므로 무중단 이전이라고 설명하지 않습니다.
3. 최종 스냅샷을 생성해 새 복제 그룹으로 복원합니다. 두 노드의 AZ와 상태, Primary endpoint, TTL과 토큰 갱신 및 멱등 기록의 보존을 확인합니다. [ElastiCache 복원 절차](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/backups-restoring.html)를 사용합니다.
4. 쓰기를 중지한 상태에서 server와 notification의 endpoint 참조를 바꾸고 소비 태스크를 모두 재배포합니다. 구 주소를 쓰는 태스크가 남지 않은 것을 확인한 뒤 쓰기와 소비를 재개합니다. 새 그룹과 구 클러스터에 쓰기가 나뉘는 롤링 전환은 허용하지 않습니다.
5. 검증과 복구 창이 끝난 뒤 구 클러스터를 별도 plan으로 삭제합니다. 새 그룹 쓰기 재개 전에는 구 주소로 복귀할 수 있지만, 재개 후에는 구 클러스터가 오래된 상태이므로 단순 주소 롤백을 하지 않습니다. 다시 쓰기를 멈추고 최신 데이터의 복원 또는 재이전 절차를 결정합니다.

리프레시 토큰은 Redis에만 있으므로 전체 유실 시 토큰 갱신이 실패하고 전 사용자 재로그인이 필요합니다. 복제 그룹도 비동기 복제를 사용하므로 장애 조치 때 최근 쓰기가 유실될 가능성은 남습니다. HA와 백업은 서로 대체하지 않습니다. [ElastiCache 자동 장애 조치](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/AutoFailover.html)와 [RDS 전환 시 I/O 영향](https://aws.amazon.com/blogs/database/best-practices-for-converting-a-single-az-amazon-rds-instance-to-a-multi-az-instance/)을 전환 리허설에 반영합니다.

### 저장소와 자산

PostgreSQL이 업무 데이터 정본이며 OpenSearch 인덱스는 파생 데이터입니다. 운영 DB와 Redis는 태스크 수명과 분리됩니다. 개발 PostgreSQL의 EFS는 태스크 교체 후 데이터를 유지하지만 Redis는 교체 시 유실됩니다. 운영 Redis는 `volatile-ttl` 축출 정책으로 짧은 TTL 키부터 축출합니다. TTL 없는 카운터와 TTL 있는 세션·핸드오프의 수명은 백엔드 Spec을 따릅니다.

알림의 멱등 기록은 dev 태스크 안 Redis의 `notification:` 접두어 키에 저장합니다. prod 목표는 서버와 같은 ElastiCache를 사용하는 것이며 Redis 보안 그룹에 알림 태스크에서 오는 ingress를 추가합니다. ([BE-051](../adr/2-backend-server-adr.md#be-051))

이미지는 비공개 S3에서 CloudFront OAC로 서빙합니다. 프리셋 키는 불변이며 변경은 새 키로 만듭니다. 썸네일 원본과 `_sm` 파생은 `scripts/upload-image-presets.sh`가 재현합니다. 생성 이미지와 사용자 업로드는 서버 태스크 역할에 허용된 prefix 안에서 저장합니다. `characters/generated/*`와 `thumbnails/generated/*` 권한을 구분하며 업로드 prefix도 별도로 제한합니다. S3 PUT·HEAD CORS는 브라우저 업로드용이며 CDN GET 서빙 정책과 별개입니다.

### 로그와 검색

공유 OpenSearch 도메인 `manyak-logs`는 dev state가 소유합니다. prod는 도메인 이름으로 조회하며 같은 리소스를 중복 소유하지 않습니다. FireLens 로그는 `manyak-logs-dev-*`·`manyak-logs-prod-*`, 검색은 `stories-dev`·`stories-prod`로 분리합니다. 한국어 분석용 `analysis-nori` 연결은 공유 도메인에서 한 번 관리하며 엔진 버전과 맞는 패키지를 사용합니다.

태스크 IAM의 `es:ESHttp*`만으로 검색 접근이 완성되지 않습니다. 서버의 `opensearch/setup-search.sh`가 관리하는 세분 접근 제어 역할과 backend role 매핑도 필요합니다. `MANYAK_OPENSEARCH_REINDEX_ON_STARTUP`은 초기 적재·복구 때 일시적으로 켠 뒤 되돌립니다. 서버의 재색인 대상과 검색 가시성은 백엔드 Spec을 따릅니다.

prod 알림도 서버와 같은 FireLens 구성으로 `manyak-logs-prod-*`에 로그를 보내고 CloudWatch 안전망을 유지하는 것이 목표입니다. Fargate FireLens에는 영속 디스크 버퍼가 없으므로 OpenSearch 장애 때 로그 유실을 막는 별도 저장 경로가 필요합니다. CloudWatch는 OpenSearch 403 진단에 필요한 로그 라우터 자체 로그도 저장합니다. 알림 CloudWatch 보존 기간은 7일로 정합니다. ([BE-051](../adr/2-backend-server-adr.md#be-051))

## 4-5. 이미지 빌드와 CI/CD

### server·ai 이미지

서비스 워크플로는 SHA 이미지를 빌드하고 환경 태그를 갱신한 뒤 ECS `force-new-deployment`를 실행합니다. ECS는 기존 태스크 정의로 새 태스크를 띄워 갱신된 환경 태그를 다시 받습니다. Terraform은 태스크 정의와 서비스 설정을 관리합니다. 개발 역할은 각 서비스 저장소의 dev 브랜치, 운영 역할은 운영 워크플로만 맡습니다. AWS 인증은 GitHub OIDC를 사용합니다.

배포 작업은 최신 브랜치 SHA를 확인하고 같은 저장소·환경의 배포를 직렬화합니다. GitHub concurrency는 저장소마다 동작하므로 server와 ai가 공유 태스크를 동시에 배포할 수 있습니다. 성공 여부는 deployment ID의 완료 상태, 실행 태스크의 이미지 digest, 각 컨테이너와 외부 API의 상태를 함께 확인합니다. 가변 태그 이름만 같다고 같은 이미지로 판단하지 않습니다.

Terraform PR 검증과 drift 검사는 자격증명과 권한을 분리합니다. 비밀이 아닌 운영값은 `dev.auto.tfvars`와 `prod.auto.tfvars`에 보관합니다. `desired_count`의 기본값 0만 보고 현재 서비스의 목표 수를 판단하지 않습니다. 커밋된 값은 환경별 1이며 일시 변경은 실행 기록에 남깁니다.

알림 서비스의 현재 `.github/workflows/docker-image.yml`은 dev push에서 GHCR SHA 이미지를 빌드하고 최신 SHA 확인 후 `ghcr.io/kim-n-kang/manyak-notification:dev`로 승격해 dev ECS를 자동 배포합니다. 같은 태스크의 server, ai, notification이 함께 갱신되며 각 컨테이너의 실행 상태와 헬스를 검증합니다.

prod는 알림 저장소 main push에서 prod ECR `manyak-notification` 이미지를 빌드하고 별도 알림 ECS 서비스를 배포하는 목표 구성입니다. 배포 실패 시 이전 이미지 digest를 복원합니다. 현재 알림 워크플로에는 prod CD가 없으며 적용 순서는 BE-051을 따릅니다. ([BE-051](../adr/2-backend-server-adr.md#be-051))

### manyak-web CI/CD

| 트리거 | 동작 |
| --- | --- |
| PR → `dev` | pnpm install, lint, typecheck, Docker build 검증 |
| PR·push → `dev`·`main` | Playwright(4 워커 병렬): Pixel 5 전체 E2E·비주얼 회귀, iPhone 13 스모크. CI가 Chromium·WebKit을 설치하고 Linux 기준 이미지와 비교 |
| push → `dev` | GHCR `dev`·`<short-sha>` push |
| push tag `v*` | GHCR release 이미지 push. build arg는 `NEXT_PUBLIC_AMPLITUDE_API_KEY`·`NEXT_PUBLIC_META_PIXEL_ID` |

비주얼 기준 이미지는 Linux 렌더링만 정본입니다. UI를 의도적으로 바꾸면 `manyak-web`에서 `pnpm test:e2e:visual:update`로 Playwright Docker 이미지 기준을 갱신하고 diff를 검토합니다. macOS 로컬 실행은 폰트·안티앨리어싱 차이 때문에 스냅샷 비교를 건너뜁니다.

운영 Terraform에는 `manyak-web` 컨테이너를 호스팅에 배포하는 리소스가 없습니다. 웹은 Vercel에서 서빙하며 release PR은 GHCR release 이미지 발행과 외부 호스팅 반영을 전제로 합니다. Web Sentry는 Vercel 환경 변수 `NEXT_PUBLIC_SENTRY_DSN`으로 활성이고, SDK는 `NODE_ENV=production`이면서 Vercel 배포일 때만 전송합니다. 배포 판별에 쓰는 `VERCEL_ENV`는 `next.config.ts`가 빌드 시점에 인라인합니다. Sentry release와 Amplitude `app_version`이 읽는 앱 버전 `NEXT_PUBLIC_APP_VERSION`도 `next.config.ts`가 `package.json`의 `version`으로 인라인하며, 같은 이름의 배포 환경 변수보다 우선합니다. GHCR release workflow와 Dockerfile에는 이 build arg가 없어 컨테이너 경로는 비활성입니다. 웹 푸시는 Vercel 환경 변수 `NEXT_PUBLIC_FIREBASE_API_KEY`·`NEXT_PUBLIC_FIREBASE_PROJECT_ID`·`NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`·`NEXT_PUBLIC_FIREBASE_APP_ID`·`NEXT_PUBLIC_FIREBASE_VAPID_KEY`(Production·Preview, 공개값)로 활성이며 하나라도 비면 전체가 꺼집니다. 값은 서버·Android와 같은 Firebase 프로젝트의 웹 앱 `manyak-web`과 클라우드 메시징의 웹 푸시 인증서에서 발급하고, GHCR 컨테이너 경로에는 이 build arg가 없어 비활성입니다.

### manyak-android CI

컨테이너 이미지가 없는 앱 저장소입니다. `.github/workflows/android-ci.yml`이 `dev`·`main` 대상 PR·push와 수동 실행에서 Temurin Java 25를 설정하고(`gradle-daemon-jvm.properties`와 일치) `./gradlew check`(ktlint·detekt·Android lint·단위 테스트)와 `./gradlew assembleDebug`를 실행한 뒤 리포트를 아티팩트로 올립니다.

release 번들(AAB)은 CI가 만들지 않습니다. 릴리스 담당자가 로컬에서 `./gradlew bundleRelease`로 만들어 Play Console에 직접 올립니다.

- **CI에 서명키를 두지 않습니다.** 릴리스가 2주에 한 번이고 올리는 사람이 한 명인 동안에는 Play Publisher API 서비스 계정과 GitHub Secrets 키스토어를 유지하는 비용이 수동 업로드보다 큽니다. 키를 CI에 올리면 유출면도 넓어집니다. 자동화는 릴리스가 주 1회를 넘거나 담당이 둘 이상이 될 때 다시 판단합니다.
- **서명키 보관.** Play 앱 서명을 쓰므로 배포 인증서는 Google이 보관하고 팀은 업로드 키만 가집니다. 업로드 키스토어는 저장소 밖에 두고 `local.properties`의 `RELEASE_STORE_FILE`·`RELEASE_STORE_PASSWORD`·`RELEASE_KEY_ALIAS`·`RELEASE_KEY_PASSWORD`로 주입합니다. 키 파일과 비밀번호는 암호화 백업 두 곳에 둡니다. 잃으면 Google 지원으로 업로드 키를 재설정할 때까지 업데이트를 올릴 수 없습니다. 키 값과 실제 경로는 문서에도 저장소에도 적지 않습니다.
- **release BuildConfig 주입값**도 `local.properties`에서 읽습니다(`GOOGLE_SERVER_CLIENT_ID_RELEASE`·`KAKAO_NATIVE_APP_KEY_RELEASE`·`AMPLITUDE_API_KEY_RELEASE`). 비어 있어도 빌드는 성공하고 해당 공급자만 런타임에 실패하므로 번들을 만들기 전에 세 값을 확인합니다. 운영 `BASE_URL`은 `app/build.gradle.kts`에 고정돼 있습니다.
- **`google-services.json`은 저장소에 커밋합니다.** CI에 주입할 시크릿이 없는데 PR마다 `assembleDebug`를 돌리므로 파일이 없으면 모든 PR이 실패합니다. 값은 APK에 실려 나가고 보호는 Firebase 보안 규칙과 API 키 제한이 맡습니다. Firebase 프로젝트는 서버 FCM과 같은 하나를 쓰며 환경별로 나누지 않습니다. `applicationId`가 빌드 타입 간 같고 debug는 `firebase_crashlytics_collection_enabled=false`로 수집하지 않습니다.
- release는 R8 축소·난독화를 적용합니다(`optimization.enable = true`, keep 규칙은 `app/proguard-rules.pro`). `bundleRelease`가 Crashlytics로 매핑 파일을 올리고 AAB의 `BUNDLE-METADATA`에도 매핑이 실립니다. 결정 이유는 [Android ADR A-047](../adr/1-3-android-adr.md#a-047)에 있습니다.

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
| FCM | 현재 dev는 server와 notification, prod는 server에 `MANYAK_FCM_SERVICE_ACCOUNT_JSON` 참조. prod 목표에서는 알림에도 주입하며 서버 값은 `local` 롤백 창 동안 유지 |
| 내부 API 인증 | dev server와 notification에 `MANYAK_INTERNAL_SHARED_SECRET`을 같은 값으로 주입. prod는 공개 ALB 차단 후 양쪽 주입이 목표 |
| 알림의 서버 주소 | `MANYAK_SERVER_INTERNAL_BASE_URL`: dev는 `http://localhost:8080`, prod 목표는 `http://server.manyak-prod.local:8080` |
| Groble·Google Play | dev·prod server에 HMAC, 서비스 계정 JSON, 패키지명 참조. 비어 있으면 구매는 503, 대사는 실행하지 않음 |

알림 시크릿은 저장 전에 값의 길이를 검사해 빈 값을 거부합니다. dev 빈 값 저장 사고를 반복하지 않도록 저장 결과의 길이도 확인하며 값 자체는 로그나 문서에 출력하지 않습니다. 빈 값 거부 외에 최소 길이 수치는 미정입니다. prod 서버의 FCM 값 제거는 롤백 창이 끝난 뒤 KNK-1367에서 처리합니다. 시크릿 등록부터 `remote` 전환까지의 순서는 BE-051을 따릅니다. ([BE-051](../adr/2-backend-server-adr.md#be-051), [KNK-1367](https://kimandkang.atlassian.net/browse/KNK-1367))

운영 AI 모델은 SSM Parameter Store의 컴파일·스토리라인·채팅 값 세 개로 관리합니다. 이미 존재하는 Parameter의 값은 `ignore_changes`이므로 Terraform 기본값 수정만으로 바뀌지 않습니다. Parameter 변경 후 새 태스크가 읽게 해야 합니다. 개발은 태스크 정의 환경변수이므로 apply가 필요합니다. 확인한 개발 선언은 컴파일 `gemini-3.7-flash`, 스토리라인·채팅 `deepseek-flash`입니다. 운영 Parameter 실값은 이번 문서 작업에서 조회하지 않았습니다. 옛 모델 이름과 새 AI 등록부가 호환되지 않는 전환은 모델 설정과 이미지를 같은 배포 단위로 맞춥니다.

## 4-7. 배포 절차

1. 작업 코드·현재 Design·ADR과 대상 환경을 확인합니다. 새 설정은 시크릿 키 존재, IAM, 태스크 참조, 공급자 모델 호환성을 먼저 점검합니다.
2. Terraform 변경은 저장소의 `scripts/tf-apply.sh`가 요구하는 최신 dev·작업트리·plan 검사를 통과한 뒤 적용합니다. 오래된 브랜치의 plan을 현재 운영 변경으로 사용하지 않습니다. plan의 replace·destroy 범위를 개별 리소스로 검토합니다.
3. 설정이 준비된 환경에 호환되는 서비스 이미지를 배포합니다. 태스크 정의 변경과 서비스 이미지 배포가 서로 다른 SHA·설정을 덮지 않는지 확인합니다.
4. 새 deployment ID, 태스크 정의 revision, 이미지 digest, 컨테이너·ALB target·API 상태를 확인합니다. AI 변경은 실제 생성·채팅 검수 결과를 따로 남깁니다.
5. 실행 시각(KST), 코드 SHA, 이미지 digest, 설정 변경 범위, 검수·복구 결과를 배포 기록에 남깁니다. 합의된 현재 구성은 이 Design에 반영합니다.

DB 변경은 expand/contract로 진행합니다. 신규 컬럼·테이블을 먼저 추가하고 구버전 태스크가 더 이상 해당 컬럼을 읽지 않는 릴리스 이후에 제거합니다. 새 태스크의 Flyway 실행 중에도 이전 태스크가 요청을 받을 수 있습니다. 이미지 롤백은 파괴적 DB 변경을 자동 복구하지 않습니다.

### Web release 이미지 배포

1. `manyak-web` 변경을 `dev`에 병합해 GHCR `dev` 이미지를 검증합니다.
2. release tag `v*`를 push하면 `release.yml`이 GHCR release 이미지를 빌드합니다.
3. 운영 웹 호스팅 반영은 Terraform이 관리하지 않는 Vercel 절차입니다. 코드화되면 이 절을 갱신합니다.

### Android 앱 릴리스

스토어에 올라가는 번들은 `main`에서만 만듭니다. v1.0.2까지는 이 규칙이 없어 `versionCode 3`을 `dev`에서 바로 빌드해 올렸고, 그 결과 스토어에 있는 코드가 `main`에 없었습니다(그래서 `main`은 2에서 4로 건너뜁니다). 어느 코드가 사용자 손에 있는지 `main`으로 답할 수 없게 되므로 반복하지 않습니다.

1. `release/v{버전}` 브랜치를 `origin/dev`에서 만들고 `app/build.gradle.kts`의 `versionName`·`versionCode` 두 줄만 커밋합니다.
2. 같은 브랜치로 PR 둘을 냅니다. `main`(`Release` 태그)과 `dev`(버전 동기화)입니다. 릴리스 커밋이 `dev`에도 돌아가야 다음 릴리스의 분기 기준이 어긋나지 않습니다.
3. `main` 병합 후 그 커밋에서 `./gradlew bundleRelease`를 실행합니다.
4. `jarsigner -verify`가 `jar verified.`를 내는지, 번들 매니페스트의 `versionCode`·`versionName`이 의도한 값인지 확인합니다.
5. 같은 AAB를 내부 테스트 트랙에 올리고 실기기에서 로그인과 핵심 흐름을 완주합니다.
6. 통과하면 같은 AAB를 비공개 테스트에서 프로덕션으로 승격합니다. 트랙마다 다시 빌드하지 않습니다. 다시 빌드하면 검증한 번들과 출시하는 번들이 달라집니다.
7. 프로덕션은 단계적 출시로 시작하고 [§4-9](#4-9-검수-관측-롤백)의 중단 기준을 관찰합니다.

버전 규칙입니다.

- `versionCode`는 업로드할 때마다 1씩 올리며 재사용할 수 없습니다. 심사 반려로 같은 내용을 다시 올릴 때도 올립니다.
- `versionName`은 사용자용입니다. 버그 수정은 patch, 기능 추가는 minor로 올립니다.
- 프로덕션 트랙은 Play 개인 개발자 계정 정책상 비공개 테스트 12명이 14일 연속 옵트인한 뒤에야 열립니다. 그 전까지 릴리스는 내부·비공개 테스트에서 끝납니다.

## 4-8. 로컬·통합 실행

`manyak-infra`의 Compose가 로컬 실행 정본입니다. 서버·AI·웹·PostgreSQL·Redis와 Prometheus 설정을 함께 확인합니다. 서비스명 DNS는 Compose 네트워크 안에서 사용합니다. AI stub과 실제 AI 호출 여부는 명시적인 실행 설정으로 확인합니다.

현재 Compose의 모델 기본값과 AWS 태스크 선언은 같다고 가정하지 않습니다. 통합 레포의 모델 기본값에는 과거 이름이 남아 있으므로 선택한 AI 이미지의 등록부와 맞는 값을 공급해야 합니다. 로컬 통합 성공은 AWS IAM·Secrets Manager 주입·CloudFront 업로드 CORS·ECS 롤링 성공의 증거가 아닙니다.

## 4-9. 검수, 관측, 롤백

### 서버·AI 검수와 복구

- 서버와 AI 컨테이너의 상태, 실제 AI 기능을 각각 확인합니다.
- FireLens 로그의 환경 인덱스와 OTLP 수집을 각각 확인합니다. 로그 수집 성공으로 메트릭 export를 판정하지 않습니다.
- DB 회전은 EventBridge 5분 주기 Lambda가 시크릿 `LastChangedDate`와 태스크 `createdAt`을 비교합니다. 필요할 때만 운영 서비스를 재배포하며 시크릿 원문 읽기 권한은 갖지 않습니다. 이 감지 간격은 무중단 보장이 아니므로 실제 재배포와 DB 연결 결과를 확인합니다.
- 이미지 장애는 이전 정상 digest로 환경 태그를 복원한 뒤 새 ECS 배포를 실행하고 같은 검수를 반복합니다. 같은 태스크 정의·가변 태그를 쓰므로 circuit breaker만으로 이전 이미지 복귀가 보장되지 않습니다.
- 모델 설정 장애는 이전 모델 설정과 호환 이미지의 조합으로 복원합니다. Terraform 기본값을 되돌리는 것만으로 기존 운영 Parameter가 바뀌지 않습니다.
- EC2는 현재 복구 대상이 아닙니다. 과거 EC2 가중치 전환·SSM 재실행은 [배포 ADR DEP-023·030](../adr/4-deployment-adr.md#전환-단계-기록)의 역사 기록입니다.

### 이중화 장애 조치 검증(계획)

이 절은 [이중화 계획](#이중화-계획) 적용 후 수행할 검증이며 완료 기록이 아닙니다. 먼저 서비스별 두 AZ 실행 상태, ALB healthy target, RDS Multi-AZ, Redis 복제와 자동 장애 조치, 각 AZ의 NAT 경로를 확인합니다. 하나의 장애가 복구되기 전에 다음 장애를 주입하지 않습니다.

| 장애 주입 | 확인할 동작 | 관측과 완료 조건 |
| --- | --- | --- |
| ECS 태스크 강제 종료 | server, ai, notification, PDC에서 한 태스크씩 종료합니다. 생존 태스크 처리와 대체 태스크 기동을 확인합니다. | CloudWatch의 실행 태스크 수와 ALB healthy target 및 5xx, 앱 로그를 대조합니다. AI 생성, 토큰 갱신, 알림 재전달과 멱등 처리, PDC 조회를 검증하고 두 AZ 분산이 회복되어야 합니다. |
| RDS 강제 장애 조치 | Multi-AZ가 준비된 DB에 `aws rds reboot-db-instance --db-instance-identifier <대상> --force-failover`를 실행합니다. 기존 endpoint의 재해석과 앱 연결 풀 재연결을 확인합니다. | RDS 이벤트와 DB 연결 오류, ALB 5xx, 실제 읽기와 쓰기 재개를 확인합니다. 대기본 생성 완료와 장애 조치 성공을 구분합니다. |
| Redis 강제 장애 조치 | 복제 그룹에 `aws elasticache test-failover --replication-group-id <대상> --node-group-id <대상-shard>`를 실행합니다. Primary 승격과 클라이언트 재연결을 확인합니다. | ElastiCache 이벤트, 복제 지연, Redis 오류, 토큰 갱신, TTL, 멱등 처리 결과를 확인합니다. 장애 전후 최근 쓰기의 보존 여부와 유실 범위를 기록합니다. |
| AZ별 외부 연결과 확장 | 각 AZ에서 이미지 pull, 외부 API와 PDC 터널을 확인합니다. 부하를 늘리고 줄여 세 앱 서비스의 2~4개 확장과 축소를 검증합니다. | 같은 AZ NAT 사용, 양쪽 AZ 배치, 처리 중 요청과 메시지의 결과를 확인합니다. 목표 추적이 반응한 지표와 cooldown, 새 태스크 준비 시간을 기록합니다. |

주입 전 정상 기준값과 허용 오류율, 최대 복구 대기 시간을 검증 계획에 정합니다. 아직 측정하지 않은 RTO나 RPO를 보장값으로 적지 않습니다. 요청 실패나 큐 적체가 합의한 한도를 넘거나 토큰 및 업무 데이터 유실, 중복 처리가 확인되면 다음 주입을 중단하고 복구합니다. 장애 시작부터 정상 요청과 중복 없는 처리가 회복될 때까지의 시간, ALB 5xx, 앱 오류와 데이터 검증 결과를 남깁니다. 개별 태스크 종료는 AZ 전체 장애 재현과 같지 않으므로 AZ 장애 검증을 완료했다고 기록하지 않습니다.

문제가 생기면 자동 확장을 일시 중지하고 검증된 고정 태스크 수를 유지하며 연결과 데이터 상태부터 복구합니다. RDS 장애 조치는 안정화와 재연결을 확인하고 성급한 역전환을 피합니다. Redis는 새 쓰기를 버리는 구 endpoint 복귀를 하지 않으며 [데이터 이전 절차](#redis-데이터-이전)의 복구 경계를 따릅니다. 명령의 대상 리소스는 실행 직전에 대조하며 이 문서 작업에서는 장애 주입이나 apply를 실행하지 않습니다.

### Definition of Done

배포는 다음을 모두 만족할 때 완료입니다.

- 변경 대상 저장소의 필수 테스트와 Docker build 검증이 통과합니다.
- 웹은 Pixel 5 전체 E2E·비주얼 회귀와 iPhone 13 스모크가 통과합니다. UI 변경이면 Linux 기준 이미지 diff를 함께 검토합니다.
- server·ai 배포는 레지스트리에 환경 태그와 `<short-sha>` 태그가 모두 있고, 그 배포가 만든 deployment ID가 완료 상태이며, 실행 태스크의 이미지 digest가 의도한 SHA와 일치합니다.
- server는 외부 `https://api.manyak.app/actuator/health`가 200과 `status=UP`을 반환합니다.
- ai는 컨테이너 health가 정상이고 실제 생성·채팅 1건이 성공합니다. 서버 헬스 성공만으로 판정하지 않습니다.
- 운영 AI 모델 변경은 직전 Parameter 값을 보관하고, 새 값을 읽은 태스크가 떴으며, 바꾼 기능의 운영 API 1건이 성공합니다. 모델명과 provider는 확인하되 키 값은 출력하지 않습니다.
- Terraform 변경은 plan 리뷰 후 적용하고, 대상 리소스와 ALB target group health 중 영향 범위를 확인합니다.
- 시크릿 변경은 값을 소비하는 서비스의 재배포까지 끝나야 반영으로 봅니다.
- 웹 release는 GHCR release 이미지 태그가 발행됩니다. 호스팅 반영은 Vercel 쪽 별도 절차로 확인합니다.
- Android 릴리스는 `main` 커밋에서 만든 AAB가 내부 테스트 실기기 스모크를 통과하고 승격한 트랙에 같은 번들이 올라갑니다. 프로덕션은 단계적 출시를 시작한 시점이 아니라 100% 도달과 중단 기준 미발동까지가 완료입니다.
- 롤백 기준 이미지 태그 또는 DB 복구 계획을 배포 전에 확인합니다. Flyway 마이그레이션은 전진 전용으로 취급합니다.

### Android 단계적 출시와 중단 기준

프로덕션은 단계적 출시로 시작합니다. 비율은 20%에서 100%이고 각 단계를 최소 하루 둡니다. 초기 설치 수에서는 5%처럼 잘게 쪼갠 비율이 표본을 만들지 못하므로, 실제 안전장치는 비율을 늘리는 것이 아니라 중단 레버가 열린 상태로 며칠 두는 것입니다.

다음 중 하나라도 걸리면 출시를 중단하고 수정판을 준비합니다. 기준은 올리기 전에 확정합니다. 정해두지 않으면 애매한 상태로 100%까지 갑니다.

| 신호 | 중단 기준 |
| --- | --- |
| Crashlytics 크래시 없는 사용자 비율 | 직전 버전 대비 1%p 이상 하락 |
| Crashlytics 신규 이슈 | 세션의 0.5% 이상에서 발생 |
| Amplitude 로그인 성공률·스토리 생성 완주율 | 직전 버전 대비 하락이 관찰될 때 |

세 기준 모두 앱 버전별 비교가 전제입니다. Crashlytics·Amplitude의 버전별 비교 대시보드는 아직 없으며 첫 프로덕션 출시 전에 만들어야 기준이 성립합니다.

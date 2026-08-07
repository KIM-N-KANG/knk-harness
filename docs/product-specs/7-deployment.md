# 7-DEPLOYMENT

이 문서는 마냑 서비스의 배포 단위, 운영 인프라, CI/CD, 런타임 설정, 검수와 롤백 기준을 정의합니다. 운영 배포 기준은 `manyak-terraform`, 로컬 통합 실행 기준은 `manyak-infra`, 서비스별 빌드와 배포 트리거는 `manyak-server`, `manyak-ai`, `manyak-web`, `manyak-android` 레포지토리의 현재 구현을 따릅니다.

```text
§7-1  목적과 범위
§7-2  기준 레포지토리와 책임 경계
§7-3  환경 구분과 배포 단위
§7-4  운영 인프라 아키텍처
§7-5  이미지 빌드와 CI/CD
§7-6  런타임 설정과 시크릿
§7-7  운영 배포 절차
§7-8  로컬·통합 실행
§7-9  검수, 관측, 롤백
§7-10 Jira·PR 추적 근거
§7-11 미정·주의 항목
```

| 항목      | 값                                                                                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 버전      | v0.8                                                                                                                                                                |
| 작성일    | 2026-07-03                                                                                                                                                          |
| 수정일    | 2026-08-07                                                                                                                                                          |
| 대상      | 마냑 운영·개발·통합 배포                                                                                                                                            |
| 작성 목적 | 배포 책임 경계, 인프라 구성, 배포 절차, 검수·롤백 기준을 정의합니다.                                                                                                |
| 기준 문서 | [`4-backend.md`](./4-backend.md), [`5-ai-server.md`](./5-ai-server.md), [`6-analytics.md`](./6-analytics.md)                                                        |
| 기준 코드 | OpenAI·Terra 전환은 `../manyak-ai` KNK-803 브랜치 `151fe75`, `../manyak-infra` dev `22090d2`(PR #14), `../manyak-terraform` dev `c167073`(PR #15) 기준입니다. OpenAI 키는 2026-08-07 운영 앱 시크릿에 등록했고 Infra·Terraform 병합도 완료했습니다. AI 브랜치 병합·Terraform apply·AI 배포는 남아 있습니다. 그 밖의 기준은 `../manyak-server` dev `f106b8e`, `../manyak-web` dev `0fac4bd`, `../manyak-android` dev `760b4d3`입니다. Langfuse 배선 적용과 키 주입은 2026-07-23 완료했습니다 |

## 7-1. 목적과 범위

### 목적

이 문서는 다음 질문에 답하기 위한 운영 스펙입니다.

1. 어떤 레포지토리가 어떤 배포 책임을 갖는가?
2. 운영 AWS 인프라는 어떤 리소스로 구성되는가?
3. `dev`, `main`, release tag가 어떤 이미지와 배포를 만드는가?
4. 런타임 환경변수와 시크릿은 어디에서 생성되고 어떻게 주입되는가?
5. 배포 성공, 장애 감지, 롤백은 무엇을 기준으로 판단하는가?

### 포함 범위

- 운영 AWS 인프라: VPC, 보안 그룹, EC2, ALB, ACM, Cloudflare DNS, ECR, RDS PostgreSQL, ElastiCache Redis, Secrets Manager, SSM, GitHub OIDC
- 서비스 이미지 빌드와 레지스트리: GHCR, ECR, multi-arch 이미지 태그
- 운영 배포 파이프라인: `manyak-server`와 `manyak-ai`의 `main` 배포
- 프론트엔드 이미지 릴리스: `manyak-web`의 GHCR `dev` 이미지와 tag 기반 release 이미지
- 로컬·통합 실행: `manyak-infra` Docker Compose
- 검수, 관측, 롤백, 시크릿 회전 기준
- 배포 관련 Jira 키와 GitHub PR 근거

### 제외 범위

- 화면 요구사항과 UX 검수: [`3-1-client.md`](./3-1-client.md)
- API, 데이터 모델, 인증, 오류 처리: [`4-backend.md`](./4-backend.md)
- AI 프롬프트와 요청·응답 계약: [`5-ai-server.md`](./5-ai-server.md)
- 이벤트·지표·관측 수집 정책: [`6-analytics.md`](./6-analytics.md)
- 실제 secret 값, 로컬 `.env`, `terraform.tfvars`, `backend.hcl`, Terraform state
- 운영 웹 호스팅의 외부 플랫폼 설정. 현재 확인한 Terraform에는 `manyak-web` 운영 호스팅 리소스가 없습니다.

### 확인 방식

Jira 원문은 사내 Jira가 소유합니다. 이 문서는 GitHub PR 제목·본문에 연결된 `KNK-*` 키, 병합된 코드, 레포지토리 문서를 근거로 배포 스펙을 정리합니다. 실제 Jira 필드와 이 문서가 다르면 해당 Jira와 병합 PR을 함께 확인해야 합니다.

### 작성 원칙

- 운영 배포 동작은 `manyak-terraform`의 운영 Terraform, SSM 문서, `deploy.sh`, `docker-compose.prod.yml`을 우선 기준으로 씁니다.
- 서비스별 이미지 빌드와 배포 트리거는 각 서비스 레포의 GitHub Actions workflow와 Dockerfile을 기준으로 씁니다.
- 로컬·통합 실행은 `manyak-infra`의 Docker Compose와 `.env.example`을 기준으로 씁니다.
- 문서, PR 설명, 코드가 다르면 병합된 코드를 기준으로 하고 차이는 [§7-11](#7-11-미정주의-항목)에 기록합니다.
- 실제 secret 값, 로컬 전용 설정, Terraform state, 사용자 입력 원문은 예시에도 넣지 않습니다.
- 운영 웹 호스팅처럼 구현 근거가 없는 영역은 추정하지 않고 `미정`으로 표기합니다.

## 7-2. 기준 레포지토리와 책임 경계

| 레포지토리         | 배포 책임                                             | 주요 근거                                                                           |
| ------------------ | ----------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `knk-harness`      | 제품·스펙 문서 정본                                   | `docs/product-specs/`                                                               |
| `manyak-terraform` | 운영 AWS IaC와 운영 compose 원본                      | `terraform/envs/prod`, `terraform/modules`, `docker-compose.prod.yml`               |
| `manyak-infra`     | 로컬·통합 Docker Compose 실행                         | `docker-compose.yml`, `.env.example`, `README.md`                                   |
| `manyak-server`    | 백엔드 이미지 빌드, 운영 server 배포, API 헬스 스모크 | `.github/workflows/docker-image.yml`, `Dockerfile`, `application-prod.yml`          |
| `manyak-ai`        | AI 이미지 빌드, 운영 AI 배포, AI 헬스 게이트          | `.github/workflows/docker-image.yml`, `Dockerfile`, `src/api/v1/health.py`          |
| `manyak-web`       | Next.js 이미지 빌드, GHCR dev/release 이미지 발행     | `.github/workflows/docker-image.yml`, `.github/workflows/release.yml`, `Dockerfile` |
| `manyak-android`   | Android 앱 소스·Gradle 빌드 소유, PR·push CI(`./gradlew check`·`./gradlew assembleDebug`) | `.github/workflows/android-ci.yml`, `app/build.gradle.kts`                          |

### 책임 경계

- 운영 AWS 리소스 생성·변경은 `manyak-terraform`에서 수행합니다.
- 운영 `server`와 `ai` 컨테이너 이미지는 각 서비스 레포의 `main` push가 ECR로 푸시하고 SSM으로 배포합니다.
- 운영 `web` 호스팅은 현재 확인한 `manyak-terraform`에 정의되어 있지 않습니다. `manyak-web`은 GHCR 이미지 발행까지만 코드로 정의합니다.
- 로컬 통합 실행은 `manyak-infra`가 GHCR `dev` 이미지를 pull해 실행합니다. 서비스 소스코드는 이 레포에서 빌드하지 않습니다.
- `manyak-android`는 현재 CI(정적 검사·단위 테스트·debug APK 조립)까지만 코드로 정의합니다. Play Store 배포, 앱 서명, release 빌드·AAB, 내부 테스트 트랙, 운영 배포·롤백 방식은 코드에 근거가 없어 미정입니다([§7-11](#7-11-미정주의-항목)).

## 7-3. 환경 구분과 배포 단위

| 환경              | 목적                    | 배포 단위                                  | 레지스트리·태그                               | 실행 위치                             |
| ----------------- | ----------------------- | ------------------------------------------ | --------------------------------------------- | ------------------------------------- |
| 운영 `prod`       | 실제 사용자 API·AI 운영 | `manyak-server`, `manyak-ai`               | ECR `latest`, `<short-sha>`                   | AWS EC2의 Docker Compose              |
| 개발 이미지 `dev` | 통합 실행과 개발 검증   | `manyak-server`, `manyak-ai`, `manyak-web` | GHCR `dev`, `<short-sha>`                     | `manyak-infra` Compose 또는 개별 실행 |
| 웹 릴리스 이미지  | 프론트엔드 버전 릴리스  | `manyak-web`                               | GHCR `{version}`, `{major}.{minor}`, `latest` | 현재 운영 호스팅 리소스는 미정        |
| 로컬·통합         | 전체 스택 수동 검증     | server, web, ai, postgres, redis           | GHCR `dev`, Docker Hub DB·Redis               | 개발자 Docker Compose                 |

### 운영 공개 엔드포인트

| 엔드포인트                                     | 소유 서비스     | 용도                                    | 공개 여부                    |
| ---------------------------------------------- | --------------- | --------------------------------------- | ---------------------------- |
| `https://api.manyak.app`                       | `manyak-server` | 백엔드 API와 헬스체크                   | 공개                         |
| `http://ai:8000`                               | `manyak-ai`     | server에서 호출하는 compose 내부 AI API | 비공개                       |
| `https://manyak.app`, `https://www.manyak.app` | `manyak-web`    | 프론트엔드 origin으로 CORS 허용         | 운영 호스팅 스택은 현재 미정 |

## 7-4. 운영 인프라 아키텍처

```mermaid
flowchart LR
  user["User / Web client"] --> dns["Cloudflare DNS"]
  dns --> alb["AWS ALB\nHTTPS 443 / HTTP 80 redirect"]
  alb --> server["EC2 private app subnet\nmanyak-server :8080"]
  server --> ai["Docker Compose network\nmanyak-ai :8000"]
  server --> rds["RDS PostgreSQL\nprivate db subnet"]
  server --> redis["ElastiCache Redis\nprivate db subnet"]
  gha["GitHub Actions"] --> ecr["Amazon ECR"]
  gha --> ssm["AWS SSM SendCommand"]
  ssm --> server
  server --> secrets["Secrets Manager\nRDS secret + app secret"]
```

### 네트워크

| 항목                | 현재 값·정책                                           |
| ------------------- | ------------------------------------------------------ |
| 리전                | `ap-northeast-2`                                       |
| VPC                 | `10.0.0.0/16`                                          |
| AZ                  | `ap-northeast-2a`, `ap-northeast-2c`                   |
| 서브넷              | 2 AZ x `public`, `app`, `db`                           |
| NAT                 | MVP 비용 절감을 위해 단일 NAT Gateway                  |
| DB 계층             | 인터넷 라우트 없는 isolated subnet                     |
| S3 Gateway Endpoint | app route table에 연결해 S3/ECR 레이어 트래픽 NAT 우회 |

### 보안 그룹과 접근

| 체인             | 허용                                                                    |
| ---------------- | ----------------------------------------------------------------------- |
| Internet -> ALB  | TCP 80, 443                                                             |
| ALB -> App EC2   | TCP 8080                                                                |
| App EC2 -> RDS   | TCP 5432                                                                |
| App EC2 -> Redis | TCP 6379                                                                |
| App EC2 outbound | ECR, SSM, CloudWatch, LLM API, DB, Redis 접근을 위해 전체 outbound 허용 |
| RDS·Redis egress | 별도 egress 없음. App에서 들어온 연결 응답만 stateful하게 허용          |
| 운영 접속        | SSH 22 미개방. SSM Session Manager 사용                                 |

### 컴퓨트와 엣지

| 항목             | 현재 값·정책                                                                  |
| ---------------- | ----------------------------------------------------------------------------- |
| EC2              | Amazon Linux 2023, `t3.small`, private app subnet 2a                          |
| 배포 위치        | `/opt/manyak/docker-compose.yml`, `/opt/manyak/.env`, `/opt/manyak/deploy.sh` |
| Compose 서비스   | `server`, `ai`                                                                |
| ALB target group | instance target, HTTP 8080, health path `/actuator/health`                    |
| TLS              | ALB가 ACM 인증서로 종단                                                       |
| DNS              | Cloudflare `api.manyak.app` CNAME -> ALB DNS, `proxied=false`                 |
| user-data 변경   | `user_data_replace_on_change=true`라 apply 시 EC2 교체와 짧은 다운타임 가능   |

### 데이터 계층

| 항목           | 현재 값·정책                                                         |
| -------------- | -------------------------------------------------------------------- |
| RDS            | PostgreSQL 16, `db.t3.micro`, gp3 20GB, storage encrypted            |
| DB 이름·사용자 | `manyak`                                                             |
| DB 비밀번호    | RDS `manage_master_user_password`로 Secrets Manager가 자동 생성·관리 |
| RDS 배치       | 단일 AZ 2a, subnet group은 2 AZ                                      |
| 백업           | 7일                                                                  |
| 삭제 보호      | MVP 기준 false                                                       |
| Redis          | ElastiCache Redis 7.1, `cache.t3.micro`, 단일 노드                   |

### DB 비밀번호 로테이션 재동기화

RDS 관리형 마스터 비밀번호는 자동 로테이션될 수 있지만, EC2의 `/opt/manyak/.env`는 `deploy.sh` 실행 시점의 스냅샷입니다. `manyak-terraform`은 KNK-359에서 EventBridge 5분 스케줄과 전용 SSM 문서 `manyak-prod-db-creds-resync`를 추가했습니다.

- SSM 문서는 secret 값이 아니라 AWSCURRENT 버전 id만 비교합니다.
- 버전 id가 바뀌면 `/opt/manyak/deploy.sh`를 override 없이 실행해 `.env`를 재생성합니다. 이 경로는 server를 pull/up하고, ECR에 AI 이미지가 있으면 AI도 `up -d --wait` healthcheck gate를 탑니다.
- 평시에는 no-op이며, 첫 적용 직후에는 상태 파일이 없어 같은 no-override 동기화가 1회 일어날 수 있습니다.

### 이미지 자산 저장·서빙 — `Phase 1 · 계획`

팀 사전 제작 프리셋 자산(썸네일·채팅 배경·캐릭터 — [`4-backend.md §4-3-9`](./4-backend.md))을 위한 정적 자산 계층입니다. **사용자 업로드는 없습니다** — 회원 presigned 업로드 경로는 이미지 정책 개정(2026-07-07, [`4-backend.md §4-8`](./4-backend.md) B10)으로 계약에서 빠졌고, 업로드 주체는 운영(시드)뿐입니다. 현재 Terraform에는 없으며, Phase 1 이미지 기능 구현과 함께 추가합니다.

| 항목        | 방향                                                                                                                                                                                                                                                                                               |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 저장소      | 비공개 S3 버킷 1개(+ CloudFront OAC). prefix로 구분 — `thumbnails/` · `backgrounds/` · `characters/`([`4-backend.md §4-3-9`](./4-backend.md) 자산 카탈로그)                                                                                                                                        |
| 업로드 경로 | 운영 시드 전용 — 자산 파일은 S3에 직접 업로드하고, 카탈로그 등재는 시드 매니페스트 검증을 거칩니다(검증 위반은 시드 실패 — [`4-backend.md §4-3-9`](./4-backend.md)). 클라이언트 업로드 API·presigned URL 발급은 없습니다. 후속에 사용자 업로드류 기능이 도입되면 같은 버킷·CDN 기반을 재사용합니다 |
| 서빙 경로   | CDN(CloudFront) 배포가 버킷을 origin으로 공개 서빙. `imageKey` → 서빙 URL 변환은 백엔드 소유, 객체 키는 불변(교체는 새 키 — 장기 캐시 전제). CDN 도메인·캐시 정책 수치는 `계획`                                                                                                                    |
| 권한        | EC2 인스턴스 role에 해당 버킷 읽기 권한 추가(presigned 발급 권한 불필요)                                                                                                                                                                                                                           |
| 소유        | S3·CloudFront·IAM 리소스 정의는 `manyak-terraform` 소유. 이 문서는 경계와 경로만 고정                                                                                                                                                                                                              |

## 7-5. 이미지 빌드와 CI/CD

### 레지스트리와 태그

| 서비스          | 개발 이미지                        | 운영 이미지         | 태그 정책                                                                         |
| --------------- | ---------------------------------- | ------------------- | --------------------------------------------------------------------------------- |
| `manyak-server` | `ghcr.io/kim-n-kang/manyak-server` | ECR `manyak-server` | dev: `dev`, `<short-sha>` / prod: `latest`, `<short-sha>`                         |
| `manyak-ai`     | `ghcr.io/kim-n-kang/manyak-ai`     | ECR `manyak-ai`     | dev: `dev`, `<short-sha>` / prod: `latest`, `<short-sha>`                         |
| `manyak-web`    | `ghcr.io/kim-n-kang/manyak-web`    | 현재 ECR 없음       | dev: `dev`, `<short-sha>` / release tag: `{version}`, `{major}.{minor}`, `latest` |

### `manyak-server` CI/CD

| 트리거         | 동작                                                                              |
| -------------- | --------------------------------------------------------------------------------- |
| PR -> `dev`    | Java 21, Gradle test, multi-arch Docker build 검증                                |
| push -> `dev`  | 테스트 후 GHCR `dev`, `<short-sha>` push                                          |
| push -> `main` | 테스트 후 ECR `latest`, `<short-sha>` push, SSM으로 server 배포, 외부 헬스 스모크 |

운영 배포는 다음 순서입니다.

1. workflow가 GitHub OIDC로 `vars.AWS_ROLE_ARN` 역할을 assume합니다.
2. ECR에 `manyak-server:<short-sha>`와 `latest`를 push합니다.
3. 최신 `main` SHA가 아니면 stale 배포를 건너뜁니다.
4. `Project=manyak`, `Name=manyak-prod-app`, `running` 태그로 EC2를 찾습니다.
5. SSM `AWS-RunShellScript`로 `SERVER_IMAGE_OVERRIDE=<ECR short-sha image> bash /opt/manyak/deploy.sh`를 실행합니다.
6. `https://api.manyak.app/actuator/health`가 `{"status":"UP"}`를 반환할 때까지 폴링합니다.

### `manyak-ai` CI/CD

| 트리거         | 동작                                                                |
| -------------- | ------------------------------------------------------------------- |
| PR -> `dev`    | Python 3.11, `pytest`, multi-arch Docker build 검증, DeepSeek·OpenAI 더미 키를 넣은 이미지 스모크 2종(기본 health · 더미 키로 Langfuse 활성 경로 health+기동 로그) |
| push -> `dev`  | 테스트 후 GHCR `dev`, `<short-sha>` push                            |
| push -> `main` | 테스트 후 ECR `latest`, `<short-sha>` push, 전용 SSM 문서로 AI 배포 |

운영 AI 배포는 `manyak-prod-ai-deploy` SSM 문서를 사용합니다.

1. workflow가 GitHub OIDC로 AI 전용 `vars.AWS_ROLE_ARN` 역할을 assume합니다.
2. ECR에 `manyak-ai:<short-sha>`와 `latest`를 push합니다.
3. 최신 `main` SHA가 아니면 stale 배포를 건너뜁니다.
4. SSM 문서에 `ImageUri=<ECR manyak-ai short-sha image>` 파라미터를 전달합니다.
5. 문서가 EC2에서 `AI_IMAGE_OVERRIDE='{{ImageUri}}' bash /opt/manyak/deploy.sh`를 실행합니다.
6. `deploy.sh`가 `docker compose up -d --wait ai`로 AI 컨테이너 healthcheck 통과까지 대기합니다. SendCommand 성공은 배포와 AI health 통과를 의미합니다.

### `manyak-web` CI/CD

| 트리거                   | 동작                                                                                                                                |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| PR -> `dev`              | pnpm install, lint, typecheck, Docker build 검증                                                                                    |
| PR·push -> `dev`, `main` | Playwright: Pixel 5 전체 E2E·비주얼 회귀, Desktop Chrome·iPhone 13 스모크. CI는 Chromium·WebKit을 설치하고 Linux 기준 이미지와 비교 |
| push -> `dev`            | GHCR `dev`, `<short-sha>` push                                                                                                      |
| push tag `v*`            | GHCR release image push. 현재 build arg는 `NEXT_PUBLIC_AMPLITUDE_API_KEY`, `NEXT_PUBLIC_APP_VERSION`, `NEXT_PUBLIC_META_PIXEL_ID`(KNK-616)를 주입                        |

비주얼 기준 이미지는 Linux 렌더링만 정본입니다. UI를 의도적으로 변경하면 `manyak-web`에서 `pnpm test:e2e:visual:update`를 실행해 Playwright Docker 이미지로 기준 이미지를 갱신하고 diff를 검토합니다. macOS 로컬 실행은 폰트·안티앨리어싱 차이 때문에 스냅샷 비교를 건너뜁니다.

현재 확인한 운영 Terraform에는 `manyak-web` 컨테이너를 운영 호스팅에 배포하는 리소스가 없습니다. `manyak-web` release PR들은 GHCR release image 발행과 외부 호스팅 반영을 전제로 합니다.

Web Sentry는 Vercel 호스팅 환경 변수 `NEXT_PUBLIC_SENTRY_DSN`으로 활성화되어 운영 이벤트를 수집하고 있습니다(GHCR release workflow·Dockerfile에는 여전히 이 build arg가 없어 컨테이너 경로는 비활성).

### `manyak-android` CI

컨테이너 이미지가 없는 앱 레포입니다. GitHub Actions(`.github/workflows/android-ci.yml`)가 `dev`·`main` 대상 PR·push와 수동 실행(workflow_dispatch)에서 다음을 수행합니다.

| 트리거                   | 동작                                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| PR·push -> `dev`, `main` | Temurin Java 25 설정(Gradle daemon toolchain `gradle-daemon-jvm.properties`와 일치) → `./gradlew check`(ktlint·detekt·Android lint·단위 테스트) → `./gradlew assembleDebug`(debug APK 조립), 리포트 아티팩트 업로드 |

배포 파이프라인(Play Store, 서명, release 빌드·AAB, 내부 테스트 트랙)은 정의되어 있지 않으며 미정입니다([§7-11](#7-11-미정주의-항목)).

Web Sentry SDK 게이팅은 `NODE_ENV=production`이면서 **Vercel 배포일 때만** 이벤트를 전송합니다(KNK-714). `NODE_ENV`만 보면 로컬 프로덕션 빌드(`pnpm build && pnpm start`)의 이벤트까지 `production` 환경으로 유입되기 때문입니다. 배포 여부는 `NEXT_PUBLIC_VERCEL_ENV`의 존재로 판별하며, 이 값은 대시보드의 시스템 환경 변수 노출 설정에 의존하지 않도록 `next.config.ts`가 `VERCEL_ENV`를 빌드 시점에 직접 인라인합니다. 로컬에서 연동을 확인할 때는 `NEXT_PUBLIC_SENTRY_FORCE_ENABLE=true`로 강제 활성화합니다.

### EC2 `deploy.sh` 공통 규칙

- 모든 배포 호출은 EC2의 `flock`으로 직렬화합니다. server와 ai는 서로 다른 GitHub 레포라 workflow concurrency만으로는 동시 배포를 막을 수 없습니다.
- 매 실행마다 Secrets Manager를 다시 읽고 `/opt/manyak/.env`를 재생성합니다.
- AI 전용 OpenAI·Langfuse 키는 공용 `.env`에 쓰지 않고 `deploy.sh`가 셸 환경변수로만 AI compose에 전달합니다.
- `SERVER_IMAGE_OVERRIDE`가 있으면 server만 pull/up 합니다.
- `AI_IMAGE_OVERRIDE`가 있으면 ai만 pull/up 하고 `--wait`로 health를 확인합니다.
- override가 없으면 server를 기동하고, ECR에 AI 이미지가 존재할 때만 ai를 함께 기동합니다.
- 한 서비스만 배포할 때 다른 서비스 이미지가 `latest`로 덮이지 않도록 기존 `.env`의 이미지 좌표를 보존합니다.

## 7-6. 런타임 설정과 시크릿

### GitHub 설정

| 레포            | 설정                                  | 용도                                                            |
| --------------- | ------------------------------------- | --------------------------------------------------------------- |
| `manyak-server` | repository variable `AWS_ROLE_ARN`    | server ECR push와 SSM 배포용 OIDC role ARN                      |
| `manyak-ai`     | repository variable `AWS_ROLE_ARN`    | AI ECR push와 전용 SSM 배포용 OIDC role ARN                     |
| `manyak-web`    | repository secret `AMPLITUDE_API_KEY` | tag release 이미지 빌드 시 `NEXT_PUBLIC_AMPLITUDE_API_KEY` 주입 |
| `manyak-web`    | repository secret `META_PIXEL_ID`     | tag release 이미지 빌드 시 `NEXT_PUBLIC_META_PIXEL_ID` 주입(KNK-616). 미등록 시 빈 값이 주입되어 픽셀은 비활성 상태로 빌드됨 |

`AWS_ROLE_ARN` 값은 `manyak-terraform/terraform/envs/prod` output에서 확인합니다.

`manyak-web`의 `NEXT_PUBLIC_SENTRY_DSN`은 코드가 참조하지만 현재 release workflow 입력으로 정의되어 있지 않습니다.

### Secrets Manager

`manyak-terraform`은 앱 시크릿 컨테이너 `manyak/prod/app`만 만들고, 실제 값은 콘솔 또는 CLI로 별도 입력합니다. 실제 secret 값은 문서나 레포지토리에 넣지 않습니다.

| 키                                     | 필수              | 주입 대상           | 설명                                                                                                                                         |
| -------------------------------------- | ----------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `SERVER_SENTRY_DSN`                    | 아니오            | server `SENTRY_DSN` | 백엔드 Sentry DSN. 비우면 Sentry 비활성                                                                                                      |
| `AI_SENTRY_DSN`                        | 아니오            | ai `SENTRY_DSN`     | AI Sentry DSN. 비우면 Sentry 비활성 |
| `AI_LANGFUSE_PUBLIC_KEY` | 아니오 | ai `LANGFUSE_PUBLIC_KEY` | Langfuse 공개 키. 비우면 관측 비활성(no-op) |
| `AI_LANGFUSE_SECRET_KEY` | 아니오 | ai `LANGFUSE_SECRET_KEY` | Langfuse 시크릿 키. 비우면 관측 비활성(no-op) |
| `AI_LANGFUSE_HOST` | 아니오 | ai `LANGFUSE_HOST` | Langfuse 리전 엔드포인트. JP `https://jp.cloud.langfuse.com` 필수 — 비우면 활성화 가드가 막아 관측 비활성(no-op) |
| `MANYAK_SLACK_FEEDBACK_WEBHOOK_URL`    | 아니오            | server              | 피드백 Slack 알림. 비우면 발송 생략                                                                                                          |
| `MANYAK_ANALYTICS_ANONYMOUS_ID_PEPPER` | 아니오            | server              | 현재 Terraform과 infra가 주입하는 pepper 키. 서버 코드는 새 `MANYAK_ANALYTICS_DEVICE_ID_PEPPER`를 먼저 보고 이 키를 fallback으로 인식합니다. |
| `DEEPSEEK_API_KEY`                     | 예(AI)            | ai                  | 기본 스토리라인·채팅 모델을 호출하는 키                                                                                                      |
| `OPENAI_API_KEY`                       | GPT 모델 선택 시 예 | ai `OPENAI_API_KEY` | 기본 컴파일 모델 Terra를 호출하는 키. `deploy.sh`가 셸 환경변수로만 전달하며 공용 `.env`에는 기록하지 않음                                      |
| `MANYAK_AUTH_JWT_SECRET`               | 예(server)        | server              | access JWT HS256 서명·검증 키. 미주입 또는 빈 값이면 server 부팅 실패                                                                        |
| `MANYAK_GOOGLE_CLIENT_IDS`             | 로그인 사용 시 예 | server              | 허용할 Google OAuth client-id 목록. 비우면 모든 Google 로그인 토큰 거부                                                                      |
| `MANYAK_KAKAO_CLIENT_IDS`              | 카카오 로그인 사용 시 예 | server       | 허용할 Kakao REST API 키 목록(ID 토큰 `aud` 검증). 비우면 모든 Kakao 로그인 토큰 거부. provider별 독립이라 미주입이 Google 로그인에 영향을 주지 않음. **시크릿에 키를 추가하는 것만으로는 서버에 전달되지 않음** — 아래 배선 문단 참조(`Phase 1 · 계획` KNK-721) |
| `SERVER_MANAGEMENT_OTLP_METRICS_EXPORT_URL` | 아니오 | server `MANAGEMENT_OTLP_METRICS_EXPORT_URL` | Grafana Cloud OTLP 게이트웨이 URL. **표준 `OTEL_EXPORTER_OTLP_ENDPOINT`가 아니라 이 Spring 전용 이름으로 주입합니다** — 공용 `.env`를 AI 컨테이너가 함께 읽어 표준 이름은 AI의 OTel SDK까지 집어 들기 때문입니다(아래 메트릭 배선 문단). **끄는 수단은 `MANYAK_OTLP_METRICS_ENABLED` 토글이며, 이 키를 빈 값으로 남기면 안 됩니다** — 미주입은 `localhost:4318` 헛푸시로, 빈 문자열은 빈 URL 전송 오류로 갈립니다([`4-backend.md §4-7`](./4-backend.md)). 끌 때는 키를 넣지 않습니다(`Phase 2 · 구현` — 2026-08-06 주입 완료) |
| `SERVER_MANAGEMENT_OTLP_METRICS_EXPORT_HEADERS_AUTHORIZATION` | 아니오 | server `MANAGEMENT_OTLP_METRICS_EXPORT_HEADERS_AUTHORIZATION` | Grafana Cloud OTLP 인증 헤더(instance ID + 토큰). 시크릿이라 문서·레포에 값을 싣지 않음. 이름 규칙과 비활성 수단은 위 행과 같습니다(`Phase 2 · 구현` — 2026-08-06 주입 완료) |

`aws secretsmanager put-secret-value`는 secret 전체를 덮어씁니다. 일부 키만 바꿀 때도 기존 키를 모두 포함해야 합니다.

**OpenAI 키를 Terra 컴파일에 전달하는 방법(KNK-803·807·808).**

- **무엇.** 컴파일 모델을 `gpt-5.6-terra`로 바꾸면서 로컬·통합 환경과 운영 AI 컨테이너에 `OPENAI_API_KEY`를 전달합니다. OpenAI 키는 2026-08-07 운영 앱 시크릿에 등록했고 Infra·Terraform 변경은 `dev`에 병합했습니다. AI 브랜치 병합과 Terraform apply는 남아 있습니다.
- **왜.** AI 서버는 선택된 모델의 공급자 키를 기동할 때 검사합니다([`5-ai-server.md`](./5-ai-server.md) D13). Terra가 기본 컴파일 모델인데 OpenAI 키가 없으면 AI 컨테이너가 기동하지 않습니다. 반대로 OpenAI를 쓰지 않는 구성에서는 이 키 때문에 server 배포나 EC2 부팅까지 막을 이유가 없습니다.
- **어떻게.** `manyak-infra`는 OpenAI 키를 AI 컨테이너에만 전달하고 컴파일 기본값을 Terra로 맞춥니다. 운영에서는 Secrets Manager의 키를 `deploy.sh`가 읽어 셸 환경변수로 export하고, compose가 AI 컨테이너의 `OPENAI_API_KEY`로 옮깁니다. 공용 필수 키 검사에는 넣지 않아, 키가 없을 때 server 배포는 계속되고 GPT를 선택한 AI만 자체 기동 검사에서 실패합니다. Terraform의 `ignore_changes = [secret_string]` 때문에 코드에 키 이름을 추가해도 기존 Secrets Manager 값은 자동으로 바뀌지 않습니다.
- **왜 그 방법.** 공용 `.env`는 server 컨테이너도 통째로 읽으므로 OpenAI 키를 적으면 AI 전용 비밀이 server까지 전달됩니다. Langfuse 키와 같은 export-only 방식을 써서 소비 범위를 AI로 제한했습니다. 공용 필수 키 검사에서 제외한 것은 조건부 AI 키 하나가 server 배포와 EC2 부팅까지 막는 실패를 피하기 위해서입니다. 대가로 `deploy.sh`를 거치지 않고 compose를 직접 실행하면 OpenAI 키가 비어 Terra를 선택한 AI가 기동하지 않으므로, 배포와 롤백은 반드시 `deploy.sh`를 거칩니다.

**카카오 로그인 배선 — `Phase 1 · 계획`(KNK-721). 아래는 전부 미구현 목표 상태이며, 현재 상태는 아래 'EC2 `.env` 생성 결과' 표가 정본입니다(카카오 키 없음).** compute user-data(`user-data.sh.tftpl`)는 시크릿 JSON에서 키를 하나씩 명시적으로 추출해 `.env`에 기록하므로, 시크릿에 `MANYAK_KAKAO_CLIENT_IDS`를 넣는 것만으로는 서버에 전달되지 않습니다. 배선에는 세 가지가 필요합니다: ① `manyak-terraform` user-data에 추출·기록 라인 추가(적용 시 아래 표에도 반영), ② 로컬·통합용 `manyak-infra` compose에 환경변수 전달 추가, ③ 웹 런타임에 `AUTH_KAKAO_ID`(REST API 키)·`AUTH_KAKAO_SECRET`(클라이언트 시크릿) 주입 — 운영 웹이 호스팅되는 **Vercel 환경 변수**로 넣습니다(Web Sentry DSN과 같은 경로, §7-5. GHCR 컨테이너 배포를 쓰게 되면 주입 방식을 별도 결정). 배포 순서는 **서버 환경변수 반영이 먼저**입니다(미주입은 fail-closed로 Kakao 401만 발생, Google 무영향 — 순서가 바뀌면 웹 버튼이 먼저 노출돼 전원 401). 웹 카카오 버튼 릴리스 전에 서버 컨테이너 `.env`의 키 존재를 릴리스 게이트로 확인하고, 릴리스 후 카카오 로그인 1회 완주(카카오 인가 화면 → 콜백 → 백엔드 200)를 운영 스모크로 확인합니다. 시크릿의 카카오 키는 **단일 카카오 앱의 REST API 키 1개**여야 합니다([`4-backend.md §4-5`](./4-backend.md) — pairwise `sub` 계정 오귀속 방지).

**메트릭(Grafana Cloud OTLP) 배선 — `Phase 2 · 구현`(KNK-781·793, 2026-08-06 활성화 완료).** user-data가 시크릿에서 두 값을 뽑아 `.env`에 기록하며, 적용 결과는 위 'EC2 `.env` 생성 결과' 표에 반영돼 있습니다. 다만 **주입할 환경변수 이름은 표준 `OTEL_EXPORTER_OTLP_*`가 아니라 Spring 전용 이름(`MANAGEMENT_OTLP_METRICS_EXPORT_URL`·`MANAGEMENT_OTLP_METRICS_EXPORT_HEADERS_AUTHORIZATION`)을 씁니다.** 공용 `.env`는 server와 ai 컨테이너가 함께 읽는데, `OTEL_EXPORTER_OTLP_ENDPOINT`·`OTEL_EXPORTER_OTLP_HEADERS`는 **OpenTelemetry 표준 변수라 AI 컨테이너의 SDK도 그대로 집어 듭니다**(Langfuse Python SDK는 OTel 기반 — [`5-ai-server.md §5-6`](./5-ai-server.md)). 공용 `.env`에 표준 이름으로 넣으면 AI 트레이스가 서버용 Grafana Cloud 자격증명으로 새어 나갈 수 있습니다. Spring 전용 이름은 AI 컨테이너가 무시하므로 Langfuse 키처럼 export-only로 우회할 필요 없이 공용 `.env`에 그대로 둘 수 있습니다. 로컬(IntelliJ 단일 프로세스)은 컨테이너 공유가 없으므로 표준 `OTEL_*` 이름을 그대로 써도 됩니다. 켜는 순서는 **주입이 먼저, 토글(`MANYAK_OTLP_METRICS_ENABLED=true`)이 나중**입니다 — 토글만 켜면 레지스트리가 `localhost:4318`로 헛푸시합니다([`4-backend.md §4-7`](./4-backend.md)). 토글 자체는 **시크릿이 아닙니다** — 위 Secrets Manager 표가 아니라 user-data가 `.env`에 직접 쓰는 리터럴이며, 끄고 켜는 데 시크릿 갱신이 필요 없어야 합니다.

시크릿 값을 바꾼 뒤에는 해당 값을 소비하는 서비스를 재기동해야 합니다. GitHub workflow 배포는 `SERVER_IMAGE_OVERRIDE` 또는 `AI_IMAGE_OVERRIDE`가 가리키는 서비스만 재기동합니다. `SERVER_SENTRY_DSN`, `MANYAK_AUTH_JWT_SECRET`, `MANYAK_GOOGLE_CLIENT_IDS`, Slack webhook, analytics pepper는 server 재배포로 반영합니다(`MANYAK_KAKAO_CLIENT_IDS`는 위 배선이 적용된 뒤에야 같은 경로를 탑니다). `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `AI_SENTRY_DSN`과 Langfuse 3키는 AI 재배포로 반영합니다. 두 서비스를 동시에 반영하려면 SSM에서 override 없이 `bash /opt/manyak/deploy.sh`를 실행합니다.

> **Langfuse 배선과 키 주입은 2026-07-23 완료했습니다(KNK-653, manyak-terraform).** user-data는 Secrets Manager의 Langfuse 3키(`AI_LANGFUSE_PUBLIC_KEY`·`AI_LANGFUSE_SECRET_KEY`·`AI_LANGFUSE_HOST`)를 배포 스크립트의 **export로만** compose에 넘깁니다. 공용 `.env`에 쓰지 않아 server 컨테이너로 새지 않는 대신, `deploy.sh`를 거치지 않은 수동 compose 실행에서는 값이 비어 Langfuse가 꺼집니다(아래 롤백 표 참고).

**백엔드 score 발행 배선 — `Phase 1 · 계획`(KNK-762).**

- **무엇.** 백엔드가 AI와 같은 Langfuse 프로젝트에 사용자 반응 score를 보내도록 전용 자격 증명과 런타임 설정을 주입합니다.
- **왜.** AI용 키는 현재 AI 컨테이너에만 전달되며, 백엔드는 사용자 반응을 직접 발행하므로 별도 소비 경계가 필요합니다. 키나 리전 설정이 잘못돼도 제작·채팅 기능은 계속 동작해야 합니다.
- **어떻게.** manyak-server는 환경 변수 이름, 키 누락·JP 리전·prod 활성화 가드, worker 기동 조건과 운영 로그를 결정합니다. manyak-terraform은 Secrets Manager 키와 운영 user-data·배포 스크립트 배선을 결정하고, manyak-infra는 로컬·통합 compose 배선을 맞춥니다. 두 인프라 레포는 서버 재기동 절차와 score 발행만 끄는 롤백 방법도 함께 기록합니다. 실제 secret 값은 문서와 레포에 넣지 않습니다.
- **왜 이 방법.** 백엔드 전용 키는 서비스별 권한과 교체 범위를 분리합니다. 서버의 활성화 가드와 인프라의 주입·롤백 책임을 나누면 Langfuse 장애나 설정 누락이 사용자 요청 실패로 번지지 않습니다.

### EC2 `.env` 생성 결과

`deploy.sh`는 RDS managed secret과 앱 secret을 읽어 `/opt/manyak/.env`를 생성합니다.

| 환경변수                                             | 소비 서비스 | 출처                                                  |
| ---------------------------------------------------- | ----------- | ----------------------------------------------------- |
| `SERVER_IMAGE`                                       | compose     | Terraform 기본 이미지 또는 server workflow override   |
| `AI_IMAGE`                                           | compose     | Terraform 기본 이미지 또는 AI workflow override       |
| `MANYAK_DB_URL`                                      | server      | Terraform RDS endpoint, port, DB 이름                 |
| `MANYAK_DB_USERNAME`, `MANYAK_DB_PASSWORD`           | server      | RDS managed secret                                    |
| `SENTRY_DSN`, `SENTRY_ENVIRONMENT`                   | server      | 앱 secret, Terraform environment                      |
| `AI_SENTRY_DSN`, `SENTRY_ENVIRONMENT`                | ai          | 앱 secret, Terraform environment                      |
| `MANYAK_SLACK_FEEDBACK_WEBHOOK_URL`                  | server      | 앱 secret                                             |
| `MANYAK_ANALYTICS_ANONYMOUS_ID_PEPPER`               | server      | 앱 secret                                             |
| `DEEPSEEK_API_KEY`                                   | ai          | 앱 secret                                             |
| `MANYAK_AUTH_JWT_SECRET`, `MANYAK_GOOGLE_CLIENT_IDS` | server      | 앱 secret                                             |
| `MANYAK_CORS_ALLOWED_ORIGINS`                        | server      | Terraform `https://manyak.app,https://www.manyak.app` |
| `SPRING_DATA_REDIS_HOST`, `SPRING_DATA_REDIS_PORT`   | server      | ElastiCache endpoint, port                            |
| `MANAGEMENT_OTLP_METRICS_EXPORT_URL`, `MANAGEMENT_OTLP_METRICS_EXPORT_HEADERS_AUTHORIZATION` | server | 앱 secret(`SERVER_` 접두 키). **URL·Authorization이 둘 다 있을 때만** 기록 |
| `MANYAK_OTLP_METRICS_ENABLED`                        | server      | user-data 리터럴 `true`. 위 두 값이 있을 때만 함께 기록 |

현재 server 코드는 `MANYAK_ANALYTICS_DEVICE_ID_PEPPER`를 우선하고 `MANYAK_ANALYTICS_ANONYMOUS_ID_PEPPER`를 fallback으로 읽습니다. Terraform과 infra는 아직 fallback 키를 주입하므로, 배포 스펙에서는 현재 주입 키와 코드 우선순위를 함께 기록합니다.

`OPENAI_API_KEY`와 Langfuse 3키는 이 표의 공용 `.env`에 들어가지 않습니다. `deploy.sh`가 같은 셸에서 export하고 AI compose에만 전달합니다.

## 7-7. 운영 배포 절차

### Terra 컴파일 전환 순서(KNK-803·805·807·808·809)

- **무엇.** AI의 컴파일 모델 선택, 통합 Compose의 모델·키 전달, 운영 Terraform의 키 전달을 함께 반영한 뒤 운영 컴파일을 `gpt-5.6-terra`로 전환합니다. OpenAI 키 등록과 Infra·Terraform 병합은 끝났고, AI 브랜치 병합·Terraform apply·AI 배포는 남아 있습니다.
- **왜.** AI 코드만 먼저 배포하면 운영 Compose가 OpenAI 키를 컨테이너에 전달하지 못해 AI가 기동하지 않습니다. 반대로 Terraform 코드만 준비해도 apply 전에는 실행 중인 EC2의 배포 스크립트와 Compose가 바뀌지 않으므로 Terra를 안전하게 호출할 수 없습니다.
- **어떻게.** ① `manyak-ai`·`manyak-infra`·`manyak-terraform` 작업 브랜치를 각각 `dev`에 병합합니다. ② 후속 운영 작업에서 Terraform plan으로 EC2 교체와 다운타임을 확인한 뒤 apply합니다. ③ 외부 server health와 AI health를 확인합니다. ④ 마지막으로 AI release를 `main`에 반영해 Terra 기본값이 든 이미지를 배포하고, 컴파일 1건의 성공과 응답 metadata의 `provider=openai`·`model=gpt-5.6-terra`를 확인합니다.
- **왜 그 방법.** 키는 이미 등록돼 있으므로 코드 병합 자체를 기다릴 이유는 없지만, 실제 운영 전달 경로는 Terraform apply가 만들어 줍니다. 세 레포를 먼저 병합하고 인프라를 적용한 뒤 모델 이미지를 배포하면, 키 전달 경로가 없는 상태에서 Terra가 먼저 선택되는 실패를 피할 수 있습니다. Terraform apply는 EC2 교체를 일으킬 수 있어 코드 병합과 분리한 후속 운영 작업으로 실행합니다.

### 최초 인프라 준비

1. `manyak-terraform/terraform/bootstrap`에서 원격 state S3 backend를 준비합니다.
2. `manyak-terraform/terraform/envs/prod`에서 `backend.hcl`과 `terraform.tfvars`를 로컬에 작성합니다. 이 파일들은 커밋하지 않습니다.
3. `terraform init -reconfigure -backend-config=backend.hcl`을 실행합니다.
4. `terraform plan`으로 변경 범위를 확인합니다.
5. 운영 반영이 승인되면 `terraform apply`를 실행합니다.
6. Terraform output의 server·AI GitHub Actions role ARN을 각 앱 레포의 `AWS_ROLE_ARN` variable에 등록합니다.
7. `manyak/prod/app` secret에 필요한 키를 모두 포함해 실제 값을 입력합니다.

### 일반 server 배포

1. `manyak-server` 변경을 `dev`에 병합해 GHCR `dev` 이미지를 검증합니다.
2. release branch를 `main`에 merge commit으로 병합합니다.
3. `main` push workflow가 ECR 이미지를 만들고 SSM으로 server를 배포합니다.
4. workflow의 `/actuator/health` 스모크가 `UP`인지 확인합니다.
5. 필요하면 `manyak-server/http/smoke-prod.http`로 수동 검증합니다.

### 일반 AI 배포

1. `manyak-ai` 변경을 `dev`에 병합해 GHCR `dev` 이미지를 검증합니다.
2. release branch를 `main`에 merge commit으로 병합합니다.
3. `main` push workflow가 ECR 이미지를 만들고 전용 SSM 문서로 AI를 배포합니다.
4. SendCommand 성공을 확인합니다. 현재 AI 배포는 전용 문서가 내부 healthcheck까지 수행하므로 별도 외부 smoke endpoint가 없습니다.

### Terraform 변경 배포

1. `terraform fmt -recursive -check`와 `terraform validate`를 먼저 실행합니다.
2. `terraform plan`에서 리소스 추가·변경·삭제와 EC2 교체 여부를 확인합니다.
3. `user-data`, `docker-compose.prod.yml`, CORS, Redis 주입처럼 compute template에 영향을 주는 변경은 EC2 교체와 짧은 다운타임을 수반할 수 있습니다.
4. `apply` 후 `https://api.manyak.app/actuator/health`와 SSM/CloudWatch/Sentry 상태를 확인합니다.

### Web release 이미지 배포

1. `manyak-web` 변경을 `dev`에 병합해 GHCR `dev` 이미지를 검증합니다.
2. release tag `v*`를 push하면 `release.yml`이 GHCR release 이미지를 빌드합니다.
3. 현재 이 문서 기준으로 운영 웹 호스팅 반영 절차는 코드화되어 있지 않습니다. 별도 호스팅 플랫폼 또는 인프라 문서가 정해지면 이 절차를 갱신합니다.

## 7-8. 로컬·통합 실행

`manyak-infra`는 GHCR에 publish된 `dev` 이미지를 실행하는 통합 환경입니다. 서비스 소스코드를 빌드하지 않습니다.

| 서비스          | 이미지                                 | 용도                    |
| --------------- | -------------------------------------- | ----------------------- |
| `manyak-server` | `ghcr.io/kim-n-kang/manyak-server:dev` | 백엔드 API              |
| `manyak-web`    | `ghcr.io/kim-n-kang/manyak-web:dev`    | Next.js 웹              |
| `manyak-ai`     | `ghcr.io/kim-n-kang/manyak-ai:dev`     | AI API                  |
| `postgres`      | `postgres:16-alpine`                   | 로컬 DB                 |
| `redis`         | `redis:7-alpine`                       | refresh token 저장소 등 |
| `prometheus`    | `prom/prometheus`(태그는 배선 시 고정) | 로컬 메트릭 스크레이프(`Phase 2 · 계획`) |

`prometheus`는 **로컬 전용**입니다. 운영 메트릭은 Grafana Cloud로 OTLP push하므로(§7-9) 운영에는 스크레이프 대상도 Prometheus 인스턴스도 두지 않습니다. 로컬 Prometheus는 server 컨테이너의 `/actuator/prometheus`를 긁어 pull 경로(스크레이프 설정·relabel·recording rule)를 실물로 확인하는 용도이며, 운영 구성으로 승격하지 않습니다([`4-backend.md §4-7`](./4-backend.md)).

**전제조건.** 스크레이프 대상(`/actuator/prometheus`)은 **`local` 프로파일에서만** 존재합니다 — exposure 목록도 Security의 무인증 허용도 `application-local.yml`·`SecurityConfig`가 local로 한정합니다. 현재 compose는 `SPRING_PROFILES_ACTIVE`를 주지 않아 `spring.profiles.default: local` 덕분에 local로 뜨는데, 누가 compose에 `SPRING_PROFILES_ACTIVE: dev`를 넣는 순간 스크레이프가 404/401로 조용히 깨집니다. compose에서 프로파일을 지정하게 되면 `local`을 명시해야 합니다. 서버 메트릭 구현은 `manyak-server` `dev`에 머지되어(KNK-779) GHCR `dev` 이미지에 엔드포인트가 들어가므로, 남은 조건은 프로파일 하나입니다.

### 실행

```sh
cd ../manyak-infra
cp .env.example .env
docker login ghcr.io
docker compose pull
docker compose up -d
docker compose ps
```

### 기본 로컬 URL

| URL                                     | 용도          |
| --------------------------------------- | ------------- |
| `http://localhost:3000`                 | Web           |
| `http://localhost:8080/actuator/health` | Server health |
| `http://localhost:8000/api/v1/health`   | AI health     |

### 로컬 환경변수 기준

- `API_BASE_URL`은 web 컨테이너가 server 컨테이너를 호출하는 URL입니다. Compose 내부 기본값은 `http://manyak-server:8080`입니다.
- `MANYAK_AI_BASE_URL`은 server가 AI를 호출하는 URL입니다. Compose 내부 기본값은 `http://manyak-ai:8000`입니다.
- `MANYAK_AI_CHAT_STUB=false`가 통합 실행 기본값입니다. AI 없이 server만 빠르게 확인하려면 `true`로 바꿀 수 있습니다.
- `NEXT_PUBLIC_*` 값은 web 이미지 빌드 시점에 반영됩니다. `manyak-infra` Compose 실행 시점에는 주입하지 않습니다.
- 실제 secret 값은 `.env`에만 두고 커밋하지 않습니다.

**통합 환경의 AI 모델·키 선택(KNK-807).**

- **무엇.** 통합 환경은 컴파일에 `gpt-5.6-terra`, 스토리라인·채팅에 `deepseek-v4-flash`를 기본으로 사용합니다.
- **왜.** Compose가 예전 컴파일 기본값 `deepseek-v4-pro`를 계속 주입하면 AI 코드의 Terra 기본값을 덮어써서, 통합 검수와 운영이 서로 다른 모델을 조용히 사용합니다.
- **어떻게.** `MANYAK_AI_STORY_COMPILE_MODEL`의 Compose 기본값을 Terra로 맞추고 `OPENAI_API_KEY`를 AI 컨테이너에만 전달합니다. 기본 구성을 실행하려면 OpenAI 키와 DeepSeek 키가 모두 필요하며, 실제 값은 로컬 `.env`에만 둡니다.
- **왜 그 방법.** 모델 변수 구조는 유지하고 기본값만 AI 코드와 맞추면 사용자가 명시한 다른 등록 모델로 바꾸는 기능을 보존할 수 있습니다. 키를 서비스별 명시 매핑으로 전달하면 OpenAI 키가 server·web 등 사용하지 않는 컨테이너로 퍼지지 않습니다.

## 7-9. 검수, 관측, 롤백

### 배포 전 검수

| 대상          | 필수 검수                                                                                                        |
| ------------- | ---------------------------------------------------------------------------------------------------------------- |
| Terraform     | `terraform fmt -recursive -check`, `terraform validate`, `terraform plan`                                        |
| server        | `./gradlew test`, Docker build workflow, 운영 health smoke                                                       |
| AI            | `pytest`, Docker build workflow, AI healthcheck                                                                  |
| web           | `pnpm typecheck`, `pnpm lint`, `pnpm test`, Playwright E2E·비주얼 회귀, Docker build workflow, tag release build |
| infra Compose | `docker compose config`, 필요 시 `docker compose up -d`와 health 확인                                            |

### 운영 헬스체크

| 서비스          | 기준                                                                                |
| --------------- | ----------------------------------------------------------------------------------- |
| server          | `GET https://api.manyak.app/actuator/health`가 200과 `status=UP`을 반환             |
| server liveness | `GET https://api.manyak.app/actuator/health/liveness`가 200 반환                    |
| AI              | 컨테이너 healthcheck가 `GET http://localhost:8000/api/v1/health`의 `status=ok` 확인 |
| ALB             | target group health path `/actuator/health`                                         |

현재 `manyak-server`의 운영 profile은 Redis endpoint를 주입받지만, 기준 코드에서는 `management.health.redis.enabled=false`입니다. Redis가 실제 장애 감지에 포함되는지 여부는 별도 후속에서 다시 확인해야 합니다.

### Definition of Done

배포는 다음 조건을 만족할 때 완료로 봅니다.

- 변경 대상 레포의 필수 테스트와 Docker build 검증이 통과해야 합니다.
- `web`은 Pixel 5 전체 E2E·비주얼 회귀와 Desktop Chrome·iPhone 13 스모크가 통과해야 합니다. UI 변경 시 Linux 기준 이미지 diff를 함께 검토해야 합니다.
- 운영 server·AI 배포는 ECR에 `latest`와 `<short-sha>` 태그가 존재하고, GitHub Actions가 최신 `main` SHA 기준으로 SSM 배포를 실행해야 합니다.
- server 배포는 외부 `https://api.manyak.app/actuator/health`가 200과 `status=UP`을 반환해야 합니다.
- AI 배포는 `docker compose up -d --wait ai`가 성공하고 컨테이너 healthcheck가 `status=ok`를 확인해야 합니다.
- Terra 컴파일 전환은 운영 AI 컨테이너에 `OPENAI_API_KEY`가 전달되고, 컴파일 1건의 응답 metadata가 `provider=openai`·`model=gpt-5.6-terra`인 것까지 확인해야 합니다. 키 값 자체는 로그나 검수 결과에 출력하지 않습니다.
- Terraform 변경은 `terraform plan` 리뷰 후 적용해야 하며, 적용 후 대상 리소스, SSM 문서, ALB target group health 중 변경 영향이 있는 항목을 확인해야 합니다.
- 시크릿 변경은 해당 값을 소비하는 서비스 재기동까지 완료해야 반영된 것으로 봅니다.
- `web` release는 GHCR release 이미지 태그가 발행되어야 합니다. 운영 호스팅 반영은 현재 스펙상 별도 외부 절차로 확인합니다.
- 롤백 기준 이미지 태그 또는 DB 복구 계획을 배포 전 확인해야 합니다. Flyway 마이그레이션은 전진 전용으로 취급합니다.

### 관측

- server는 구조화 로그, Sentry, `ai_call_logs`, Actuator health를 사용합니다.
- server 메트릭은 Micrometer로 계측해 **Grafana Cloud로 OTLP push**합니다(`Phase 2 · 구현` — 서버 계측 KNK-779·784, 운영 배선 KNK-781·793, **2026-08-06 v0.2.7 배포로 활성화 완료**. [`4-backend.md §4-7`](./4-backend.md)). Prometheus·Grafana를 별도 EC2에 자체 호스팅하지 않습니다. push 방식이라 운영은 `/actuator/prometheus`를 노출하지 않고 인바운드 경로도 열지 않습니다. 환경은 `service.name`으로 가릅니다(운영 `manyak-server` / 로컬 `manyak-server-local`). 전송 주기는 운영 60초입니다. 대시보드는 RED(요청률·5xx 오류율·p95)와 AI 호출 지연(`feature`별 p95), JVM·CPU·HikariCP를 봅니다. **알림 임계값은 운영 기준선이 쌓인 뒤 정하며**, 서버 정지 시 규칙이 No Data로 발화하므로 No Data 동작을 함께 설계합니다.
- AI는 Sentry와 request correlation middleware를 사용합니다.
- AI는 정상·실패 LLM 호출의 프롬프트·응답 원문을 Langfuse에 트레이스로 남깁니다(§6-7 원문 예외 — JP 리전·prod 전용). 키·JP host·prod 환경이 모두 충족될 때만 켜지고(활성화 가드, [`5-ai-server.md §5-6`](./5-ai-server.md)) 미충족 시 no-op입니다. 프로덕션은 2026-07-23 활성화했습니다.
- web은 Amplitude, API 오류 캡처, Sentry 연동 코드를 사용합니다. 운영 Sentry 수집은 Vercel 환경 변수 `NEXT_PUBLIC_SENTRY_DSN`으로 활성 상태입니다(§7-5). GHCR release 이미지에는 여전히 주입 경로가 없어 컨테이너 배포 경로는 비활성입니다.
- `X-Manyak-Request-Id`, `X-Manyak-Session-Id`, `X-Manyak-Device-Id-Hash` 계열은 server와 AI 관측 연결에 사용합니다.
- 운영 Swagger UI와 OpenAPI 문서는 비공개입니다. 해당 경로는 운영에서 404여야 합니다.

### Langfuse 활성화 점검 — `Phase 1 · 구현`

프로덕션 Langfuse는 2026-07-23 활성화했습니다. 아래 항목으로 적용 상태를 확인합니다.

- **Langfuse 코드가 담긴 AI 릴리스가 배포됐는지** — **충족**: 관측 그릇(KNK-624·640)과 안전장치(KNK-652)가 `v0.2.1`(2026-07-22)로 운영에 배포됐습니다. 그 이전 릴리스에는 켜질 코드 자체가 없었습니다.
- **배선이 apply됐는지** — **충족**: KNK-653(manyak-terraform) 배선을 2026-07-23 적용했습니다. user-data가 Secrets Manager의 `AI_LANGFUSE_PUBLIC_KEY`·`AI_LANGFUSE_SECRET_KEY`·`AI_LANGFUSE_HOST` 3키를 배포 스크립트의 **export로만** compose에 보간합니다. 공용 `.env`에는 기록하지 않습니다.
- **apply의 파급을 확인했는지** — **충족**: user-data(+임베드된 compose) 변경으로 EC2가 교체됐고 외부 백엔드 health와 AI `v0.2.1` health를 확인했습니다.
- **활성화 가드가 릴리스에 실렸는지** — **충족**: 키가 있어도 `LANGFUSE_HOST`가 JP가 아니거나 환경이 `prod`가 아니면 no-op + 오류 로그로 막는 가드가 `v0.2.1`에 포함됐습니다([`5-ai-server.md §5-6`](./5-ai-server.md)). 원칙: **키 주입은 가드가 담긴 릴리스 배포 뒤**여야 합니다 — 관측 그릇(KNK-624)만 실리고 가드가 없는 릴리스는 키만 있으면 켜지기 때문입니다.
- **`LANGFUSE_HOST`가 JP(`https://jp.cloud.langfuse.com`)인지** — **충족**: 운영 AI 기동 로그의 host와 `env=prod`를 확인했습니다. 가드는 JP가 아니거나 값이 누락되면 Langfuse를 켜지 않습니다.
- **직접 입력 장르 임시 관측 정책을 확인했는지** — KNK-669 결정에 따라 Langfuse 활성화는 KNK-621 배포를 기다리지 않습니다. 활성화 시점부터 사전 정의 장르와 직접 입력 장르가 모두 `genre:*` 필터용 라벨로 저장됩니다. 목적은 기본 장르 목록에서 빠진 사용자 수요를 확인하는 것이며, 직접 입력값이 검색 가능해지고 카디널리티가 커지는 점을 수용합니다. KNK-621이 장르 직접 입력을 차단하면 이 예외는 종료됩니다([`6-analytics.md §6-6-12·§6-7`](./6-analytics.md)).
- **채팅 트레이스 장르 태그 제거가 릴리스에 실렸는지** — **충족**: `v0.2.1`에 포함됐습니다. 장르 태그는 스토리 제작 트레이스에만 싣습니다([`5-ai-server.md §5-6`](./5-ai-server.md)).
- §6-7 원문 수집 예외 조건(JP 리전·1년 보존·AI 담당자 한정 접근·prod 전용)이 지켜지는지([`6-analytics.md §6-7`](./6-analytics.md)).

켠 뒤에는 다음을 확인합니다.

- **AI 컨테이너 기동 로그에 `Langfuse 활성 — host=… env=…`이 있는지** — 가드를 통과해 실제로 켜졌다는 유일한 신호입니다. 조건 미충족이면 같은 자리에 비활성 사유가 오류 로그로 남습니다. 실패 격리 때문에 관측이 비어도 요청은 성공하므로, 로그를 보지 않으면 꺼진 것을 알 수 없습니다([`5-ai-server.md §5-6`](./5-ai-server.md)).
- **Langfuse 웹에 트레이스가 유입되는지**(실호출 1건 — 과금 발생, 실행 전 승인).
- **server 컨테이너에는 `AI_LANGFUSE_*`가 없는지** — 배선이 공용 `.env`가 아니라 export로만 넘기는지 확인하는 점검입니다.

### 롤백

| 상황                     | 기준 롤백                                                                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| server 이미지 문제       | ECR의 직전 정상 `<short-sha>` 이미지를 `SERVER_IMAGE_OVERRIDE`로 지정해 `bash /opt/manyak/deploy.sh`를 실행합니다. 배포 스크립트가 이미지를 고정하고 server만 pull/up합니다. |
| AI 이미지 문제           | ECR의 직전 정상 `<short-sha>` 이미지를 `AI_IMAGE_OVERRIDE`로 지정해 `bash /opt/manyak/deploy.sh`를 실행합니다. 배포 스크립트가 OpenAI·Langfuse 키를 다시 읽어 AI에 전달하고 `--wait`로 health를 확인합니다. `/opt/manyak/.env` 수정 뒤 Compose를 직접 실행하면 export-only 키가 비므로 금지합니다. |
| main release 문제        | revert PR 또는 이전 정상 커밋을 release합니다. 단, 이미 실행된 Flyway 마이그레이션은 전진 전용으로 취급합니다.                                                                 |
| DB 마이그레이션 문제     | 보상 마이그레이션 또는 RDS snapshot 복구가 필요합니다. 파괴적 스키마 변경은 배포 직전 snapshot을 남깁니다.                                                                     |
| Terraform user-data 문제 | Terraform revert apply가 EC2 교체를 유발할 수 있습니다. 다운타임 창을 잡고 plan을 먼저 확인합니다.                                                                             |

ECR은 태그가 붙은 이미지를 레포지토리별 최신 10개만 보존합니다. 보존 범위를 벗어난 버전으로 되돌릴 때는 해당 커밋을 다시 release해 새 이미지를 만들거나 이미지를 재푸시해야 합니다.

## 7-10. Jira·PR 추적 근거

### 운영 AWS 배포 기반

| Jira 키 | PR                                                                       | 배포상 의미                                            |
| ------- | ------------------------------------------------------------------------ | ------------------------------------------------------ |
| KNK-234 | [manyak-server #44](https://github.com/KIM-N-KANG/manyak-server/pull/44) | 컨테이너 healthcheck, prod profile, 아키텍처 문서      |
| KNK-235 | [manyak-server #45](https://github.com/KIM-N-KANG/manyak-server/pull/45) | Terraform bootstrap, S3 remote state 토대              |
| KNK-236 | [manyak-server #46](https://github.com/KIM-N-KANG/manyak-server/pull/46) | ECR, GitHub OIDC, dev=GHCR/main=ECR                    |
| KNK-237 | [manyak-server #47](https://github.com/KIM-N-KANG/manyak-server/pull/47) | VPC 3계층 네트워크                                     |
| KNK-238 | [manyak-server #48](https://github.com/KIM-N-KANG/manyak-server/pull/48) | SG 체인, EC2 IAM, SSH 미개방                           |
| KNK-239 | [manyak-server #50](https://github.com/KIM-N-KANG/manyak-server/pull/50) | RDS PostgreSQL, ElastiCache Redis                      |
| KNK-240 | [manyak-server #51](https://github.com/KIM-N-KANG/manyak-server/pull/51) | EC2, Docker Compose, ALB, ACM, Cloudflare DNS          |
| KNK-241 | [manyak-server #52](https://github.com/KIM-N-KANG/manyak-server/pull/52) | Secrets Manager, `deploy.sh`, SSM deploy, health smoke |

### 운영 보강과 장애 대응

| Jira 키 | PR                                                                           | 배포상 의미                                       |
| ------- | ---------------------------------------------------------------------------- | ------------------------------------------------- |
| KNK-250 | [manyak-server #54](https://github.com/KIM-N-KANG/manyak-server/pull/54)     | server/AI Sentry DSN 분리, analytics pepper 배선  |
| KNK-253 | [manyak-server #56](https://github.com/KIM-N-KANG/manyak-server/pull/56)     | Cloudflare provider `content` 인자 전환           |
| KNK-258 | [manyak-server #59](https://github.com/KIM-N-KANG/manyak-server/pull/59)     | GitHub OIDC owner 대소문자 정정                   |
| KNK-260 | [manyak-server #60](https://github.com/KIM-N-KANG/manyak-server/pull/60)     | 운영 AI 컨테이너 배선, AI 전용 OIDC role, `flock` |
| KNK-268 | [manyak-server #64](https://github.com/KIM-N-KANG/manyak-server/pull/64)     | AI Sentry environment 주입                        |
| KNK-284 | [manyak-server #75](https://github.com/KIM-N-KANG/manyak-server/pull/75)     | 운영 ElastiCache endpoint 주입                    |
| KNK-294 | [manyak-server #77](https://github.com/KIM-N-KANG/manyak-server/pull/77)     | 운영 CORS 허용 origin 주입                        |
| KNK-296 | [manyak-server #79](https://github.com/KIM-N-KANG/manyak-server/pull/79)     | 운영 Terraform을 `manyak-terraform`으로 분리      |
| KNK-321 | [manyak-server #81](https://github.com/KIM-N-KANG/manyak-server/pull/81)     | 운영 Swagger·OpenAPI 비공개화                     |
| KNK-287 | [manyak-terraform #2](https://github.com/KIM-N-KANG/manyak-terraform/pull/2) | 운영 인증 env 주입                                |
| KNK-359 | [manyak-terraform #3](https://github.com/KIM-N-KANG/manyak-terraform/pull/3) | DB 비밀번호 로테이션 후 `.env` 자동 재동기화      |

### 서비스 이미지와 통합 실행

| Jira 키 | PR                                                                     | 배포상 의미                              |
| ------- | ---------------------------------------------------------------------- | ---------------------------------------- |
| KNK-120 | [manyak-web #1](https://github.com/KIM-N-KANG/manyak-web/pull/1)       | web Dockerfile, GHCR dev workflow        |
| KNK-121 | [manyak-ai #3](https://github.com/KIM-N-KANG/manyak-ai/pull/3)         | AI Dockerfile 검증, GHCR dev workflow    |
| KNK-122 | [manyak-infra #1](https://github.com/KIM-N-KANG/manyak-infra/pull/1)   | GHCR dev 이미지 기반 통합 Compose        |
| KNK-130 | [manyak-server #7](https://github.com/KIM-N-KANG/manyak-server/pull/7) | server multi-arch GHCR                   |
| KNK-131 | [manyak-web #2](https://github.com/KIM-N-KANG/manyak-web/pull/2)       | web multi-arch GHCR                      |
| KNK-132 | [manyak-ai #5](https://github.com/KIM-N-KANG/manyak-ai/pull/5)         | AI multi-arch GHCR                       |
| KNK-133 | [manyak-infra #2](https://github.com/KIM-N-KANG/manyak-infra/pull/2)   | Apple Silicon platform workaround 제거   |
| KNK-151 | [manyak-infra #5](https://github.com/KIM-N-KANG/manyak-infra/pull/5)   | web `API_BASE_URL` 주입                  |
| KNK-184 | [manyak-infra #6](https://github.com/KIM-N-KANG/manyak-infra/pull/6)   | server AI stub 비활성화                  |
| KNK-201 | [manyak-infra #7](https://github.com/KIM-N-KANG/manyak-infra/pull/7)   | Slack webhook env 반영                   |
| KNK-214 | [manyak-infra #8](https://github.com/KIM-N-KANG/manyak-infra/pull/8)   | AI 환경변수 Upstage에서 DeepSeek로 전환  |
| KNK-297 | [manyak-infra #9](https://github.com/KIM-N-KANG/manyak-infra/pull/9)   | Redis, JWT, Google, analytics env 최신화 |

### 릴리스와 lockstep

| Jira 키 | PR                                                                       | 배포상 의미                                          |
| ------- | ------------------------------------------------------------------------ | ---------------------------------------------------- |
| KNK-255 | [manyak-server #58](https://github.com/KIM-N-KANG/manyak-server/pull/58) | server v0.1.0 첫 운영 배포                           |
| KNK-264 | [manyak-server #62](https://github.com/KIM-N-KANG/manyak-server/pull/62) | server v0.1.1, UUID 계약과 프론트 lockstep           |
| KNK-270 | [manyak-server #65](https://github.com/KIM-N-KANG/manyak-server/pull/65) | server v0.1.2, AI correlation header와 AI Sentry env |
| KNK-347 | [manyak-server #82](https://github.com/KIM-N-KANG/manyak-server/pull/82) | server v0.1.3, 인증 스택과 운영 env 선행 조건        |
| KNK-352 | [manyak-server #84](https://github.com/KIM-N-KANG/manyak-server/pull/84) | server v0.1.4, 운영 springdoc 404 보강               |
| KNK-259 | [manyak-ai #28](https://github.com/KIM-N-KANG/manyak-ai/pull/28)         | AI 운영 배포 workflow                                |
| KNK-293 | [manyak-ai #33](https://github.com/KIM-N-KANG/manyak-ai/pull/33)         | AI v0.1.0 운영 배포                                  |
| KNK-261 | [manyak-web #24](https://github.com/KIM-N-KANG/manyak-web/pull/24)       | web v0.1.0 release image                             |
| KNK-279 | [manyak-web #29](https://github.com/KIM-N-KANG/manyak-web/pull/29)       | web v0.1.1 release image                             |
| KNK-308 | [manyak-web #33](https://github.com/KIM-N-KANG/manyak-web/pull/33)       | web v0.1.2 release image                             |
| KNK-341 | [manyak-web #38](https://github.com/KIM-N-KANG/manyak-web/pull/38)       | web v0.1.3 release image                             |

### 현재 열린 PR 중 배포 영향 가능 항목

2026-07-03 현재 확인한 기준 레포지토리(`knk-harness`, `manyak-web`, `manyak-server`, `manyak-ai`, `manyak-terraform`, `manyak-infra`)에는 열린 PR이 없습니다.

### 최근 반영 완료된 PR

| Jira 키 | PR                                                                   | 반영 상태          | 배포상 의미                                                                                                                    |
| ------- | -------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| KNK-370 | [manyak-web #42](https://github.com/KIM-N-KANG/manyak-web/pull/42)   | Merged, 2026-07-03 | 공통 용어·네이밍·컴포넌트 구조 정리와 orval 재생성 결과가 `manyak-web` dev에 반영되었습니다. 직접 인프라 배포 영향은 없습니다. |
| KNK-371 | [manyak-ai #38](https://github.com/KIM-N-KANG/manyak-ai/pull/38)     | Merged, 2026-07-03 | AI 와이어 계약 리네임(`storyline`, `additional_info`)과 용어 정렬이 `manyak-ai` dev에 반영되었습니다.                          |
| KNK-362 | [knk-harness #16](https://github.com/KIM-N-KANG/knk-harness/pull/16) | Merged, 2026-07-03 | 분석·프론트 문서의 `tag`, `채팅 화면`, `AI 출력` 명명이 하네스 dev에 반영되었습니다.                                           |

## 7-11. 미정·주의 항목

| 항목                      | 상태      | 처리 기준                                                                                                                                                                           |
| ------------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Web 운영 호스팅           | 미정      | 현재 Terraform에는 web hosting, CDN, web container 배포가 정의되어 있지 않습니다. 호스팅 플랫폼이 정해지면 배포 절차와 도메인 소유를 추가합니다.                                    |
| Android 배포 파이프라인   | 미정      | `manyak-android`는 PR·push CI(`./gradlew check`·`assembleDebug`)만 코드로 정의합니다. Play Store 배포, 앱 서명, release 빌드·AAB, 내부 테스트 트랙, 운영 배포·롤백 방식은 결정·구현 후 §7-2·§7-5와 함께 갱신합니다. |
| Terraform apply 자동화    | 미정      | 현재 `manyak-terraform`에는 GitHub Actions apply workflow가 없습니다. 운영 apply는 수동 절차와 plan 리뷰를 기준으로 합니다.                                                         |
| Web Sentry DSN 주입       | 부분 해결 | Vercel 호스팅 경로는 환경 변수 `NEXT_PUBLIC_SENTRY_DSN`으로 활성입니다(§7-5, KNK-714). 다만 GHCR release 이미지 빌드에는 여전히 build arg가 없어, 컨테이너 배포를 쓰게 되면 주입 방식을 정해야 합니다. |
| 단일 EC2·단일 AZ compute  | MVP       | EC2와 RDS는 MVP 단일 AZ 중심입니다. HA 요구가 생기면 ECS/Fargate 또는 multi-AZ 설계를 별도 버전으로 정의합니다.                                                                     |
| Cloudflare proxy/WAF      | 미적용    | `api.manyak.app` 레코드는 `proxied=false`입니다. CDN/WAF 요구가 생기면 edge 정책을 별도 정의합니다.                                                                                 |
| Redis health              | 확인 필요 | Redis endpoint는 주입하지만 기준 server 코드는 운영 Redis health를 비활성화합니다. Redis를 배포 게이트에 포함할지는 후속 결정이 필요합니다.                                         |
| Analytics pepper env 명칭 | 전환기    | 코드의 우선 키는 `MANYAK_ANALYTICS_DEVICE_ID_PEPPER`, Terraform·infra 주입 키는 fallback인 `MANYAK_ANALYTICS_ANONYMOUS_ID_PEPPER`입니다. 후속 정렬 시 양쪽을 함께 바꿉니다.         |
| DB schema rollback        | 전진 전용 | Flyway 마이그레이션은 전진 전용입니다. 파괴적 변경 전에는 RDS snapshot과 lockstep 배포 계획이 필요합니다.                                                                           |

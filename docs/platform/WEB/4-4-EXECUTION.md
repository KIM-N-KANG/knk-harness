# 4-4 실행: 웹

기준: [상태 관리](4-3-STATE-MANAGEMENT.md).

<br>

### 4-4-1 이미지

뷰어는 원본 비율로 contain 영역을 계산해 그림 위 탭과 배경 탭을 구분한다. touch-action=none 아래 포인터로 확대와 이동을 처리한다. 두 탭 300ms와 30px, 이동 8px 문턱, 더블 탭 2.5배와 1~5배 범위 및 영역 밖 이동 제한을 사용한다. 테스트 이미지는 srcset 밀도 처리로 크기가 0이 되지 않도록 60px 이미지를 쓴다.

Next 최적화 허용 호스트는 Google lh3.googleusercontent.com, 운영과 개발 API의 /profile-presets/, 운영과 개발 CDN이다. 모델 출력 이미지는 이 허용만으로 신뢰하지 않고 HTTPS, 정확한 CDN과 도메인별 경로 검사를 별도로 거친다. 저장 마커의 파싱과 실패 처리는 CHAT 계약을 따른다.

<br>

### 4-4-2 관측

공용 발화 경로가 screen_name을 보완하고 Sentry breadcrumb 뒤 활성화한 Amplitude로 전달한다. 운영은 기본 활성, 다른 환경은 기본 콘솔 출력이다. Amplitude device ID를 오류 관측과 API 헤더에 연결한다. 루트 오류는 Sentry에 보고하고 자유 입력 원문과 토큰은 제외한다.

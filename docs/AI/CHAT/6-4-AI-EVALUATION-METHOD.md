# 6-4 AI 평가 방법

채팅 AI의 성능, 시간과 비용을 평가하는 데이터와 채점 방법을 정한다.

<br>

### 6-4-1 채팅 응답 생성

평가 데이터와 채점 장치는 `manyak-ai/evaluation/`에 있다. ([6-5-1 채팅 응답 생성](6-5-AI-EVALUATION-IMPLEMENTATION.md#6-5-1-채팅-응답-생성))

<br>

**1. 평가 범위**

| 항목 | 내용 |
|---|---|
| 평가 대상 | configuration(프롬프트 버전, 모델, 추론 강도)의 출력 |
| 평가 단위 | 채팅 1개의 마지막 AI 답변 1개 |
| 생성 입력 | 1~N−1턴 대화<br>N번째 사용자 입력<br>응답 직전의 생성 설정 |
| 실행 경로 | 기준 AI 레포의 프롬프트 조립, 모델 호출과 출력 파서를 그대로 사용<br>사건과 엔딩 판정, 선택지, 이미지 호출 제외 |
| 생성 설정 | 프롬프트 버전, 모델과 추론 강도는 6-3-1의 configuration을 따름 |
| 채점 대상 | 생성한 답변을 붙인 N턴 대화 전체 |

<br>

**2. 데이터셋 샘플링**

| 제외 조건 |
|---|
| 일반 제작 스토리의 채팅 |
| 삭제된 채팅이나 스토리 |
| 제외 요청이 있는 채팅 |
| 1~2턴 채팅 |
| 마지막 턴 이후 7일이 지나지 않은 채팅 |
| 채점기 개발에 쓴 채팅 |
| 개발자 채팅 |
| 엔딩에 도달한 채팅 |
| 스토리 태그에 성인·가학 태그가 있는 채팅 |
| 생성 입력이 남아 있지 않거나 손상된 레거시 채팅(보존 기한이 지난 채팅 포함) |
| 안전성 문제가 있는 채팅 |
| 서비스 취지에서 벗어난 입력(탈옥, 현실 정치 등)이 있는 채팅 |
| 마지막 사용자 입력이 대화를 끝내는 채팅 |

<br>

**3. 평가 데이터**

| 항목 | train | test |
|---|---|---|
| 용도 | 프롬프트를 고칠 때 사례 확인 | grid search와 configuration 비교의 점수 |
| 위치 | `evaluation/datasets/train/` | `evaluation/datasets/test/` |
| 규모 | test에 넣지 않은 운영 수집본<br>계속 추가 | 60개 |
| 사례 열람 | 허용 | 점수와 집계만 확인<br>사례 원문은 보지 않음 |
| 변경 | 추가 가능 | 고정<br>입력 해시로 변경 여부 검사<br>새로 뽑으면 새 버전으로 만들고 이전 버전 결과와 비교하지 않음 |

<details>
<summary><b>test 데이터셋 분포</b></summary>

<table>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "대화 길이 (%)"
    x-axis ["3~5턴", "6~19턴", "20턴 이상"]
    y-axis 0 --> 100
    bar [50, 30, 20]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "유저 (%)"
    x-axis ["게스트", "회원"]
    y-axis 0 --> 100
    bar [48, 52]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "스토리 종류 (%)"
    x-axis ["오리지널", "간편 제작"]
    y-axis 0 --> 100
    bar [38, 62]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 (%)"
    x-axis ["선택지", "직접 입력", "선택지 수정"]
    y-axis 0 --> 100
    bar [60, 38, 2]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 156, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "리텐션 (%)"
    x-axis ["재방문 없음"]
    y-axis 0 --> 100
    bar [100]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 324, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "마지막 입력 길이 (%)"
    x-axis ["1~20자", "21~50자", "51~100자", "101자+"]
    y-axis 0 --> 100
    bar [12, 20, 57, 12]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 228, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "대표 장르 (%)"
    x-axis ["로맨스", "탈출물", "현대 판타지", "로맨스 판타지", "군대 로맨스", "학원", "기타"]
    y-axis 0 --> 100
    bar [33, 27, 8, 7, 7, 3, 15]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 204, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "스토리 묶음 (%)"
    x-axis ["간편 제작", "0호선", "그건 반칙이지 말입니다", "나만 기억하는 멸망", "백룸: 미귀환", "대공님, 계약 위반입니다"]
    y-axis 0 --> 100
    bar [62, 25, 7, 3, 2, 2]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 · 3~5턴 (%)"
    x-axis ["선택지", "직접 입력", "선택지 수정"]
    y-axis 0 --> 100
    bar [33, 63, 3]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 · 6~19턴 (%)"
    x-axis ["선택지", "직접 입력"]
    y-axis 0 --> 100
    bar [89, 11]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 · 20턴 이상 (%)"
    x-axis ["선택지", "직접 입력"]
    y-axis 0 --> 100
    bar [83, 17]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 324, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 길이 · 직접 입력 (%)"
    x-axis ["1~20자", "21~50자", "51~100자", "101자+"]
    y-axis 0 --> 100
    bar [30, 26, 35, 9]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 길이 · 선택지 (%)"
    x-axis ["21~50자", "51~100자", "101자+"]
    y-axis 0 --> 100
    bar [17, 69, 14]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 204, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "장르 · 3~5턴 (%)"
    x-axis ["로맨스", "탈출물", "현대 판타지", "로맨스 판타지", "군대 로맨스", "기타"]
    y-axis 0 --> 100
    bar [37, 13, 13, 7, 13, 17]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 180, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "장르 · 6~19턴 (%)"
    x-axis ["로맨스", "탈출물", "현대 판타지", "학원", "기타"]
    y-axis 0 --> 100
    bar [28, 50, 6, 6, 11]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 180, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "장르 · 20턴 이상 (%)"
    x-axis ["로맨스", "탈출물", "로맨스 판타지", "학원", "기타"]
    y-axis 0 --> 100
    bar [33, 25, 17, 8, 17]
```

</td>
</tr>
</table>

</details>

<br>

**4. 평가 모델**

| 항목 | 내용 |
|---|---|
| 모델 | `gpt-5.6-sol`, 추론 강도 `medium` |
| 생성 모델과의 관계 | 생성 모델과 다른 모델 사용 |
| 채점 프롬프트 | chat-judge v0.2 고정본<br>`evaluation/` 안에 보관 |
| 채점 질문 | 마지막 정상 AI 응답까지 읽은 사용자가 다음 행동이나 대사를 이어가고 싶은 정도<br>완결된 이야기는 처음부터 결말까지의 재미와 여운 |
| 채점 입력 | `sample_id`, `prologue`, `turns`<br>태그와 인물 정보는 전달하지 않음 |
| 출력 | 0~100점 정수 1개 |
| 호출 방식 | 대화 1개당 별도 호출<br>다른 답변과 점수는 전달하지 않음 |
| 반복 | 답변당 독립 채점 3회 |
| 학습 | 평가 모델을 학습하지 않음<br>채점 프롬프트만 개선 |
| 사람 평가와의 비교 | 사람이 두 채팅 중 고른 쪽에 더 높은 점수를 준 쌍의 비율<br>v0.2는 72쌍에서 6회 평균 70.4% |

<br>

**5. 평가 지표**

채팅 응답 실패율과 본문 재생성률은 오프라인 평가에서 계산하지 않고 운영 기록으로 확인한다. ([2-2 운영 요구사항](2-2-OPERATION-REQUIREMENTS.md), [7-3 관측](7-3-OBSERVABILITY.md))

| 지표 | 계산 방법 | 2-2 목표 |
|---|---|---|
| 채팅 재미 점수 | 답변별 채점 3회의 평균을 구한 뒤 데이터셋 전체 입력의 평균 | — |
| 턴당 본문 생성 비용 | 입력별 최초 호출과 재생성의 API 비용 `cost_usd`를 합산한 뒤 평균<br>호출 비용이 하나라도 미측정이면 해당 입력의 총비용은 평균에서 빼고 개수를 함께 기록 | 목표 $0.01 이하, 상한 $0.03 |
| 본문 생성 시간 | 입력별 최초 요청 시작부터 재생성을 포함한 최종 종료까지의 p95 | 기록만 함<br>채팅 응답 완료 시간은 운영 기록으로 판정 |

<br>

**6. 반복과 실패 처리**

| 항목 | 처리 |
|---|---|
| 채점 변동 | 같은 답변의 채점 3회로 채점 점수의 변동만 확인<br>답변을 다시 생성했을 때의 편차는 측정하지 않음 |
| 빈 본문, 잘림 종료 | 같은 입력으로 1회 재생성해 채점<br>configuration별 재생성 횟수 기록<br>재생성 후에도 같으면 해당 입력은 실패로 처리 |
| 실패 | 재시도 후에도 생성이나 채점이 실패하면 해당 configuration의 평가 전체를 실패로 처리<br>성공한 입력만 모아 평균을 내지 않음 |
| 비교 조건 | 데이터셋, 채점 프롬프트, 채점 입력과 반복 횟수가 같은 결과끼리만 비교 |

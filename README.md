# 달리기 자세 라벨링 툴 v0.5.3

본 버전은 고객 피드백을 반영하여 **평균값 중심 MotionMetrix 입력**, **자동 계산값 처리**, **Skeleton 평균값 / MotionMetrix 값 최종 비교표**를 강화한 버전입니다.

## v0.5.3 반영 사항

- 촬영 Wizard에서 MotionMetrix 입력 영역을 제거했습니다.
- MotionMetrix 입력은 측면/후면/종합 입력 탭에서 별도로 진행합니다.
- 오버스트라이드, 수직진폭, 케이던스, 지면접촉시간은 좌우 세부값 대신 전체 평균값 중심으로 입력합니다.
- 고관절 ROM은 좌우 굴곡/신전 입력값을 기준으로 자동 계산합니다.
- 슬관절 ROM은 착지시 굴곡각/유각기 최대굴곡 입력값을 기준으로 자동 계산합니다.
- 최종 비교 화면에서 항목별 `Skeleton 평균값 / MotionMetrix 값 / 차이값 / 비교 상태`를 한눈에 확인할 수 있습니다.
- Export 시 고객 확인용 `final_comparison_summary.csv`, `final_comparison_summary.xlsx`를 생성합니다.
- 기존 모델링용 상세 CSV(`frame_metrics.csv`, `gait_events.csv`, `second_summary.csv`, `clip_summary.csv`)는 유지합니다.

## 1. 툴의 목적

본 Streamlit 앱은 정형외과 전문의 음성 소견 기반 달리기 자세 교정 AI 프로젝트의 2차 라벨링 툴 개발 산출물입니다.

2차 단계에서는 고객이 MotionMetrix 결과값을 직접 입력하고, 같은 세션의 측면/후면 영상과 Skeleton 평균 측정값을 함께 저장합니다. 3차에서는 이 데이터를 기반으로 스마트폰 Skeleton feature로 MotionMetrix 기준 값을 예측하는 보정/학습 구조로 확장합니다.

```text
세션 정보 입력
→ 후면/측면 영상 업로드
→ Skeleton Overlay 및 평균 측정값 생성
→ MotionMetrix 평균값 직접 입력
→ 최종 비교표 확인
→ Export
```

최종 학습 정답값은 Skeleton Preview 값이 아니라 고객이 직접 입력한 MotionMetrix 값입니다.

## 2. 고객 기준 사용 순서

```text
1. 세션 정보 입력
2. 후면 정지/달리기 영상 업로드
3. 측면 정지/달리기 영상 업로드
4. Skeleton 결과 영상 및 평균값 생성
5. 측면/후면/종합 MotionMetrix 평균값 입력
6. 최종 비교 화면에서 Skeleton 평균값과 MotionMetrix 값 확인
7. Export 생성
8. final_comparison_summary.xlsx 우선 확인
```

## 3. 고객이 먼저 확인할 파일

| 파일 | 용도 |
|---|---|
| `final_comparison_summary.xlsx` | 고객 확인용 1순위 파일. Skeleton 평균값과 MotionMetrix 값이 같은 행에 정리됩니다. |
| `final_comparison_summary.csv` | 위 Excel 파일과 동일한 CSV 버전입니다. |
| `training_dataset_wide.csv` | 세션별 입력값 전체를 넓은 형태로 저장한 모델링용 CSV입니다. |
| `frame_metrics.csv` | 프레임/시점별 Skeleton feature입니다. |
| `gait_events.csv` | 착지 시점, 접촉시간, 착지 각도 등 이벤트 기반 feature입니다. |
| `second_summary.csv` | 초별 요약 feature입니다. |
| `clip_summary.csv` | 영상 단위 Skeleton 평균 feature와 MotionMetrix target 연결용 파일입니다. |

## 4. 최종 비교표 구조

`final_comparison_summary.xlsx`는 아래 형태로 구성됩니다.

| 구분 | 측정 항목 | Skeleton 평균값 | Skeleton 단위 | MotionMetrix 값 | MotionMetrix 단위 | 차이값 | 비교 상태 |
|---|---|---:|---|---:|---|---:|---|
| 측면 | 척추기울기 | 6.0 | deg | 7.0 | deg | -1.0 | 비교 가능 |
| 측면 | 오버스트라이드 평균 | 120 | px | 180 | mm |  | 단위 상이 또는 수동 기준 |
| 측면 | 지면접촉시간 평균 | 218 | ms | 225 | ms | -7 | 비교 가능 |

색상 기준:

- 파란색 계열: Skeleton 평균값
- 주황색 계열: MotionMetrix 입력값
- 초록색: 비교 가능
- 노란색: 입력 필요 또는 단위 상이

## 5. 평균값 중심 입력 정책

| 항목 | 입력 방식 |
|---|---|
| 오버스트라이드 | 전체 평균값만 입력 |
| 수직진폭 | 전체 평균값만 입력, 단위 mm |
| 케이던스 | 평균/표준 케이던스만 입력 |
| 지면접촉시간 | 좌우 구분 없이 평균값만 입력 |
| 고관절 ROM | 좌우 굴곡/신전 입력 → ROM, 전체 평균, 좌우차이 자동 계산 |
| 슬관절 ROM | 좌우 착지시 굴곡각/유각기 최대굴곡 입력 → ROM, 전체 평균, 좌우차이 자동 계산 |
| 착지 타입 | MotionMetrix 비교값이 아니라 별도 수동 라벨로 저장 |
| Running Economy / Running Type | MotionMetrix 직접 입력값이며 3차 학습 target으로 사용 |

## 6. Windows 권장 실행 방법

Windows에서는 제공된 배치 파일 사용을 권장합니다.

```bat
setup_windows.bat
run_windows.bat
```

직접 실행해야 하는 경우:

```bat
rmdir /s /q .venv
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Python 3.11이 없다면 `py -3.12`로 변경해서 실행합니다.

## 7. 주의사항

- Skeleton 측정값은 MotionMetrix 정답값이 아니라 참고 feature입니다.
- px 단위 Skeleton 값과 mm 단위 MotionMetrix 값은 보정 전 직접 차이값을 계산하지 않습니다.
- Streamlit Cloud는 테스트용 경량 환경입니다. 생성한 데이터는 Export 또는 백업 ZIP으로 자주 다운로드하세요.
- 실제 고객 영상, 개인정보, 실제 MotionMetrix 원본 파일은 GitHub에 올리지 마세요.

## 8. 주요 폴더

```text
app.py
src/
data/metric_definitions/
sample_data/
docs/
exports/
```

`data/sessions/`, `exports/`, `backups/`는 실행 중 생성되는 데이터 폴더입니다.

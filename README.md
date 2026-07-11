# 달리기 자세 라벨링 툴 v0.5.4

본 버전은 고객 피드백을 반영하여 **MediaPipe world landmark 기반 Skeleton 평균값 보정**, **후면 MotionMetrix 입력 제거**, **Shank Angle 위치 정리**, **고관절 ROM 합산 계산**, **Skeleton 평균값 / MotionMetrix 값 최종 비교표**를 강화한 버전입니다.

## v0.5.4 반영 사항

- 정강이 각도(Shank Angle)를 측면 입력의 슬관절 운동범위 다음 위치로 정리했습니다.
- 후면 지표는 MotionMetrix 직접 입력값이 없다는 피드백을 반영하여 입력 영역을 제거하고 Skeleton-only 참고값으로 관리합니다.
- MediaPipe `pose_world_landmarks`가 제공되는 경우 각도/ROM 계열 계산에 world landmark 기반 값을 우선 사용합니다.
- Overstride, Step Width, Vertical Oscillation은 world landmark 기반 mm 추정값을 함께 생성합니다.
- 고관절 ROM은 고객 기준에 맞춰 `abs(굴곡) + abs(신전)`으로 계산합니다. 예: 굴곡 20도 + 신전 20도 = ROM 40도.
- 진행 방향(왼쪽→오른쪽 / 오른쪽→왼쪽) 옵션을 추가하여 Forward Lean, Overstride, Shank Angle 부호 보정에 사용합니다.
- 수동 지면선 y좌표와 접촉 허용 오차 옵션을 추가하여 착지/접촉 이벤트 판별을 보정할 수 있게 했습니다.
- 최종 비교표에 `Skeleton 계산 방식` 컬럼을 추가했습니다.
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
   - 진행 방향, FPS, 필요 시 수동 지면선/접촉 허용 오차 입력
2. 후면 정지/달리기 영상 업로드
3. 측면 정지/달리기 영상 업로드
4. Skeleton 결과 영상 및 평균값 생성
5. 측면/종합 MotionMetrix 평균값 입력
6. 최종 비교 화면에서 Skeleton 평균값과 MotionMetrix 값 확인
7. Export 생성
8. final_comparison_summary.xlsx 우선 확인
```

후면 지표는 고객 피드백에 따라 MotionMetrix 입력값 없이 Skeleton-only 참고값으로 표시합니다.

## 3. 고객이 먼저 확인할 파일

| 파일 | 용도 |
|---|---|
| `final_comparison_summary.xlsx` | 고객 확인용 1순위 파일. Skeleton 평균값과 MotionMetrix 값이 같은 행에 정리됩니다. |
| `final_comparison_summary.csv` | 위 Excel 파일과 동일한 CSV 버전입니다. |
| `training_dataset_wide.csv` | 세션별 입력값 전체를 넓은 형태로 저장한 모델링용 CSV입니다. |
| `frame_metrics.csv` | 프레임/시점별 Skeleton feature입니다. image 좌표와 world 좌표가 함께 저장됩니다. |
| `gait_events.csv` | 착지 시점, 접촉시간, 착지 각도 등 이벤트 기반 feature입니다. |
| `second_summary.csv` | 초별 요약 feature입니다. |
| `clip_summary.csv` | 영상 단위 Skeleton 평균 feature와 MotionMetrix target 연결용 파일입니다. |

## 4. 최종 비교표 구조

`final_comparison_summary.xlsx`는 아래 형태로 구성됩니다.

| 구분 | 측정 항목 | Skeleton 평균값 | Skeleton 단위 | MotionMetrix 값 | MotionMetrix 단위 | 차이값 | 비교 상태 | Skeleton 계산 방식 |
|---|---|---:|---|---:|---|---:|---|---|
| 측면 | 척추기울기 | 6.0 | deg | 7.0 | deg | -1.0 | 비교 가능 | MediaPipe world/image landmark |
| 측면 | 오버스트라이드 평균 | 120 | mm | 180 | mm | -60 | 비교 가능(추정값 주의) | MediaPipe world landmark estimate |
| 후면 | 골반낙하 평균 | 3.2 | deg |  |  |  | Skeleton-only / 후면 MotionMetrix 없음 | rear skeleton-only |

색상 기준:

- 파란색 계열: Skeleton 평균값
- 주황색 계열: MotionMetrix 입력값
- 초록색: 비교 가능
- 노란색: 추정값 주의, 입력 필요, Skeleton-only 등 확인 필요 상태

## 5. 평균값 중심 입력 정책

| 항목 | 입력 방식 |
|---|---|
| 오버스트라이드 | 전체 평균값만 입력 |
| 수직진폭 | 전체 평균값만 입력, 단위 mm |
| 케이던스 | 평균/표준 케이던스만 입력 |
| 지면접촉시간 | 좌우 구분 없이 평균값만 입력 |
| 고관절 ROM | 좌우 굴곡/신전 입력 → ROM, 전체 평균, 좌우차이 자동 계산. ROM = abs(굴곡) + abs(신전) |
| 슬관절 ROM | 좌우 착지시 굴곡각/유각기 최대굴곡 입력 → ROM, 전체 평균, 좌우차이 자동 계산 |
| 착지 타입 | MotionMetrix 비교값이 아니라 별도 수동 라벨로 저장 |
| Running Economy / Running Type | MotionMetrix 직접 입력값이며 3차 학습 target으로 사용 |

## 6. MediaPipe world landmark 적용 주의사항

MediaPipe는 world landmark 3D 좌표를 제공하므로 각도/ROM 계열은 기존 image pixel 기반 계산보다 MotionMetrix 정의에 더 가깝게 맞출 수 있습니다. 다만 MotionMetrix는 depth camera와 treadmill calibration 기반의 계측 시스템이므로, MediaPipe world 좌표를 MotionMetrix와 완전히 동일한 계측값으로 보지는 않습니다.

따라서 최종 비교표에서 `비교 가능(추정값 주의)`로 표시되는 항목은 수치 비교는 가능하지만, 3차 보정 학습 대상이라는 전제를 유지합니다.

## 7. Windows 권장 실행 방법

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

## 8. 주의사항

- Skeleton 측정값은 MotionMetrix 정답값이 아니라 참고 feature입니다.
- Braking Force, Running Economy, Running Type은 Skeleton 직접 계산값이 아니라 MotionMetrix 입력값을 3차 학습 target으로 사용합니다.
- Streamlit Cloud는 테스트용 경량 환경입니다. 생성한 데이터는 Export 또는 백업 ZIP으로 자주 다운로드하세요.
- 실제 고객 영상, 개인정보, 실제 MotionMetrix 원본 파일은 GitHub에 올리지 마세요.

## 9. 주요 폴더

```text
app.py
src/
data/metric_definitions/
sample_data/
docs/
exports/
```

`data/sessions/`, `exports/`, `backups/`는 실행 중 생성되는 데이터 폴더입니다.

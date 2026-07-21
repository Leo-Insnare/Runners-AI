# 달리기 자세 라벨링 툴 v0.5.11

## v0.5.11 업데이트 요약

- Shank Angle은 raw touchdown 값 우선 사용, baseline offset이 과도하면 보정 제외
- Cadence는 side/rear best-source에 더해 짧은 클립 edge compensation 적용
- Contact Time은 저FPS 영상에서 toe-off plateau endpoint를 보강
- Overstride는 visible-side 및 robust median 대표값으로 과대 이상치 완화
- Vertical Displacement/Step Separation은 수동 mm/px scale 입력 시 high confidence로 표시
- Hip/Thigh/Knee ROM은 raw max 대신 neutral-relative 및 percentile 기반으로 안정화
- 최종 비교표에 raw/audit 값, adjusted 값, selected 값 선택 사유를 추가


- Cadence는 후방/측방 이벤트 품질을 비교해 rear 또는 side 중 best-source를 자동 선택합니다.
- Contact Time은 저FPS 영상에서 toe-off가 1프레임 빨리 잡히는 문제를 완화하고, 실제 영상 FPS 기준으로 산출합니다.
- Vertical Displacement는 전체 클립 max-min이 아니라 보행 cycle별 pelvis vertical range의 median을 사용합니다.
- Overstride는 이벤트별 이상치 영향을 줄이도록 median/trimmed mean 기반 robust 값을 사용합니다.
- Knee Flexion @ touch-down은 contact window 내 가장 펴진 무릎 프레임을 사용하여 착지 직후 과대 산출을 줄입니다.
- Hip/Thigh ROM은 raw max/min 대신 robust percentile 기반으로 산출합니다.
- 최종 비교표는 10% 기준과 지표별 절대 허용오차를 함께 사용해 Forward Lean/Shank Angle처럼 작은 각도값의 과대 퍼센트 오류를 줄입니다.


## v0.5.11 업데이트 요약

- 분석 FPS는 업로드 영상의 실제 메타데이터 FPS를 자동 사용합니다.
- UI의 FPS 선택은 계산용이 아니라 결과 영상 출력/용량 조절용으로 변경했습니다.
- 최종 비교표에 `차이율(%)`, `10% 이내 여부`, `문제 유형`, 실제 FPS, 이벤트 수, 스케일 신뢰도 컬럼을 추가했습니다.
- Cadence / Contact Time / touch-down 기반 항목의 이벤트 검출 보조 로직을 보완했습니다.
- Contact Time은 접촉 plateau 구간을 포함하도록 보정해 1프레임 접촉으로 과소 산출되는 문제를 완화했습니다.
- Max Thigh Extension은 MotionMetrix 입력 부호가 양수/음수 모두 들어올 수 있어 10% 판정은 magnitude 기준으로 비교합니다.
- Vertical Displacement / Step Separation 등 거리 계열에는 scale source/confidence를 표시합니다.
- gait_events CSV에 event별 overstride raw/estimate 값을 포함해 debug package만으로 원인 추적이 가능하도록 보완했습니다.


본 버전은 v0.5.4~v0.5.6의 UI 흐름은 유지하면서, 후방/측방 Skeleton raw data와 최종 비교표의 연결성을 강화한 검증용 보정 버전입니다.

## v0.5.11 핵심 반영 사항


- 후방/측방 Skeleton 생성 후 `*_all_frame_metrics.csv`를 추가 생성하여 프레임별 raw data를 한 파일에서 볼 수 있습니다.
- 최종 Export 시 세션 통합 파일을 추가 생성합니다.
  - `{session_id}_session_all_skeleton_frames.csv`
  - `{session_id}_session_gait_events.csv`
  - `{session_id}_session_skeleton_metric_summary.csv`
  - `{session_id}_debug_export_package_*.zip`
- 최종 비교표 source mapping을 고정했습니다.
  - 측면 running 지표는 `side_running` 결과만 참조
  - 후면 지표는 `rear_running` 결과만 참조
  - `side_static` 결과가 cadence/contact/ROM 등 running 지표 source로 잡히는 문제 차단
- Contact Time 입력값은 MotionMetrix 화면처럼 `0.225` 초 단위로 입력해도 비교표에서 정상적으로 `0.225 s`로 표시됩니다.
- Cadence/Contact Time 이벤트 검출은 foot-y local peak 기반 보조 로직을 추가하여, 한 발이 계속 contact로 잡혀 cadence가 과소 산출되는 문제를 완화했습니다.
- Hip/Knee ROM 계열은 MotionMetrix sagittal plane 비교에 맞춰 image-plane primary 계산값을 우선 사용하고, MediaPipe world 좌표는 audit column으로 유지합니다.
- Shank Angle은 stance/static baseline offset을 추정하여 touch-down 값의 systematic bias를 줄이도록 보정했습니다.

- 최종 비교표를 MotionMetrix 실제 화면 기준으로 재정렬했습니다.
  - Running Performance
  - Gait Characteristics
- Skeleton 평균값은 단순 프레임 평균이 아니라 항목별 MotionMetrix 정의에 맞춰 산출합니다.
- Forward Lean은 진행 방향 부호를 반영하되, MotionMetrix 화면 비교용으로 절대값 평균을 표시합니다.
- Knee Flexion은 관절 내각이 아니라 `180 - hip-knee-ankle 내각`으로 굴곡각 기준 표시합니다.
- Shank Angle, Overstride, Knee Flexion @ touch-down은 initial contact 이벤트 기준으로 산출합니다.
- Vertical Displacement는 골반 중심 평균값이 아니라 vertical range 기준으로 계산합니다.
- 고관절 ROM은 고객 기준대로 `abs(굴곡) + abs(신전)`으로 계산합니다.
- Skeleton 분석은 모든 원본 프레임 기준으로 수행하고, 결과 영상만 선택 FPS로 생성합니다.
- Export 시 고객 확인용 `final_comparison_summary.csv`, `final_comparison_summary.xlsx`를 생성합니다.
- `docs/GitHub_Streamlit_배포_가이드.md`는 제공 패키지에서 제외했습니다.

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
   - 진행 방향, FPS, 측정 시작/종료 구간, 필요 시 수동 지면선/접촉 허용 오차 입력
2. 후면 정지/달리기 영상 업로드
3. 측면 정지/달리기 영상 업로드
4. 후방 running / 측방 running 각각 Skeleton 결과 생성
5. 측면/종합 MotionMetrix 평균값 입력
6. 최종 비교 화면에서 Skeleton 평균값과 MotionMetrix 값 확인
7. Export 생성
8. final_comparison_summary.xlsx와 debug_export_package.zip 우선 확인
```

## 3. 고객이 먼저 확인할 파일

| 파일 | 용도 |
|---|---|
| `final_comparison_summary.xlsx` | 고객 확인용 1순위 파일. MotionMetrix 화면별로 Skeleton 평균값과 MotionMetrix 값이 같은 행에 정리됩니다. |
| `final_comparison_summary.csv` | 위 Excel 파일과 동일한 CSV 버전입니다. |
| `training_dataset_wide.csv` | 세션별 입력값 전체를 넓은 형태로 저장한 모델링용 CSV입니다. |
| `*_all_frame_metrics.csv` | v0.5.11 권장 파일. 후방/측방 영상별 모든 프레임 raw·좌표·각도·접촉 상태를 한 파일에서 확인합니다. |
| `{session_id}_session_all_skeleton_frames.csv` | 현재 세션의 후방/측방 Skeleton frame raw를 통합한 CSV입니다. |
| `{session_id}_session_gait_events.csv` | 현재 세션의 착지/접촉 이벤트를 통합한 CSV입니다. |
| `{session_id}_session_skeleton_metric_summary.csv` | final comparison에 들어가는 Skeleton summary와 source 정보를 확인하는 CSV입니다. |
| `{session_id}_debug_export_package_*.zip` | 고객 피드백 분석용 묶음 파일입니다. final/raw/event/source CSV가 함께 들어갑니다. |
| `frame_metrics.csv` | 개별 처리 결과의 프레임/시점별 Skeleton feature입니다. image 좌표와 world 좌표가 함께 저장됩니다. |
| `gait_events.csv` | 착지 시점, 접촉시간, 착지 각도 등 이벤트 기반 feature입니다. |
| `second_summary.csv` | 초별 요약 feature입니다. |
| `clip_summary.csv` | 영상 단위 Skeleton 평균 feature와 MotionMetrix target 연결용 파일입니다. |

## 4. 최종 비교표 구조

`final_comparison_summary.xlsx`는 아래 형태로 구성됩니다.

| MotionMetrix 화면 | 구분 | 측정 항목 | Skeleton 평균값 | Skeleton 단위 | MotionMetrix 값 | MotionMetrix 단위 | 차이값 | 비교 상태 | Skeleton 계산 방식 |
|---|---|---|---:|---|---:|---|---:|---|---|
| Running Performance | 측면 | Forward Lean | 4.2 | deg | 4.2 | deg | 0.0 | 비교 가능 | valid side frames / MotionMetrix-style display |
| Running Performance | 측면 | Contact Time | 0.225 | s | 0.225 | s | 0.0 | 비교 가능(추정값 주의) | contact event average |
| Gait Characteristics | 측면 | Knee Flexion @ touch-down | 18.8 | deg | 18.8 | deg | 0.0 | 비교 가능 | 180 - included knee angle |
| Gait Characteristics | 측면 | Max Thigh Flexion | 32.1 | deg | 32.1 | deg | 0.0 | 비교 가능 | thigh vector vs vertical |

색상 기준:

- 파란색 계열: Skeleton 평균값
- 주황색 계열: MotionMetrix 입력값
- 초록색: 비교 가능
- 노란색: 추정값 주의, 입력 필요, Skeleton-only 등 확인 필요 상태

## 5. MotionMetrix 화면 기준 입력 항목

### Running Performance

- Running Economy
- Cadence
- Contact Time
- Forward Lean
- Overstride
- Vertical Displacement
- Braking Force
- Vertical Force / Lateral Force / Stride Rating 선택 입력

### Gait Characteristics

- Step Separation
- Knee Alignment @ mid-stance
- Max Thigh Flexion
- Max Thigh Extension
- Shank Angle @ touch-down
- Knee Flexion @ touch-down
- Max Knee Flexion @ stance
- Max Knee Flexion @ swing

## 6. 평균값 중심 입력 정책

| 항목 | 입력 방식 |
|---|---|
| 오버스트라이드 | 전체 평균값만 입력 |
| 수직진폭 / Vertical Displacement | 전체 평균값만 입력, 단위 mm |
| 케이던스 | 평균 케이던스만 입력 |
| 지면접촉시간 | MotionMetrix 화면은 초(s)이므로 비교표에서는 초 단위로 표시 |
| 고관절 ROM | 좌우 굴곡/신전 입력 → ROM, 전체 평균, 좌우차이 자동 계산. ROM = abs(굴곡) + abs(신전) |
| 슬관절 ROM | 좌우 착지시 굴곡각/유각기 최대굴곡 입력 → ROM, 전체 평균, 좌우차이 자동 계산 |
| 착지 타입 | MotionMetrix 비교값이 아니라 별도 수동 라벨로 저장 |
| Running Economy / Running Type | MotionMetrix 직접 입력값이며 3차 학습 target으로 사용 |

## 7. MediaPipe world landmark 적용 주의사항

MediaPipe는 world landmark 3D 좌표를 제공하므로 각도/ROM 계열은 image pixel 기반 계산보다 MotionMetrix 정의에 더 가깝게 맞출 수 있습니다. 다만 MotionMetrix는 depth camera와 treadmill calibration 기반의 계측 시스템이므로, MediaPipe world 좌표를 MotionMetrix와 완전히 동일한 계측값으로 보지는 않습니다.

따라서 최종 비교표에서 `비교 가능(추정값 주의)`로 표시되는 항목은 수치 비교는 가능하지만, 3차 보정 학습 대상이라는 전제를 유지합니다.

## 8. Windows 권장 실행 방법

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

## 9. 주의사항

- Skeleton 측정값은 MotionMetrix 정답값이 아니라 참고 feature입니다. 다만 v0.5.11부터 어떤 raw/event/summary에서 최종값이 왔는지 source CSV로 추적할 수 있습니다.
- Braking Force, Running Economy, Running Type은 Skeleton 직접 계산값이 아니라 MotionMetrix 입력값을 3차 학습 target으로 사용합니다.
- Streamlit Cloud는 테스트용 경량 환경입니다. 생성한 데이터는 Export 또는 백업 ZIP으로 자주 다운로드하세요.
- 실제 고객 영상, 개인정보, 실제 MotionMetrix 원본 파일은 GitHub에 올리지 마세요.

## v0.5.12 Update

- 최종 비교표에서 고객이 보는 결과 공란을 `N/A`, `MotionMetrix 미입력`, `Skeleton 직접 산출 대상 아님`, `Skeleton-only` 등 명시 문구로 대체했습니다.
- 후면 영상에서 산출 가능한 Skeleton 각도 항목을 최종 비교표에 추가했습니다: Pelvic Drop, Trunk Lateral Tilt, Rear Shoulder Tilt, Rear Knee Alignment Left/Right/Mean.
- 후면 각도는 단일 RGB Skeleton 기반 참고값이며 MotionMetrix depth-camera 계측값과 완전 동일한 값으로 보지 않습니다.

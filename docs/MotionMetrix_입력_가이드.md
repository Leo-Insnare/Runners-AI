# MotionMetrix 결과지 입력 가이드 v0.5.5

본 가이드는 MotionMetrix 실제 화면을 보면서 라벨링 툴에 어떤 값을 입력해야 하는지 안내하기 위한 문서입니다.

## 1. 기본 원칙

- MotionMetrix 수치는 고객 측에서 확인한 값을 직접 입력합니다.
- 촬영 Wizard에서는 MotionMetrix 값을 입력하지 않습니다.
- UI 흐름은 v0.5.4와 동일하게 유지하되, 최종 비교표는 MotionMetrix 화면 기준으로 정리됩니다.
- Skeleton Preview/Overlay 값은 참고 feature이며, 최종 학습 정답값은 MotionMetrix 직접 입력값입니다.
- 최종 확인은 `final_comparison_summary.xlsx`에서 Skeleton 평균값과 MotionMetrix 값을 같은 행으로 비교합니다.

## 2. Running Performance 화면 입력

| MotionMetrix 화면 항목 | 입력/저장 방식 | 단위 |
|---|---|---|
| Running Economy | 직접 입력 | J/kg/m |
| Cadence | 평균값 입력 | /min |
| Contact Time | MotionMetrix 화면값이 초(s)인 경우 ms로 환산 입력 가능. 비교표에서는 s로 표시 | s |
| Forward Lean | 평균값 입력 | deg |
| Overstride | 평균값 입력 | mm |
| Vertical Displacement | 평균값 입력 | mm |
| Braking Force (max) | 직접 입력 | Fv 등 화면 단위 |
| Vertical Force / Lateral Force / Stride Rating | 선택 입력 | 화면 단위 |

## 3. Gait Characteristics 화면 입력

| MotionMetrix 화면 항목 | 입력/저장 방식 | 단위 |
|---|---|---|
| Step Separation | 필요 시 입력 | mm |
| Knee Alignment @ mid-stance | Skeleton proxy와 비교 시 주의 | deg |
| Max Thigh Flexion | 좌우값 입력 시 평균 자동 계산 | deg |
| Max Thigh Extension | 좌우값 입력 시 평균 자동 계산 | deg |
| Shank Angle @ touch-down | 평균값 입력 | deg |
| Knee Flexion @ touch-down | 좌우 착지시 굴곡각 입력 시 평균 자동 계산 | deg |
| Max Knee Flexion @ stance | 선택 입력 | deg |
| Max Knee Flexion @ swing | 좌우값 입력 시 평균 자동 계산 | deg |

## 4. 자동 계산 항목

### 고관절 ROM

- 왼쪽 고관절 ROM = abs(왼쪽 Max Thigh Flexion) + abs(왼쪽 Max Thigh Extension)
- 오른쪽 고관절 ROM = abs(오른쪽 Max Thigh Flexion) + abs(오른쪽 Max Thigh Extension)
- 전체 평균과 좌우 차이는 자동 계산됩니다.

예시:

```text
굴곡 20도, 신전 20도 → ROM 40도
굴곡 20도, 신전 -20도 → ROM 40도
```

### 슬관절 ROM

- 왼쪽 슬관절 ROM = abs(왼쪽 Max Knee Flexion @ swing - 왼쪽 Knee Flexion @ touch-down)
- 오른쪽 슬관절 ROM = abs(오른쪽 Max Knee Flexion @ swing - 오른쪽 Knee Flexion @ touch-down)
- 전체 평균과 좌우 차이는 자동 계산됩니다.

## 5. Skeleton 평균값 산출 기준

| 항목 | Skeleton 산출 기준 |
|---|---|
| Forward Lean | 측면 유효 프레임 평균, MotionMetrix 화면 비교용 절대값 표시 |
| Overstride | initial contact 기준 pelvis/COM projection과 착지 발목 거리 |
| Contact Time | 접촉 시작~toe-off 이벤트 평균, 비교표에서는 초(s) 표시 |
| Vertical Displacement | 골반/COM vertical range 기준, height 기반 px→mm 추정 |
| Shank Angle @ touch-down | initial contact 기준 정강이-수직축 각도 |
| Knee Flexion @ touch-down | initial contact 기준 `180 - hip-knee-ankle 내각` |
| Max Thigh Flexion / Extension | 대퇴선과 수직축 기준 cycle max magnitude |
| Max Knee Flexion @ stance/swing | 지지/유각 구간의 최대 무릎 굴곡각 |

## 6. 최종 비교 파일

Export 후 고객은 먼저 아래 파일을 확인합니다.

```text
final_comparison_summary.xlsx
```

이 파일에는 아래 정보가 한 줄에 정리됩니다.

```text
MotionMetrix 화면 / 측정 항목 / Skeleton 평균값 / MotionMetrix 값 / 단위 / 차이값 / 비교 상태 / Skeleton 계산 방식
```

## 7. 주의사항

- MediaPipe world landmark는 추정 3D 좌표이며, MotionMetrix depth camera 계측값과 완전히 동일한 계측값은 아닙니다.
- 거리/시간/힘 계열은 영상 FPS, 지면선, 접촉 판별, scale 보정에 따라 차이가 날 수 있습니다.
- Braking Force, Running Economy, Running Type은 Skeleton 직접 계산값이 아니라 MotionMetrix 입력값을 3차 학습 target으로 사용합니다.

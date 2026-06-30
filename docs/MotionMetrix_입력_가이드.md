# MotionMetrix 결과지 입력 가이드

본 가이드는 MotionMetrix 결과 화면 또는 리포트를 보면서 라벨링 툴에 어떤 값을 입력해야 하는지 안내하기 위한 문서입니다.

---

## 1. 기본 원칙

- MotionMetrix 수치는 고객 측에서 확인한 값을 직접 입력합니다.
- 입력값은 동일 측정 세션 기준으로 저장합니다.
- 좌/우 값은 화면 기준이 아니라 실제 신체 기준의 왼쪽/오른쪽으로 입력합니다.
- 단위가 다른 경우 앱의 단위 선택값을 맞춘 뒤 입력합니다.
- 실제 결과지에 없는 항목은 비워도 되지만, `core` 필수 항목은 가능하면 입력합니다.
- Preview/Live 값은 참고값이며 최종 학습 정답값은 MotionMetrix 직접 입력값입니다.

---

## 2. Running Performance 계열

MotionMetrix Running Performance 화면 또는 리포트에서 아래 항목을 확인합니다.

| MotionMetrix 항목 | 라벨링 툴 입력 위치 | 비고 |
|---|---|---|
| Running Economy | `6. 종합/선택 입력` | J/kg/m |
| Runner Profile / Running Type | `6. 종합/선택 입력` | Long Strider, Power Racer, Eco Sprinter, Quick Stepper, Constant Glider, Easy Strider 중 선택 |
| Cadence | `4. MotionMetrix 입력 - 측면` > 시간 기반 지표 | steps/min 또는 strides/min 선택 |
| Contact Time | `4. MotionMetrix 입력 - 측면` > 시간 기반 지표 | ms 또는 sec 선택 |
| Forward Lean | `4. MotionMetrix 입력 - 측면` > 측면 생체역학 지표 | deg |
| Overstride | `4. MotionMetrix 입력 - 측면` > 측면 생체역학 지표 | cm 또는 mm 선택 |
| Vertical Displacement / Vertical Oscillation | `4. MotionMetrix 입력 - 측면` > 측면 생체역학 지표 | cm 또는 mm 선택 |
| Braking Force | `4. MotionMetrix 입력 - 측면` > 측면 생체역학 지표 | MotionMetrix 표시 단위 그대로 입력 |
| Vertical Force / Lateral Force | `6. 종합/선택 입력` | 결과지에 있으면 선택 입력 |
| Stride Rating | `6. 종합/선택 입력` | 결과지에 있으면 선택 입력 |

---

## 3. Gait Characteristics 계열

| MotionMetrix 항목 | 라벨링 툴 입력 위치 | 비고 |
|---|---|---|
| Hip / Thigh Flexion | `4. MotionMetrix 입력 - 측면` > 관절 운동범위 | 좌/우 최대값 |
| Hip / Thigh Extension | `4. MotionMetrix 입력 - 측면` > 관절 운동범위 | 좌/우 최대값 |
| Hip ROM | `4. MotionMetrix 입력 - 측면` > 관절 운동범위 | 좌/우/평균 |
| Knee Flexion @ Landing | `4. MotionMetrix 입력 - 측면` > 관절 운동범위 | 착지 순간 좌/우 |
| Knee Flexion @ Swing Max | `4. MotionMetrix 입력 - 측면` > 관절 운동범위 | 유각기 최대 좌/우 |
| Knee ROM | `4. MotionMetrix 입력 - 측면` > 관절 운동범위 | 좌/우/평균 |
| Shank Angle | `4. MotionMetrix 입력 - 측면` > 측면 생체역학 지표 | 착지 순간 좌/우 |
| Step Separation / Step Width | `5. MotionMetrix 입력 - 후면` | 결과지 또는 육안 기준 |
| Knee Alignment | `5. MotionMetrix 입력 - 후면` | 무릎 안쪽 붕괴/정렬 항목과 연결 |

---

## 4. 수동 입력 우선 항목

아래 항목은 MotionMetrix 결과보다 원장님 또는 고객의 육안 판단을 우선합니다.

- 착지 타입: 힐 착지 / 미드풋 / 포어풋
- 팔 스윙 대칭성
- 걷듯이 뛴다
- 뒤뚱거린다
- 좌우 비대칭
- 팔 동작 비대칭
- 상체 좌우 흔들림
- 무릎 상승 부족

---

## 5. 단위 입력 기준

| 항목 | 입력 가능 단위 | Export 표준 단위 |
|---|---|---|
| Overstride | cm, mm | cm |
| Contact Time | ms, sec | ms |
| Vertical Oscillation | cm, mm | cm |
| Step / Stride Length | cm, m | cm |
| Flight Time | ms, sec | ms |
| Cadence | steps/min, strides/min | steps/min |

---

## 6. 입력 순서 권장안

1. 세션 정보 입력
2. 측면/후면 영상 업로드
3. 촬영 Wizard / Overlay에서 Skeleton Point 확인
4. Running Performance 항목 입력
5. Gait Characteristics 항목 입력
6. 착지 타입 및 수동 평가 입력
7. 최종 검토에서 누락값 확인
8. Export 생성

---

## 7. 고객 측 확인이 필요한 항목

실제 MotionMetrix 결과지 양식에 따라 아래 항목은 고객 확인 후 입력 순서나 필드명을 미세조정할 수 있습니다.

- Overstride 단위: cm 또는 mm
- Contact Time 단위: ms 또는 sec
- Cadence 단위: steps/min 또는 strides/min
- Braking Force 표시 단위
- Running Type 표기명
- 좌/우 표기 기준
- MotionMetrix 결과지에서 제공되지 않는 optional 항목 여부

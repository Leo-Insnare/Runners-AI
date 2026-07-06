# MotionMetrix 결과지 입력 가이드 v0.5.3

본 가이드는 MotionMetrix 결과 화면 또는 리포트를 보면서 라벨링 툴에 어떤 값을 입력해야 하는지 안내하기 위한 문서입니다.

## 1. 기본 원칙

- MotionMetrix 수치는 고객 측에서 확인한 값을 직접 입력합니다.
- 촬영 Wizard에서는 MotionMetrix 값을 입력하지 않습니다.
- MotionMetrix 입력은 `측면 입력`, `후면 입력`, `종합/선택 입력` 탭에서 진행합니다.
- 고객 요청에 따라 입력값은 가능한 한 **전체 평균값 중심**으로 정리합니다.
- Skeleton Preview/Overlay 값은 참고 feature이며, 최종 학습 정답값은 MotionMetrix 직접 입력값입니다.
- 최종 확인은 `final_comparison_summary.xlsx`에서 Skeleton 평균값과 MotionMetrix 값을 같은 행으로 비교합니다.

## 2. 평균값 중심 입력 항목

| 항목 | 입력 방식 | 단위 |
|---|---|---|
| Forward Lean / 척추기울기 | MotionMetrix 평균값 입력 | deg |
| Overstride / 오버스트라이드 | 좌우값 없이 전체 평균값만 입력 | mm |
| Vertical Oscillation / 수직진폭 | 좌우값 없이 전체 평균값만 입력 | mm |
| Cadence / 케이던스 | 평균/표준 케이던스만 입력 | steps/min |
| Contact Time / 지면접촉시간 | 좌우값 없이 전체 평균값만 입력 | ms |
| Shank Angle / 정강이 각도 | 평균값만 입력 | deg |
| Braking Force / 제동력 | MotionMetrix 평균값 입력 | MotionMetrix 표시 단위 |

## 3. 자동 계산 항목

### 고관절 ROM

고객 입력값:

- 왼쪽 최대 굴곡
- 왼쪽 최대 신전
- 오른쪽 최대 굴곡
- 오른쪽 최대 신전

자동 계산값:

- 왼쪽 고관절 ROM
- 오른쪽 고관절 ROM
- 고관절 ROM 전체 평균
- 고관절 ROM 좌우 차이

### 슬관절 ROM

고객 입력값:

- 왼쪽 착지시 굴곡각
- 왼쪽 유각기 최대굴곡
- 오른쪽 착지시 굴곡각
- 오른쪽 유각기 최대굴곡

자동 계산값:

- 왼쪽 슬관절 ROM
- 오른쪽 슬관절 ROM
- 슬관절 ROM 전체 평균
- 슬관절 ROM 좌우 차이
- 착지시 무릎 굴곡각 평균

## 4. 수동 라벨 항목

아래 항목은 MotionMetrix 비교값이 아니라 고객/원장님 수동 판단값으로 저장합니다.

- 착지 타입: 힐 착지 / 미드풋 / 포어풋
- 팔 스윙 대칭성
- 걷듯이 뛴다
- 뒤뚱거린다
- 좌우 비대칭
- 팔 동작 비대칭
- 상체 좌우 흔들림
- 무릎 상승 부족

## 5. 후면 입력 항목

| 항목 | 입력 방식 |
|---|---|
| 골반 낙하 | 평균값 중심 입력 |
| 무릎 안쪽 붕괴 | 평균값 중심 입력 |
| 스텝 폭 | 평균값 중심 입력 |
| 크로스오버 | 경향 선택 |
| 몸통 좌우 기울기 | 평균값 중심 입력 |

## 6. 최종 비교 파일

Export 후 고객은 먼저 아래 파일을 확인합니다.

```text
final_comparison_summary.xlsx
```

이 파일에는 아래 정보가 한 줄에 정리됩니다.

```text
측정 항목 / Skeleton 평균값 / Skeleton 단위 / MotionMetrix 값 / MotionMetrix 단위 / 차이값 / 비교 상태
```

예시:

```text
척추기울기 / Skeleton 6도 / MotionMetrix 7도 / 차이 -1도
```

px와 mm처럼 단위가 다른 항목은 직접 차이값을 계산하지 않고 `단위 상이 또는 수동 기준`으로 표시합니다.

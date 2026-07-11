# MotionMetrix 결과지 입력 가이드 v0.5.4

본 가이드는 MotionMetrix 결과 화면 또는 리포트를 보면서 라벨링 툴에 어떤 값을 입력해야 하는지 안내하기 위한 문서입니다.

## 1. 기본 원칙

- MotionMetrix 수치는 고객 측에서 확인한 값을 직접 입력합니다.
- 촬영 Wizard에서는 MotionMetrix 값을 입력하지 않습니다.
- MotionMetrix 입력은 `측면 입력`, `종합/선택 입력` 탭에서 진행합니다.
- 후면 지표는 고객 피드백에 따라 MotionMetrix 입력값 없이 Skeleton-only 참고값으로 관리합니다.
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
| Contact Time / 지면접촉시간 | 좌우값 없이 평균값만 입력 | ms |
| Shank Angle / 정강이 각도 | 슬관절 ROM 다음 항목으로 입력, 평균값만 입력 | deg |
| Braking Force / 제동력 | MotionMetrix 평균값 입력 | MotionMetrix 표시 단위 |

## 3. 자동 계산 항목

### 고관절 ROM

고객 입력값:

- 왼쪽 최대 굴곡
- 왼쪽 최대 신전
- 오른쪽 최대 굴곡
- 오른쪽 최대 신전

자동 계산값:

- 왼쪽 고관절 ROM = abs(왼쪽 굴곡) + abs(왼쪽 신전)
- 오른쪽 고관절 ROM = abs(오른쪽 굴곡) + abs(오른쪽 신전)
- 고관절 ROM 전체 평균
- 고관절 ROM 좌우 차이

예시:

```text
굴곡 20도, 신전 20도 → ROM 40도
굴곡 20도, 신전 -20도 → ROM 40도
```

### 슬관절 ROM

고객 입력값:

- 왼쪽 착지시 굴곡각
- 왼쪽 유각기 최대굴곡
- 오른쪽 착지시 굴곡각
- 오른쪽 유각기 최대굴곡

자동 계산값:

- 왼쪽 슬관절 ROM = abs(왼쪽 유각기 최대굴곡 - 왼쪽 착지시 굴곡각)
- 오른쪽 슬관절 ROM = abs(오른쪽 유각기 최대굴곡 - 오른쪽 착지시 굴곡각)
- 슬관절 ROM 전체 평균
- 슬관절 ROM 좌우 차이
- 착지시 무릎 굴곡각 평균

## 4. 후면 지표

아래 항목은 MotionMetrix 입력값을 받지 않고 Skeleton-only 참고값으로 표시합니다.

| 항목 | 처리 방식 |
|---|---|
| 골반 낙하 | Skeleton 평균값 표시 |
| 무릎 안쪽 붕괴 | Skeleton 평균값 표시 |
| 스텝 폭 | Skeleton 평균값 표시 |
| 크로스오버 | Skeleton 비율/경향 표시 |
| 몸통 좌우 기울기 | Skeleton 평균값 표시 |

## 5. 수동 라벨 항목

아래 항목은 MotionMetrix 비교값이 아니라 고객/원장님 수동 판단값으로 저장합니다.

- 착지 타입: 힐 착지 / 미드풋 / 포어풋
- 팔 스윙 대칭성
- 걷듯이 뛴다
- 뒤뚱거린다
- 좌우 비대칭
- 팔 동작 비대칭
- 상체 좌우 흔들림
- 무릎 상승 부족

## 6. Skeleton 계산값 보정 옵션

세션 정보에서 아래 항목을 필요 시 입력합니다.

| 항목 | 용도 |
|---|---|
| 측면 영상 진행 방향 | Forward Lean, Overstride, Shank Angle 부호 보정 |
| 측면 수동 지면선 y좌표 | 착지/접촉 이벤트 판별 보정 |
| 후면 수동 지면선 y좌표 | 후면 지지/접촉 참고 보정 |
| 발 접촉 허용 오차 | Contact Time, Initial Contact 판별 민감도 조정 |

## 7. 최종 비교 파일

Export 후 고객은 먼저 아래 파일을 확인합니다.

```text
final_comparison_summary.xlsx
```

이 파일에는 아래 정보가 한 줄에 정리됩니다.

```text
측정 항목 / Skeleton 평균값 / Skeleton 단위 / MotionMetrix 값 / MotionMetrix 단위 / 차이값 / 비교 상태 / Skeleton 계산 방식
```

예시:

```text
척추기울기 / Skeleton 6도 / MotionMetrix 7도 / 차이 -1도
```

MediaPipe world landmark 기반 mm 추정값은 MotionMetrix와 같은 단위로 비교할 수 있도록 표시하지만, depth camera 기반 계측값과 완전히 동일하다고 보지 않고 `비교 가능(추정값 주의)`로 관리합니다.

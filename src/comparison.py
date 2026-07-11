from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .storage import BASE_DIR, EXPORTS_DIR, SESSIONS_DIR, read_json, session_path


def _num(value: Any) -> float | None:
    if value in (None, "", [], {}):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round(value: Any, digits: int = 3) -> Any:
    n = _num(value)
    if n is None:
        return value if value not in (None, []) else ""
    return round(n, digits)


def _mean(values: list[Any]) -> float | None:
    nums = [_num(v) for v in values]
    nums = [v for v in nums if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


def _diff(a: Any, b: Any) -> Any:
    na, nb = _num(a), _num(b)
    if na is None or nb is None:
        return ""
    return round(na - nb, 3)


def _value(values: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        val = values.get(key)
        if val not in (None, "", [], {}):
            return val
    return ""


def compute_auto_motionmetrix_values(values: dict[str, Any]) -> dict[str, Any]:
    """Compute customer-requested derived MotionMetrix fields.

    Customers enter only source values such as flexion/extension or landing/swing max.
    ROM, overall average, and left-right difference are computed automatically here.
    The function also keeps backward compatibility with older field names.
    """
    out = dict(values or {})

    # Backward-compatible unit normalization for older exports.
    over_cm = _num(out.get("overstride_mean_cm"))
    if "overstride_mean_mm" not in out and over_cm is not None:
        out["overstride_mean_mm"] = round(over_cm * 10.0, 3)

    vo_cm = _num(out.get("vertical_oscillation_mean_cm"))
    if "vertical_oscillation_mean_mm" not in out and vo_cm is not None:
        out["vertical_oscillation_mean_mm"] = round(vo_cm * 10.0, 3)

    raw_cadence = _num(out.get("cadence_raw_value"))
    raw_unit = out.get("cadence_raw_unit")
    if "cadence_steps_per_min" not in out and raw_cadence is not None:
        if raw_unit == "strides/min":
            out["cadence_steps_per_min"] = round(raw_cadence * 2.0, 3)
        elif raw_unit == "steps/min":
            out["cadence_steps_per_min"] = round(raw_cadence, 3)

    contact_sec = _num(out.get("contact_time_mean_sec"))
    if "contact_time_mean_ms" not in out and contact_sec is not None:
        out["contact_time_mean_ms"] = round(contact_sec * 1000.0, 3)

    # Hip/thigh ROM: customer confirmed flexion and extension are summed as magnitudes.
    # Example: flexion 20 deg + extension 20 deg = ROM 40 deg.
    # This works whether extension is entered as +20 or -20.
    lf = _num(out.get("left_thigh_flexion_max_deg"))
    le = _num(out.get("left_thigh_extension_max_deg"))
    rf = _num(out.get("right_thigh_flexion_max_deg"))
    re = _num(out.get("right_thigh_extension_max_deg"))
    left_hip_rom = (abs(lf) + abs(le)) if lf is not None and le is not None else _num(out.get("left_hip_rom_deg"))
    right_hip_rom = (abs(rf) + abs(re)) if rf is not None and re is not None else _num(out.get("right_hip_rom_deg"))
    if left_hip_rom is not None:
        out["left_hip_rom_deg"] = round(left_hip_rom, 3)
    if right_hip_rom is not None:
        out["right_hip_rom_deg"] = round(right_hip_rom, 3)
    hip_mean = _mean([left_hip_rom, right_hip_rom])
    if hip_mean is not None:
        out["hip_rom_mean_deg"] = round(hip_mean, 3)
    if left_hip_rom is not None and right_hip_rom is not None:
        out["hip_rom_asymmetry_deg"] = round(abs(left_hip_rom - right_hip_rom), 3)

    # Knee ROM: swing max flexion minus landing flexion.
    ll = _num(out.get("left_knee_flexion_landing_deg"))
    ls = _num(out.get("left_knee_flexion_swing_max_deg"))
    rl = _num(out.get("right_knee_flexion_landing_deg"))
    rs = _num(out.get("right_knee_flexion_swing_max_deg"))
    left_knee_rom = abs(ls - ll) if ls is not None and ll is not None else _num(out.get("left_knee_rom_deg"))
    right_knee_rom = abs(rs - rl) if rs is not None and rl is not None else _num(out.get("right_knee_rom_deg"))
    if left_knee_rom is not None:
        out["left_knee_rom_deg"] = round(left_knee_rom, 3)
    if right_knee_rom is not None:
        out["right_knee_rom_deg"] = round(right_knee_rom, 3)
    knee_mean = _mean([left_knee_rom, right_knee_rom])
    if knee_mean is not None:
        out["knee_rom_mean_deg"] = round(knee_mean, 3)
    if left_knee_rom is not None and right_knee_rom is not None:
        out["knee_rom_asymmetry_deg"] = round(abs(left_knee_rom - right_knee_rom), 3)
    landing_mean = _mean([ll, rl])
    if landing_mean is not None:
        out["knee_flexion_landing_mean_deg"] = round(landing_mean, 3)

    # Backward-compatible averages for rear/side metrics.
    shank_mean = _mean([out.get("left_shank_angle_signed_deg"), out.get("right_shank_angle_signed_deg")])
    if "shank_angle_mean_signed_deg" not in out and shank_mean is not None:
        out["shank_angle_mean_signed_deg"] = round(shank_mean, 3)

    pelvic_mean = _mean([out.get("left_stance_pelvic_drop_deg"), out.get("right_stance_pelvic_drop_deg")])
    if "pelvic_drop_mean_deg" not in out and pelvic_mean is not None:
        out["pelvic_drop_mean_deg"] = round(pelvic_mean, 3)

    trunk_mean = _mean([out.get("left_stance_trunk_lateral_tilt_deg"), out.get("right_stance_trunk_lateral_tilt_deg")])
    if "trunk_lateral_tilt_mean_deg" not in out and trunk_mean is not None:
        out["trunk_lateral_tilt_mean_deg"] = round(trunk_mean, 3)

    kcollapse_mean = _mean([out.get("left_knee_medial_collapse_mean"), out.get("right_knee_medial_collapse_mean")])
    if "knee_medial_collapse_mean" not in out and kcollapse_mean is not None:
        out["knee_medial_collapse_mean"] = round(kcollapse_mean, 3)

    step_cm = _num(out.get("step_width_mean_cm"))
    if "step_width_mean_mm" not in out and step_cm is not None:
        out["step_width_mean_mm"] = round(step_cm * 10.0, 3)

    return out


def _latest_clip_summaries(session_id: str) -> dict[str, dict[str, Any]]:
    rows = read_json(session_path(session_id) / "processed_videos.json", [])
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(rows, list):
        return result
    for meta in rows:
        if not isinstance(meta, dict):
            continue
        view = meta.get("view_type") or "unknown"
        rel = meta.get("clip_summary_csv_path")
        if not rel:
            continue
        path = BASE_DIR / rel
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
            if df.empty:
                continue
            data = df.iloc[0].to_dict()
            data["_clip_summary_path"] = str(path.relative_to(BASE_DIR))
            data["_created_at"] = meta.get("created_at", "")
            data["_source_video"] = meta.get("source_video", "")
            result[view] = data
        except Exception:
            continue
    return result


COMPARISON_SPECS = [
    {"view":"side", "metric":"척추기울기", "sk":"forward_lean_avg_deg", "sk_unit":"deg", "mm":"forward_lean_deg", "mm_unit":"deg", "source":"MediaPipe world/image landmark"},
    {"view":"side", "metric":"오버스트라이드 평균", "sk":"overstride_avg_mm_est", "sk_unit":"mm", "mm":"overstride_mean_mm", "mm_unit":"mm", "caution":True, "source":"MediaPipe world landmark estimate", "note":"MediaPipe world 좌표 기반 mm 추정값입니다. MotionMetrix depth camera 계측값과 완전 동일하다고 보지는 않고 보정 학습 대상으로 관리합니다."},
    {"view":"side", "metric":"수직진폭 평균", "sk":"pelvis_vertical_oscillation_mm_est", "sk_unit":"mm", "mm":"vertical_oscillation_mean_mm", "mm_unit":"mm", "caution":True, "source":"MediaPipe world landmark estimate", "note":"MediaPipe world 골반 중심 y축 range 기반 mm 추정값입니다."},
    {"view":"side", "metric":"정강이 각도 평균", "sk":"shank_angle_at_contact_avg_deg", "sk_unit":"deg", "mm":"shank_angle_mean_signed_deg", "mm_unit":"deg", "source":"initial contact event + MediaPipe world/image landmark"},
    {"view":"side", "metric":"착지시 무릎 굴곡각 평균", "sk":"knee_angle_at_contact_avg_deg", "sk_unit":"deg", "mm":"knee_flexion_landing_mean_deg", "mm_unit":"deg", "source":"initial contact event + MediaPipe world/image landmark"},
    {"view":"side", "metric":"고관절 ROM 전체평균", "sk":"hip_rom_avg_deg", "sk_unit":"deg", "mm":"hip_rom_mean_deg", "mm_unit":"deg", "auto":True, "source":"MediaPipe world/image landmark"},
    {"view":"side", "metric":"고관절 ROM 좌우차이", "sk":"hip_rom_asymmetry_deg", "sk_unit":"deg", "mm":"hip_rom_asymmetry_deg", "mm_unit":"deg", "auto":True, "source":"MediaPipe world/image landmark"},
    {"view":"side", "metric":"슬관절 ROM 전체평균", "sk":"knee_rom_avg_deg", "sk_unit":"deg", "mm":"knee_rom_mean_deg", "mm_unit":"deg", "auto":True, "source":"MediaPipe world/image landmark"},
    {"view":"side", "metric":"슬관절 ROM 좌우차이", "sk":"knee_rom_asymmetry_deg", "sk_unit":"deg", "mm":"knee_rom_asymmetry_deg", "mm_unit":"deg", "auto":True, "source":"MediaPipe world/image landmark"},
    {"view":"side", "metric":"케이던스 평균", "sk":"estimated_cadence_spm", "sk_unit":"steps/min", "mm":"cadence_steps_per_min", "mm_unit":"steps/min", "source":"gait event count"},
    {"view":"side", "metric":"지면접촉시간 평균", "sk":"contact_time_avg_ms", "sk_unit":"ms", "mm":"contact_time_mean_ms", "mm_unit":"ms", "caution":True, "source":"contact event estimate", "note":"FPS와 지면선/접촉 판별에 영향을 받습니다."},
    {"view":"side", "metric":"제동력 평균", "sk":"", "sk_unit":"", "mm":"braking_force_mean_value", "mm_unit":"braking_force_unit", "target_only":True, "source":"MotionMetrix target", "note":"MotionMetrix 평균값을 학습 정답으로 사용합니다."},
    {"view":"side", "metric":"착지 타입", "sk":"foot_strike_type_summary", "sk_unit":"candidate", "mm":"session_representative_strike_type", "mm_unit":"manual", "manual_label":True, "source":"manual label + skeleton candidate", "note":"MotionMetrix 비교값이 아니라 고객 수동 라벨입니다."},
    {"view":"rear", "metric":"골반낙하 평균", "sk":"rear_pelvic_tilt_avg_deg", "sk_unit":"deg", "mm":"", "mm_unit":"", "skeleton_only":True, "source":"rear skeleton-only", "note":"고객 피드백 기준 후면 MotionMetrix 입력값 없음."},
    {"view":"rear", "metric":"무릎안쪽붕괴 평균", "sk":"knee_medial_collapse_avg_px", "sk_unit":"px", "mm":"", "mm_unit":"", "skeleton_only":True, "source":"rear skeleton-only", "note":"후면 Skeleton-only 참고값입니다."},
    {"view":"rear", "metric":"스텝 폭 평균", "sk":"step_width_avg_mm_est", "sk_unit":"mm", "mm":"", "mm_unit":"", "skeleton_only":True, "source":"rear skeleton-only / MediaPipe world estimate", "note":"후면 MotionMetrix 입력값 없이 Skeleton 참고값으로 저장합니다."},
    {"view":"rear", "metric":"크로스오버", "sk":"crossover_ratio", "sk_unit":"ratio", "mm":"", "mm_unit":"", "skeleton_only":True, "source":"rear skeleton-only"},
    {"view":"rear", "metric":"몸통 좌우 기울기 평균", "sk":"rear_trunk_lateral_tilt_avg_deg", "sk_unit":"deg", "mm":"", "mm_unit":"", "skeleton_only":True, "source":"rear skeleton-only"},
    {"view":"aggregate", "metric":"러닝효율", "sk":"", "sk_unit":"", "mm":"running_economy_j_kg_m", "mm_unit":"J/kg/m", "target_only":True, "source":"MotionMetrix target", "note":"여러 Skeleton feature를 이용해 3차에서 예측할 MotionMetrix 정답값입니다."},
    {"view":"aggregate", "metric":"러닝타입", "sk":"", "sk_unit":"", "mm":"running_type", "mm_unit":"class", "target_only":True, "source":"MotionMetrix target", "note":"3차 분류 모델의 MotionMetrix 기준 정답값입니다."},
]


def build_final_comparison_rows(session_id: str) -> list[dict[str, Any]]:
    values = read_json(session_path(session_id) / "motionmetrix_values.json", {})
    values = compute_auto_motionmetrix_values(values if isinstance(values, dict) else {})
    clips = _latest_clip_summaries(session_id)
    rows: list[dict[str, Any]] = []
    for spec in COMPARISON_SPECS:
        view = spec["view"]
        clip = clips.get(view, {}) if view in ("side", "rear") else {}
        sk_key = spec.get("sk", "")
        mm_key = spec.get("mm", "")
        sk_value = _value(clip, sk_key) if sk_key else ""
        mm_value = _value(values, mm_key) if mm_key else ""
        mm_unit_spec = spec.get("mm_unit", "")
        mm_unit = values.get(mm_unit_spec, "") if mm_unit_spec in values else mm_unit_spec
        sk_unit = spec.get("sk_unit", "")
        comparable = bool(sk_value not in ("", None) and mm_value not in ("", None) and sk_unit == mm_unit and sk_unit not in ("", "px", "raw", "ratio", "candidate", "manual", "class"))
        target_only = bool(spec.get("target_only"))
        skeleton_only = bool(spec.get("skeleton_only"))
        manual_label = bool(spec.get("manual_label"))
        caution = bool(spec.get("caution"))
        if target_only:
            status = "MotionMetrix 입력값 / 3차 학습 정답"
        elif skeleton_only:
            status = "Skeleton-only / 후면 MotionMetrix 없음"
        elif manual_label:
            status = "수동 라벨 / 비교 대상 아님"
        elif comparable and caution:
            status = "비교 가능(추정값 주의)"
        elif comparable:
            status = "비교 가능"
        elif sk_value in ("", None) and mm_value in ("", None):
            status = "값 없음"
        elif sk_value in ("", None):
            status = "Skeleton 평균값 없음"
        elif mm_value in ("", None):
            status = "MotionMetrix 입력 필요"
        else:
            status = "단위 상이 또는 수동 기준"
        rows.append({
            "session_id": session_id,
            "구분": {"side":"측면", "rear":"후면", "aggregate":"종합"}.get(view, view),
            "측정 항목": spec["metric"],
            "Skeleton 평균값": _round(sk_value),
            "Skeleton 단위": sk_unit,
            "MotionMetrix 값": _round(mm_value),
            "MotionMetrix 단위": mm_unit,
            "차이값(Skeleton-MM)": _diff(sk_value, mm_value) if comparable else "",
            "비교 상태": status,
            "Skeleton 계산 방식": spec.get("source", ""),
            "비고": spec.get("note", "") + (" / 자동계산" if spec.get("auto") else ""),
        })
    return rows


def export_final_comparison_summary() -> list[Path]:
    rows: list[dict[str, Any]] = []
    if not SESSIONS_DIR.exists():
        return []
    for session_dir in SESSIONS_DIR.iterdir():
        if session_dir.is_dir():
            rows.extend(build_final_comparison_rows(session_dir.name))
    df = pd.DataFrame(rows)
    csv_path = EXPORTS_DIR / "final_comparison_summary.csv"
    xlsx_path = EXPORTS_DIR / "final_comparison_summary.xlsx"
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    paths = [csv_path]
    try:
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Skeleton_vs_MotionMetrix")
            ws = writer.book["Skeleton_vs_MotionMetrix"]
            from openpyxl.styles import Font, PatternFill, Alignment
            header_fill = PatternFill("solid", fgColor="1F2937")
            header_font = Font(color="FFFFFF", bold=True)
            skeleton_fill = PatternFill("solid", fgColor="DBEAFE")
            mm_fill = PatternFill("solid", fgColor="FFEDD5")
            auto_fill = PatternFill("solid", fgColor="DCFCE7")
            warn_fill = PatternFill("solid", fgColor="FEF3C7")
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
            col_names = [cell.value for cell in ws[1]]
            for idx, name in enumerate(col_names, start=1):
                if name and "Skeleton" in str(name):
                    for cell in ws.iter_cols(min_col=idx, max_col=idx, min_row=2):
                        for c in cell:
                            c.fill = skeleton_fill
                if name and "MotionMetrix" in str(name):
                    for cell in ws.iter_cols(min_col=idx, max_col=idx, min_row=2):
                        for c in cell:
                            c.fill = mm_fill
            status_col = col_names.index("비교 상태") + 1 if "비교 상태" in col_names else None
            if status_col:
                for row in range(2, ws.max_row + 1):
                    status = str(ws.cell(row=row, column=status_col).value or "")
                    fill = auto_fill if "비교 가능" in status else warn_fill if "단위" in status or "입력" in status else None
                    if fill:
                        ws.cell(row=row, column=status_col).fill = fill
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 12), 40)
            ws.freeze_panes = "A2"
        paths.append(xlsx_path)
    except Exception:
        pass
    return paths

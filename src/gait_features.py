from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import numpy as np

SIDE_DIRECT_TARGETS = [
    "Braking Force", "Overstride", "Contact Time", "Cadence", "Vertical Oscillation",
    "Running Economy", "Running Type", "Shank Angle", "Knee Flexion", "Foot Strike Type",
]
REAR_DIRECT_TARGETS = ["Pelvic Drop", "Knee Medial Collapse", "Step Width / Crossover", "Trunk Lateral Tilt"]


def pt(points: dict[int, dict[str, float]], idx: int):
    if idx not in points:
        return None
    return (float(points[idx]["x"]), float(points[idx]["y"]))


def midpoint(points: dict[int, dict[str, float]], a: int, b: int):
    pa, pb = pt(points, a), pt(points, b)
    if not pa or not pb:
        return None
    return ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0)


def angle_between(a, b, c) -> float | None:
    if not a or not b or not c:
        return None
    v1 = np.array([a[0] - b[0], a[1] - b[1]], dtype=float)
    v2 = np.array([c[0] - b[0], c[1] - b[1]], dtype=float)
    denom = float(np.linalg.norm(v1) * np.linalg.norm(v2))
    if denom == 0:
        return None
    return float(math.degrees(math.acos(float(np.clip(np.dot(v1, v2) / denom, -1.0, 1.0)))))


def angle_to_vertical(p_low, p_high) -> float | None:
    if not p_low or not p_high:
        return None
    dx = p_high[0] - p_low[0]
    dy = p_low[1] - p_high[1]
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return None
    return float(math.degrees(math.atan2(dx, dy)))


def _small_angle_deg(angle: float | None) -> float | None:
    if angle is None:
        return None
    # Normalize line angle to the closest representation around 0 degrees.
    # This avoids rear pelvis angles such as 176 deg when the line is actually -4 deg from horizontal.
    while angle > 90:
        angle -= 180
    while angle < -90:
        angle += 180
    return angle


def angle_to_horizontal(p1, p2) -> float | None:
    if not p1 or not p2:
        return None
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return None
    return _small_angle_deg(float(math.degrees(math.atan2(-dy, dx))))


def line_offset_px(p, a, b) -> float | None:
    """Signed perpendicular distance from p to line a-b in pixels."""
    if not p or not a or not b:
        return None
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    denom = math.hypot(vx, vy)
    if denom == 0:
        return None
    return float(((px - ax) * vy - (py - ay) * vx) / denom)


def _round(v: Any, ndigits: int = 3):
    if v is None:
        return ""
    try:
        if isinstance(v, (float, int, np.floating, np.integer)) and math.isfinite(float(v)):
            return round(float(v), ndigits)
    except Exception:
        return v
    return v


def compute_frame_metrics(points: dict[int, dict[str, float]], frame_index: int, timestamp_sec: float, source_fps: float, view_type: str) -> dict[str, Any]:
    view_type = view_type or "unknown"
    shoulder = midpoint(points, 11, 12)
    pelvis = midpoint(points, 23, 24)
    left_foot_low_y = max([points[i]["y"] for i in [29, 31, 27] if i in points], default=None)
    right_foot_low_y = max([points[i]["y"] for i in [30, 32, 28] if i in points], default=None)
    left_ankle, right_ankle = pt(points, 27), pt(points, 28)
    left_heel, right_heel = pt(points, 29), pt(points, 30)
    left_toe, right_toe = pt(points, 31), pt(points, 32)

    row: dict[str, Any] = {
        "frame_index": int(frame_index),
        "timestamp_sec": round(float(timestamp_sec), 3),
        "source_fps": round(float(source_fps or 0), 3),
        "view_type": view_type,
        "pose_detected": bool(points),
        "detected_points_count": len([k for k, v in points.items() if v.get("visibility", 0) >= 0.5]),
        "shoulder_center_x": _round(shoulder[0] if shoulder else None),
        "shoulder_center_y": _round(shoulder[1] if shoulder else None),
        "pelvis_center_x": _round(pelvis[0] if pelvis else None),
        "pelvis_center_y": _round(pelvis[1] if pelvis else None),
        "left_ankle_x": _round(left_ankle[0] if left_ankle else None),
        "left_ankle_y": _round(left_ankle[1] if left_ankle else None),
        "right_ankle_x": _round(right_ankle[0] if right_ankle else None),
        "right_ankle_y": _round(right_ankle[1] if right_ankle else None),
        "left_heel_x": _round(left_heel[0] if left_heel else None),
        "left_heel_y": _round(left_heel[1] if left_heel else None),
        "left_toe_x": _round(left_toe[0] if left_toe else None),
        "left_toe_y": _round(left_toe[1] if left_toe else None),
        "right_heel_x": _round(right_heel[0] if right_heel else None),
        "right_heel_y": _round(right_heel[1] if right_heel else None),
        "right_toe_x": _round(right_toe[0] if right_toe else None),
        "right_toe_y": _round(right_toe[1] if right_toe else None),
        "left_foot_low_y": _round(left_foot_low_y),
        "right_foot_low_y": _round(right_foot_low_y),
    }

    row.update({
        "forward_lean_deg": _round(angle_to_vertical(pelvis, shoulder)),
        "left_knee_angle_deg": _round(angle_between(pt(points, 23), pt(points, 25), pt(points, 27))),
        "right_knee_angle_deg": _round(angle_between(pt(points, 24), pt(points, 26), pt(points, 28))),
        "left_shank_angle_deg": _round(angle_to_vertical(pt(points, 27), pt(points, 25))),
        "right_shank_angle_deg": _round(angle_to_vertical(pt(points, 28), pt(points, 26))),
        "left_thigh_angle_deg": _round(angle_to_vertical(pt(points, 23), pt(points, 25))),
        "right_thigh_angle_deg": _round(angle_to_vertical(pt(points, 24), pt(points, 26))),
        "left_foot_angle_deg": _round(angle_to_horizontal(left_heel, left_toe)),
        "right_foot_angle_deg": _round(angle_to_horizontal(right_heel, right_toe)),
    })

    # Side-view landing candidates and overstride proxy.
    if pelvis and left_ankle and right_ankle:
        active = "left" if (left_foot_low_y or -1) >= (right_foot_low_y or -1) else "right"
        ankle = left_ankle if active == "left" else right_ankle
        row["landing_foot_candidate"] = active
        row["landing_ankle_x"] = _round(ankle[0])
        row["landing_ankle_y"] = _round(ankle[1])
        row["pelvis_to_landing_ankle_dx_px"] = _round(ankle[0] - pelvis[0])
    else:
        row["landing_foot_candidate"] = ""
        row["landing_ankle_x"] = ""
        row["landing_ankle_y"] = ""
        row["pelvis_to_landing_ankle_dx_px"] = ""

    # Rear-view features.
    row["rear_pelvic_tilt_deg"] = _round(angle_to_horizontal(pt(points, 23), pt(points, 24)))
    row["rear_trunk_lateral_tilt_deg"] = _round(angle_to_vertical(pelvis, shoulder))
    row["left_knee_medial_offset_px"] = _round(line_offset_px(pt(points, 25), pt(points, 23), pt(points, 27)))
    row["right_knee_medial_offset_px"] = _round(line_offset_px(pt(points, 26), pt(points, 24), pt(points, 28)))
    if left_ankle and right_ankle:
        row["step_width_px"] = _round(abs(left_ankle[0] - right_ankle[0]))
        center_x = pelvis[0] if pelvis else (left_ankle[0] + right_ankle[0]) / 2.0
        row["crossover_flag"] = bool((left_ankle[0] - center_x) * (right_ankle[0] - center_x) > 0)
    else:
        row["step_width_px"] = ""
        row["crossover_flag"] = ""

    return row


def infer_contacts(frame_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not frame_rows:
        return []
    left_y = [float(r["left_foot_low_y"]) for r in frame_rows if r.get("left_foot_low_y") not in ("", None)]
    right_y = [float(r["right_foot_low_y"]) for r in frame_rows if r.get("right_foot_low_y") not in ("", None)]
    all_y = left_y + right_y
    if not all_y:
        for r in frame_rows:
            r.update({"left_foot_contact": False, "right_foot_contact": False, "support_phase": "unknown", "active_support_foot": ""})
        return frame_rows
    ground_y = float(np.percentile(all_y, 95))
    threshold = max(8.0, abs(ground_y) * 0.015)
    prev_pelvis_x = None
    prev_t = None
    prev_pelvis_y = None
    for r in frame_rows:
        ly, ry = r.get("left_foot_low_y"), r.get("right_foot_low_y")
        left_contact = ly not in ("", None) and float(ly) >= ground_y - threshold
        right_contact = ry not in ("", None) and float(ry) >= ground_y - threshold
        if left_contact and not right_contact:
            phase, active = "left_support", "left"
        elif right_contact and not left_contact:
            phase, active = "right_support", "right"
        elif left_contact and right_contact:
            phase, active = "double_support", "both"
        else:
            phase, active = "flight", ""
        r.update({
            "ground_y_px": round(ground_y, 3),
            "contact_threshold_px": round(threshold, 3),
            "left_foot_contact": bool(left_contact),
            "right_foot_contact": bool(right_contact),
            "support_phase": phase,
            "active_support_foot": active,
        })
        px = r.get("pelvis_center_x")
        py = r.get("pelvis_center_y")
        ts = r.get("timestamp_sec")
        try:
            if prev_pelvis_x is not None and px not in ("", None) and prev_t is not None and float(ts) > prev_t:
                dt = float(ts) - prev_t
                r["pelvis_vx_px_s"] = round((float(px) - prev_pelvis_x) / dt, 3)
                if prev_pelvis_y is not None and py not in ("", None):
                    r["pelvis_vy_px_s"] = round((float(py) - prev_pelvis_y) / dt, 3)
                else:
                    r["pelvis_vy_px_s"] = ""
            else:
                r["pelvis_vx_px_s"] = ""
                r["pelvis_vy_px_s"] = ""
            if px not in ("", None):
                prev_pelvis_x = float(px)
            if py not in ("", None):
                prev_pelvis_y = float(py)
            prev_t = float(ts)
        except Exception:
            r["pelvis_vx_px_s"] = ""
            r["pelvis_vy_px_s"] = ""
    return frame_rows


def _mean(vals):
    nums = [float(v) for v in vals if v not in ("", None) and str(v).lower() != "nan"]
    return round(float(np.mean(nums)), 3) if nums else ""


def _max(vals):
    nums = [float(v) for v in vals if v not in ("", None) and str(v).lower() != "nan"]
    return round(float(np.max(nums)), 3) if nums else ""


def _min(vals):
    nums = [float(v) for v in vals if v not in ("", None) and str(v).lower() != "nan"]
    return round(float(np.min(nums)), 3) if nums else ""


def _event_foot_angle(row: dict[str, Any], foot: str):
    return row.get(f"{foot}_foot_angle_deg", "")


def _foot_strike_type(row: dict[str, Any], foot: str) -> str:
    heel_y = row.get(f"{foot}_heel_y")
    toe_y = row.get(f"{foot}_toe_y")
    if heel_y in ("", None) or toe_y in ("", None):
        return "unknown"
    diff = float(heel_y) - float(toe_y)
    if diff > 8:
        return "heel_candidate"
    if diff < -8:
        return "forefoot_candidate"
    return "midfoot_candidate"


def _window_mean_vx(rows: list[dict[str, Any]], center_idx: int, before: bool, n: int = 3):
    if before:
        subset = rows[max(0, center_idx - n):center_idx]
    else:
        subset = rows[center_idx + 1:min(len(rows), center_idx + 1 + n)]
    return _mean([r.get("pelvis_vx_px_s") for r in subset])


def detect_gait_events(frame_rows: list[dict[str, Any]], view_type: str = "side") -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not frame_rows:
        return events
    for foot in ["left", "right"]:
        contact_key = f"{foot}_foot_contact"
        prev = bool(frame_rows[0].get(contact_key))
        start_i = 0 if prev else None
        for i in range(1, len(frame_rows)):
            curr = bool(frame_rows[i].get(contact_key))
            if curr and not prev:
                start_i = i
            if prev and not curr and start_i is not None:
                events.append(_build_event(frame_rows, start_i, i - 1, foot, len(events) + 1, view_type))
                start_i = None
            prev = curr
        if start_i is not None and start_i < len(frame_rows) - 1:
            events.append(_build_event(frame_rows, start_i, len(frame_rows) - 1, foot, len(events) + 1, view_type, incomplete=True))
    events.sort(key=lambda e: e.get("initial_contact_time_sec", 0))
    for idx, event in enumerate(events, start=1):
        event["event_id"] = idx
    return events


def _build_event(rows: list[dict[str, Any]], start_i: int, end_i: int, foot: str, event_id: int, view_type: str, incomplete: bool = False) -> dict[str, Any]:
    start = rows[start_i]
    end = rows[end_i]
    contact_ms = max(0.0, (float(end.get("timestamp_sec", 0)) - float(start.get("timestamp_sec", 0))) * 1000.0)
    early_end_i = min(end_i, start_i + max(1, int(round((end_i - start_i + 1) * 0.30))))
    early_end = rows[early_end_i]
    before_vx = _window_mean_vx(rows, start_i, before=True)
    after_vx = _window_mean_vx(rows, start_i, before=False)
    decel = ""
    try:
        if before_vx not in ("", None) and after_vx not in ("", None):
            decel = round(float(after_vx) - float(before_vx), 3)
    except Exception:
        pass
    knee = start.get(f"{foot}_knee_angle_deg", "")
    shank = start.get(f"{foot}_shank_angle_deg", "")
    ankle_x = start.get(f"{foot}_ankle_x", "")
    ankle_y = start.get(f"{foot}_ankle_y", "")
    pelvis_x = start.get("pelvis_center_x", "")
    pelvis_y = start.get("pelvis_center_y", "")
    dx = ""
    try:
        if ankle_x not in ("", None) and pelvis_x not in ("", None):
            dx = round(float(ankle_x) - float(pelvis_x), 3)
    except Exception:
        pass
    return {
        "event_id": event_id,
        "view_type": view_type,
        "foot": foot,
        "event_type": "initial_contact_to_toe_off" if not incomplete else "initial_contact_to_clip_end",
        "initial_contact_frame": start.get("frame_index", ""),
        "initial_contact_time_sec": start.get("timestamp_sec", ""),
        "toe_off_frame": end.get("frame_index", ""),
        "toe_off_time_sec": end.get("timestamp_sec", ""),
        "contact_time_ms": round(contact_ms, 1),
        "initial_support_start_sec": start.get("timestamp_sec", ""),
        "initial_support_end_sec": early_end.get("timestamp_sec", ""),
        "support_duration_ms": round(max(0.0, (float(early_end.get("timestamp_sec", 0)) - float(start.get("timestamp_sec", 0))) * 1000.0), 1),
        "pelvis_center_x_at_contact": pelvis_x,
        "pelvis_center_y_at_contact": pelvis_y,
        "landing_ankle_x": ankle_x,
        "landing_ankle_y": ankle_y,
        "pelvis_to_landing_ankle_dx_px": dx,
        "knee_angle_at_contact_deg": knee,
        "shank_angle_at_contact_deg": shank,
        "foot_angle_at_contact_deg": _event_foot_angle(start, foot),
        "foot_strike_type_estimate": _foot_strike_type(start, foot),
        "pelvis_vx_before_contact_px_s": before_vx,
        "pelvis_vx_after_contact_px_s": after_vx,
        "pelvis_forward_deceleration_px_s2_proxy": decel,
        "confidence_contact": "medium" if not incomplete else "low_clip_boundary",
        "confidence_foot_strike": "medium",
        "confidence_event": "medium" if not incomplete else "low_clip_boundary",
        "missing_reason": "" if not incomplete else "toe-off not observed before clip end",
    }


def build_second_summary(frame_rows: list[dict[str, Any]], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[int, list[dict[str, Any]]] = {}
    for r in frame_rows:
        sec = int(float(r.get("timestamp_sec", 0)))
        groups.setdefault(sec, []).append(r)
    event_groups: dict[int, list[dict[str, Any]]] = {}
    for e in events:
        try:
            sec = int(float(e.get("initial_contact_time_sec", 0)))
            event_groups.setdefault(sec, []).append(e)
        except Exception:
            pass
    out = []
    for sec in sorted(groups):
        rows = groups[sec]
        evs = event_groups.get(sec, [])
        valid = [r for r in rows if r.get("pose_detected")]
        duration = max(1e-6, (float(rows[-1].get("timestamp_sec", 0)) - float(rows[0].get("timestamp_sec", 0)) + 1.0 / max(float(rows[0].get("source_fps", 30) or 30), 1)))
        out.append({
            "second": sec,
            "frame_start": rows[0].get("frame_index", ""),
            "frame_end": rows[-1].get("frame_index", ""),
            "pose_detection_rate": round(len(valid) / max(len(rows), 1), 3),
            "mean_forward_lean_deg": _mean([r.get("forward_lean_deg") for r in rows]),
            "mean_left_knee_angle_deg": _mean([r.get("left_knee_angle_deg") for r in rows]),
            "mean_right_knee_angle_deg": _mean([r.get("right_knee_angle_deg") for r in rows]),
            "mean_left_shank_angle_deg": _mean([r.get("left_shank_angle_deg") for r in rows]),
            "mean_right_shank_angle_deg": _mean([r.get("right_shank_angle_deg") for r in rows]),
            "mean_pelvis_vx_px_s": _mean([r.get("pelvis_vx_px_s") for r in rows]),
            "mean_pelvis_vertical_position_px": _mean([r.get("pelvis_center_y") for r in rows]),
            "left_contact_frame_count": sum(1 for r in rows if r.get("left_foot_contact")),
            "right_contact_frame_count": sum(1 for r in rows if r.get("right_foot_contact")),
            "contact_event_count": len(evs),
            "estimated_cadence_spm": round(len(evs) / duration * 60.0, 3) if evs else "",
            "mean_contact_time_ms": _mean([e.get("contact_time_ms") for e in evs]),
            "mean_pelvis_to_ankle_dx_px": _mean([e.get("pelvis_to_landing_ankle_dx_px") for e in evs]),
        })
    return out


def build_clip_summary(frame_rows: list[dict[str, Any]], events: list[dict[str, Any]], motionmetrix_values: dict[str, Any] | None = None) -> dict[str, Any]:
    motionmetrix_values = motionmetrix_values or {}
    if not frame_rows:
        return {}
    duration = max(1e-6, float(frame_rows[-1].get("timestamp_sec", 0)) - float(frame_rows[0].get("timestamp_sec", 0)))
    left_events = [e for e in events if e.get("foot") == "left"]
    right_events = [e for e in events if e.get("foot") == "right"]
    pelvis_y = [r.get("pelvis_center_y") for r in frame_rows]
    pelvis_y_nums = [float(v) for v in pelvis_y if v not in ("", None)]
    vertical_osc = round(max(pelvis_y_nums) - min(pelvis_y_nums), 3) if pelvis_y_nums else ""
    left_thigh_vals = [r.get("left_thigh_angle_deg") for r in frame_rows]
    right_thigh_vals = [r.get("right_thigh_angle_deg") for r in frame_rows]
    left_knee_vals = [r.get("left_knee_angle_deg") for r in frame_rows]
    right_knee_vals = [r.get("right_knee_angle_deg") for r in frame_rows]
    left_thigh_rom = None
    right_thigh_rom = None
    try:
        lt_nums = [float(v) for v in left_thigh_vals if v not in ("", None)]
        rt_nums = [float(v) for v in right_thigh_vals if v not in ("", None)]
        left_thigh_rom = round(max(lt_nums) - min(lt_nums), 3) if lt_nums else ""
        right_thigh_rom = round(max(rt_nums) - min(rt_nums), 3) if rt_nums else ""
    except Exception:
        left_thigh_rom, right_thigh_rom = "", ""
    try:
        lk_nums = [float(v) for v in left_knee_vals if v not in ("", None)]
        rk_nums = [float(v) for v in right_knee_vals if v not in ("", None)]
        left_knee_rom = round(max(lk_nums) - min(lk_nums), 3) if lk_nums else ""
        right_knee_rom = round(max(rk_nums) - min(rk_nums), 3) if rk_nums else ""
    except Exception:
        left_knee_rom, right_knee_rom = "", ""

    summary = {
        "valid_duration_sec": round(duration, 3),
        "valid_frame_count": len(frame_rows),
        "pose_detection_rate": round(sum(1 for r in frame_rows if r.get("pose_detected")) / max(len(frame_rows), 1), 3),
        "left_step_count": len(left_events),
        "right_step_count": len(right_events),
        "estimated_cadence_spm": round(len(events) / duration * 60.0, 3) if duration > 0 else "",
        "forward_lean_avg_deg": _mean([r.get("forward_lean_deg") for r in frame_rows]),
        "left_contact_time_avg_ms": _mean([e.get("contact_time_ms") for e in left_events]),
        "right_contact_time_avg_ms": _mean([e.get("contact_time_ms") for e in right_events]),
        "contact_time_avg_ms": _mean([e.get("contact_time_ms") for e in events]),
        "left_overstride_avg_px": _mean([e.get("pelvis_to_landing_ankle_dx_px") for e in left_events]),
        "right_overstride_avg_px": _mean([e.get("pelvis_to_landing_ankle_dx_px") for e in right_events]),
        "overstride_avg_px": _mean([e.get("pelvis_to_landing_ankle_dx_px") for e in events]),
        "left_knee_angle_at_contact_avg_deg": _mean([e.get("knee_angle_at_contact_deg") for e in left_events]),
        "right_knee_angle_at_contact_avg_deg": _mean([e.get("knee_angle_at_contact_deg") for e in right_events]),
        "knee_angle_at_contact_avg_deg": _mean([e.get("knee_angle_at_contact_deg") for e in events]),
        "left_shank_angle_at_contact_avg_deg": _mean([e.get("shank_angle_at_contact_deg") for e in left_events]),
        "right_shank_angle_at_contact_avg_deg": _mean([e.get("shank_angle_at_contact_deg") for e in right_events]),
        "shank_angle_at_contact_avg_deg": _mean([e.get("shank_angle_at_contact_deg") for e in events]),
        "left_foot_angle_at_contact_avg_deg": _mean([e.get("foot_angle_at_contact_deg") for e in left_events]),
        "right_foot_angle_at_contact_avg_deg": _mean([e.get("foot_angle_at_contact_deg") for e in right_events]),
        "foot_angle_at_contact_avg_deg": _mean([e.get("foot_angle_at_contact_deg") for e in events]),
        "foot_strike_type_summary": ", ".join(sorted(set(str(e.get("foot_strike_type_estimate", "")) for e in events if e.get("foot_strike_type_estimate")))) or "",
        "pelvis_vertical_oscillation_px": vertical_osc,
        "pelvis_forward_deceleration_avg_px_s2_proxy": _mean([e.get("pelvis_forward_deceleration_px_s2_proxy") for e in events]),
        "left_hip_rom_est_deg": left_thigh_rom,
        "right_hip_rom_est_deg": right_thigh_rom,
        "hip_rom_avg_deg": _mean([left_thigh_rom, right_thigh_rom]),
        "hip_rom_asymmetry_deg": round(abs(float(left_thigh_rom) - float(right_thigh_rom)), 3) if left_thigh_rom not in ("", None) and right_thigh_rom not in ("", None) else "",
        "left_knee_rom_est_deg": left_knee_rom,
        "right_knee_rom_est_deg": right_knee_rom,
        "knee_rom_avg_deg": _mean([left_knee_rom, right_knee_rom]),
        "knee_rom_asymmetry_deg": round(abs(float(left_knee_rom) - float(right_knee_rom)), 3) if left_knee_rom not in ("", None) and right_knee_rom not in ("", None) else "",
        "rear_pelvic_tilt_avg_deg": _mean([r.get("rear_pelvic_tilt_deg") for r in frame_rows]),
        "rear_trunk_lateral_tilt_avg_deg": _mean([r.get("rear_trunk_lateral_tilt_deg") for r in frame_rows]),
        "knee_medial_collapse_avg_px": _mean([abs(float(v)) for r in frame_rows for v in [r.get("left_knee_medial_offset_px"), r.get("right_knee_medial_offset_px")] if v not in ("", None)]),
        "step_width_avg_px": _mean([r.get("step_width_px") for r in frame_rows]),
        "crossover_ratio": round(sum(1 for r in frame_rows if r.get("crossover_flag") is True) / max(len(frame_rows), 1), 3),
    }
    for k, v in motionmetrix_values.items():
        if v not in ("", None, []):
            summary[f"motionmetrix_target_{k}"] = v
    return summary


def nearest_event(events: list[dict[str, Any]], timestamp_sec: float) -> dict[str, Any] | None:
    if not events:
        return None
    return min(events, key=lambda e: abs(float(e.get("initial_contact_time_sec", 0) or 0) - timestamp_sec))


def insight_lines(frame_row: dict[str, Any], event: dict[str, Any] | None, view_type: str = "side", max_lines: int = 10) -> list[str]:
    if not frame_row:
        return ["No pose features"]
    lines = [f"Time {frame_row.get('timestamp_sec', '')}s | Frame {frame_row.get('frame_index', '')}"]
    if view_type.startswith("rear") or view_type == "rear":
        items = [
            ("Pelvic Tilt", frame_row.get("rear_pelvic_tilt_deg"), "deg"),
            ("Trunk Tilt", frame_row.get("rear_trunk_lateral_tilt_deg"), "deg"),
            ("Knee Offset L", frame_row.get("left_knee_medial_offset_px"), "px"),
            ("Knee Offset R", frame_row.get("right_knee_medial_offset_px"), "px"),
            ("Step Width", frame_row.get("step_width_px"), "px"),
            ("Crossover", frame_row.get("crossover_flag"), ""),
        ]
    else:
        items = [
            ("Support", frame_row.get("support_phase"), ""),
            ("Forward Lean", frame_row.get("forward_lean_deg"), "deg"),
            ("Pelvis-Ankle X", frame_row.get("pelvis_to_landing_ankle_dx_px"), "px"),
            ("Knee L/R", f"{frame_row.get('left_knee_angle_deg','')}/{frame_row.get('right_knee_angle_deg','')}", "deg"),
            ("Shank L/R", f"{frame_row.get('left_shank_angle_deg','')}/{frame_row.get('right_shank_angle_deg','')}", "deg"),
            ("Foot Angle L/R", f"{frame_row.get('left_foot_angle_deg','')}/{frame_row.get('right_foot_angle_deg','')}", "deg"),
            ("Pelvis Vx", frame_row.get("pelvis_vx_px_s"), "px/s"),
        ]
    for name, val, unit in items:
        if val not in ("", None):
            lines.append(f"{name}: {val}{(' ' + unit) if unit else ''}")
        if len(lines) >= max_lines:
            break
    if event:
        lines.append(f"IC: {event.get('foot','')} {event.get('initial_contact_time_sec','')}s")
        lines.append(f"Contact: {event.get('contact_time_ms','')} ms")
        lines.append(f"Strike: {event.get('foot_strike_type_estimate','')}")
    return lines[:max_lines]


def direct_target_lines(view_type: str = "side") -> list[str]:
    targets = REAR_DIRECT_TARGETS if view_type == "rear" else SIDE_DIRECT_TARGETS
    return ["MM Target Input:"] + [f"- {t}" for t in targets[:7]]


def write_csv(path: Path, rows: list[dict[str, Any]] | dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(rows, dict):
        rows = [rows]
    fieldnames = sorted({k for row in rows for k in row.keys()}) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        if not fieldnames:
            f.write("")
            return
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

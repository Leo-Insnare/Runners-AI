from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .storage import BASE_DIR, session_path, write_json, read_json

try:
    import cv2
except Exception:
    cv2 = None

try:
    import mediapipe as mp
except Exception:
    mp = None

MP_POSE = None
MP_IMPORT_ERROR = None
MP_VERSION = None
if mp is not None:
    MP_VERSION = getattr(mp, "__version__", "unknown")
    try:
        MP_POSE = mp.solutions.pose
    except Exception as exc:
        try:
            from mediapipe.python.solutions import pose as MP_POSE
        except Exception as fallback_exc:
            MP_POSE = None
            MP_IMPORT_ERROR = (
                f"현재 mediapipe {MP_VERSION}에서 legacy mp.solutions.pose를 찾지 못했습니다. "
                "mediapipe 0.10.31 이상에서는 기존 Solutions API가 제거되어 Preview가 동작하지 않습니다. "
                "requirements.txt 기준으로 mediapipe==0.10.21을 재설치해 주세요. "
                f"original: {exc}; fallback: {fallback_exc}"
            )
else:
    MP_IMPORT_ERROR = "mediapipe is not installed"

MP_POSE_IDS = {7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32}
POSE_EDGES = [
    (7, 11), (8, 12), (11, 12),
    (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (25, 27), (27, 29), (27, 31),
    (24, 26), (26, 28), (28, 30), (28, 32),
]

WORKFLOW_STEPS = [
    {
        "step_id": "rear_static",
        "title": "1. 후면 전신 정지 2~3초",
        "slot": "rear_static",
        "view": "rear",
        "guide": "후면 중앙에서 전신이 보이도록 세우고 골반 23·24, 발목 27·28, 몸통 중심선을 확인합니다.",
        "metrics": ["pelvic_drop", "trunk_lateral_tilt"],
    },
    {
        "step_id": "rear_running",
        "title": "2. 후면 달리기 촬영/확인",
        "slot": "rear_running",
        "view": "rear",
        "guide": "골반 낙하, 무릎 안쪽 붕괴, 스텝 폭/크로스오버, 몸통 좌우 기울기를 확인합니다.",
        "metrics": ["pelvic_drop", "knee_medial_collapse", "step_width_crossover", "trunk_lateral_tilt"],
    },
    {
        "step_id": "side_static",
        "title": "3. 측면 전신 정지 2~3초",
        "slot": "side_static",
        "view": "side",
        "guide": "측면에서 어깨 중심, 골반 중심, 수직 기준선, 지면선을 확인합니다.",
        "metrics": ["forward_lean_deg"],
    },
    {
        "step_id": "side_running",
        "title": "4. 측면 달리기 촬영/확인",
        "slot": "side_running",
        "view": "side",
        "guide": "Forward Lean, Overstride, Shank Angle, Contact Time 등 측면 지표를 확인합니다.",
        "metrics": ["forward_lean_deg", "overstride", "braking_force", "hip_thigh_flexion_extension", "knee_flexion_rom", "shank_angle", "foot_strike_type", "cadence", "contact_time", "vertical_oscillation", "step_stride_length", "flight_time"],
    },
]


def python_runtime_status() -> dict[str, Any]:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    preview_supported = (sys.version_info.major == 3 and 9 <= sys.version_info.minor <= 12)
    return {"version": version, "preview_supported": preview_supported}


def dependencies_status() -> dict[str, bool | str]:
    py = python_runtime_status()
    return {
        "python_version": py["version"],
        "python_preview_supported": py["preview_supported"],
        "opencv": cv2 is not None,
        "mediapipe": MP_POSE is not None,
        "mediapipe_version": MP_VERSION or "not_installed",
    }


def dependency_message() -> str:
    py = python_runtime_status()
    if not py["preview_supported"]:
        return (
            f"현재 Python {py['version']} 환경입니다. Skeleton Preview는 MediaPipe 호환성을 위해 "
            "Python 3.9~3.12 환경을 권장합니다. Windows에서는 setup_windows.bat로 전용 가상환경을 생성해 주세요."
        )
    if cv2 is None and MP_POSE is None:
        return "OpenCV와 MediaPipe Pose backend를 사용할 수 없습니다. requirements.txt 기준으로 재설치해 주세요."
    if cv2 is None:
        return "OpenCV를 사용할 수 없습니다. opencv-python-headless를 재설치해 주세요."
    if MP_POSE is None:
        return (
            "MediaPipe Pose backend를 사용할 수 없습니다. "
            "현재 환경에 설치된 mediapipe가 legacy mp.solutions.pose를 제공하지 않는 버전일 수 있습니다. "
            "setup_windows.bat를 다시 실행하거나 아래 명령으로 재설치해 주세요: "
            "`.venv\\Scripts\\python.exe -m pip install --force-reinstall mediapipe==0.10.21 numpy<2 protobuf<5` "
            f"({MP_IMPORT_ERROR})"
        )
    return ""


def _to_pil(frame: Any) -> Image.Image:
    if isinstance(frame, Image.Image):
        return frame.convert("RGB")
    arr = np.asarray(frame)
    if arr.ndim == 2:
        return Image.fromarray(arr).convert("RGB")
    if arr.shape[-1] == 4:
        return Image.fromarray(arr[:, :, :3]).convert("RGB")
    return Image.fromarray(arr).convert("RGB")


def _pil_to_rgb_array(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("RGB"))


def extract_frame(video_path: Path, timestamp_sec: float) -> Image.Image:
    if cv2 is None:
        raise RuntimeError("OpenCV가 설치되어 있지 않습니다.")
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("영상을 열 수 없습니다.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_index = max(0, int(timestamp_sec * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("해당 시점의 프레임을 읽지 못했습니다.")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame)


def _detect_landmarks(image: Image.Image) -> dict[int, dict[str, float]]:
    if MP_POSE is None:
        return {}
    arr = _pil_to_rgb_array(image)
    with MP_POSE.Pose(static_image_mode=True, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5) as pose:
        result = pose.process(arr)
    if not result.pose_landmarks:
        return {}
    h, w = arr.shape[:2]
    points = {}
    for idx, lm in enumerate(result.pose_landmarks.landmark):
        if idx not in MP_POSE_IDS:
            continue
        points[idx] = {"x": float(lm.x * w), "y": float(lm.y * h), "visibility": float(getattr(lm, "visibility", 0.0))}
    return points


def _midpoint(points: dict[int, dict[str, float]], a: int, b: int):
    if a not in points or b not in points:
        return None
    return ((points[a]["x"] + points[b]["x"]) / 2, (points[a]["y"] + points[b]["y"]) / 2)


def _angle_between(p1, p2, p3) -> float | None:
    if not p1 or not p2 or not p3:
        return None
    v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]], dtype=float)
    v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]], dtype=float)
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return None
    cosang = float(np.clip(np.dot(v1, v2) / denom, -1.0, 1.0))
    return float(math.degrees(math.acos(cosang)))


def _line_angle_to_vertical(p_low, p_high) -> float | None:
    if not p_low or not p_high:
        return None
    dx = p_high[0] - p_low[0]
    dy = p_low[1] - p_high[1]
    if dy == 0 and dx == 0:
        return None
    return float(math.degrees(math.atan2(dx, dy)))


def _point_tuple(points, idx):
    if idx not in points:
        return None
    return (points[idx]["x"], points[idx]["y"])


def _fmt(v, unit=""):
    if v is None:
        return "N/A"
    return f"{v:.1f}{unit}"


def compute_reference_values(points: dict[int, dict[str, float]], metric_id: str) -> dict[str, str]:
    shoulder = _midpoint(points, 11, 12)
    pelvis = _midpoint(points, 23, 24)
    values: dict[str, str] = {}

    if metric_id == "forward_lean_deg":
        values["Forward Lean"] = _fmt(_line_angle_to_vertical(pelvis, shoulder), " deg")
        values["Basis"] = "pelvis center to shoulder center vs vertical axis"

    elif metric_id == "trunk_lateral_tilt":
        values["Trunk lateral tilt"] = _fmt(_line_angle_to_vertical(pelvis, shoulder), " deg")
        values["Basis"] = "shoulder center to pelvis center line in rear view"

    elif metric_id == "overstride":
        if pelvis and 27 in points and 28 in points:
            ankle_id = 27 if points[27]["y"] >= points[28]["y"] else 28
            px = points[ankle_id]["x"] - pelvis[0]
            values["Landing ankle candidate"] = f"point {ankle_id}"
            values["Pelvis-ankle horizontal distance"] = _fmt(px, " px")
            values["Note"] = "cm conversion requires scale calibration in phase 3"

    elif metric_id == "knee_flexion_rom":
        l = _angle_between(_point_tuple(points, 23), _point_tuple(points, 25), _point_tuple(points, 27))
        r = _angle_between(_point_tuple(points, 24), _point_tuple(points, 26), _point_tuple(points, 28))
        values["Left knee angle"] = _fmt(l, " deg")
        values["Right knee angle"] = _fmt(r, " deg")

    elif metric_id == "hip_thigh_flexion_extension":
        if 23 in points and 25 in points:
            values["Left thigh vs vertical"] = _fmt(_line_angle_to_vertical(_point_tuple(points, 23), _point_tuple(points, 25)), " deg")
        if 24 in points and 26 in points:
            values["Right thigh vs vertical"] = _fmt(_line_angle_to_vertical(_point_tuple(points, 24), _point_tuple(points, 26)), " deg")

    elif metric_id == "shank_angle":
        values["Left shank angle"] = _fmt(_line_angle_to_vertical(_point_tuple(points, 27), _point_tuple(points, 25)), " deg")
        values["Right shank angle"] = _fmt(_line_angle_to_vertical(_point_tuple(points, 28), _point_tuple(points, 26)), " deg")

    elif metric_id == "pelvic_drop":
        if 23 in points and 24 in points:
            values["Pelvis line tilt"] = _fmt(_line_angle_to_vertical(_point_tuple(points, 23), _point_tuple(points, 24)), " deg")
            values["Basis"] = "left hip point 23 to right hip point 24"

    elif metric_id == "knee_medial_collapse":
        l = _angle_between(_point_tuple(points, 23), _point_tuple(points, 25), _point_tuple(points, 27))
        r = _angle_between(_point_tuple(points, 24), _point_tuple(points, 26), _point_tuple(points, 28))
        values["Left hip-knee-ankle alignment"] = _fmt(l, " deg")
        values["Right hip-knee-ankle alignment"] = _fmt(r, " deg")

    elif metric_id == "step_width_crossover":
        if 27 in points and 28 in points:
            values["Ankle horizontal distance"] = _fmt(abs(points[27]["x"] - points[28]["x"]), " px")
            values["Note"] = "crossover decision requires segment/centerline review"

    elif metric_id == "foot_strike_type":
        if 29 in points and 31 in points:
            values["Left heel-toe height diff"] = _fmt(points[29]["y"] - points[31]["y"], " px")
        if 30 in points and 32 in points:
            values["Right heel-toe height diff"] = _fmt(points[30]["y"] - points[32]["y"], " px")
        values["Note"] = "foot strike type is saved as manual input"

    elif metric_id in {"contact_time", "cadence", "flight_time", "vertical_oscillation", "step_stride_length", "braking_force"}:
        values["Note"] = "event/segment-based metric; current frame is for point verification"

    detected = len([k for k, v in points.items() if v.get("visibility", 0) >= 0.5])
    values["Detected points"] = f"{detected}/{len(MP_POSE_IDS)}"
    return values

def overlay_pose(image: Image.Image, metric: dict[str, Any] | None = None, show_all: bool = False) -> tuple[Image.Image, dict[str, str]]:
    metric = metric or {}
    active_points = {int(p) for p in metric.get("required_points", []) if str(p).isdigit()}
    image = _to_pil(image)
    draw = ImageDraw.Draw(image)
    if MP_POSE is None:
        msg = dependency_message()
        draw.rounded_rectangle((10, 10, min(image.width - 10, 820), 88), radius=8, fill=(255, 255, 255))
        draw.text((18, 22), "MediaPipe Pose backend unavailable", fill=(0, 0, 0))
        draw.text((18, 46), "Use Python 3.9-3.12 venv and run setup_windows.bat", fill=(0, 0, 0))
        draw.text((18, 68), "Saved video upload and manual labeling still work.", fill=(0, 0, 0))
        return image, {"Status": "MediaPipe Pose backend unavailable", "Action": "Run setup_windows.bat or reinstall dependencies from requirements.txt", "Detail": msg}
    points = _detect_landmarks(image)
    stats = compute_reference_values(points, metric.get("metric_id", "")) if points else {"Status": "Pose landmark detection failed"}

    if not points:
        draw.rounded_rectangle((10, 10, min(image.width - 10, 680), 72), radius=8, fill=(255, 255, 255))
        draw.text((18, 22), "Pose landmark detection failed", fill=(0, 0, 0))
        draw.text((18, 46), "Check full-body visibility, lighting, and frame timing.", fill=(0, 0, 0))
        return image, stats

    visible_points = set(points) if show_all or not active_points else active_points
    for a, b in POSE_EDGES:
        if a in points and b in points and (show_all or a in visible_points or b in visible_points):
            color = (60, 180, 120) if (a in active_points or b in active_points) else (150, 150, 150)
            draw.line([(points[a]["x"], points[a]["y"]), (points[b]["x"], points[b]["y"])], fill=color, width=4 if color[1] == 180 else 2)

    shoulder = _midpoint(points, 11, 12)
    pelvis = _midpoint(points, 23, 24)
    if shoulder and pelvis:
        draw.line([pelvis, shoulder], fill=(255, 140, 0), width=4)
        draw.line([(pelvis[0], 0), (pelvis[0], image.height)], fill=(80, 160, 255), width=2)
    foot_ys = [points[i]["y"] for i in [29, 30, 31, 32] if i in points]
    if foot_ys:
        ground_y = max(foot_ys)
        draw.line([(0, ground_y), (image.width, ground_y)], fill=(255, 80, 80), width=2)

    for idx, p in points.items():
        if idx not in visible_points:
            continue
        active = idx in active_points
        r = 7 if active else 5
        fill = (255, 200, 0) if active else (235, 235, 235)
        outline = (0, 0, 0)
        x, y = p["x"], p["y"]
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=2)
        draw.text((x + 8, y - 8), str(idx), fill=(0, 0, 0))

    y = 12
    title = metric.get("display_name_en") or metric.get("metric_id", "Skeleton Preview")
    info_lines = [title] + [f"{k}: {v}" for k, v in list(stats.items())[:6]]
    for line in info_lines:
        box_w = min(image.width - 20, max(360, len(line) * 12))
        draw.rounded_rectangle((10, y - 4, box_w, y + 22), radius=6, fill=(255, 255, 255))
        draw.text((18, y), line, fill=(0, 0, 0))
        y += 28
    return image, stats


def _safe_slug(value: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "_-" else "_" for c in str(value))
    return cleaned.strip("_") or "overlay"


def create_overlay_video(
    session_id: str,
    video_path: Path,
    metric: dict[str, Any],
    start_sec: float = 0.0,
    duration_sec: float = 5.0,
    output_fps: float = 10.0,
    show_all: bool = False,
    progress_callback=None,
) -> dict[str, Any]:
    """Create a short downloadable Skeleton Overlay result video and per-frame CSV.

    This is intentionally a bounded preview/export helper for customer validation.
    Long full-video processing belongs to phase 3 or an offline batch pipeline.
    """
    if cv2 is None:
        raise RuntimeError("OpenCV가 설치되어 있지 않습니다.")
    if MP_POSE is None:
        raise RuntimeError(dependency_message() or "MediaPipe Pose backend를 사용할 수 없습니다.")

    start_sec = max(0.0, float(start_sec or 0.0))
    duration_sec = max(0.5, min(float(duration_sec or 5.0), 30.0))
    output_fps = max(1.0, min(float(output_fps or 10.0), 20.0))

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("영상을 열 수 없습니다.")

    source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if width <= 0 or height <= 0:
        cap.release()
        raise RuntimeError("영상 크기 정보를 읽지 못했습니다.")

    start_frame = int(start_sec * source_fps)
    end_frame = int(min(frame_count if frame_count else start_frame + duration_sec * source_fps, start_frame + duration_sec * source_fps))
    if frame_count and start_frame >= frame_count:
        cap.release()
        raise RuntimeError("시작 시간이 영상 길이를 벗어났습니다.")
    frame_step = max(1, int(round(source_fps / output_fps)))
    expected_frames = max(1, len(range(start_frame, max(start_frame + 1, end_frame), frame_step)))

    out_dir = session_path(session_id) / "processed_videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metric_id = metric.get("metric_id", "metric")
    slug = _safe_slug(f"{Path(video_path).stem}_{metric_id}_{stamp}")
    output_video = out_dir / f"{slug}.mp4"
    output_csv = out_dir / f"{slug}_frame_stats.csv"
    output_meta = out_dir / f"{slug}_meta.json"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_video), fourcc, output_fps, (width, height))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("결과 영상 파일을 생성하지 못했습니다.")

    rows: list[dict[str, Any]] = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    processed = 0
    current_frame = start_frame
    try:
        while current_frame < end_frame:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ok, frame_bgr = cap.read()
            if not ok:
                break
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            overlay_img, stats = overlay_pose(Image.fromarray(frame_rgb), metric=metric, show_all=show_all)
            overlay_rgb = np.array(overlay_img.convert("RGB"))
            overlay_bgr = cv2.cvtColor(overlay_rgb, cv2.COLOR_RGB2BGR)
            writer.write(overlay_bgr)

            row = {
                "frame_index": current_frame,
                "timestamp_sec": round(current_frame / source_fps, 3),
                "metric_id": metric_id,
                "metric_name_kr": metric.get("display_name_kr", ""),
                "metric_name_en": metric.get("display_name_en", ""),
            }
            row.update({str(k): v for k, v in stats.items()})
            rows.append(row)
            processed += 1
            if progress_callback:
                progress_callback(min(1.0, processed / expected_frames))
            current_frame += frame_step
    finally:
        cap.release()
        writer.release()

    if processed == 0:
        try:
            output_video.unlink(missing_ok=True)
        except Exception:
            pass
        raise RuntimeError("처리 가능한 프레임이 없습니다. 시작 시간과 영상 길이를 확인하세요.")

    fieldnames = sorted({key for row in rows for key in row.keys()})
    with output_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer_csv = csv.DictWriter(f, fieldnames=fieldnames)
        writer_csv.writeheader()
        writer_csv.writerows(rows)

    meta = {
        "created_at": stamp,
        "source_video": str(Path(video_path).relative_to(BASE_DIR)) if Path(video_path).is_relative_to(BASE_DIR) else str(video_path),
        "result_video_path": str(output_video.relative_to(BASE_DIR)),
        "frame_stats_csv_path": str(output_csv.relative_to(BASE_DIR)),
        "metric_id": metric_id,
        "metric_name_kr": metric.get("display_name_kr", ""),
        "start_sec": start_sec,
        "duration_sec": duration_sec,
        "source_fps": round(float(source_fps), 3),
        "output_fps": output_fps,
        "frames_processed": processed,
        "show_all_points": show_all,
    }
    write_json(output_meta, meta)
    index_path = session_path(session_id) / "processed_videos.json"
    index = read_json(index_path, [])
    if not isinstance(index, list):
        index = []
    index.append(meta)
    write_json(index_path, index)
    return meta


def processed_video_results(session_id: str) -> list[dict[str, Any]]:
    rows = read_json(session_path(session_id) / "processed_videos.json", [])
    return rows if isinstance(rows, list) else []


def save_preview_result(session_id: str, image: Image.Image, meta: dict[str, Any]) -> str:
    base = session_path(session_id) / "preview"
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = base / f"preview_{stamp}.png"
    image.save(image_path)
    result = {
        "created_at": stamp,
        "image_path": str(image_path.relative_to(BASE_DIR)),
        **meta,
    }
    path = session_path(session_id) / "preview_results.json"
    rows = read_json(path, [])
    if not isinstance(rows, list):
        rows = []
    rows.append(result)
    write_json(path, rows)
    return result["image_path"]


def preview_summary_for_session(session_id: str) -> dict[str, Any]:
    rows = read_json(session_path(session_id) / "preview_results.json", [])
    if not isinstance(rows, list) or not rows:
        return {
            "preview_count": 0,
            "latest_preview_image_path": "",
            "latest_preview_metric_id": "",
            "latest_preview_step_id": "",
            "latest_preview_stats": "",
        }
    latest = rows[-1]
    return {
        "preview_count": len(rows),
        "latest_preview_image_path": latest.get("image_path", ""),
        "latest_preview_metric_id": latest.get("metric_id", ""),
        "latest_preview_step_id": latest.get("step_id", ""),
        "latest_preview_stats": json.dumps(latest.get("stats", {}), ensure_ascii=False),
    }

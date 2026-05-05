import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
import sys
import tempfile
import shutil

import cv2
import numpy as np

from .config import FRAME_HEIGHT, FRAME_WIDTH, JPEG_QUALITY, SESSION_TIMEOUT_SECONDS
from .database import insert_session, save_student_latest_results


@dataclass
class SessionStats:
    session_name: str = "Amaliy dars sessiyasi"
    started_at: float = field(default_factory=time.time)
    total_frames: int = 0
    face_frames: int = 0
    total_detected_faces: int = 0
    max_detected_faces: int = 0
    attentive_frames: int = 0
    movement_frames: int = 0
    score_sum: float = 0.0
    max_score: float = 0.0
    participant_scores: dict[str, dict] = field(default_factory=dict)

    def update(
        self,
        detected_faces: int,
        attentive_count: int,
        moving_count: int,
        score: float,
    ) -> None:
        self.total_frames += 1
        if detected_faces > 0:
            self.face_frames += 1
        if attentive_count > 0:
            self.attentive_frames += 1
        if moving_count > 0:
            self.movement_frames += 1
        self.total_detected_faces += detected_faces
        self.max_detected_faces = max(self.max_detected_faces, detected_faces)
        self.score_sum += score
        self.max_score = max(self.max_score, score)

    @property
    def absence_frames(self) -> int:
        return max(0, self.total_frames - self.face_frames)

    @property
    def duration_seconds(self) -> float:
        return max(0.0, time.time() - self.started_at)

    @property
    def presence_ratio(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return (self.face_frames / self.total_frames) * 100

    @property
    def attention_ratio(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return (self.attentive_frames / self.total_frames) * 100

    @property
    def movement_ratio(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return (self.movement_frames / self.total_frames) * 100

    @property
    def average_score(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return self.score_sum / self.total_frames

    @property
    def average_detected_faces(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return self.total_detected_faces / self.total_frames

    @property
    def participant_summary(self) -> list[dict]:
        summary: list[dict] = []
        for participant_id, data in sorted(self.participant_scores.items()):
            frames = data.get("frames", 0)
            event_counts = data.get("event_counts", {})
            summary.append(
                {
                    "participant_id": participant_id,
                    "assigned_name": data.get("assigned_name", ""),
                    "display_name": data.get("assigned_name") or participant_id,
                    "frames": frames,
                    "average_score": round(data["score_sum"] / frames, 2) if frames else 0.0,
                    "max_score": round(data.get("max_score", 0.0), 2),
                    "presence_ratio": round((frames / self.total_frames) * 100, 2) if self.total_frames else 0.0,
                    "event_counts": {
                        "phone_suspect": int(event_counts.get("phone_suspect", 0)),
                        "question_gesture": int(event_counts.get("question_gesture", 0)),
                        "drowsy_suspect": int(event_counts.get("drowsy_suspect", 0)),
                        "looking_away": int(event_counts.get("looking_away", 0)),
                    },
                }
            )
        return summary

    @property
    def event_totals(self) -> dict:
        totals = {
            "phone_suspect": 0,
            "question_gesture": 0,
            "drowsy_suspect": 0,
            "looking_away": 0,
        }
        for data in self.participant_scores.values():
            event_counts = data.get("event_counts", {})
            for key in totals:
                totals[key] += int(event_counts.get(key, 0))
        return totals

    def to_payload(self) -> dict:
        payload = asdict(self)
        payload.update(
            {
                "duration_seconds": round(self.duration_seconds, 1),
                "absence_frames": self.absence_frames,
                "presence_ratio": round(self.presence_ratio, 2),
                "attention_ratio": round(self.attention_ratio, 2),
                "movement_ratio": round(self.movement_ratio, 2),
                "average_score": round(self.average_score, 2),
                "average_detected_faces": round(self.average_detected_faces, 2),
                "max_score": round(self.max_score, 2),
                "participant_summary": self.participant_summary,
                "event_totals": self.event_totals,
            }
        )
        return payload


class ActivityMonitor:
    def __init__(self) -> None:
        self.face_detector = self._load_face_detector()
        self.face_detector_alt = self._load_face_detector("haarcascade_frontalface_alt2.xml")
        self.lock = threading.RLock()
        self.camera: cv2.VideoCapture | None = None
        self.stats = SessionStats()
        self.previous_face_rois: list[np.ndarray] = []
        self.last_frame: np.ndarray | None = None
        self.last_encoded_frame: bytes | None = None
        self.running = False
        self.last_error = ""
        self.last_face_seen_at: float | None = None
        self.active_camera_index = -1
        self.active_backend = "none"
        self.active_source_label = "webcam:auto"
        self.last_attempts: list[str] = []
        self.tracked_faces: list[dict] = []
        self.previous_gray_frame: np.ndarray | None = None

    def _load_face_detector(self, filename: str = "haarcascade_frontalface_default.xml") -> cv2.CascadeClassifier:
        candidate_paths = [
            Path(cv2.data.haarcascades) / filename,
            Path(sys.base_prefix) / "Lib" / "site-packages" / "cv2" / "data" / filename,
            Path(sys.base_prefix) / "lib" / "site-packages" / "cv2" / "data" / filename,
            Path.cwd() / "venv" / "Lib" / "site-packages" / "cv2" / "data" / filename,
        ]
        for path in candidate_paths:
            if path.exists():
                load_path = path
                # OpenCV on Windows can fail when XML is loaded from non-ASCII paths.
                # Copying the cascade to a temp ASCII path makes detector loading stable.
                safe_dir = Path(tempfile.gettempdir()) / "dars_faollik_cascades"
                safe_dir.mkdir(parents=True, exist_ok=True)
                safe_path = safe_dir / filename
                try:
                    shutil.copyfile(path, safe_path)
                    load_path = safe_path
                except OSError:
                    load_path = path

                detector = cv2.CascadeClassifier(str(load_path))
                if not detector.empty():
                    return detector
        return cv2.CascadeClassifier()

    def _detect_faces(self, gray: np.ndarray):
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        softened = cv2.GaussianBlur(enhanced, (5, 5), 0)

        detector_variants = [
            (self.face_detector, gray, 1.15, 5, (60, 60)),
            (self.face_detector, enhanced, 1.12, 4, (48, 48)),
            (self.face_detector_alt, enhanced, 1.1, 4, (48, 48)),
            (self.face_detector_alt, softened, 1.08, 4, (42, 42)),
        ]

        for detector, source, scale_factor, min_neighbors, min_size in detector_variants:
            if detector.empty():
                continue
            faces = detector.detectMultiScale(
                source,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
            )
            if len(faces) > 0:
                return faces

        return ()

    def start(
        self,
        camera_index: int = 0,
        session_name: str = "Amaliy dars sessiyasi",
        camera_source: str | None = None,
    ) -> None:
        with self.lock:
            if self.running:
                return
            normalized_source = (camera_source or "").strip()
            self.camera = self._open_camera(camera_index, normalized_source or None)
            if self.camera is None:
                self.active_camera_index = -1
                self.active_backend = "none"
                self.active_source_label = normalized_source or "webcam:auto"
                self.last_error = (
                    "Kamera ochilmadi. `0` yoki `1` indeksni sinab ko'ring, "
                    "yoki RTSP/IP manzil to'g'ri kiritilganini tekshiring."
                )
                raise RuntimeError(self.last_error)

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            self.stats = SessionStats(session_name=session_name)
            self.previous_face_rois = []
            self.tracked_faces = []
            self.last_frame = None
            self.last_encoded_frame = None
            self.previous_gray_frame = None
            self.running = True
            self.last_error = ""
            self.last_face_seen_at = None

    def _camera_candidates(
        self,
        preferred_index: int,
        camera_source: str | None,
    ) -> list[tuple[int | str, int | None, str, str]]:
        candidates: list[tuple[int | str, int | None, str, str]] = []
        if camera_source:
            if hasattr(cv2, "CAP_FFMPEG"):
                candidates.append((camera_source, int(cv2.CAP_FFMPEG), "FFmpeg", f"rtsp:{camera_source}"))
            if hasattr(cv2, "CAP_MSMF"):
                candidates.append((camera_source, int(cv2.CAP_MSMF), "MediaFoundation", f"stream:{camera_source}"))
            candidates.append((camera_source, None, "Auto", f"stream:{camera_source}"))
            return candidates

        preferred_order = []
        if preferred_index >= 0:
            preferred_order.append(preferred_index)
        for extra in (0, 1, 2, 3):
            if extra not in preferred_order:
                preferred_order.append(extra)

        for index in preferred_order:
            if hasattr(cv2, "CAP_DSHOW"):
                candidates.append((index, int(cv2.CAP_DSHOW), "DirectShow", f"webcam:{index}"))
            if hasattr(cv2, "CAP_MSMF"):
                candidates.append((index, int(cv2.CAP_MSMF), "MediaFoundation", f"webcam:{index}"))
            candidates.append((index, None, "Auto", f"webcam:{index}"))
        return candidates

    def _open_camera(self, preferred_index: int, camera_source: str | None = None) -> cv2.VideoCapture | None:
        self.last_attempts = []
        for index, backend_flag, backend_name, source_label in self._camera_candidates(preferred_index, camera_source):
            self.last_attempts.append(f"{backend_name}:{index}")
            camera = (
                cv2.VideoCapture(index, backend_flag)
                if backend_flag is not None
                else cv2.VideoCapture(index)
            )
            if not camera.isOpened():
                camera.release()
                continue

            camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

            readable = False
            for _ in range(12):
                ok, frame = camera.read()
                if ok and frame is not None and frame.size > 0:
                    readable = True
                    break
                time.sleep(0.08)

            if readable:
                self.active_camera_index = index if isinstance(index, int) else -1
                self.active_backend = backend_name
                self.active_source_label = source_label
                return camera

            camera.release()

        return None

    def stop(self, save: bool = True) -> dict | None:
        with self.lock:
            payload = None
            if save and self.stats.total_frames > 0:
                payload = self._save_current_session()

            if self.camera is not None:
                self.camera.release()
            self.camera = None
            self.running = False
            self.previous_face_rois = []
            self.tracked_faces = []
            self.last_frame = None
            self.last_encoded_frame = None
            self.previous_gray_frame = None
            self.active_camera_index = -1
            self.active_backend = "none"
            self.active_source_label = "webcam:auto"
            return payload

    def reset(self, session_name: str | None = None) -> None:
        with self.lock:
            current_name = session_name or self.stats.session_name
            self.stats = SessionStats(session_name=current_name)
            self.previous_face_rois = []
            self.tracked_faces = []
            self.previous_gray_frame = None
            self.last_face_seen_at = None

    def _match_faces(self, faces) -> list[dict]:
        previous_tracks = list(self.tracked_faces)
        matched: list[dict] = []

        for face_box in sorted(faces, key=lambda box: box[0]):
            x, y, w, h = face_box
            center_x = x + (w / 2)
            center_y = y + (h / 2)
            best_index = None
            best_distance = float("inf")

            for index, track in enumerate(previous_tracks):
                tx, ty = track["center"]
                distance = abs(center_x - tx) + abs(center_y - ty)
                if distance < best_distance:
                    best_distance = distance
                    best_index = index

            if best_index is not None and best_distance < 170:
                track = previous_tracks.pop(best_index)
                participant_id = track["participant_id"]
                previous_roi = track.get("roi")
            else:
                participant_id = f"Tinglovchi {len(self.stats.participant_scores) + len(matched) + 1}"
                previous_roi = None

            matched.append(
                {
                    "participant_id": participant_id,
                    "box": face_box,
                    "center": (center_x, center_y),
                    "roi": previous_roi,
                }
            )

        return matched

    def _save_current_session(self) -> dict:
        now = time.time()
        payload = self.stats.to_payload()
        session_row = {
            "session_name": self.stats.session_name,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.stats.started_at)),
            "ended_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
            "duration_seconds": round(now - self.stats.started_at, 2),
            "total_frames": self.stats.total_frames,
            "face_frames": self.stats.face_frames,
            "average_detected_faces": round(self.stats.average_detected_faces, 2),
            "max_detected_faces": self.stats.max_detected_faces,
            "absence_frames": self.stats.absence_frames,
            "presence_ratio": round(self.stats.presence_ratio, 2),
            "attention_ratio": round(self.stats.attention_ratio, 2),
            "movement_ratio": round(self.stats.movement_ratio, 2),
            "average_score": round(self.stats.average_score, 2),
            "max_score": round(self.stats.max_score, 2),
            "notes": "Avtomatik saqlangan monitoring sessiyasi",
        }
        session_id = insert_session(session_row)
        save_student_latest_results(
            session_id=session_id,
            participant_summary=payload.get("participant_summary", []),
            updated_at=session_row["ended_at"],
        )
        payload["saved_session_id"] = session_id
        return payload

    def assign_participant_name(self, participant_id: str, student_name: str) -> dict:
        with self.lock:
            student_name = student_name.strip()
            if participant_id not in self.stats.participant_scores:
                raise KeyError("Track topilmadi")
            self.stats.participant_scores[participant_id]["assigned_name"] = student_name
            return self.get_status()

    def _compute_activity_score(
        self,
        face_box: tuple[int, int, int, int] | None,
        frame_shape: tuple[int, int, int],
        gray_frame: np.ndarray,
        previous_face_roi: np.ndarray | None,
    ) -> tuple[float, bool, bool, np.ndarray | None, float]:
        if face_box is None:
            return 0.0, False, False, None, 0.0

        x, y, w, h = face_box
        frame_h, frame_w = frame_shape[:2]
        roi = gray_frame[y : y + h, x : x + w]
        if roi.size == 0:
            return 0.0, False, False, None, 0.0

        face_center_x = x + w / 2
        face_center_y = y + h / 2
        screen_center_x = frame_w / 2
        screen_center_y = frame_h / 2

        dx = abs(face_center_x - screen_center_x) / max(screen_center_x, 1)
        dy = abs(face_center_y - screen_center_y) / max(screen_center_y, 1)
        center_distance = dx + dy
        attentive = center_distance < 0.75

        score = 35.0
        score += max(0.0, 30.0 - (center_distance * 20.0))

        resized_roi = cv2.resize(roi, (96, 96))
        movement_level = 0.0
        if previous_face_roi is not None and previous_face_roi.shape == resized_roi.shape:
            diff = cv2.absdiff(previous_face_roi, resized_roi)
            movement_level = float(np.mean(diff))
        moving = 2.5 <= movement_level <= 22.0
        score += min(movement_level * 1.5, 20.0)

        face_area_ratio = (w * h) / max(frame_w * frame_h, 1)
        if 0.03 <= face_area_ratio <= 0.22:
            score += 10.0
        if attentive:
            score += 5.0
        if moving:
            score += 5.0

        return min(score, 100.0), attentive, moving, resized_roi, movement_level

    def _safe_region_mean_diff(
        self,
        current_gray: np.ndarray,
        previous_gray: np.ndarray | None,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> float:
        if previous_gray is None:
            return 0.0
        height, width = current_gray.shape[:2]
        x1 = max(0, min(width, x1))
        x2 = max(0, min(width, x2))
        y1 = max(0, min(height, y1))
        y2 = max(0, min(height, y2))
        if x2 <= x1 or y2 <= y1:
            return 0.0
        current_roi = current_gray[y1:y2, x1:x2]
        previous_roi = previous_gray[y1:y2, x1:x2]
        if current_roi.size == 0 or previous_roi.shape != current_roi.shape:
            return 0.0
        return float(np.mean(cv2.absdiff(previous_roi, current_roi)))

    def _classify_behavior_events(
        self,
        face_box: tuple[int, int, int, int],
        frame_shape: tuple[int, int, int],
        gray_frame: np.ndarray,
        previous_gray_frame: np.ndarray | None,
        attentive: bool,
        movement_level: float,
        participant_state: dict,
    ) -> dict:
        x, y, w, h = face_box
        frame_h, _ = frame_shape[:2]
        upper_motion = self._safe_region_mean_diff(
            gray_frame,
            previous_gray_frame,
            int(x - (w * 0.35)),
            int(y - (h * 1.05)),
            int(x + (w * 1.35)),
            y,
        )
        lower_motion = self._safe_region_mean_diff(
            gray_frame,
            previous_gray_frame,
            int(x - (w * 0.2)),
            int(y + h),
            int(x + (w * 1.2)),
            int(y + (h * 2.3)),
        )
        center_y = y + (h / 2)
        head_down_like = center_y > frame_h * 0.62
        still_like = movement_level < 1.4

        participant_state["low_motion_streak"] = participant_state.get("low_motion_streak", 0) + 1 if still_like else 0
        participant_state["head_down_streak"] = participant_state.get("head_down_streak", 0) + 1 if head_down_like else 0
        participant_state["away_streak"] = participant_state.get("away_streak", 0) + 1 if not attentive else 0

        question_gesture = upper_motion >= 10.5
        phone_suspect = lower_motion >= 11.5 and not attentive and head_down_like
        drowsy_suspect = participant_state["low_motion_streak"] >= 18 and participant_state["head_down_streak"] >= 10
        looking_away = participant_state["away_streak"] >= 8

        return {
            "phone_suspect": phone_suspect,
            "question_gesture": question_gesture,
            "drowsy_suspect": drowsy_suspect,
            "looking_away": looking_away,
            "upper_motion": round(upper_motion, 2),
            "lower_motion": round(lower_motion, 2),
        }

    def _draw_overlay(
        self,
        frame: np.ndarray,
        current_score: float,
        attentive: bool,
        moving: bool,
        detected_faces: int,
    ) -> np.ndarray:
        overlay = frame.copy()
        cv2.rectangle(overlay, (20, 20), (430, 185), (8, 24, 40), -1)
        cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)

        lines = [
            f"Joriy ball: {current_score:.1f}",
            f"Tinglovchilar: {detected_faces}",
            f"Mavjudlik: {self.stats.presence_ratio:.1f}%",
            f"Diqqat: {self.stats.attention_ratio:.1f}%",
            f"Harakat: {self.stats.movement_ratio:.1f}%",
            f"Holat: {'Faol' if attentive or moving else 'Nazorat'}",
        ]
        colors = [
            (70, 220, 255),
            (70, 240, 120),
            (255, 240, 140),
            (220, 180, 255),
            (255, 210, 160),
            (255, 255, 255),
        ]
        for index, text in enumerate(lines):
            cv2.putText(
                frame,
                text,
                (35, 46 + (index * 24)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                colors[index],
                2,
            )

        cv2.putText(
            frame,
            self.stats.session_name,
            (35, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 210, 220),
            1,
        )
        return frame

    def process_next_frame(self) -> bytes | None:
        with self.lock:
            if not self.running or self.camera is None:
                return self._placeholder_frame(
                    "Monitoring hali boshlanmagan",
                    "Start tugmasini bosing va kamera indeksini tekshiring",
                )

            ok, frame = self.camera.read()
            if not ok:
                self.last_error = "Kameradan kadr olib bo'lmadi."
                return self._placeholder_frame(
                    "Kameradan tasvir kelmadi",
                    "Kamera boshqa dastur tomonidan band bo'lishi mumkin",
                )

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = ()
            if self.face_detector.empty():
                self.face_detector = self._load_face_detector()
            if self.face_detector_alt.empty():
                self.face_detector_alt = self._load_face_detector("haarcascade_frontalface_alt2.xml")

            if self.face_detector.empty() and self.face_detector_alt.empty():
                self.last_error = "Yuzni aniqlash modeli yuklanmadi."
            else:
                faces = self._detect_faces(gray)
                self.last_error = "" if len(faces) > 0 else "Yuz aniqlanmadi. Yorug'likni biroz pasaytiring."

            matched_faces = self._match_faces(faces)
            detected_faces = len(matched_faces)
            current_score = 0.0
            attentive_count = 0
            moving_count = 0
            new_face_rois: list[np.ndarray] = []
            new_tracks: list[dict] = []

            if detected_faces > 0:
                for matched_face in matched_faces:
                    face_box = matched_face["box"]
                    x, y, w, h = face_box
                    face_score, face_attentive, face_moving, resized_roi, movement_level = self._compute_activity_score(
                        face_box,
                        frame.shape,
                        gray,
                        matched_face.get("roi"),
                    )
                    current_score += face_score
                    attentive_count += int(face_attentive)
                    moving_count += int(face_moving)
                    new_face_rois.append(resized_roi if resized_roi is not None else None)
                    new_tracks.append(
                        {
                            "participant_id": matched_face["participant_id"],
                            "center": matched_face["center"],
                            "roi": resized_roi,
                        }
                    )

                    participant_stats = self.stats.participant_scores.setdefault(
                        matched_face["participant_id"],
                        {
                            "frames": 0,
                            "score_sum": 0.0,
                            "max_score": 0.0,
                            "event_counts": {},
                            "state": {},
                            "assigned_name": "",
                        },
                    )
                    participant_stats["frames"] += 1
                    participant_stats["score_sum"] += face_score
                    participant_stats["max_score"] = max(participant_stats["max_score"], face_score)
                    participant_stats.setdefault("event_counts", {})
                    participant_stats.setdefault("state", {})

                    event_flags = self._classify_behavior_events(
                        face_box,
                        frame.shape,
                        gray,
                        self.previous_gray_frame,
                        face_attentive,
                        movement_level,
                        participant_stats["state"],
                    )
                    labels: list[str] = []
                    if event_flags["phone_suspect"]:
                        participant_stats["event_counts"]["phone_suspect"] = (
                            participant_stats["event_counts"].get("phone_suspect", 0) + 1
                        )
                        labels.append("telefon?")
                    if event_flags["question_gesture"]:
                        participant_stats["event_counts"]["question_gesture"] = (
                            participant_stats["event_counts"].get("question_gesture", 0) + 1
                        )
                        labels.append("savol-ishora")
                    if event_flags["drowsy_suspect"]:
                        participant_stats["event_counts"]["drowsy_suspect"] = (
                            participant_stats["event_counts"].get("drowsy_suspect", 0) + 1
                        )
                        labels.append("uyquchan")
                    if event_flags["looking_away"]:
                        participant_stats["event_counts"]["looking_away"] = (
                            participant_stats["event_counts"].get("looking_away", 0) + 1
                        )
                        labels.append("chalg'igan")

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (46, 204, 113), 2)
                    cv2.putText(
                        frame,
                        f"{matched_face['participant_id']}: {face_score:.0f}",
                        (x, max(30, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (46, 204, 113),
                        2,
                    )
                    if labels:
                        cv2.putText(
                            frame,
                            ", ".join(labels),
                            (x, min(frame.shape[0] - 18, y + h + 22)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 210, 120),
                            2,
                        )

                current_score = current_score / detected_faces
                self.previous_face_rois = new_face_rois
                self.tracked_faces = new_tracks
                self.last_face_seen_at = time.time()
            else:
                if (
                    self.last_face_seen_at is not None
                    and time.time() - self.last_face_seen_at > SESSION_TIMEOUT_SECONDS
                ):
                    self.previous_face_rois = []
                    self.tracked_faces = []
                cv2.putText(
                    frame,
                    "Yuz aniqlanmadi",
                    (30, frame.shape[0] - 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (80, 80, 255),
                    2,
                )

            attentive = attentive_count > 0
            moving = moving_count > 0
            self.stats.update(detected_faces, attentive_count, moving_count, current_score)
            self.previous_gray_frame = gray.copy()
            frame = self._draw_overlay(frame, current_score, attentive, moving, detected_faces)
            self.last_frame = frame
            ok, encoded = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY],
            )
            if ok:
                self.last_encoded_frame = encoded.tobytes()
            return self.last_encoded_frame

    def _placeholder_frame(self, title: str, subtitle: str) -> bytes | None:
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
        frame[:] = (14, 22, 32)
        cv2.circle(frame, (160, 120), 120, (24, 53, 82), -1)
        cv2.circle(frame, (800, 420), 180, (35, 73, 58), -1)
        cv2.rectangle(frame, (70, 80), (890, 460), (245, 248, 250), 2)
        cv2.putText(
            frame,
            title,
            (110, 220),
            cv2.FONT_HERSHEY_DUPLEX,
            1.3,
            (245, 248, 250),
            2,
        )
        cv2.putText(
            frame,
            subtitle,
            (110, 275),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (176, 194, 210),
            2,
        )
        cv2.putText(
            frame,
            f"Aktiv kamera: {self.active_camera_index} | Backend: {self.active_backend}",
            (110, 335),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 204, 120),
            2,
        )
        cv2.putText(
            frame,
            self.last_error or "Tizim tayyor",
            (110, 390),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (125, 220, 160),
            2,
        )
        attempts_text = "Urinishlar: " + (", ".join(self.last_attempts[:4]) if self.last_attempts else "hali yo'q")
        cv2.putText(
            frame,
            attempts_text,
            (110, 435),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (180, 190, 200),
            1,
        )
        ok, encoded = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY],
        )
        if ok:
            self.last_encoded_frame = encoded.tobytes()
        return self.last_encoded_frame

    def generate_mjpeg(self):
        while True:
            frame = self.process_next_frame()
            if frame is None:
                time.sleep(0.15)
                continue
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    def get_frame_bytes(self) -> bytes | None:
        try:
            if self.running and self.camera is not None:
                return self.process_next_frame()
            return self._placeholder_frame(
                "Monitoring hali boshlanmagan",
                "Start tugmasini bosing va kamera indeksini tekshiring",
            )
        except Exception as exc:
            self.last_error = f"Kadrni tayyorlashda xatolik: {exc}"
            return self._placeholder_frame(
                "Tasvirni chiqarishda xatolik",
                "Sahifani yangilang yoki monitoringni qayta ishga tushiring",
            )

    def get_status(self) -> dict:
        with self.lock:
            payload = self.stats.to_payload()
            payload.update(
                {
                    "running": self.running,
                    "last_error": self.last_error,
                    "camera_ready": self.camera is not None,
                    "active_camera_index": self.active_camera_index,
                    "active_backend": self.active_backend,
                    "active_source_label": self.active_source_label,
                    "last_attempts": self.last_attempts,
                }
            )
            return payload

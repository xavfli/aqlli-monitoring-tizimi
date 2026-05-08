import re
import time
from pathlib import Path

import cv2

try:
    import pytesseract
except ImportError:
    pytesseract = None


class ZoomNameOcr:
    def __init__(self) -> None:
        self.last_error = ""
        self.last_scan_at = 0.0
        self.scan_interval_seconds = 2.2
        self.available = self._check_available()

    def _check_available(self) -> bool:
        if pytesseract is None:
            self.last_error = "pytesseract o'rnatilmagan"
            return False
        for path in (
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\tmp\Tesseract-OCR\tesseract.exe"),
        ):
            if path.exists():
                pytesseract.pytesseract.tesseract_cmd = str(path)
                break
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            self.last_error = "Tesseract OCR Windows PATH ichida topilmadi"
            return False

    def read_name_near_face(self, frame, face_box: tuple[int, int, int, int]) -> str:
        if not self.available:
            return ""
        if time.time() - self.last_scan_at < self.scan_interval_seconds:
            return ""
        self.last_scan_at = time.time()

        x, y, w, h = face_box
        frame_h, frame_w = frame.shape[:2]
        x1 = max(0, x - int(w * 0.35))
        x2 = min(frame_w, x + int(w * 1.35))
        y1 = min(frame_h, y + h)
        y2 = min(frame_h, y + h + max(34, int(h * 0.45)))
        if x2 <= x1 or y2 <= y1:
            return ""

        crop = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        try:
            text = pytesseract.image_to_string(gray, config="--psm 7")
        except Exception as exc:
            self.last_error = f"OCR ishlamadi: {exc}"
            return ""

        name = self._clean_name(text)
        if name:
            self.last_error = ""
        return name

    def _clean_name(self, text: str) -> str:
        text = re.sub(r"[^A-Za-zА-Яа-яЁё0-9'` ._-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" ._-")
        ignored = {"mute", "unmute", "zoom", "audio", "video", "meeting"}
        if len(text) < 2 or text.lower() in ignored:
            return ""
        return text[:64]

    def get_status(self) -> dict:
        return {
            "available": self.available,
            "ready": self.available,
            "last_error": self.last_error,
        }

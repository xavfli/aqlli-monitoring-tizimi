import queue
import threading
import time
import wave
from pathlib import Path

try:
    import sounddevice as sd
except ImportError:
    sd = None

from .config import AUDIO_DIR


class AudioRecorder:
    def __init__(self, samplerate: int = 16000, channels: int = 1) -> None:
        self.samplerate = samplerate
        self.channels = channels
        self.stream = None
        self.writer_thread: threading.Thread | None = None
        self.audio_queue: queue.Queue[bytes | None] = queue.Queue()
        self.running = False
        self.last_error = ""
        self.output_path: Path | None = None

    def start(self, session_name: str) -> None:
        if self.running:
            return
        if sd is None:
            self.last_error = "sounddevice paketi o'rnatilmagan, audio yozib bo'lmadi."
            return

        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in session_name)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.output_path = AUDIO_DIR / f"{timestamp}_{safe_name[:42] or 'zoom_darsi'}.wav"
        self.last_error = ""
        self.audio_queue = queue.Queue()
        self.running = True

        self.writer_thread = threading.Thread(target=self._write_wav, daemon=True)
        self.writer_thread.start()

        try:
            self.stream = sd.RawInputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                dtype="int16",
                callback=self._callback,
            )
            self.stream.start()
        except Exception as exc:
            self.last_error = f"Audio manba ochilmadi: {exc}"
            self.stop()

    def _callback(self, indata, frames, time_info, status) -> None:
        if status:
            self.last_error = str(status)
        self.audio_queue.put(bytes(indata))

    def _write_wav(self) -> None:
        if self.output_path is None:
            return
        with wave.open(str(self.output_path), "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.samplerate)
            while True:
                chunk = self.audio_queue.get()
                if chunk is None:
                    break
                wav_file.writeframes(chunk)

    def stop(self) -> str:
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as exc:
                self.last_error = f"Audio to'xtatishda xatolik: {exc}"
        self.stream = None

        if self.running:
            self.running = False
            self.audio_queue.put(None)
            if self.writer_thread is not None:
                self.writer_thread.join(timeout=3)
        self.writer_thread = None
        return str(self.output_path) if self.output_path else ""

    def get_status(self) -> dict:
        return {
            "running": self.running,
            "last_error": self.last_error,
            "output_path": str(self.output_path) if self.output_path else "",
            "available": sd is not None,
        }

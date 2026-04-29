"""
Вспомогательные функции
"""

import time
from typing import List, Any
from pathlib import Path


def format_time(seconds: float) -> str:
    """Форматирование времени в MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Ограничение значения в диапазоне"""
    return max(min_val, min(value, max_val))


def lerp(a: float, b: float, t: float) -> float:
    """Линейная интерполяция"""
    return a + (b - a) * t


def find_songs_directory() -> Path:
    """Поиск директории с песнями"""
    paths = [
        Path("songs"),
        Path.home() / "BeatBumper/songs",
        Path.home() / "Documents/BeatBumper/songs",
    ]
    
    for path in paths:
        if path.exists():
            return path
    
    # Создаем дефолтную
    default_path = Path("songs")
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path


class FPSCounter:
    """Счетчик FPS"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.times: List[float] = []
    
    def tick(self) -> None:
        """Отметка времени кадра"""
        self.times.append(time.time())
        if len(self.times) > self.window_size:
            self.times.pop(0)
    
    @property
    def fps(self) -> float:
        """Текущий FPS"""
        if len(self.times) < 2:
            return 0.0
        duration = self.times[-1] - self.times[0]
        return (len(self.times) - 1) / duration if duration > 0 else 0.0

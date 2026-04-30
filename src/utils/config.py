"""
Конфигурация BeatBumper
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Глобальная конфигурация игры"""

    def __init__(self):
        # Определение платформы
        self.is_steam_deck = self._detect_steam_deck()

        # Экран
        self.screen_width = 1280
        self.screen_height = 720
        self.fullscreen = False
        self.target_fps = 60
        self.debug_mode = False

        # Игровые параметры
        self.note_speed = 600  # Пикселей в секунду
        self.hit_line_x = 150  # Вертикальная линия удара (больше не используется)
        self.hit_line_y = self.screen_height - 150  # Линия удара внизу

        # Позиции дорожек для нот
        self.red_lane_x = int(self.screen_width * 0.58)  # Красные ноты (правая дорожка)
        self.blue_lane_x = int(self.screen_width * 0.42)  # Синие ноты (левая дорожка)
        self.lane_width = 100  # Ширина дорожки в пикселях
        self.lane_alpha = 15  # Прозрачность дорожки (0-255)

        # Аудио
        self.audio_latency_ms = -50  # Компенсация задержки аудио
        self.music_volume = 0.8  # Громкость музыки (0.0 - 1.0)
        self.sfx_volume = 0.7  # Громкость звуковых эффектов (0.0 - 1.0)
        self.audio_buffer_size = 2048  # Размер буфера аудио

        # Загрузка из файла
        self._load_from_file()

    def _detect_steam_deck(self) -> bool:
        """Автоопределение Steam Deck"""
        # Проверка наличия Steam Controller
        if os.path.exists("/dev/input/by-id/usb-Valve_Software_Steam_Controller"):
            return True
        # Проверка переменной окружения
        if os.environ.get("SteamDeck", "") == "1":
            return True
        # Проверка имени хоста
        try:
            with open("/etc/hostname", "r") as f:
                hostname = f.read().strip()
                if "steamdeck" in hostname.lower():
                    return True
        except:
            pass
        return False

    def _load_from_file(self) -> None:
        """Загрузка конфигурации из config.json"""
        config_path = Path("config.json")
        if not config_path.exists():
            self._create_default_config()
            return

        try:
            with open(config_path, "r") as f:
                data = json.load(f)

            # Экран
            self.screen_width = data.get("screen_width", self.screen_width)
            self.screen_height = data.get("screen_height", self.screen_height)
            self.fullscreen = data.get("fullscreen", self.fullscreen)
            self.target_fps = data.get("target_fps", self.target_fps)
            self.debug_mode = data.get("debug_mode", self.debug_mode)

            # Игровые параметры
            self.note_speed = data.get("note_speed", self.note_speed)
            self.hit_line_y = data.get("hit_line_y", self.hit_line_y)

            # Позиции дорожек
            red_lane_position = data.get("red_lane_position", 0.58)
            blue_lane_position = data.get("blue_lane_position", 0.42)
            self.red_lane_x = int(self.screen_width * red_lane_position)
            self.blue_lane_x = int(self.screen_width * blue_lane_position)
            self.lane_width = data.get("lane_width", self.lane_width)
            self.lane_alpha = data.get("lane_alpha", self.lane_alpha)

            # Аудио
            self.audio_latency_ms = data.get("audio_latency_ms", self.audio_latency_ms)
            self.music_volume = data.get("music_volume", self.music_volume)
            self.sfx_volume = data.get("sfx_volume", self.sfx_volume)
            self.audio_buffer_size = data.get(
                "audio_buffer_size", self.audio_buffer_size
            )

            if self.is_steam_deck:
                print("🕹️  Режим Steam Deck активирован")

        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфига: {e}")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """Создание конфигурации по умолчанию"""
        config = {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "fullscreen": self.fullscreen,
            "target_fps": self.target_fps,
            "debug_mode": self.debug_mode,
            "note_speed": self.note_speed,
            "hit_line_y": self.hit_line_y,
            "red_lane_position": 0.58,
            "blue_lane_position": 0.42,
            "lane_width": self.lane_width,
            "lane_alpha": self.lane_alpha,
            "audio_latency_ms": self.audio_latency_ms,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "audio_buffer_size": self.audio_buffer_size,
        }

        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)

        print("⚙️  Создан config.json с настройками по умолчанию")

    def toggle_fullscreen(self) -> None:
        """Переключение полноэкранного режима"""
        self.fullscreen = not self.fullscreen
        print(f"🖥️  Полноэкранный режим: {'вкл' if self.fullscreen else 'выкл'}")

    def update_resolution(self, width: int, height: int) -> None:
        """Обновление разрешения экрана"""
        self.screen_width = width
        self.screen_height = height

        # Пересчёт позиций при изменении разрешения
        red_position = self.red_lane_x / max(1, self.screen_width)
        blue_position = self.blue_lane_x / max(1, self.screen_width)

        self.red_lane_x = int(width * red_position) if width > 0 else int(width * 0.58)
        self.blue_lane_x = (
            int(width * blue_position) if width > 0 else int(width * 0.42)
        )
        self.hit_line_y = height - 150

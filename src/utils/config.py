"""
Конфигурация игры
"""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Настройки игры"""

    CONFIG_FILE = "config.json"

    def __init__(self):
        # Экран
        self.fullscreen = self._detect_steam_deck()
        self.screen_width = 1280
        self.screen_height = 800
        self.target_fps = 60

        # Аудио
        self.music_volume = 0.8
        self.sfx_volume = 0.6
        self.audio_buffer_size = 1024
        self.audio_latency_ms = 0  # Будет откалибровано

        # Геймплей
        self.note_speed = 600  # пикселей в секунду
        self.hit_line_x = 200  # позиция линии удара
        self.hit_line_y = self.screen_height - 150  # Линия удара внизу
        self.note_spawn_offset = 2.0  # секунд до появления

        # Отладка
        self.debug_mode = False

        # Steam Deck специфичные
        self.steam_deck_mode = self._detect_steam_deck()

    def _detect_steam_deck(self) -> bool:
        """Определение запуска на Steam Deck"""
        # Проверка типичных признаков Steam Deck
        if os.path.exists("/home/deck"):
            return True
        if os.environ.get("SteamDeck", "") == "1":
            return True
        return False

    def apply(self) -> None:
        """Применение настроек"""
        if self.steam_deck_mode:
            # Оптимизации для Steam Deck
            self.screen_width = 1280
            self.screen_height = 800
            self.target_fps = 60
            self.audio_latency_ms = 30  # Типичная задержка на Deck
            print("🕹️  Режим Steam Deck активирован")

    def toggle_fullscreen(self) -> None:
        """Переключение полноэкранного режима"""
        self.fullscreen = not self.fullscreen
        # Здесь должен быть код пересоздания окна

    @classmethod
    def load(cls) -> "Config":
        """Загрузка конфигурации из файла"""
        config = cls()

        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
                print("⚙️  Конфигурация загружена")
            except Exception as e:
                print(f"⚠️  Ошибка загрузки конфига: {e}")
        else:
            config.save()

        return config

    def save(self) -> None:
        """Сохранение конфигурации"""
        data = {
            "fullscreen": self.fullscreen,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "note_speed": self.note_speed,
            "debug_mode": self.debug_mode,
        }

        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print("💾 Конфигурация сохранена")
        except Exception as e:
            print(f"⚠️  Ошибка сохранения конфига: {e}")

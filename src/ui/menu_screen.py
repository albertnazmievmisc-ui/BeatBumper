"""
Экран меню выбора песни
"""

import pygame
from pathlib import Path
from typing import List, Dict

from utils.config import Config
from input.input_handler import InputHandler, Action
from parser.beatmap_loader import BeatmapLoader
from parser.beatmap_parser import BeatmapParser


class MenuScreen:
    """Экран главного меню"""

    def __init__(self, screen: pygame.Surface, config: Config):
        self.screen = screen
        self.config = config
        self.start_game_requested = False
        self.selected_song = None

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)

        # Список песен
        self.songs: List[Dict] = []
        self.selected_index = 0
        self._scan_songs()

        # Загрузчик мап
        self.loader = BeatmapLoader()
        self.parser = BeatmapParser()

    def _scan_songs(self) -> None:
        """Сканирование папки с песнями"""
        songs_dir = Path("songs")
        if not songs_dir.exists():
            songs_dir.mkdir(parents=True)

        for item in songs_dir.iterdir():
            if item.suffix == ".zip":
                self.songs.append(
                    {
                        "path": item,
                        "name": item.stem,
                    }
                )

        print(f"📂 Найдено песен: {len(self.songs)}")

    def update(self, dt: float, input_handler: InputHandler) -> None:
        """Обновление меню"""
        # Навигация
        if input_handler.is_action_just_pressed(Action.MENU_UP):
            self.selected_index = max(0, self.selected_index - 1)
        elif input_handler.is_action_just_pressed(Action.MENU_DOWN):
            self.selected_index = min(len(self.songs) - 1, self.selected_index + 1)

        # Выбор песни
        if input_handler.is_action_just_pressed(Action.MENU_SELECT):
            if self.songs and self.selected_index < len(self.songs):
                song = self.songs[self.selected_index]
                loaded = self.loader.load_zip(song["path"])
                if loaded:
                    notes = self.parser.parse(loaded["beatmap"])
                    self.selected_song = {
                        "name": loaded["song_name"],
                        "author": loaded["song_author"],
                        "audio_path": loaded["audio_path"],
                        "notes": notes,
                        "bpm": loaded["bpm"],
                    }
                    self.start_game_requested = True

    def render(self) -> None:
        """Отрисовка меню"""
        self.screen.fill((20, 20, 40))

        # Заголовок
        title = self.title_font.render("BeatBumper", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.config.screen_width // 2, y=100)
        self.screen.blit(title, title_rect)

        # Подсказка
        hint = self.menu_font.render(
            "Drop Beat Saber zip files to ./songs/", True, (150, 150, 150)
        )
        hint_rect = hint.get_rect(centerx=self.config.screen_width // 2, y=180)
        self.screen.blit(hint, hint_rect)

        # Список песен
        y_start = 250
        for i, song in enumerate(self.songs):
            color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)
            text = self.menu_font.render(song["name"], True, color)
            text_rect = text.get_rect(x=100, y=y_start + i * 50)
            self.screen.blit(text, text_rect)

            if i == self.selected_index:
                pygame.draw.line(
                    self.screen,
                    (255, 255, 0),
                    (80, text_rect.centery),
                    (90, text_rect.centery),
                    3,
                )

        if not self.songs:
            no_songs = self.menu_font.render("No songs found!", True, (255, 100, 100))
            no_rect = no_songs.get_rect(center=(self.config.screen_width // 2, 350))
            self.screen.blit(no_songs, no_rect)

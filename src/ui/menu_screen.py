"""
Экран меню выбора песни и сложности с выходом
"""

import pygame
from pathlib import Path
from typing import List, Dict, Optional

from utils.config import Config
from input.input_handler import InputHandler, Action
from parser.beatmap_loader import BeatmapLoader
from parser.beatmap_parser import BeatmapParser


class MenuScreen:
    """Экран главного меню с выбором песни и сложности"""

    def __init__(self, screen: pygame.Surface, config: Config):
        self.screen = screen
        self.config = config
        self.start_game_requested = False
        self.quit_requested = False  # Флаг выхода из игры
        self.selected_song = None

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Список песен
        self.songs: List[Dict] = []
        self.selected_index = 0
        self._scan_songs()

        # Выбор сложности
        self.difficulties: List[Dict] = []
        self.selected_difficulty_index = 0
        self.showing_difficulties = False

        # Загрузчик мап
        self.loader = BeatmapLoader()
        self.parser = BeatmapParser()

    def _scan_songs(self) -> None:
        """Сканирование папки с песнями"""
        songs_dir = Path("songs")
        if not songs_dir.exists():
            songs_dir.mkdir(parents=True)

        for item in sorted(songs_dir.iterdir()):
            if item.suffix == ".zip":
                self.songs.append(
                    {
                        "path": item,
                        "name": item.stem,
                    }
                )

        print(f"📂 Найдено песен: {len(self.songs)}")

    def _load_difficulties(self, song_index: int) -> None:
        """Загрузка списка сложностей для выбранной песни"""
        if 0 <= song_index < len(self.songs):
            song = self.songs[song_index]
            self.difficulties = self.loader.get_difficulties(song["path"])
            self.selected_difficulty_index = 0
            print(f"📊 Найдено сложностей: {len(self.difficulties)}")
            for diff in self.difficulties:
                print(
                    f"   - {diff['difficulty']} ({diff.get('label', diff['characteristic'])})"
                )

    def _load_selected_song(self) -> None:
        """Загрузка выбранной песни с выбранной сложностью"""
        if not self.songs:
            return

        song = self.songs[self.selected_index]
        difficulty_filename = None

        if self.difficulties and self.selected_difficulty_index < len(
            self.difficulties
        ):
            difficulty_filename = self.difficulties[self.selected_difficulty_index][
                "filename"
            ]

        loaded = self.loader.load_zip(song["path"], difficulty_filename)
        if loaded:
            notes = self.parser.parse(loaded["beatmap"])
            self.selected_song = {
                "name": loaded["song_name"],
                "author": loaded["song_author"],
                "audio_path": loaded["audio_path"],
                "notes": notes,
                "bpm": loaded["bpm"],
                "difficulty": loaded.get("difficulty", "Unknown"),
            }
            self.start_game_requested = True

    def update(self, dt: float, input_handler: InputHandler) -> None:
        """Обновление меню"""
        # Проверка выхода
        if input_handler.is_quit_pressed():
            self.quit_requested = True
            return

        if self.showing_difficulties:
            self._update_difficulty_selection(input_handler)
        else:
            self._update_song_selection(input_handler)

    def _update_song_selection(self, input_handler: InputHandler) -> None:
        """Обновление выбора песни"""
        # Навигация
        if input_handler.is_action_just_pressed(Action.MENU_UP):
            self.selected_index = max(0, self.selected_index - 1)

        elif input_handler.is_action_just_pressed(Action.MENU_DOWN):
            self.selected_index = min(len(self.songs) - 1, self.selected_index + 1)

        # Выбор песни — переход к выбору сложности
        elif input_handler.is_action_just_pressed(Action.MENU_SELECT):
            if self.songs:
                self._load_difficulties(self.selected_index)
                self.showing_difficulties = True

        # Выход из игры
        elif input_handler.is_action_just_pressed(Action.QUIT):
            self.quit_requested = True

    def _update_difficulty_selection(self, input_handler: InputHandler) -> None:
        """Обновление выбора сложности"""
        # Навигация по сложностям
        if input_handler.is_action_just_pressed(Action.MENU_UP):
            self.selected_difficulty_index = max(0, self.selected_difficulty_index - 1)

        elif input_handler.is_action_just_pressed(Action.MENU_DOWN):
            self.selected_difficulty_index = min(
                len(self.difficulties) - 1, self.selected_difficulty_index + 1
            )

        # Подтверждение выбора сложности
        elif input_handler.is_action_just_pressed(Action.MENU_SELECT):
            self._load_selected_song()

        # Отмена — назад к выбору песни
        elif input_handler.is_action_just_pressed(Action.MENU_BACK):
            self.showing_difficulties = False
            self.selected_difficulty_index = 0

        # Выход из игры
        elif input_handler.is_action_just_pressed(Action.QUIT):
            self.quit_requested = True

    def render(self) -> None:
        """Отрисовка меню"""
        if self.showing_difficulties:
            self._render_difficulty_selection()
        else:
            self._render_song_selection()

    def _render_song_selection(self) -> None:
        """Отрисовка выбора песни"""
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

        # Инструкция
        instr = self.small_font.render(
            "A/Enter — Select   Back/Q — Quit", True, (150, 150, 150)
        )
        instr_rect = instr.get_rect(centerx=self.config.screen_width // 2, y=220)
        self.screen.blit(instr, instr_rect)

        # Список песен
        y_start = 270
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

    def _render_difficulty_selection(self) -> None:
        """Отрисовка выбора сложности"""
        self.screen.fill((20, 20, 40))

        # Название песни
        song_name = self.songs[self.selected_index]["name"]
        title = self.title_font.render("Select Difficulty", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.config.screen_width // 2, y=100)
        self.screen.blit(title, title_rect)

        subtitle = self.menu_font.render(song_name, True, (200, 200, 100))
        sub_rect = subtitle.get_rect(centerx=self.config.screen_width // 2, y=160)
        self.screen.blit(subtitle, sub_rect)

        # Инструкция
        instr = self.small_font.render(
            "A/Enter — Start   B/Back — Cancel   Q — Quit", True, (150, 150, 150)
        )
        instr_rect = instr.get_rect(centerx=self.config.screen_width // 2, y=200)
        self.screen.blit(instr, instr_rect)

        # Список сложностей
        y_start = 270
        for i, diff in enumerate(self.difficulties):
            is_selected = i == self.selected_difficulty_index

            # Цвет в зависимости от сложности
            diff_colors = {
                "Easy": (100, 255, 100),
                "Normal": (200, 255, 100),
                "Hard": (255, 200, 50),
                "Expert": (255, 100, 50),
                "ExpertPlus": (255, 50, 100),
            }
            base_color = diff_colors.get(diff["difficulty"], (200, 200, 200))
            color = (
                (
                    min(base_color[0] + 55, 255),
                    min(base_color[1] + 55, 255),
                    min(base_color[2] + 55, 255),
                )
                if is_selected
                else base_color
            )

            # Текст сложности
            label = diff.get("label") or diff["difficulty"]
            display_text = f"{diff['difficulty']}"
            if label and label != diff["difficulty"]:
                display_text += f" - {label}"

            text = self.menu_font.render(display_text, True, color)
            text_rect = text.get_rect(x=100, y=y_start + i * 50)
            self.screen.blit(text, text_rect)

            # Индикатор выбора
            if is_selected:
                pygame.draw.line(
                    self.screen,
                    color,
                    (80, text_rect.centery),
                    (90, text_rect.centery),
                    3,
                )

            # Дополнительная информация
            if diff.get("mappers"):
                mapper_text = self.small_font.render(
                    f"by {diff['mappers']}", True, (150, 150, 150)
                )
                mapper_rect = mapper_text.get_rect(
                    x=text_rect.right + 20, centery=text_rect.centery
                )
                self.screen.blit(mapper_text, mapper_rect)

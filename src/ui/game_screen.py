"""
Игровой экран (ноты сверху вниз, RT/LT для ударов, меню паузы с выходом)
"""

import pygame
from typing import Dict, Optional, List, Tuple
from enum import Enum, auto

from utils.config import Config
from input.input_handler import InputHandler, Action
from audio.audio_manager import AudioManager
from core.note_controller import NoteController, HitResult, NoteColor, Note
from core.score_manager import ScoreManager, GameStats
from render.renderer import Renderer


class PauseMenuOption(Enum):
    """Пункты меню паузы"""

    RESUME = auto()
    RESTART = auto()
    QUIT = auto()


class FloatingText:
    """Всплывающий текст результата на позиции ноты"""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        lifetime: float = 0.6,
    ):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vy = -100

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        self.y += self.vy * dt
        return True

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text_surf, rect)


class GameScreen:
    """Основной игровой экран"""

    def __init__(
        self,
        screen: pygame.Surface,
        config: Config,
        audio_manager: AudioManager,
        song_data: Dict,
    ):
        self.screen = screen
        self.config = config
        self.audio = audio_manager
        self.game_over = False
        self.paused = False
        self.quit_requested = False  # Флаг выхода из игры

        # Меню паузы
        self.pause_menu_options = [
            (PauseMenuOption.RESUME, "Resume"),
            (PauseMenuOption.RESTART, "Restart"),
            (PauseMenuOption.QUIT, "Quit to Menu"),
        ]
        self.pause_selected_index = 0

        # Контроллеры
        self.note_controller = NoteController(config)
        self.score_manager = ScoreManager()
        self.renderer = Renderer(screen, config)

        # Загрузка песни
        self.note_controller.load_beatmap(song_data["notes"])
        self.audio.load_song(song_data["audio_path"])

        # Запуск
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.audio.play()

        # Всплывающие тексты
        self.floating_texts: List[FloatingText] = []
        self.result_font = pygame.font.Font(None, 36)
        self.result_font_big = pygame.font.Font(None, 48)

        # Позиции дорожек
        self.red_x = config.red_lane_x
        self.blue_x = config.blue_lane_x
        self.hit_line_y = config.hit_line_y

    def update(self, dt: float, input_handler: InputHandler) -> None:
        """Обновление игрового состояния"""
        if self.game_over:
            return

        # Выход из игры (работает всегда)
        if input_handler.is_quit_pressed():
            self.game_over = True
            self.quit_requested = True
            return

        # Пауза
        if input_handler.is_pause_pressed():
            if self.paused:
                self._handle_pause_menu_select()
            else:
                self.audio.pause()
                self.paused = True
                self.pause_selected_index = 0
            return

        if self.paused:
            # Навигация в меню паузы
            if input_handler.is_action_just_pressed(Action.MENU_UP):
                self.pause_selected_index = max(0, self.pause_selected_index - 1)
            elif input_handler.is_action_just_pressed(Action.MENU_DOWN):
                self.pause_selected_index = min(
                    len(self.pause_menu_options) - 1, self.pause_selected_index + 1
                )
            elif input_handler.is_action_just_pressed(Action.MENU_SELECT):
                self._handle_pause_menu_select()
            return

        # Текущая позиция в песне
        song_position = self.audio.get_adjusted_position()

        # Проверка на конец песни
        if not self.audio.is_playing():
            self._end_game()
            return

        # Обновление нот
        self.note_controller.update(dt, song_position)
        self.renderer.effects.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

        # Проверка попаданий по КРАСНЫМ нотам
        if input_handler.is_hit_red_pressed():
            self.renderer.effects.create_button_press_red(self.red_x, self.hit_line_y)
            result, note = self.note_controller.check_hit_red(song_position)
            self._process_hit_result(result, note, NoteColor.RED)

        # Проверка попаданий по СИНИМ нотам
        if input_handler.is_hit_blue_pressed():
            self.renderer.effects.create_button_press_blue(self.blue_x, self.hit_line_y)
            result, note = self.note_controller.check_hit_blue(song_position)
            self._process_hit_result(result, note, NoteColor.BLUE)

        # Проверка пропущенных нот
        missed_notes = self.note_controller.check_missed_notes(song_position)
        for note in missed_notes:
            self.score_manager.add_hit(HitResult.MISS)
            self.audio.play_sfx("miss")
            self._add_floating_text("MISS", note.x, note.y, (255, 80, 80), big=True)

    def _process_hit_result(
        self, result: HitResult, note: Optional[Note], color: NoteColor
    ) -> None:
        """Обработка результата попадания"""
        if result == HitResult.MISS:
            x_pos = self.red_x if color == NoteColor.RED else self.blue_x
            self._add_floating_text(
                "MISS", x_pos, self.hit_line_y, (255, 100, 100), big=True
            )
        elif result == HitResult.WRONG_COLOR:
            self.score_manager.add_hit(HitResult.MISS)
            self.audio.play_sfx("miss")
            if note:
                self._add_floating_text(
                    "WRONG!", note.x, note.y, (255, 150, 50), big=True
                )
                self.renderer.effects.create_explosion(note.x, note.y, False)
        else:
            score = self.score_manager.add_hit(result)
            if note:
                if result == HitResult.PERFECT:
                    self._add_floating_text(
                        "PERFECT!", note.x, note.y, (255, 215, 0), big=True
                    )
                else:
                    self._add_floating_text("Good", note.x, note.y, (100, 255, 100))
                self.renderer.effects.create_explosion(
                    note.x, note.y, result == HitResult.PERFECT
                )
            self.audio.play_sfx("hit")

    def _handle_pause_menu_select(self) -> None:
        """Обработка выбора в меню паузы"""
        option = self.pause_menu_options[self.pause_selected_index][0]

        if option == PauseMenuOption.RESUME:
            self.audio.unpause()
            self.paused = False
        elif option == PauseMenuOption.RESTART:
            self.audio.stop()
            self.game_over = True
            self.quit_requested = False  # Будет рестарт, а не выход
        elif option == PauseMenuOption.QUIT:
            self.audio.stop()
            self.game_over = True
            self.quit_requested = True

    def _add_floating_text(
        self,
        text: str,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        big: bool = False,
    ) -> None:
        lifetime = 0.7 if big else 0.5
        self.floating_texts.append(FloatingText(text, x, y, color, lifetime))

    def render(self) -> None:
        """Отрисовка игры"""
        self.renderer.render_background()
        self.renderer.render_hit_line()
        self.renderer.render_effects(0.016)

        visible_notes = self.note_controller.get_visible_notes()
        self.renderer.render_notes(visible_notes)

        for ft in self.floating_texts:
            if ft.text in ("PERFECT!", "MISS", "WRONG!"):
                ft.draw(self.screen, self.result_font_big)
            else:
                ft.draw(self.screen, self.result_font)

        self.renderer.render_score(self.score_manager.stats.score)
        self.renderer.render_combo(self.score_manager.stats.current_combo)

        if self.paused:
            self._render_pause_menu()

    def _render_pause_menu(self) -> None:
        """Отрисовка меню паузы"""
        # Затемнение
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Заголовок
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.config.screen_width // 2, 200))
        self.screen.blit(title, title_rect)

        # Пункты меню
        font_menu = pygame.font.Font(None, 48)
        y_start = 320

        for i, (option, label) in enumerate(self.pause_menu_options):
            is_selected = i == self.pause_selected_index
            color = (255, 255, 0) if is_selected else (200, 200, 200)

            text = font_menu.render(label, True, color)
            text_rect = text.get_rect(
                center=(self.config.screen_width // 2, y_start + i * 60)
            )
            self.screen.blit(text, text_rect)

            if is_selected:
                # Индикатор выбора
                pygame.draw.line(
                    self.screen,
                    (255, 255, 0),
                    (text_rect.left - 20, text_rect.centery),
                    (text_rect.left - 10, text_rect.centery),
                    3,
                )

        # Подсказка
        font_hint = pygame.font.Font(None, 28)
        hint = font_hint.render(
            "↑↓ — Navigate   A — Select   Start — Resume", True, (150, 150, 150)
        )
        hint_rect = hint.get_rect(
            center=(self.config.screen_width // 2, self.config.screen_height - 50)
        )
        self.screen.blit(hint, hint_rect)

    def _end_game(self) -> None:
        """Завершение игры"""
        self.audio.stop()
        total_notes = len(self.note_controller.notes)
        self.score_manager.calculate_final_stats(total_notes)
        self.game_over = True
        print("🏁 Игра завершена")

    def get_stats(self) -> GameStats:
        """Получение статистики"""
        return self.score_manager.stats

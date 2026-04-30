"""
Игровой экран (ноты сверху вниз, RT/LT для ударов, эффекты нажатий, результаты на нотах)
"""

import pygame
from typing import Dict, Optional, List, Tuple

from utils.config import Config
from input.input_handler import InputHandler
from audio.audio_manager import AudioManager
from core.note_controller import NoteController, HitResult, NoteColor, Note
from core.score_manager import ScoreManager, GameStats
from render.renderer import Renderer


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
        self.vy = -100  # Скорость всплытия вверх (пикселей/сек)

    def update(self, dt: float) -> bool:
        """Обновление. Возвращает False если истекло время"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        self.y += self.vy * dt
        return True

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Отрисовка всплывающего текста"""
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

        # Всплывающие тексты результатов
        self.floating_texts: List[FloatingText] = []
        self.result_font = pygame.font.Font(None, 36)
        self.result_font_big = pygame.font.Font(None, 48)

        # Позиции дорожек из конфига
        self.red_x = config.red_lane_x
        self.blue_x = config.blue_lane_x
        self.hit_line_y = config.hit_line_y

    def update(self, dt: float, input_handler: InputHandler) -> None:
        """Обновление игрового состояния"""
        if self.game_over:
            return

        # Выход из игры
        if input_handler.is_quit_pressed():
            self.game_over = True
            return

        # Пауза
        if input_handler.is_pause_pressed():
            if self.paused:
                self.audio.unpause()
                self.paused = False
            else:
                self.audio.pause()
                self.paused = True

        if self.paused:
            return

        # Текущая позиция в песне
        song_position = self.audio.get_adjusted_position()

        # Проверка на конец песни
        if not self.audio.is_playing():
            self._end_game()
            return

        # Обновление нот
        self.note_controller.update(dt, song_position)

        # Обновление эффектов
        self.renderer.effects.update(dt)

        # Обновление всплывающих текстов
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

        # Проверка попаданий по КРАСНЫМ нотам (RT / →)
        if input_handler.is_hit_red_pressed():
            self.renderer.effects.create_button_press_red(self.red_x, self.hit_line_y)

            result, note = self.note_controller.check_hit_red(song_position)

            if result == HitResult.MISS:
                self._add_floating_text(
                    "MISS", self.red_x, self.hit_line_y, (255, 100, 100), big=True
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

        # Проверка попаданий по СИНИМ нотам (LT / ←)
        if input_handler.is_hit_blue_pressed():
            self.renderer.effects.create_button_press_blue(self.blue_x, self.hit_line_y)

            result, note = self.note_controller.check_hit_blue(song_position)

            if result == HitResult.MISS:
                self._add_floating_text(
                    "MISS", self.blue_x, self.hit_line_y, (255, 100, 100), big=True
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

        # Проверка пропущенных нот
        missed_notes = self.note_controller.check_missed_notes(song_position)
        for note in missed_notes:
            self.score_manager.add_hit(HitResult.MISS)
            self.audio.play_sfx("miss")
            self._add_floating_text("MISS", note.x, note.y, (255, 80, 80), big=True)

    def _add_floating_text(
        self,
        text: str,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        big: bool = False,
    ) -> None:
        """Добавление всплывающего текста"""
        lifetime = 0.7 if big else 0.5
        self.floating_texts.append(FloatingText(text, x, y, color, lifetime))

    def render(self) -> None:
        """Отрисовка игры"""
        self.renderer.render_background()
        self.renderer.render_hit_line()

        # Эффекты кнопок и волн (под нотами)
        self.renderer.render_effects(0.016)

        # Отрисовка нот
        visible_notes = self.note_controller.get_visible_notes()
        self.renderer.render_notes(visible_notes)

        # Всплывающие тексты (поверх нот)
        for ft in self.floating_texts:
            if ft.text in ("PERFECT!", "MISS", "WRONG!"):
                ft.draw(self.screen, self.result_font_big)
            else:
                ft.draw(self.screen, self.result_font)

        # Счет и комбо
        self.renderer.render_score(self.score_manager.stats.score)
        self.renderer.render_combo(self.score_manager.stats.current_combo)

        # Пауза
        if self.paused:
            self._render_pause_overlay()

    def _render_pause_overlay(self) -> None:
        """Оверлей паузы"""
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 72)
        text = font.render("PAUSED", True, (255, 255, 255))
        rect = text.get_rect(
            center=(self.config.screen_width // 2, self.config.screen_height // 2)
        )
        self.screen.blit(text, rect)

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

"""
Игровой экран
"""

import pygame
from typing import Dict, Optional

from utils.config import Config
from input.input_handler import InputHandler
from audio.audio_manager import AudioManager
from core.note_controller import NoteController, HitResult
from core.score_manager import ScoreManager, GameStats
from render.renderer import Renderer


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

        # Статистика
        self.last_hit_result: Optional[HitResult] = None
        self.result_display_timer = 0.0

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

        # Проверка попаданий
        if input_handler.is_hit_pressed():
            result, note = self.note_controller.check_hit(song_position)

            if result != HitResult.MISS:
                score = self.score_manager.add_hit(result)
                self.last_hit_result = result
                self.result_display_timer = 0.5

                # Эффект взрыва
                if note:
                    self.renderer.add_explosion(
                        note.x, note.y, result == HitResult.PERFECT
                    )

                # Звуковой эффект
                self.audio.play_sfx("hit")

        # Проверка пропущенных нот
        missed_notes = self.note_controller.check_missed_notes(song_position)
        for note in missed_notes:
            self.score_manager.add_hit(HitResult.MISS)
            self.audio.play_sfx("miss")

        # Таймер отображения результата
        if self.result_display_timer > 0:
            self.result_display_timer -= dt

    def render(self) -> None:
        """Отрисовка игры"""
        self.renderer.render_background()
        self.renderer.render_hit_line()

        # Отрисовка нот
        visible_notes = self.note_controller.get_visible_notes()
        self.renderer.render_notes(visible_notes)

        # Эффекты
        self.renderer.render_effects(0.016)  # ~60 FPS

        # Счет и комбо
        self.renderer.render_score(self.score_manager.stats.score)
        self.renderer.render_combo(self.score_manager.stats.current_combo)

        # Результат последнего попадания
        if self.result_display_timer > 0 and self.last_hit_result:
            self._render_hit_result()

        # Пауза
        if self.paused:
            self._render_pause_overlay()

    def _render_hit_result(self) -> None:
        """Отображение результата попадания"""
        if self.last_hit_result == HitResult.PERFECT:
            text = "PERFECT!"
            color = (255, 215, 0)
        elif self.last_hit_result == HitResult.GOOD:
            text = "Good"
            color = (100, 255, 100)
        else:
            return

        font = pygame.font.Font(None, 48)
        surf = font.render(text, True, color)
        rect = surf.get_rect(
            center=(self.config.screen_width // 2, self.config.screen_height - 100)
        )
        self.screen.blit(surf, rect)

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

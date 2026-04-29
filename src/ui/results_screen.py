"""
Экран результатов
"""

import pygame
from utils.config import Config
from input.input_handler import InputHandler, Action
from core.score_manager import GameStats, Rank


class ResultsScreen:
    """Отображение результатов игры"""

    def __init__(self, screen: pygame.Surface, config: Config, stats: GameStats):
        self.screen = screen
        self.config = config
        self.stats = stats
        self.back_to_menu = False

        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.stat_font = pygame.font.Font(None, 36)
        self.rank_font = pygame.font.Font(None, 96)

    def update(self, dt: float, input_handler: InputHandler) -> None:
        """Обновление экрана результатов"""
        if input_handler.is_action_just_pressed(
            Action.MENU_SELECT
        ) or input_handler.is_action_just_pressed(Action.MENU_BACK):
            self.back_to_menu = True

    def render(self) -> None:
        """Отрисовка результатов"""
        self.screen.fill((20, 20, 40))

        # Заголовок
        title = self.title_font.render("Results", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.config.screen_width // 2, y=80)
        self.screen.blit(title, title_rect)

        # Ранг
        rank_colors = {
            Rank.SS: (255, 215, 0),
            Rank.S: (255, 255, 0),
            Rank.A: (0, 255, 0),
            Rank.B: (0, 200, 255),
            Rank.C: (255, 165, 0),
            Rank.D: (255, 100, 100),
            Rank.F: (255, 50, 50),
        }
        rank_color = rank_colors.get(self.stats.rank, (255, 255, 255))
        rank_text = self.rank_font.render(self.stats.rank.value, True, rank_color)
        rank_rect = rank_text.get_rect(centerx=self.config.screen_width // 2, y=180)
        self.screen.blit(rank_text, rank_rect)

        # Статистика
        stats_lines = [
            f"Score: {self.stats.score:,}",
            f"Max Combo: {self.stats.max_combo}x",
            f"Perfect: {self.stats.perfect_count}",
            f"Good: {self.stats.good_count}",
            f"Miss: {self.stats.miss_count}",
            f"Accuracy: {self.stats.accuracy:.1f}%",
        ]

        y_offset = 300
        for line in stats_lines:
            text = self.stat_font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(centerx=self.config.screen_width // 2, y=y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 50

        # Подсказка
        hint = self.stat_font.render(
            "Press A or Enter to return to menu", True, (150, 150, 150)
        )
        hint_rect = hint.get_rect(
            centerx=self.config.screen_width // 2, y=self.config.screen_height - 80
        )
        self.screen.blit(hint, hint_rect)

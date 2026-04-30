"""
Основной рендерер игры (ноты сверху вниз, красные справа, синие слева)
"""

import pygame
from typing import List

from utils.config import Config
from core.note_controller import Note, NoteColor
from render.note_sprite import NoteSprite
from render.effects import EffectsManager


class Renderer:
    """Управление рендерингом игровых объектов"""

    def __init__(self, screen: pygame.Surface, config: Config):
        self.screen = screen
        self.config = config
        self.note_sprite = NoteSprite(config)
        self.effects = EffectsManager(config)

        # Цвета
        self.bg_color = (10, 10, 30)
        self.hit_line_color = (255, 255, 255)
        self.combo_color = (255, 215, 0)

        # Позиции дорожек из конфига
        self.red_x = config.red_lane_x
        self.blue_x = config.blue_lane_x
        self.hit_line_y = config.hit_line_y
        self.lane_width = config.lane_width
        self.lane_alpha = config.lane_alpha

        # Шрифты
        self.combo_font = pygame.font.Font(None, 72)
        self.score_font = pygame.font.Font(None, 36)
        self.zone_font = pygame.font.Font(None, 28)

    def render_background(self) -> None:
        """Отрисовка фона"""
        self.screen.fill(self.bg_color)

        # Декоративные линии
        for i in range(0, self.config.screen_width, 100):
            alpha = 15
            surf = pygame.Surface((2, self.config.screen_height))
            surf.set_alpha(alpha)
            surf.fill((50, 50, 80))
            self.screen.blit(surf, (i, 0))

    def render_hit_line(self) -> None:
        """Отрисовка линии удара и дорожек"""
        y = self.hit_line_y

        # Горизонтальная линия удара
        pygame.draw.line(
            self.screen,
            self.hit_line_color,
            (50, y),
            (self.config.screen_width - 50, y),
            3,
        )

        # Левая дорожка (синие ноты)
        lane_half = self.lane_width // 2
        blue_zone = pygame.Surface(
            (self.lane_width, self.config.screen_height), pygame.SRCALPHA
        )
        blue_zone.fill((0, 100, 255, self.lane_alpha))
        self.screen.blit(blue_zone, (self.blue_x - lane_half, 0))

        # Правая дорожка (красные ноты)
        red_zone = pygame.Surface(
            (self.lane_width, self.config.screen_height), pygame.SRCALPHA
        )
        red_zone.fill((255, 0, 0, self.lane_alpha))
        self.screen.blit(red_zone, (self.red_x - lane_half, 0))

        # Подписи дорожек
        lt_text = self.zone_font.render("LT / ←", True, (100, 150, 255))
        rt_text = self.zone_font.render("RT / →", True, (255, 100, 100))

        self.screen.blit(lt_text, (self.blue_x - 40, y + 20))
        self.screen.blit(rt_text, (self.red_x - 40, y + 20))

        # Зоны попадания
        pygame.draw.circle(
            self.screen, (100, 150, 255, 100), (int(self.blue_x), y), 50, 2
        )
        pygame.draw.circle(
            self.screen, (255, 100, 100, 100), (int(self.red_x), y), 50, 2
        )

    def render_notes(self, notes: List[Note]) -> None:
        """Отрисовка нот с учётом цвета"""
        for note in notes:
            if note.hit or note.missed:
                continue

            distance = abs(note.y - self.hit_line_y)
            max_distance = self.config.screen_height
            brightness = max(0.3, 1.0 - (distance / max_distance))

            self.note_sprite.draw(self.screen, note.x, note.y, note.color, brightness)

    def render_effects(self, dt: float) -> None:
        """Отрисовка эффектов"""
        self.effects.update(dt)
        self.effects.draw(self.screen)

    def render_combo(self, combo: int) -> None:
        """Отрисовка счетчика комбо"""
        if combo > 1:
            text = self.combo_font.render(f"{combo}x", True, self.combo_color)
            if combo >= 50:
                scale = 1.0 + (combo % 10) * 0.05
                text = pygame.transform.scale(
                    text,
                    (int(text.get_width() * scale), int(text.get_height() * scale)),
                )

            text_rect = text.get_rect(center=(self.config.screen_width // 2, 50))
            self.screen.blit(text, text_rect)

    def render_score(self, score: int) -> None:
        """Отрисовка счета"""
        text = self.score_font.render(f"Score: {score:,}", True, (255, 255, 255))
        self.screen.blit(text, (20, 20))

    def add_explosion(self, x: float, y: float, perfect: bool = False) -> None:
        """Добавление эффекта взрыва"""
        self.effects.create_explosion(x, y, perfect)

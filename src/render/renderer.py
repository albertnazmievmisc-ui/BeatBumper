"""
Основной рендерер игры
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
        self.bg_color = (10, 10, 30)  # Темно-синий фон
        self.hit_line_color = (255, 255, 255)  # Белая линия удара
        self.hit_line_red = (255, 80, 80, 100)  # Полупрозрачная красная
        self.hit_line_blue = (80, 140, 255, 100)  # Полупрозрачная синяя
        self.combo_color = (255, 215, 0)  # Золотой для комбо

        # Шрифты
        self.combo_font = pygame.font.Font(None, 72)
        self.score_font = pygame.font.Font(None, 36)

    def render_background(self) -> None:
        """Отрисовка фона"""
        self.screen.fill(self.bg_color)

        # Декоративные линии
        for i in range(0, self.config.screen_height, 100):
            alpha = 20
            surf = pygame.Surface((self.config.screen_width, 2))
            surf.set_alpha(alpha)
            surf.fill((50, 50, 80))
            self.screen.blit(surf, (0, i))

    def render_hit_line(self) -> None:
        """Отрисовка линии удара и зон для красных/синих нот"""
        x = self.config.hit_line_x

        # Основная линия удара
        pygame.draw.line(
            self.screen,
            self.hit_line_color,
            (x, 50),
            (x, self.config.screen_height - 50),
            3,
        )

        # Зоны удара для красных и синих нот (визуальная подсказка)
        zone_width = 80
        zone_height = self.config.screen_height // 2

        # Красная зона (сверху)
        red_zone = pygame.Surface((zone_width, zone_height), pygame.SRCALPHA)
        red_zone.fill((255, 0, 0, 20))
        self.screen.blit(red_zone, (x - zone_width // 2, 50))

        # Синяя зона (снизу)
        blue_zone = pygame.Surface((zone_width, zone_height), pygame.SRCALPHA)
        blue_zone.fill((0, 100, 255, 20))
        self.screen.blit(blue_zone, (x - zone_width // 2, zone_height + 50))

        # Подписи
        font = pygame.font.Font(None, 24)
        red_text = font.render("A / SPACE", True, (255, 100, 100))
        blue_text = font.render("X / SHIFT", True, (100, 150, 255))
        self.screen.blit(red_text, (x - 200, self.config.screen_height // 2 - 100))
        self.screen.blit(blue_text, (x - 200, self.config.screen_height // 2 + 60))

    def render_notes(self, notes: List[Note]) -> None:
        """Отрисовка нот с учётом цвета"""
        for note in notes:
            if note.hit or note.missed:
                continue

            # Яркость зависит от расстояния до линии удара
            distance = abs(note.x - self.config.hit_line_x)
            max_distance = self.config.screen_width
            brightness = max(0.3, 1.0 - (distance / max_distance))

            self.note_sprite.draw(
                self.screen,
                note.x,
                note.y,
                note.color,  # Передаём цвет ноты
                brightness,
            )

    def render_effects(self, dt: float) -> None:
        """Отрисовка эффектов"""
        self.effects.update(dt)
        self.effects.draw(self.screen)

    def render_combo(self, combo: int) -> None:
        """Отрисовка счетчика комбо"""
        if combo > 1:
            text = self.combo_font.render(f"{combo}x", True, self.combo_color)
            # Пульсация при высоком комбо
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

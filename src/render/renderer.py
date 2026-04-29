"""
Основной рендерер игры
"""

import pygame
from typing import List

from utils.config import Config
from core.note_controller import Note
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
        """Отрисовка линии удара"""
        x = self.config.hit_line_x
        pygame.draw.line(
            self.screen,
            self.hit_line_color,
            (x, 0),
            (x, self.config.screen_height),
            3
        )
    
    def render_notes(self, notes: List[Note]) -> None:
        """Отрисовка нот"""
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
                brightness
            )
    
    def render_effects(self, dt: float) -> None:
        """Отрисовка эффектов"""
        self.effects.update(dt)
        self.effects.draw(self.screen)
    
    def render_combo(self, combo: int) -> None:
        """Отрисовка счетчика комбо"""
        if combo > 1:
            text = self.combo_font.render(
                f"{combo}x", 
                True, 
                self.combo_color
            )
            # Пульсация при высоком комбо
            if combo >= 50:
                scale = 1.0 + (combo % 10) * 0.05
                text = pygame.transform.scale(
                    text,
                    (int(text.get_width() * scale),
                     int(text.get_height() * scale))
                )
            
            text_rect = text.get_rect(
                center=(self.config.screen_width // 2, 50)
            )
            self.screen.blit(text, text_rect)
    
    def render_score(self, score: int) -> None:
        """Отрисовка счета"""
        text = self.score_font.render(
            f"Score: {score:,}", 
            True, 
            (255, 255, 255)
        )
        self.screen.blit(text, (20, 20))
    
    def add_explosion(self, x: float, y: float, perfect: bool = False) -> None:
        """Добавление эффекта взрыва"""
        self.effects.create_explosion(x, y, perfect)

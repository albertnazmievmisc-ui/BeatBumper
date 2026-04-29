"""
Спрайт ноты
"""

import pygame
from utils.config import Config


class NoteSprite:
    """Графическое представление ноты"""
    
    def __init__(self, config: Config):
        self.config = config
        self.note_width = 80
        self.note_height = 80
        
        # Создание спрайта ноты
        self.sprite = self._create_note_sprite()
        
    def _create_note_sprite(self) -> pygame.Surface:
        """Создание спрайта ноты"""
        surface = pygame.Surface(
            (self.note_width, self.note_height), 
            pygame.SRCALPHA
        )
        
        # Красный круг с градиентом
        center = (self.note_width // 2, self.note_height // 2)
        max_radius = self.note_width // 2 - 5
        
        for radius in range(max_radius, 0, -1):
            alpha = min(255, int(255 * (radius / max_radius)))
            color = (255, 50 - int(30 * radius / max_radius), 50, alpha)
            pygame.draw.circle(surface, color, center, radius)
        
        # Белая обводка
        pygame.draw.circle(
            surface, 
            (255, 255, 255, 200), 
            center, 
            max_radius, 
            2
        )
        
        return surface
    
    def draw(self, screen: pygame.Surface, x: float, y: float, brightness: float = 1.0) -> None:
        """Отрисовка ноты"""
        # Применяем яркость
        sprite_copy = self.sprite.copy()
        
        # Затемнение
        if brightness < 1.0:
            dark_surface = pygame.Surface(
                (self.note_width, self.note_height),
                pygame.SRCALPHA
            )
            alpha = int(255 * (1 - brightness))
            dark_surface.fill((0, 0, 0, alpha))
            sprite_copy.blit(dark_surface, (0, 0))
        
        # Позиционирование
        rect = sprite_copy.get_rect()
        rect.centerx = int(x)
        rect.centery = int(y)
        
        screen.blit(sprite_copy, rect)

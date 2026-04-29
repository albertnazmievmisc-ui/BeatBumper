"""
Спрайты нот (красные и синие)
"""

import pygame
from utils.config import Config
from core.note_controller import NoteColor


class NoteSprite:
    """Графическое представление ноты"""

    def __init__(self, config: Config):
        self.config = config
        self.note_width = 80
        self.note_height = 80

        # Создаём спрайты для обоих цветов
        self.red_sprite = self._create_note_sprite(NoteColor.RED)
        self.blue_sprite = self._create_note_sprite(NoteColor.BLUE)

    def _create_note_sprite(self, color: NoteColor) -> pygame.Surface:
        """Создание спрайта ноты указанного цвета"""
        surface = pygame.Surface((self.note_width, self.note_height), pygame.SRCALPHA)

        center = (self.note_width // 2, self.note_height // 2)
        max_radius = self.note_width // 2 - 5

        # Определяем цвета для градиента
        if color == NoteColor.RED:
            dark_color = (180, 30, 30)  # Тёмно-красный
            light_color = (255, 80, 80)  # Светло-красный
            arrow_direction = "down"
        else:
            dark_color = (30, 60, 200)  # Тёмно-синий
            light_color = (80, 140, 255)  # Светло-синий
            arrow_direction = "up"

        # Градиентный круг (от светлого края к тёмному центру)
        for radius in range(max_radius, 0, -1):
            progress = radius / max_radius
            alpha = min(255, int(255 * progress))

            r = int(light_color[0] + (dark_color[0] - light_color[0]) * (1 - progress))
            g = int(light_color[1] + (dark_color[1] - light_color[1]) * (1 - progress))
            b = int(light_color[2] + (dark_color[2] - light_color[2]) * (1 - progress))

            pygame.draw.circle(surface, (r, g, b, alpha), center, radius)

        # Белая обводка
        pygame.draw.circle(surface, (255, 255, 255, 220), center, max_radius, 3)

        # Стрелка направления
        arrow_size = 18
        arrow_y_offset = 8

        if arrow_direction == "down":
            # Стрелка вниз (красные ноты)
            points = [
                (center[0], center[1] - arrow_size + arrow_y_offset),
                (
                    center[0] - arrow_size // 2,
                    center[1] + arrow_size // 3 + arrow_y_offset,
                ),
                (
                    center[0] + arrow_size // 2,
                    center[1] + arrow_size // 3 + arrow_y_offset,
                ),
            ]
        else:
            # Стрелка вверх (синие ноты)
            points = [
                (center[0], center[1] + arrow_size - arrow_y_offset),
                (
                    center[0] - arrow_size // 2,
                    center[1] - arrow_size // 3 - arrow_y_offset,
                ),
                (
                    center[0] + arrow_size // 2,
                    center[1] - arrow_size // 3 - arrow_y_offset,
                ),
            ]

        pygame.draw.polygon(surface, (255, 255, 255, 220), points)

        return surface

    def draw(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        color: NoteColor,
        brightness: float = 1.0,
    ) -> None:
        """Отрисовка ноты выбранного цвета"""
        # Выбираем спрайт по цвету
        sprite = self.red_sprite if color == NoteColor.RED else self.blue_sprite
        sprite_copy = sprite.copy()

        # Применяем яркость (дальние ноты темнее)
        if brightness < 1.0:
            dark_surface = pygame.Surface(
                (self.note_width, self.note_height), pygame.SRCALPHA
            )
            alpha = int(255 * (1 - brightness))
            dark_surface.fill((0, 0, 0, alpha))
            sprite_copy.blit(dark_surface, (0, 0))

        # Позиционирование
        rect = sprite_copy.get_rect()
        rect.centerx = int(x)
        rect.centery = int(y)

        screen.blit(sprite_copy, rect)

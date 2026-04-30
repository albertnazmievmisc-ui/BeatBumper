"""
Визуальные эффекты: взрывы, ударные волны, эффекты нажатия кнопок
"""

import pygame
import random
import math
from typing import List, Tuple
from utils.config import Config


class Particle:
    """Частица для эффектов"""

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        speed: float = 0,
        angle: float = 0,
        lifetime: float = 1.0,
        size: int = 3,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.angle = angle
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self, dt: float) -> bool:
        """Обновление частицы. Возвращает False если частица умерла"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.95  # Затухание
        self.vy *= 0.95

        return True

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка частицы"""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))

        if size > 0:
            color = (*self.color, alpha)
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size, size), size)
            screen.blit(surf, (int(self.x - size), int(self.y - size)))


class Shockwave:
    """Ударная волна"""

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        max_radius: float = 100,
        lifetime: float = 0.5,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 0
        self.max_radius = max_radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self, dt: float) -> bool:
        """Обновление волны"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        progress = 1 - (self.lifetime / self.max_lifetime)
        self.radius = self.max_radius * progress
        return True

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка волны"""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha)

        surf = pygame.Surface(
            (self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            surf,
            color,
            (self.max_radius, self.max_radius),
            int(self.radius),
            max(1, int(3 * self.lifetime / self.max_lifetime)),
        )
        screen.blit(
            surf, (int(self.x - self.max_radius), int(self.y - self.max_radius))
        )


class ButtonPressEffect:
    """Эффект нажатия кнопки (свечение дорожки)"""

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        lane_width: int = 120,
        lifetime: float = 0.3,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.lane_width = lane_width
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.flash_alpha = 255

    def update(self, dt: float) -> bool:
        """Обновление эффекта"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        self.flash_alpha = int(255 * (self.lifetime / self.max_lifetime))
        return True

    def draw(self, screen: pygame.Surface, screen_height: int) -> None:
        """Отрисовка свечения дорожки"""
        # Вертикальная полоса свечения
        surf = pygame.Surface((self.lane_width, screen_height), pygame.SRCALPHA)

        # Градиент от яркого к прозрачному (сверху вниз)
        for i in range(screen_height):
            # Самая яркая часть внизу (у линии удара)
            distance_from_bottom = screen_height - i
            alpha = int(self.flash_alpha * (distance_from_bottom / screen_height) * 0.5)

            if alpha > 0:
                color = (*self.color, alpha)
                pygame.draw.line(surf, color, (0, i), (self.lane_width, i))

        screen.blit(surf, (int(self.x - self.lane_width // 2), 0))

        # Яркая вспышка внизу (имитация нажатия)
        flash_size = int(80 * (self.lifetime / self.max_lifetime))
        if flash_size > 0:
            flash_surf = pygame.Surface(
                (flash_size * 2, flash_size * 2), pygame.SRCALPHA
            )
            alpha = self.flash_alpha
            flash_color = (255, 255, 255, alpha)
            pygame.draw.circle(
                flash_surf, flash_color, (flash_size, flash_size), flash_size
            )
            screen.blit(
                flash_surf, (int(self.x - flash_size), int(self.y - flash_size))
            )


class EffectsManager:
    """Менеджер всех визуальных эффектов"""

    def __init__(self, config: Config):
        self.config = config
        self.particles: List[Particle] = []
        self.shockwaves: List[Shockwave] = []
        self.button_effects: List[ButtonPressEffect] = []

        # Цвета
        self.red_color = (255, 80, 80)
        self.blue_color = (80, 140, 255)
        self.gold_color = (255, 215, 0)
        self.white_color = (255, 255, 255)

    def create_explosion(self, x: float, y: float, perfect: bool = False) -> None:
        """Создание взрыва при попадании по ноте"""
        color = self.gold_color if perfect else self.white_color
        num_particles = 30 if perfect else 15

        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300) if perfect else random.uniform(50, 150)
            lifetime = random.uniform(0.3, 0.8) if perfect else random.uniform(0.2, 0.5)
            size = random.randint(3, 6) if perfect else random.randint(2, 4)

            self.particles.append(Particle(x, y, color, speed, angle, lifetime, size))

        # Ударная волна
        self.shockwaves.append(
            Shockwave(x, y, color, 80 if perfect else 50, 0.5 if perfect else 0.3)
        )

    def create_button_press_red(self, x: float, y: float) -> None:
        """Эффект нажатия красной кнопки (RT)"""
        self.button_effects.append(ButtonPressEffect(x, y, self.red_color, 120, 0.3))

        # Несколько частиц для отдачи
        for _ in range(8):
            angle = random.uniform(-math.pi * 0.3, math.pi * 0.3)  # Вверх
            speed = random.uniform(50, 150)
            self.particles.append(Particle(x, y, self.red_color, speed, angle, 0.3, 3))

    def create_button_press_blue(self, x: float, y: float) -> None:
        """Эффект нажатия синей кнопки (LT)"""
        self.button_effects.append(ButtonPressEffect(x, y, self.blue_color, 120, 0.3))

        # Несколько частиц для отдачи
        for _ in range(8):
            angle = random.uniform(-math.pi * 0.3, math.pi * 0.3)  # Вверх
            speed = random.uniform(50, 150)
            self.particles.append(Particle(x, y, self.blue_color, speed, angle, 0.3, 3))

    def update(self, dt: float) -> None:
        """Обновление всех эффектов"""
        # Обновление частиц
        self.particles = [p for p in self.particles if p.update(dt)]

        # Обновление ударных волн
        self.shockwaves = [s for s in self.shockwaves if s.update(dt)]

        # Обновление эффектов кнопок
        self.button_effects = [b for b in self.button_effects if b.update(dt)]

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка всех эффектов"""
        # Сначала эффекты кнопок (фон)
        for effect in self.button_effects:
            effect.draw(screen, self.config.screen_height)

        # Затем ударные волны
        for wave in self.shockwaves:
            wave.draw(screen)

        # Затем частицы (поверх всего)
        for particle in self.particles:
            particle.draw(screen)

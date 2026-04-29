"""
Визуальные эффекты
"""

import pygame
import random
import math
from typing import List, Tuple


class Particle:
    """Частица для эффектов"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-200, 200)
        self.vy = random.uniform(-200, -100)
        self.color = color
        self.life = random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.size = random.randint(3, 8)
    
    def update(self, dt: float) -> bool:
        """Обновление частицы, возвращает False если умерла"""
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 500 * dt  # Гравитация
        return self.life > 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка частицы"""
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        
        surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.size, self.size), self.size)
        
        screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))


class Shockwave:
    """Ударная волна"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10
        self.max_radius = 80
        self.speed = 200
        self.life = 0.5
    
    def update(self, dt: float) -> bool:
        """Обновление волны"""
        self.radius += self.speed * dt
        self.life -= dt
        return self.life > 0 and self.radius < self.max_radius
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка волны"""
        alpha = int(255 * (self.life / 0.5))
        color = (*self.color, alpha)
        
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.radius, self.radius), int(self.radius), 3)
        
        screen.blit(surface, (int(self.x - self.radius), int(self.y - self.radius)))


class EffectsManager:
    """Менеджер визуальных эффектов"""
    
    def __init__(self, config):
        self.config = config
        self.particles: List[Particle] = []
        self.shockwaves: List[Shockwave] = []
    
    def create_explosion(self, x: float, y: float, perfect: bool = False) -> None:
        """Создание взрыва"""
        if perfect:
            colors = [(255, 215, 0), (255, 255, 100)]  # Золотой
            particle_count = 30
        else:
            colors = [(255, 50, 50), (255, 100, 100)]  # Красный
            particle_count = 15
        
        # Создание частиц
        for _ in range(particle_count):
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color))
        
        # Создание ударной волны
        wave_color = colors[0]
        self.shockwaves.append(Shockwave(x, y, wave_color))
    
    def update(self, dt: float) -> None:
        """Обновление всех эффектов"""
        self.particles = [p for p in self.particles if p.update(dt)]
        self.shockwaves = [w for w in self.shockwaves if w.update(dt)]
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка всех эффектов"""
        for wave in self.shockwaves:
            wave.draw(screen)
        for particle in self.particles:
            particle.draw(screen)

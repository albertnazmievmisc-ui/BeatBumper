#!/usr/bin/env python3
"""
BeatBumper - Ритм-игра для Steam Deck
Главная точка входа
"""

import sys
import os
import pygame
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.game_engine import GameEngine
from utils.config import Config


def main() -> None:
    """Инициализация и запуск игры"""
    print("🎵 BeatBumper v0.1.0")
    print(f"📁 Рабочая директория: {os.getcwd()}")

    # Загрузка конфигурации
    config = Config.load()
    config.apply()

    # Инициализация Pygame
    pygame.init()
    pygame.display.set_caption("BeatBumper")

    # Определение режима экрана
    if config.fullscreen:
        screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        )
    else:
        screen = pygame.display.set_mode(
            (config.screen_width, config.screen_height),
            pygame.DOUBLEBUF | pygame.HWSURFACE,
        )

    print(f"🖥️  Разрешение: {screen.get_width()}x{screen.get_height()}")

    # Запуск игрового движка
    engine = GameEngine(screen, config)

    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        raise
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()

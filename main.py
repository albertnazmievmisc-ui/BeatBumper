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
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Убеждаемся, что src в пути
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))


def main() -> None:
    """Инициализация и запуск игры"""
    print("🎵 BeatBumper v0.2.0")
    print(f"📁 Рабочая директория: {os.getcwd()}")

    # Инициализация Pygame ДО загрузки конфига
    # (нужно для определения разрешения экрана)
    pygame.init()

    # Загрузка конфигурации
    from utils.config import Config

    config = Config()
    print("⚙️  Конфигурация загружена")

    # Определение режима экрана
    if config.fullscreen:
        screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        # Обновляем разрешение в конфиге
        config.update_resolution(screen.get_width(), screen.get_height())
    else:
        screen = pygame.display.set_mode(
            (config.screen_width, config.screen_height),
            pygame.DOUBLEBUF | pygame.HWSURFACE,
        )

    pygame.display.set_caption("BeatBumper")

    print(f"🖥️  Разрешение: {screen.get_width()}x{screen.get_height()}")

    # Импортируем GameEngine после настройки путей
    from core.game_engine import GameEngine

    # Запуск игрового движка
    engine = GameEngine(screen, config)

    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()

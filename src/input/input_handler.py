"""
Обработчик ввода для Steam Deck
"""

import pygame
from enum import Enum, auto
from typing import Set

from utils.config import Config


class Action(Enum):
    """Игровые действия"""

    HIT = auto()  # Нажатие пробела / A кнопки
    PAUSE = auto()  # Пауза
    QUIT = auto()  # Выход
    FULLSCREEN = auto()  # Переключение полноэкранного режима
    MENU_UP = auto()  # Навигация в меню
    MENU_DOWN = auto()
    MENU_SELECT = auto()
    MENU_BACK = auto()


class InputHandler:
    """Обработка всего ввода"""

    def __init__(self, config: Config):
        self.config = config

        # Инициализация джойстика (Steam Deck геймпад)
        self.joystick = None
        self._init_joystick()

        # Состояния клавиш
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()

        # Состояния кнопок геймпада
        self.buttons_pressed: Set[int] = set()
        self.buttons_just_pressed: Set[int] = set()

        # Маппинг действий
        self.action_map = {
            Action.HIT: [pygame.K_SPACE],
            Action.PAUSE: [pygame.K_ESCAPE, pygame.K_p],
            Action.QUIT: [pygame.K_q],
            Action.FULLSCREEN: [(pygame.K_RETURN, pygame.KMOD_ALT)],
            Action.MENU_UP: [pygame.K_UP],
            Action.MENU_DOWN: [pygame.K_DOWN],
            Action.MENU_SELECT: [pygame.K_RETURN],
            Action.MENU_BACK: [pygame.K_ESCAPE],
        }

        # Маппинг геймпада

        self.joystick_action_map = {
            Action.HIT: [0],  # A кнопка
            Action.PAUSE: [7],  # Start
            Action.MENU_BACK: [1],  # B кнопка
            Action.QUIT: [6],  # Back/Select - добавить эту строку
        }

    def _init_joystick(self) -> None:
        """Инициализация геймпада"""
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"🎮 Геймпад подключен: {self.joystick.get_name()}")

    def update(self) -> None:
        """Обновление состояния ввода"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.buttons_just_pressed.clear()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                self.keys_just_released.add(event.key)

            elif event.type == pygame.JOYBUTTONDOWN:
                self.buttons_pressed.add(event.button)
                self.buttons_just_pressed.add(event.button)

            elif event.type == pygame.JOYBUTTONUP:
                self.buttons_pressed.discard(event.button)

    def is_action_pressed(self, action: Action) -> bool:
        """Проверка удержания действия"""
        # Проверка клавиатуры
        for key in self.action_map.get(action, []):
            if isinstance(key, tuple):
                k, mod = key
                if k in self.keys_pressed and pygame.key.get_mods() & mod:
                    return True
            elif key in self.keys_pressed:
                return True

        # Проверка геймпада
        for button in self.joystick_action_map.get(action, []):
            if button in self.buttons_pressed:
                return True

        return False

    def is_action_just_pressed(self, action: Action) -> bool:
        """Проверка однократного нажатия"""
        # Клавиатура
        for key in self.action_map.get(action, []):
            if not isinstance(key, tuple) and key in self.keys_just_pressed:
                return True

        # Геймпад
        for button in self.joystick_action_map.get(action, []):
            if button in self.buttons_just_pressed:
                return True

        return False

    def is_hit_pressed(self) -> bool:
        """Проверка нажатия для удара (мгновенное)"""
        return self.is_action_just_pressed(Action.HIT)

    def is_quit_pressed(self) -> bool:
        return self.is_action_just_pressed(Action.QUIT)

    def is_pause_pressed(self) -> bool:
        return self.is_action_just_pressed(Action.PAUSE)

    def is_fullscreen_toggle(self) -> bool:
        return self.is_action_just_pressed(Action.FULLSCREEN)

"""
Обработчик ввода для Steam Deck (триггеры для ударов)
"""

import pygame
from enum import Enum, auto
from typing import Set

from utils.config import Config


class Action(Enum):
    """Игровые действия"""

    HIT_RED = auto()  # RT - правый триггер / красные ноты
    HIT_BLUE = auto()  # LT - левый триггер / синие ноты
    PAUSE = auto()
    QUIT = auto()
    FULLSCREEN = auto()
    MENU_UP = auto()
    MENU_DOWN = auto()
    MENU_SELECT = auto()
    MENU_BACK = auto()


class InputHandler:
    """Обработка всего ввода"""

    def __init__(self, config: Config):
        self.config = config

        # Инициализация джойстика
        self.joystick = None
        self._init_joystick()

        # Состояния клавиш
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()

        # Состояния кнопок геймпада
        self.buttons_pressed: Set[int] = set()
        self.buttons_just_pressed: Set[int] = set()

        # Состояния осей (для триггеров)
        self.axes_values: List[float] = []
        self.rt_just_pressed = False  # Правый триггер
        self.lt_just_pressed = False  # Левый триггер
        self.rt_was_pressed = False
        self.lt_was_pressed = False

        # Маппинг действий на клавиатуру
        self.action_map = {
            Action.HIT_RED: [pygame.K_RIGHT, pygame.K_d],  # Стрелка вправо / D
            Action.HIT_BLUE: [pygame.K_LEFT, pygame.K_a],  # Стрелка влево / A
            Action.PAUSE: [pygame.K_ESCAPE, pygame.K_p],
            Action.QUIT: [pygame.K_q],
            Action.FULLSCREEN: [(pygame.K_RETURN, pygame.KMOD_ALT)],
            Action.MENU_UP: [pygame.K_UP],
            Action.MENU_DOWN: [pygame.K_DOWN],
            Action.MENU_SELECT: [pygame.K_RETURN],
            Action.MENU_BACK: [pygame.K_ESCAPE],
        }

        # Маппинг действий на геймпад
        self.joystick_action_map = {
            Action.PAUSE: [7],  # Start
            Action.MENU_SELECT: [0],  # A
            Action.MENU_BACK: [1],  # B
            Action.QUIT: [6],  # Back/Select
        }

    def _init_joystick(self) -> None:
        """Инициализация геймпада"""
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"🎮 Геймпад подключен: {self.joystick.get_name()}")
            self.axes_values = [0.0] * self.joystick.get_numaxes()

    def update(self) -> None:
        """Обновление состояния ввода"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.buttons_just_pressed.clear()
        self.rt_just_pressed = False
        self.lt_just_pressed = False

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

            elif event.type == pygame.JOYAXISMOTION:
                if event.axis < len(self.axes_values):
                    self.axes_values[event.axis] = event.value

        # Обработка триггеров (оси 4 = LT, 5 = RT на Xbox/Steam Deck)
        if self.joystick:
            # Правый триггер (RT) - обычно ось 5 или 4
            rt_value = self._get_trigger_value(5)  # RT
            rt_pressed = rt_value > 0.3
            if rt_pressed and not self.rt_was_pressed:
                self.rt_just_pressed = True
            self.rt_was_pressed = rt_pressed

            # Левый триггер (LT) - обычно ось 4 или 2
            lt_value = self._get_trigger_value(4)  # LT
            lt_pressed = lt_value > 0.3
            if lt_pressed and not self.lt_was_pressed:
                self.lt_just_pressed = True
            self.lt_was_pressed = lt_pressed

    def _get_trigger_value(self, axis: int) -> float:
        """Безопасное получение значения оси триггера"""
        if self.joystick and axis < len(self.axes_values):
            return self.axes_values[axis]
        return 0.0

    def is_action_pressed(self, action: Action) -> bool:
        """Проверка удержания действия"""
        # Клавиатура
        for key in self.action_map.get(action, []):
            if isinstance(key, tuple):
                k, mod = key
                if k in self.keys_pressed and pygame.key.get_mods() & mod:
                    return True
            elif key in self.keys_pressed:
                return True

        # Геймпад (кнопки)
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

        # Геймпад (кнопки)
        for button in self.joystick_action_map.get(action, []):
            if button in self.buttons_just_pressed:
                return True

        return False

    def is_hit_red_pressed(self) -> bool:
        """Проверка нажатия RT (правый триггер) или клавиш"""
        if self.is_action_just_pressed(Action.HIT_RED):
            return True
        return self.rt_just_pressed

    def is_hit_blue_pressed(self) -> bool:
        """Проверка нажатия LT (левый триггер) или клавиш"""
        if self.is_action_just_pressed(Action.HIT_BLUE):
            return True
        return self.lt_just_pressed

    def is_quit_pressed(self) -> bool:
        return self.is_action_just_pressed(Action.QUIT)

    def is_pause_pressed(self) -> bool:
        return self.is_action_just_pressed(Action.PAUSE)

    def is_fullscreen_toggle(self) -> bool:
        return self.is_action_just_pressed(Action.FULLSCREEN)

"""
Главный игровой движок BeatBumper
Управляет игровым циклом и состояниями игры
"""

import pygame
import time
from enum import Enum, auto
from typing import Optional

from utils.config import Config
from input.input_handler import InputHandler, Action
from audio.audio_manager import AudioManager
from ui.menu_screen import MenuScreen
from ui.game_screen import GameScreen
from ui.results_screen import ResultsScreen


class GameState(Enum):
    """Состояния игры"""

    MENU = auto()
    PLAYING = auto()
    RESULTS = auto()
    QUIT = auto()


class GameEngine:
    """Основной игровой движок"""

    def __init__(self, screen: pygame.Surface, config: Config):
        self.screen = screen
        self.config = config
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU

        # Подсистемы
        self.input_handler = InputHandler(config)
        self.audio_manager = AudioManager(config)

        # Экраны
        self.menu_screen = MenuScreen(screen, config)
        self.game_screen: Optional[GameScreen] = None
        self.results_screen: Optional[ResultsScreen] = None

        # Статистика FPS
        self.fps_history = []
        self.show_fps = config.debug_mode

    def run(self) -> None:
        """Главный игровой цикл"""
        while self.running:
            dt = self.clock.tick(self.config.target_fps) / 1000.0

            # Обработка ввода
            self.input_handler.update()
            self._handle_global_input()

            # Обновление текущего состояния
            self._update_state(dt)

            # Рендеринг
            self._render()

            # Обновление дисплея
            pygame.display.flip()

            # Мониторинг FPS
            if self.show_fps:
                self._update_fps_monitor()

    def _handle_global_input(self) -> None:
        """Обработка глобальных клавиш (работают всегда)"""
        # Alt+Enter для переключения полноэкранного режима
        if self.input_handler.is_fullscreen_toggle():
            self.config.toggle_fullscreen()

    def _update_state(self, dt: float) -> None:
        """Обновление текущего состояния игры"""
        if self.state == GameState.MENU:
            self.menu_screen.update(dt, self.input_handler)

            # Проверка выхода из меню
            if self.menu_screen.quit_requested:
                print("👋 Выход из игры (меню)")
                self.running = False
                return

            if self.menu_screen.start_game_requested:
                self._start_game()

        elif self.state == GameState.PLAYING:
            if self.game_screen:
                self.game_screen.update(dt, self.input_handler)

                # Проверка завершения игры
                if self.game_screen.game_over:
                    # Останавливаем аудио если ещё играет
                    if self.audio_manager.is_playing():
                        self.audio_manager.stop()

                    # Если запрошен выход в меню
                    if self.game_screen.quit_requested:
                        print("📋 Выход в главное меню")
                        self._return_to_menu()
                    else:
                        # Показываем результаты
                        self._show_results()

        elif self.state == GameState.RESULTS:
            if self.results_screen:
                self.results_screen.update(dt, self.input_handler)

                # Проверка выхода из результатов (Q или Back)
                if self.input_handler.is_quit_pressed():
                    print("👋 Выход из игры (результаты)")
                    self.running = False
                    return

                if self.results_screen.back_to_menu:
                    self._return_to_menu()

    def _return_to_menu(self) -> None:
        """Возврат в главное меню"""
        self.state = GameState.MENU
        self.game_screen = None
        self.results_screen = None
        self.menu_screen.start_game_requested = False
        self.menu_screen.quit_requested = False
        self.menu_screen.selected_song = None

    def _render(self) -> None:
        """Отрисовка текущего состояния"""
        self.screen.fill((0, 0, 0))

        if self.state == GameState.MENU:
            self.menu_screen.render()
        elif self.state == GameState.PLAYING:
            if self.game_screen:
                self.game_screen.render()
        elif self.state == GameState.RESULTS:
            if self.results_screen:
                self.results_screen.render()

        # FPS счетчик
        if self.show_fps:
            self._render_fps()

    def _start_game(self) -> None:
        """Запуск игровой сессии"""
        selected_song = self.menu_screen.selected_song
        if not selected_song:
            print("❌ Нет выбранной песни!")
            return

        self.game_screen = GameScreen(
            self.screen, self.config, self.audio_manager, selected_song
        )
        self.state = GameState.PLAYING
        print(f"🎮 Запуск: {selected_song['name']}")

    def _show_results(self) -> None:
        """Показ результатов"""
        if self.game_screen:
            stats = self.game_screen.get_stats()
            self.results_screen = ResultsScreen(self.screen, self.config, stats)
            self.state = GameState.RESULTS
            self.game_screen = None

    def _update_fps_monitor(self) -> None:
        """Обновление статистики FPS"""
        self.fps_history.append(self.clock.get_fps())
        if len(self.fps_history) > 100:
            self.fps_history.pop(0)

    def _render_fps(self) -> None:
        """Отрисовка счетчика FPS"""
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            font = pygame.font.Font(None, 24)
            fps_text = font.render(f"FPS: {int(avg_fps)}", True, (0, 255, 0))
            self.screen.blit(fps_text, (10, 10))

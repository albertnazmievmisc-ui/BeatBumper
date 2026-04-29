"""
Менеджер аудио для BeatBumper
"""

import pygame
from pathlib import Path
from typing import Optional

from utils.config import Config


class AudioManager:
    """Управление музыкой и звуковыми эффектами"""
    
    def __init__(self, config: Config):
        self.config = config
        self.current_song: Optional[str] = None
        self.sfx_volume = config.sfx_volume
        self.music_volume = config.music_volume
        
        # Инициализация микшера
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=config.audio_buffer_size
        )
        
        # Загрузка звуковых эффектов
        self.sfx = {}
        self._load_sfx()
        
        # Задержка аудио (для синхронизации)
        self.latency_offset = config.audio_latency_ms / 1000.0
        
    def _load_sfx(self) -> None:
        """Загрузка звуковых эффектов"""
        sfx_path = Path("assets/sounds")
        
        sfx_files = {
            'hit': 'hit.wav',
            'miss': 'miss.wav',
            'perfect': 'hit.wav',  # Пока используем тот же звук
        }
        
        for name, filename in sfx_files.items():
            file_path = sfx_path / filename
            if file_path.exists():
                try:
                    self.sfx[name] = pygame.mixer.Sound(str(file_path))
                except Exception as e:
                    print(f"⚠️  Не удалось загрузить звук {name}: {e}")
    
    def load_song(self, audio_path: str) -> bool:
        """Загрузка песни"""
        try:
            pygame.mixer.music.load(audio_path)
            self.current_song = audio_path
            print(f"🎵 Загружена песня: {Path(audio_path).name}")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки песни: {e}")
            return False
    
    def play(self, loops: int = 0, start: float = 0.0) -> None:
        """Воспроизведение музыки"""
        pygame.mixer.music.play(loops, start)
        print("▶️  Воспроизведение начато")
    
    def pause(self) -> None:
        """Пауза"""
        pygame.mixer.music.pause()
    
    def unpause(self) -> None:
        """Снять с паузы"""
        pygame.mixer.music.unpause()
    
    def stop(self) -> None:
        """Остановка"""
        pygame.mixer.music.stop()
    
    def get_position(self) -> float:
        """Получение текущей позиции в секундах"""
        return pygame.mixer.music.get_pos() / 1000.0
    
    def get_adjusted_position(self) -> float:
        """Позиция с учетом задержки"""
        return self.get_position() + self.latency_offset
    
    def play_sfx(self, name: str) -> None:
        """Воспроизведение звукового эффекта"""
        if name in self.sfx:
            self.sfx[name].set_volume(self.sfx_volume)
            self.sfx[name].play()
    
    def set_music_volume(self, volume: float) -> None:
        """Установка громкости музыки"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def is_playing(self) -> bool:
        """Проверка воспроизведения"""
        return pygame.mixer.music.get_busy()

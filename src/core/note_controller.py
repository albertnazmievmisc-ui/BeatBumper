"""
Контроллер нот - управление движением и попаданиями
"""

import pygame
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto

from utils.config import Config


class HitResult(Enum):
    """Результат попадания по ноте"""
    PERFECT = auto()    # ±50ms
    GOOD = auto()       # ±100ms
    MISS = auto()       # >100ms


@dataclass
class Note:
    """Данные ноты"""
    time: float         # Время в секундах
    lane: int           # Линия (пока не используется)
    hit: bool = False
    missed: bool = False
    hit_result: Optional[HitResult] = None
    x: float = 0.0
    y: float = 0.0


class NoteController:
    """Управление нотами на экране"""
    
    # Окна попаданий в секундах
    PERFECT_WINDOW = 0.05
    GOOD_WINDOW = 0.10
    
    def __init__(self, config: Config):
        self.config = config
        self.notes: List[Note] = []
        self.current_index = 0
        
        # Скорость движения нот (пикселей в секунду)
        self.note_speed = config.note_speed
        
        # Позиция линии удара
        self.hit_line_x = config.hit_line_x
        
        # Спавн позиция (справа за экраном)
        self.spawn_x = config.screen_width + 100
        
        # Вертикальная позиция нот
        self.note_y = config.screen_height // 2
        
    def load_beatmap(self, notes_data: List[Dict]) -> None:
        """Загрузка нот из битмапы"""
        self.notes = [
            Note(time=note['time'], lane=0)
            for note in notes_data
        ]
        self.current_index = 0
        print(f"📝 Загружено нот: {len(self.notes)}")
    
    def update(self, dt: float, song_position: float) -> None:
        """Обновление позиций нот"""
        # Поиск нот, которые должны появиться
        while (self.current_index < len(self.notes) and 
               self.notes[self.current_index].time <= song_position + 2.0):
            
            note = self.notes[self.current_index]
            if not note.hit and not note.missed:
                # Вычисляем начальную позицию
                time_to_hit = note.time - song_position
                note.x = self.hit_line_x + time_to_hit * self.note_speed
                note.y = self.note_y
            
            self.current_index += 1
        
        # Движение всех активных нот
        for note in self.notes:
            if not note.hit and not note.missed:
                time_to_hit = note.time - song_position
                note.x = self.hit_line_x + time_to_hit * self.note_speed
    
    def check_hit(self, hit_time: float) -> Tuple[HitResult, Optional[Note]]:
        """Проверка попадания по ближайшей ноте"""
        closest_note = None
        min_diff = float('inf')
        
        # Ищем ближайшую неотмеченную ноту
        for note in self.notes:
            if note.hit or note.missed:
                continue
            
            diff = abs(hit_time - note.time)
            if diff < min_diff and diff <= self.GOOD_WINDOW:
                min_diff = diff
                closest_note = note
        
        if closest_note is None:
            return HitResult.MISS, None
        
        # Определяем точность
        if min_diff <= self.PERFECT_WINDOW:
            result = HitResult.PERFECT
        else:
            result = HitResult.GOOD
        
        closest_note.hit = True
        closest_note.hit_result = result
        
        return result, closest_note
    
    def check_missed_notes(self, song_position: float) -> List[Note]:
        """Проверка пропущенных нот"""
        missed = []
        for note in self.notes:
            if (not note.hit and not note.missed and 
                song_position - note.time > self.GOOD_WINDOW):
                note.missed = True
                note.hit_result = HitResult.MISS
                missed.append(note)
        
        return missed
    
    def get_visible_notes(self) -> List[Note]:
        """Получение видимых на экране нот"""
        return [
            note for note in self.notes
            if not note.hit and not note.missed
            and 0 <= note.x <= self.config.screen_width + 100
        ]
    
    def reset(self) -> None:
        """Сброс контроллера"""
        self.notes.clear()
        self.current_index = 0

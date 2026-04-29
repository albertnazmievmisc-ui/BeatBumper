"""
Парсер данных битмапы
"""

from typing import List, Dict
import json


class BeatmapParser:
    """Парсинг и обработка данных битмапы"""
    
    # Типы объектов в Beat Saber
    NOTE_RED = 0
    NOTE_BLUE = 1
    BOMB = 3
    
    # Направления разреза (пока не используются)
    CUT_UP = 0
    CUT_DOWN = 1
    CUT_LEFT = 2
    CUT_RIGHT = 3
    
    def __init__(self):
        self.bpm = 120.0
        self.shuffle = 0.0
        self.shuffle_period = 0.5
    
    def parse(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг данных битмапы в список нот"""
        # Извлечение BPM и других параметров
        self.bpm = beatmap_data.get('_beatsPerMinute', 120.0)
        self.shuffle = beatmap_data.get('_shuffle', 0.0)
        self.shuffle_period = beatmap_data.get('_shufflePeriod', 0.5)
        
        notes = beatmap_data.get('_notes', [])
        parsed_notes = []
        
        for note in notes:
            # Фильтруем только красные ноты
            if note.get('_type') != self.NOTE_RED:
                continue
            
            # Конвертируем время из битов в секунды
            beat_time = note.get('_time', 0.0)
            time_in_seconds = self._beats_to_seconds(beat_time)
            
            parsed_notes.append({
                'time': time_in_seconds,
                'line_layer': note.get('_lineLayer', 0),
                'line_index': note.get('_lineIndex', 0),
                'cut_direction': note.get('_cutDirection', 0),
            })
        
        # Сортировка по времени
        parsed_notes.sort(key=lambda x: x['time'])
        
        print(f"🎵 Парсинг завершен: {len(parsed_notes)} красных нот")
        print(f"   BPM: {self.bpm}")
        print(f"   Длительность: {parsed_notes[-1]['time']:.1f} сек" if parsed_notes else "")
        
        return parsed_notes
    
    def _beats_to_seconds(self, beats: float) -> float:
        """Конвертация битов в секунды"""
        return (beats / self.bpm) * 60.0
    
    def _seconds_to_beats(self, seconds: float) -> float:
        """Конвертация секунд в биты"""
        return (seconds * self.bpm) / 60.0

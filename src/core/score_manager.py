"""
Менеджер очков и комбо
"""

from dataclasses import dataclass
from typing import List
from enum import Enum

from core.note_controller import HitResult


class Rank(Enum):
    """Ранги по итогам игры"""
    SS = "SS"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class GameStats:
    """Статистика игры"""
    score: int = 0
    max_combo: int = 0
    current_combo: int = 0
    perfect_count: int = 0
    good_count: int = 0
    miss_count: int = 0
    total_notes: int = 0
    accuracy: float = 0.0
    rank: Rank = Rank.F


class ScoreManager:
    """Управление счетом и комбо"""
    
    # Базовые очки за попадание
    SCORE_PERFECT = 100
    SCORE_GOOD = 50
    SCORE_MISS = -20
    
    # Множитель комбо
    COMBO_MULTIPLIER = 0.1  # +10% за каждые 10 комбо
    
    def __init__(self):
        self.stats = GameStats()
    
    def add_hit(self, result: HitResult) -> int:
        """Обработка попадания"""
        if result == HitResult.PERFECT:
            self.stats.current_combo += 1
            self.stats.perfect_count += 1
            base_score = self.SCORE_PERFECT
            
        elif result == HitResult.GOOD:
            self.stats.current_combo += 1
            self.stats.good_count += 1
            base_score = self.SCORE_GOOD
            
        else:  # MISS
            self.stats.current_combo = 0
            self.stats.miss_count += 1
            base_score = self.SCORE_MISS
        
        # Множитель комбо
        combo_bonus = 1.0 + (self.stats.current_combo // 10) * self.COMBO_MULTIPLIER
        final_score = int(base_score * combo_bonus)
        
        # Обновление статистики
        self.stats.score += final_score
        if self.stats.current_combo > self.stats.max_combo:
            self.stats.max_combo = self.stats.current_combo
        
        return final_score
    
    def calculate_final_stats(self, total_notes: int) -> None:
        """Подсчет итоговой статистики"""
        self.stats.total_notes = total_notes
        
        if total_notes > 0:
            hits = self.stats.perfect_count + self.stats.good_count
            self.stats.accuracy = (hits / total_notes) * 100
            
            # Определение ранга
            if self.stats.accuracy >= 100:
                self.stats.rank = Rank.SS
            elif self.stats.accuracy >= 95:
                self.stats.rank = Rank.S
            elif self.stats.accuracy >= 85:
                self.stats.rank = Rank.A
            elif self.stats.accuracy >= 70:
                self.stats.rank = Rank.B
            elif self.stats.accuracy >= 55:
                self.stats.rank = Rank.C
            elif self.stats.accuracy >= 40:
                self.stats.rank = Rank.D
            else:
                self.stats.rank = Rank.F
    
    def reset(self) -> None:
        """Сброс статистики"""
        self.stats = GameStats()

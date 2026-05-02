"""
Менеджер очков и комбо
"""

import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
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
            
        else:  # MISS or WRONG_COLOR
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
    
    def save_high_score(self, song_name: str, difficulty: str) -> bool:
        """Сохранение рекорда"""
        scores_file = Path("scores.json")
        
        # Загружаем существующие рекорды
        high_scores = {}
        if scores_file.exists():
            try:
                with open(scores_file, 'r') as f:
                    high_scores = json.load(f)
            except:
                pass
        
        # Ключ для песни и сложности
        key = f"{song_name}|{difficulty}"
        
        # Сохраняем только если это новый рекорд
        current_best = high_scores.get(key, {}).get("score", 0)
        if self.stats.score > current_best:
            high_scores[key] = {
                "score": self.stats.score,
                "accuracy": self.stats.accuracy,
                "rank": self.stats.rank.value,
                "max_combo": self.stats.max_combo,
                "perfect": self.stats.perfect_count,
                "good": self.stats.good_count,
                "miss": self.stats.miss_count,
                "date": datetime.now().isoformat()
            }
            
            with open(scores_file, 'w') as f:
                json.dump(high_scores, f, indent=2)
            
            print(f"🏆 Новый рекорд! {self.stats.score:,} очков")
            return True
        return False
    
    def get_high_score(self, song_name: str, difficulty: str) -> Optional[Dict]:
        """Получение текущего рекорда"""
        scores_file = Path("scores.json")
        if not scores_file.exists():
            return None
        
        try:
            with open(scores_file, 'r') as f:
                high_scores = json.load(f)
            key = f"{song_name}|{difficulty}"
            return high_scores.get(key)
        except:
            return None
    
    def reset(self) -> None:
        """Сброс статистики"""
        self.stats = GameStats()

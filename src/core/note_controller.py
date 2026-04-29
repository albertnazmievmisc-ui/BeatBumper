"""
Контроллер нот - управление движением и попаданиями
"""

import pygame
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto

from utils.config import Config


class NoteColor(Enum):
    """Цвет ноты"""

    RED = 0
    BLUE = 1


class HitResult(Enum):
    """Результат попадания по ноте"""

    PERFECT = auto()  # ±50ms
    GOOD = auto()  # ±100ms
    MISS = auto()  # >100ms
    WRONG_COLOR = auto()  # Удар не того цвета


@dataclass
class Note:
    """Данные ноты"""

    time: float  # Время в секундах
    color: NoteColor  # Цвет ноты (RED/BLUE)
    lane: int = 0  # Линия
    line_index: int = 0  # Горизонтальная позиция (0-3)
    line_layer: int = 0  # Вертикальный слой (0-2)
    cut_direction: int = 0  # Направление разреза
    hit: bool = False
    missed: bool = False
    wrong_color: bool = False  # Попадание не тем цветом
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

        # Вертикальные позиции для разных линий (lane)
        self.lane_positions = self._calculate_lane_positions()

    def _calculate_lane_positions(self) -> Dict[int, float]:
        """Расчёт вертикальных позиций для 4-х линий"""
        base_y = self.config.screen_height // 2
        spacing = 80  # Расстояние между линиями

        return {
            0: base_y - spacing * 1.5,  # Верхняя
            1: base_y - spacing * 0.5,  # Средне-верхняя
            2: base_y + spacing * 0.5,  # Средне-нижняя
            3: base_y + spacing * 1.5,  # Нижняя
        }

    def load_beatmap(self, notes_data: List[Dict]) -> None:
        """Загрузка нот из битмапы с цветами"""
        self.notes = []

        for note in notes_data:
            # Определяем цвет из данных парсера
            note_color_str = note.get("color", "red")
            color = NoteColor.RED if note_color_str == "red" else NoteColor.BLUE

            self.notes.append(
                Note(
                    time=note["time"],
                    color=color,
                    line_index=note.get("line_index", 0),
                    line_layer=note.get("line_layer", 0),
                    cut_direction=note.get("cut_direction", 0),
                )
            )

        # Сортируем по времени (на всякий случай)
        self.notes.sort(key=lambda n: n.time)
        self.current_index = 0

        red_count = sum(1 for n in self.notes if n.color == NoteColor.RED)
        blue_count = sum(1 for n in self.notes if n.color == NoteColor.BLUE)
        print(
            f"📝 Загружено нот: {len(self.notes)} (🔴 {red_count} красных, 🔵 {blue_count} синих)"
        )

    def update(self, dt: float, song_position: float) -> None:
        """Обновление позиций нот"""
        # Поиск нот, которые должны появиться на экране
        while (
            self.current_index < len(self.notes)
            and self.notes[self.current_index].time <= song_position + 2.0
        ):

            note = self.notes[self.current_index]
            if not note.hit and not note.missed:
                # Вычисляем начальную позицию
                time_to_hit = note.time - song_position
                note.x = self.hit_line_x + time_to_hit * self.note_speed
                # Позиция Y зависит от line_index
                note.y = self.lane_positions.get(
                    note.line_index, self.config.screen_height // 2
                )

            self.current_index += 1

        # Движение всех активных нот
        for note in self.notes:
            if not note.hit and not note.missed:
                time_to_hit = note.time - song_position
                note.x = self.hit_line_x + time_to_hit * self.note_speed

    def check_hit_red(self, hit_time: float) -> Tuple[HitResult, Optional[Note]]:
        """Проверка попадания по красной ноте"""
        return self._check_hit_by_color(hit_time, NoteColor.RED)

    def check_hit_blue(self, hit_time: float) -> Tuple[HitResult, Optional[Note]]:
        """Проверка попадания по синей ноте"""
        return self._check_hit_by_color(hit_time, NoteColor.BLUE)

    def _check_hit_by_color(
        self, hit_time: float, expected_color: NoteColor
    ) -> Tuple[HitResult, Optional[Note]]:
        """Проверка попадания с учётом цвета"""
        closest_note = None
        min_diff = float("inf")

        # Ищем ближайшую неотмеченную ноту ЛЮБОГО цвета
        for note in self.notes:
            if note.hit or note.missed:
                continue

            diff = abs(hit_time - note.time)
            if diff < min_diff and diff <= self.GOOD_WINDOW:
                min_diff = diff
                closest_note = note

        if closest_note is None:
            return HitResult.MISS, None

        # Проверяем соответствие цвета
        if closest_note.color != expected_color:
            # Попадание не тем цветом — считаем промахом
            closest_note.wrong_color = True
            closest_note.hit = True  # Нота считается обработанной
            closest_note.hit_result = HitResult.WRONG_COLOR
            return HitResult.WRONG_COLOR, closest_note

        # Определяем точность
        if min_diff <= self.PERFECT_WINDOW:
            result = HitResult.PERFECT
        else:
            result = HitResult.GOOD

        closest_note.hit = True
        closest_note.hit_result = result

        return result, closest_note

    def check_missed_notes(self, song_position: float) -> List[Note]:
        """Проверка пропущенных нот (ушли за линию удара)"""
        missed = []
        for note in self.notes:
            if (
                not note.hit
                and not note.missed
                and song_position - note.time > self.GOOD_WINDOW
            ):
                note.missed = True
                note.hit_result = HitResult.MISS
                missed.append(note)

        return missed

    def get_visible_notes(self) -> List[Note]:
        """Получение видимых на экране нот"""
        return [
            note
            for note in self.notes
            if not note.hit
            and not note.missed
            and 0 <= note.x <= self.config.screen_width + 100
        ]

    def reset(self) -> None:
        """Сброс контроллера"""
        self.notes.clear()
        self.current_index = 0

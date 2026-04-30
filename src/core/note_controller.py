"""
Контроллер нот - управление движением и попаданиями (сверху вниз)
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

    PERFECT = auto()
    GOOD = auto()
    MISS = auto()
    WRONG_COLOR = auto()


@dataclass
class Note:
    """Данные ноты"""

    time: float
    color: NoteColor
    lane: int = 0
    line_index: int = 0
    line_layer: int = 0
    cut_direction: int = 0
    hit: bool = False
    missed: bool = False
    wrong_color: bool = False
    hit_result: Optional[HitResult] = None
    x: float = 0.0
    y: float = 0.0


class NoteController:
    """Управление нотами на экране (сверху вниз)"""

    PERFECT_WINDOW = 0.05
    GOOD_WINDOW = 0.10

    def __init__(self, config: Config):
        self.config = config
        self.notes: List[Note] = []
        self.current_index = 0

        # Скорость движения нот (пикселей в секунду)
        self.note_speed = config.note_speed

        # Позиция линии удара (внизу экрана)
        self.hit_line_y = config.screen_height - 150

        # Спавн позиция (сверху за экраном)
        self.spawn_y = -100

        # Позиции для красных (справа) и синих (слева) нот
        self.red_x = config.screen_width * 0.75  # Правая сторона
        self.blue_x = config.screen_width * 0.25  # Левая сторона

    def load_beatmap(self, notes_data: List[Dict]) -> None:
        """Загрузка нот из битмапы с цветами"""
        self.notes = []

        for note in notes_data:
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

        self.notes.sort(key=lambda n: n.time)
        self.current_index = 0

        red_count = sum(1 for n in self.notes if n.color == NoteColor.RED)
        blue_count = sum(1 for n in self.notes if n.color == NoteColor.BLUE)
        print(
            f"📝 Загружено нот: {len(self.notes)} (🔴 {red_count} красных, 🔵 {blue_count} синих)"
        )

    def update(self, dt: float, song_position: float) -> None:
        """Обновление позиций нот (движение сверху вниз)"""
        # Поиск нот, которые должны появиться на экране
        while (
            self.current_index < len(self.notes)
            and self.notes[self.current_index].time <= song_position + 2.0
        ):

            note = self.notes[self.current_index]
            if not note.hit and not note.missed:
                # Вычисляем позицию: Y увеличивается (движение вниз)
                time_to_hit = note.time - song_position
                # Нота спавнится сверху и летит вниз к hit_line_y
                note.y = self.hit_line_y - time_to_hit * self.note_speed

                # X позиция зависит от цвета
                if note.color == NoteColor.RED:
                    note.x = self.red_x
                else:
                    note.x = self.blue_x

            self.current_index += 1

        # Движение всех активных нот
        for note in self.notes:
            if not note.hit and not note.missed:
                time_to_hit = note.time - song_position
                note.y = self.hit_line_y - time_to_hit * self.note_speed

    def check_hit_red(self, hit_time: float) -> Tuple[HitResult, Optional[Note]]:
        """Проверка попадания по красной ноте (RT)"""
        return self._check_hit_by_color(hit_time, NoteColor.RED)

    def check_hit_blue(self, hit_time: float) -> Tuple[HitResult, Optional[Note]]:
        """Проверка попадания по синей ноте (LT)"""
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
            closest_note.wrong_color = True
            closest_note.hit = True
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
        """Проверка пропущенных нот (ушли за линию удара вниз)"""
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
            and -100 <= note.y <= self.config.screen_height + 100
        ]

    def reset(self) -> None:
        """Сброс контроллера"""
        self.notes.clear()
        self.current_index = 0

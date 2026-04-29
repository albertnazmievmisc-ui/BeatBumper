"""
Парсер данных битмапы с поддержкой форматов v2 и v3+
"""

from typing import List, Dict, Optional
import json


class BeatmapParser:
    """Парсинг и обработка данных битмапы"""

    # Типы объектов в Beat Saber (v2)
    NOTE_RED_V2 = 0
    NOTE_BLUE_V2 = 1
    BOMB_V2 = 3

    # Цвета нот в v3+
    COLOR_RED = 0
    COLOR_BLUE = 1

    def __init__(self):
        self.bpm = 120.0
        self.shuffle = 0.0
        self.shuffle_period = 0.5
        self.version = None

    def _detect_format(self, beatmap_data: Dict) -> str:
        """Определение формата битмапы"""
        version = beatmap_data.get("version", beatmap_data.get("_version", "2.0.0"))
        self.version = version

        # v3+ использует colorNotes и burstSliders
        if "colorNotes" in beatmap_data:
            return "v3"
        # v2 использует _notes
        elif "_notes" in beatmap_data:
            return "v2"
        else:
            raise ValueError(f"❌ Неизвестный формат битмапы: {version}")

    def _parse_bpm_events(self, beatmap_data: Dict) -> Optional[List[Dict]]:
        """Парсинг BPM изменений для v3+"""
        if "bpmEvents" in beatmap_data:
            return beatmap_data["bpmEvents"]
        return None

    def parse(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг данных битмапы в список нот"""
        format_type = self._detect_format(beatmap_data)
        print(f"📄 Формат битмапы: {format_type} (v{self.version})")

        if format_type == "v3":
            return self._parse_v3(beatmap_data)
        else:
            return self._parse_v2(beatmap_data)

    def _parse_v3(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг формата v3+ (colorNotes)"""
        # Извлечение BPM
        bpm_events = self._parse_bpm_events(beatmap_data)
        if bpm_events:
            # Берём первый BPM как основной
            self.bpm = bpm_events[0].get("m", 120.0) if bpm_events else 120.0
        else:
            self.bpm = beatmap_data.get("_beatsPerMinute", 120.0)

        # Получаем ноты
        color_notes = beatmap_data.get("colorNotes", [])
        parsed_notes = []

        for note in color_notes:
            # Фильтруем только красные ноты (c: 0)
            if note.get("c") != self.COLOR_RED:
                continue

            # Время в битах
            beat_time = note.get("b", 0.0)
            time_in_seconds = self._beats_to_seconds_v3(beat_time, bpm_events)

            parsed_notes.append(
                {
                    "time": time_in_seconds,
                    "line_layer": note.get("y", 0),  # y — это слой в v3
                    "line_index": note.get("x", 0),  # x — позиция в v3
                    "cut_direction": note.get("d", 0),  # d — направление в v3
                    "angle_offset": note.get("a", 0),  # a — угол (новое в v3)
                }
            )

        # Сортировка по времени
        parsed_notes.sort(key=lambda x: x["time"])

        print(f"🎵 Парсинг завершен: {len(parsed_notes)} красных нот (v3)")
        print(f"   BPM: {self.bpm}")
        if parsed_notes:
            print(f"   Длительность: {parsed_notes[-1]['time']:.1f} сек")
            print(f"   Первая нота: {parsed_notes[0]['time']:.2f}с")
            print(f"   Последняя нота: {parsed_notes[-1]['time']:.2f}с")

        return parsed_notes

    def _parse_v2(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг формата v2 (_notes)"""
        # Извлечение BPM и других параметров
        self.bpm = beatmap_data.get("_beatsPerMinute", 120.0)
        self.shuffle = beatmap_data.get("_shuffle", 0.0)
        self.shuffle_period = beatmap_data.get("_shufflePeriod", 0.5)

        notes = beatmap_data.get("_notes", [])
        parsed_notes = []

        for note in notes:
            # Фильтруем только красные ноты
            if note.get("_type") != self.NOTE_RED_V2:
                continue

            # Конвертируем время из битов в секунды
            beat_time = note.get("_time", 0.0)
            time_in_seconds = self._beats_to_seconds(beat_time)

            parsed_notes.append(
                {
                    "time": time_in_seconds,
                    "line_layer": note.get("_lineLayer", 0),
                    "line_index": note.get("_lineIndex", 0),
                    "cut_direction": note.get("_cutDirection", 0),
                }
            )

        # Сортировка по времени
        parsed_notes.sort(key=lambda x: x["time"])

        print(f"🎵 Парсинг завершен: {len(parsed_notes)} красных нот (v2)")
        print(f"   BPM: {self.bpm}")
        if parsed_notes:
            print(f"   Длительность: {parsed_notes[-1]['time']:.1f} сек")

        return parsed_notes

    def _beats_to_seconds_v3(
        self, beats: float, bpm_events: Optional[List[Dict]] = None
    ) -> float:
        """Конвертация битов в секунды с учётом изменений BPM (v3+)"""
        if not bpm_events:
            # Если нет BPM событий, используем постоянный BPM
            return (beats / self.bpm) * 60.0

        # Сортировка BPM событий
        bpm_events = sorted(bpm_events, key=lambda e: e.get("b", 0))

        total_seconds = 0.0
        current_beat = 0.0

        for i, event in enumerate(bpm_events):
            event_beat = event.get("b", 0)
            bpm = event.get("m", self.bpm)

            if event_beat >= beats:
                # Дошли до нужного бита
                segment_beats = beats - current_beat
                total_seconds += (segment_beats / bpm) * 60.0
                return total_seconds

            # Считаем длительность до следующего BPM изменения
            if i < len(bpm_events) - 1:
                next_beat = bpm_events[i + 1].get("b", beats)
            else:
                next_beat = beats

            segment_beats = next_beat - current_beat
            total_seconds += (segment_beats / bpm) * 60.0
            current_beat = next_beat

        return total_seconds

    def _beats_to_seconds(self, beats: float) -> float:
        """Конвертация битов в секунды (v2, простой BPM)"""
        return (beats / self.bpm) * 60.0

    def _seconds_to_beats(self, seconds: float) -> float:
        """Конвертация секунд в биты"""
        return (seconds * self.bpm) / 60.0

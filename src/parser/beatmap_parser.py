"""
Парсер данных битмапы с поддержкой v2, v3, v4.1.0
"""

from typing import List, Dict, Optional


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

    def _detect_format(self, beatmap_data: Dict) -> str:
        """Определение формата битмапы"""
        version = beatmap_data.get("version", beatmap_data.get("_version", "2.0.0"))
        self.version = version

        # v4: есть colorNotes + colorNotesData (индексная адресация)
        if "colorNotes" in beatmap_data and "colorNotesData" in beatmap_data:
            return "v4"
        # v3: есть colorNotes с полными данными (без отдельного Data-массива)
        elif "colorNotes" in beatmap_data:
            return "v3"
        # v2: старый формат _notes
        elif "_notes" in beatmap_data:
            return "v2"
        else:
            print(f"⚠️ Неизвестный формат битмапы: {version}, пробуем v2")
            return "v2"

    def parse(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг данных битмапы в список нот (только красные)"""
        format_type = self._detect_format(beatmap_data)
        print(f"📄 Формат битмапы: {format_type} (v{self.version})")

        if format_type == "v4":
            return self._parse_object_with_data(
                beatmap_data,
                object_key="colorNotes",
                data_key="colorNotesData",
                is_red_fn=lambda data: data.get("c") == self.COLOR_RED,
            )
        elif format_type == "v3":
            return self._parse_v3(beatmap_data)
        else:
            return self._parse_v2(beatmap_data)

    def _parse_object_with_data(
        self, beatmap_data: Dict, object_key: str, data_key: str, is_red_fn
    ) -> List[Dict]:
        """Универсальный парсер для v4 (объекты + отдельные метаданные)"""
        # BPM может быть в bpmEvents или отдельно
        self.bpm = self._get_bpm(beatmap_data)

        objects = beatmap_data.get(object_key, [])
        data_list = beatmap_data.get(data_key, [])

        parsed_notes = []

        for obj in objects:
            # Индекс в data-массиве
            data_index = obj.get("i", 0)

            if data_index >= len(data_list):
                print(
                    f"⚠️ Индекс {data_index} вне границ {data_key} (размер: {len(data_list)})"
                )
                continue

            note_data = data_list[data_index]

            # Фильтруем только красные ноты (c == 0)
            if not is_red_fn(note_data):
                continue

            # Время в битах
            beat_time = obj.get("b", 0.0)
            time_in_seconds = self._beats_to_seconds(beat_time)

            parsed_notes.append(
                {
                    "time": time_in_seconds,
                    "line_layer": note_data.get("y", 0),
                    "line_index": note_data.get("x", 0),
                    "cut_direction": note_data.get("d", 0),
                    "angle_offset": note_data.get("a", 0),
                }
            )

        # Сортировка по времени
        parsed_notes.sort(key=lambda x: x["time"])

        print(
            f"🎵 Парсинг завершен: {len(parsed_notes)} красных нот из {len(objects)} объектов"
        )
        print(f"   BPM: {self.bpm}")
        if parsed_notes:
            print(f"   Первая нота: {parsed_notes[0]['time']:.2f}с")
            print(f"   Последняя нота: {parsed_notes[-1]['time']:.2f}с")

        return parsed_notes

    def _parse_v3(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг v3: colorNotes с полными данными внутри"""
        self.bpm = self._get_bpm(beatmap_data)
        color_notes = beatmap_data.get("colorNotes", [])
        parsed_notes = []

        for note in color_notes:
            if note.get("c") != self.COLOR_RED:
                continue

            beat_time = note.get("b", 0.0)
            time_in_seconds = self._beats_to_seconds(beat_time)

            parsed_notes.append(
                {
                    "time": time_in_seconds,
                    "line_layer": note.get("y", 0),
                    "line_index": note.get("x", 0),
                    "cut_direction": note.get("d", 0),
                    "angle_offset": note.get("a", 0),
                }
            )

        parsed_notes.sort(key=lambda x: x["time"])

        print(f"🎵 Парсинг завершен: {len(parsed_notes)} красных нот (v3)")
        print(f"   BPM: {self.bpm}")
        if parsed_notes:
            print(f"   Длительность: {parsed_notes[-1]['time']:.1f} сек")

        return parsed_notes

    def _parse_v2(self, beatmap_data: Dict) -> List[Dict]:
        """Парсинг v2: _notes с _type, _lineLayer, _lineIndex"""
        self.bpm = beatmap_data.get("_beatsPerMinute", 120.0)
        notes = beatmap_data.get("_notes", [])
        parsed_notes = []

        for note in notes:
            if note.get("_type") != self.NOTE_RED_V2:
                continue

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

        parsed_notes.sort(key=lambda x: x["time"])

        print(f"🎵 Парсинг завершен: {len(parsed_notes)} красных нот (v2)")
        print(f"   BPM: {self.bpm}")

        return parsed_notes

    def _get_bpm(self, beatmap_data: Dict) -> float:
        """Извлечение BPM (поддержка bpmEvents)"""
        bpm_events = beatmap_data.get("bpmEvents")
        if bpm_events and len(bpm_events) > 0:
            return bpm_events[0].get("m", 120.0)
        return beatmap_data.get("_beatsPerMinute", 120.0)

    def _beats_to_seconds(self, beats: float) -> float:
        """Конвертация битов в секунды (упрощённая, без учёта variable BPM)"""
        return (beats / self.bpm) * 60.0

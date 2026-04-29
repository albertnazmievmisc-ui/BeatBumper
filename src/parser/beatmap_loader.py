"""
Загрузчик Beat Saber мап
"""

import zipfile
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BeatmapLoader:
    """Загрузка и валидация Beat Saber карт"""

    REQUIRED_FILES = ["Info.dat"]
    SUPPORTED_MODES = ["Standard"]
    DIFFICULTY_ORDER = ["Easy", "Normal", "Hard", "Expert", "ExpertPlus"]

    def __init__(self):
        self.temp_dir = None

    def get_difficulties(self, zip_path: Path) -> List[Dict]:
        """
        Получить список доступных сложностей из zip-архива.
        Не извлекает аудио, только читает Info.dat.
        Возвращает список словарей с информацией о сложностях.
        """
        if not zip_path.exists():
            return []

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                file_list = zf.namelist()

                if "Info.dat" not in file_list:
                    return []

                info_data = json.loads(zf.read("Info.dat").decode("utf-8"))
                difficulty_sets = info_data.get("_difficultyBeatmapSets", [])

                difficulties = []
                for diff_set in difficulty_sets:
                    characteristic = diff_set.get("_beatmapCharacteristicName", "")

                    # Проверяем, что характеристика поддерживается
                    if characteristic not in self.SUPPORTED_MODES:
                        continue

                    for diff_map in diff_set.get("_difficultyBeatmaps", []):
                        filename = diff_map.get("_beatmapFilename", "")

                        # Проверяем, что файл сложности существует в архиве
                        if filename not in file_list:
                            continue

                        difficulty_name = diff_map.get("_difficulty", "Unknown")

                        # Сортируем: вначале стандартные названия, потом кастомные
                        sort_key = (
                            (0, self.DIFFICULTY_ORDER.index(difficulty_name))
                            if difficulty_name in self.DIFFICULTY_ORDER
                            else (1, difficulty_name)
                        )

                        difficulties.append(
                            {
                                "characteristic": characteristic,
                                "difficulty": difficulty_name,
                                "filename": filename,
                                "njs": diff_map.get("_noteJumpMovementSpeed", 16),
                                "note_offset": diff_map.get(
                                    "_noteJumpStartBeatOffset", 0
                                ),
                                "label": diff_map.get("_customData", {}).get(
                                    "_difficultyLabel", ""
                                ),
                                "mappers": ", ".join(
                                    [
                                        m.get("_mapperName", m.get("_name", "Unknown"))
                                        for m in diff_map.get(
                                            "_beatmapAuthors", {}
                                        ).get("_mappers", [])
                                    ]
                                ),
                            }
                        )

                # Сортируем по сложности
                difficulties.sort(key=lambda d: d.get("sort_key", (0, 0)))

                return difficulties

        except Exception as e:
            print(f"❌ Ошибка чтения сложностей из {zip_path.name}: {e}")
            return []

    def load_zip(
        self, zip_path: Path, difficulty_filename: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Загрузка мапы из zip-архива.

        Args:
            zip_path: путь к zip-файлу
            difficulty_filename: имя файла сложности для загрузки.
                                Если None, загружается первая поддерживаемая.
        """
        if not zip_path.exists():
            print(f"❌ Файл не найден: {zip_path}")
            return None

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                # Проверка наличия обязательных файлов
                file_list = zf.namelist()

                if "Info.dat" not in file_list:
                    print("❌ Info.dat не найден в архиве")
                    return None

                # Чтение Info.dat
                info_data = json.loads(zf.read("Info.dat").decode("utf-8"))

                # Поиск аудиофайла
                audio_filename = info_data.get("_songFilename")
                if not audio_filename:
                    print("❌ Аудиофайл не указан в Info.dat")
                    return None

                # Извлечение аудио во временную директорию
                self.temp_dir = tempfile.mkdtemp()
                audio_path = Path(self.temp_dir) / audio_filename

                with zf.open(audio_filename) as audio_file:
                    with open(audio_path, "wb") as f:
                        f.write(audio_file.read())

                # Поиск файлов сложности
                difficulty_sets = info_data.get("_difficultyBeatmapSets", [])
                beatmap_data = None
                selected_difficulty = None

                # Если указан конкретный файл сложности — ищем только его
                if difficulty_filename:
                    for diff_set in difficulty_sets:
                        for diff_map in diff_set.get("_difficultyBeatmaps", []):
                            if diff_map.get("_beatmapFilename") == difficulty_filename:
                                if difficulty_filename in file_list:
                                    beatmap_data = json.loads(
                                        zf.read(difficulty_filename).decode("utf-8")
                                    )
                                    selected_difficulty = diff_map.get(
                                        "_difficulty", "Unknown"
                                    )
                                    break
                        if beatmap_data:
                            break
                else:
                    # Ищем ПЕРВУЮ ПОДДЕРЖИВАЕМУЮ сложность (Standard)
                    for diff_set in difficulty_sets:
                        if (
                            diff_set.get("_beatmapCharacteristicName")
                            in self.SUPPORTED_MODES
                        ):
                            for diff_map in diff_set.get("_difficultyBeatmaps", []):
                                filename = diff_map.get("_beatmapFilename")
                                if filename and filename in file_list:
                                    beatmap_data = json.loads(
                                        zf.read(filename).decode("utf-8")
                                    )
                                    selected_difficulty = diff_map.get(
                                        "_difficulty", "Unknown"
                                    )
                                    break
                        if beatmap_data:
                            break

                if not beatmap_data:
                    print("❌ Поддерживаемая сложность (Standard) не найдена")
                    return None

                print(f"📊 Загружена сложность: {selected_difficulty}")

                return {
                    "info": info_data,
                    "beatmap": beatmap_data,
                    "audio_path": str(audio_path),
                    "song_name": info_data.get("_songName", "Unknown"),
                    "song_author": info_data.get("_songAuthorName", "Unknown"),
                    "bpm": info_data.get("_beatsPerMinute", 120),
                    "difficulty": selected_difficulty,
                }

        except zipfile.BadZipFile:
            print(f"❌ Поврежденный архив: {zip_path}")
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None

    def cleanup(self) -> None:
        """Очистка временных файлов"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

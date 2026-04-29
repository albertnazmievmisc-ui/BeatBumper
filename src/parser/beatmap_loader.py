"""
Загрузчик Beat Saber мап с поддержкой Info.dat v2 и v4
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

    def _get_info_format(self, info_data: Dict) -> str:
        """Определение формата Info.dat"""
        version = info_data.get("version", "2.0.0")
        if version.startswith("4."):
            return "v4"
        elif version.startswith("3."):
            return "v3"
        else:
            return "v2"

    def _get_audio_filename(self, info_data: Dict, format_type: str) -> Optional[str]:
        """Получение имени аудиофайла в зависимости от формата"""
        if format_type in ("v3", "v4"):
            return info_data.get("audio", {}).get("songFilename")
        else:
            return info_data.get("_songFilename")

    def _get_difficulty_list(self, info_data: Dict, format_type: str) -> List[Dict]:
        """Получение списка сложностей в унифицированном виде"""
        difficulties = []

        if format_type in ("v3", "v4"):
            # Плоский список difficultyBeatmaps
            raw_list = info_data.get("difficultyBeatmaps", [])
            for dm in raw_list:
                characteristic = dm.get("characteristic", "Standard")
                if characteristic not in self.SUPPORTED_MODES:
                    continue
                difficulties.append(
                    {
                        "characteristic": characteristic,
                        "difficulty": dm.get("difficulty", "Unknown"),
                        "filename": dm.get("beatmapDataFilename", ""),
                        "njs": dm.get("noteJumpMovementSpeed", 16),
                        "note_offset": dm.get("noteJumpStartBeatOffset", 0),
                        "label": dm.get("customData", {}).get("difficultyLabel", ""),
                        "mappers": ", ".join(
                            [
                                m.get("name", m) if isinstance(m, dict) else m
                                for m in dm.get("beatmapAuthors", {}).get("mappers", [])
                            ]
                        ),
                    }
                )
        else:
            # Старая структура _difficultyBeatmapSets
            sets = info_data.get("_difficultyBeatmapSets", [])
            for diff_set in sets:
                characteristic = diff_set.get("_beatmapCharacteristicName", "")
                if characteristic not in self.SUPPORTED_MODES:
                    continue
                for dm in diff_set.get("_difficultyBeatmaps", []):
                    difficulties.append(
                        {
                            "characteristic": characteristic,
                            "difficulty": dm.get("_difficulty", "Unknown"),
                            "filename": dm.get("_beatmapFilename", ""),
                            "njs": dm.get("_noteJumpMovementSpeed", 16),
                            "note_offset": dm.get("_noteJumpStartBeatOffset", 0),
                            "label": dm.get("_customData", {}).get(
                                "_difficultyLabel", ""
                            ),
                            "mappers": ", ".join(
                                [
                                    m.get("_name", m) if isinstance(m, dict) else m
                                    for m in dm.get("_beatmapAuthors", {}).get(
                                        "_mappers", []
                                    )
                                ]
                            ),
                        }
                    )
        return difficulties

    def get_difficulties(self, zip_path: Path) -> List[Dict]:
        """Получить список доступных сложностей из zip"""
        if not zip_path.exists():
            return []

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                file_list = zf.namelist()
                if "Info.dat" not in file_list:
                    return []

                info_data = json.loads(zf.read("Info.dat").decode("utf-8"))
                format_type = self._get_info_format(info_data)

                difficulties = self._get_difficulty_list(info_data, format_type)

                # Фильтруем только существующие файлы
                valid_difficulties = []
                for d in difficulties:
                    if d["filename"] in file_list:
                        # Добавляем ключ сортировки
                        if d["difficulty"] in self.DIFFICULTY_ORDER:
                            d["sort_key"] = (
                                0,
                                self.DIFFICULTY_ORDER.index(d["difficulty"]),
                            )
                        else:
                            d["sort_key"] = (1, d["difficulty"])
                        valid_difficulties.append(d)

                valid_difficulties.sort(key=lambda x: x["sort_key"])
                return valid_difficulties

        except Exception as e:
            print(f"❌ Ошибка чтения сложностей из {zip_path.name}: {e}")
            return []

    def load_zip(
        self, zip_path: Path, difficulty_filename: Optional[str] = None
    ) -> Optional[Dict]:
        """Загрузка мапы из zip-архива"""
        if not zip_path.exists():
            print(f"❌ Файл не найден: {zip_path}")
            return None

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                file_list = zf.namelist()

                if "Info.dat" not in file_list:
                    print("❌ Info.dat не найден в архиве")
                    return None

                info_data = json.loads(zf.read("Info.dat").decode("utf-8"))
                format_type = self._get_info_format(info_data)

                # Ищем аудиофайл
                audio_filename = self._get_audio_filename(info_data, format_type)
                if not audio_filename:
                    print("❌ Аудиофайл не указан в Info.dat")
                    return None

                if audio_filename not in file_list:
                    print(f"❌ Аудиофайл {audio_filename} не найден в архиве")
                    return None

                # Извлечение аудио
                self.temp_dir = tempfile.mkdtemp()
                audio_path = Path(self.temp_dir) / audio_filename

                with zf.open(audio_filename) as audio_file:
                    with open(audio_path, "wb") as f:
                        f.write(audio_file.read())

                # Получаем унифицированный список сложностей
                difficulties = self._get_difficulty_list(info_data, format_type)
                beatmap_data = None
                selected_difficulty = None

                if difficulty_filename:
                    # Ищем указанную сложность
                    for d in difficulties:
                        if d["filename"] == difficulty_filename:
                            if difficulty_filename in file_list:
                                beatmap_data = json.loads(
                                    zf.read(difficulty_filename).decode("utf-8")
                                )
                                selected_difficulty = d["difficulty"]
                            break
                else:
                    # Берём первую поддерживаемую (Standard)
                    for d in difficulties:
                        if d["filename"] in file_list:
                            beatmap_data = json.loads(
                                zf.read(d["filename"]).decode("utf-8")
                            )
                            selected_difficulty = d["difficulty"]
                            break

                if not beatmap_data:
                    print("❌ Поддерживаемая сложность (Standard) не найдена")
                    return None

                print(f"📊 Загружена сложность: {selected_difficulty}")

                # Извлечение названия и автора
                if format_type in ("v3", "v4"):
                    song_name = info_data.get("song", {}).get("title", "Unknown")
                    song_author = info_data.get("song", {}).get("author", "Unknown")
                    bpm = info_data.get("audio", {}).get("bpm", 120)
                else:
                    song_name = info_data.get("_songName", "Unknown")
                    song_author = info_data.get("_songAuthorName", "Unknown")
                    bpm = info_data.get("_beatsPerMinute", 120)

                return {
                    "info": info_data,
                    "beatmap": beatmap_data,
                    "audio_path": str(audio_path),
                    "song_name": song_name,
                    "song_author": song_author,
                    "bpm": bpm,
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

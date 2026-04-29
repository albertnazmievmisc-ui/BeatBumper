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
    
    REQUIRED_FILES = ['Info.dat']
    SUPPORTED_MODES = ['Standard']
    
    def __init__(self):
        self.temp_dir = None
    
    def load_zip(self, zip_path: Path) -> Optional[Dict]:
        """Загрузка мапы из zip-архива"""
        if not zip_path.exists():
            print(f"❌ Файл не найден: {zip_path}")
            return None
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Проверка наличия обязательных файлов
                file_list = zf.namelist()
                
                if 'Info.dat' not in file_list:
                    print("❌ Info.dat не найден в архиве")
                    return None
                
                # Чтение Info.dat
                info_data = json.loads(zf.read('Info.dat').decode('utf-8'))
                
                # Поиск аудиофайла
                audio_filename = info_data.get('_songFilename')
                if not audio_filename:
                    print("❌ Аудиофайл не указан в Info.dat")
                    return None
                
                # Извлечение аудио во временную директорию
                self.temp_dir = tempfile.mkdtemp()
                audio_path = Path(self.temp_dir) / audio_filename
                
                with zf.open(audio_filename) as audio_file:
                    with open(audio_path, 'wb') as f:
                        f.write(audio_file.read())
                
                # Поиск файлов сложности
                difficulty_sets = info_data.get('_difficultyBeatmapSets', [])
                beatmap_data = None
                
                for diff_set in difficulty_sets:
                    if diff_set.get('_beatmapCharacteristicName') in self.SUPPORTED_MODES:
                        for diff_map in diff_set.get('_difficultyBeatmaps', []):
                            filename = diff_map.get('_beatmapFilename')
                            if filename and filename in file_list:
                                beatmap_data = json.loads(
                                    zf.read(filename).decode('utf-8')
                                )
                                break
                
                if not beatmap_data:
                    print("❌ Поддерживаемая сложность не найдена")
                    return None
                
                return {
                    'info': info_data,
                    'beatmap': beatmap_data,
                    'audio_path': str(audio_path),
                    'song_name': info_data.get('_songName', 'Unknown'),
                    'song_author': info_data.get('_songAuthorName', 'Unknown'),
                    'bpm': info_data.get('_beatsPerMinute', 120),
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

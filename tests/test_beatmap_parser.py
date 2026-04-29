"""
Тесты парсера битмап
"""

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parser.beatmap_parser import BeatmapParser


class TestBeatmapParser(unittest.TestCase):
    """Тестирование парсера битмап"""
    
    def setUp(self):
        self.parser = BeatmapParser()
        
        # Тестовые данные
        self.test_beatmap = {
            "_beatsPerMinute": 120,
            "_notes": [
                {"_time": 0, "_type": 0, "_cutDirection": 1},
                {"_time": 1, "_type": 1, "_cutDirection": 1},  # Синяя - игнорируем
                {"_time": 2, "_type": 0, "_cutDirection": 1},
                {"_time": 3, "_type": 0, "_cutDirection": 1},
            ]
        }
    
    def test_parse_red_notes_only(self):
        """Проверка фильтрации красных нот"""
        notes = self.parser.parse(self.test_beatmap)
        self.assertEqual(len(notes), 3)
        
    def test_time_conversion(self):
        """Проверка конвертации времени"""
        notes = self.parser.parse(self.test_beatmap)
        # При BPM=120: 0 битов = 0 сек, 2 бита = 1 сек
        self.assertAlmostEqual(notes[0]['time'], 0.0)
        self.assertAlmostEqual(notes[1]['time'], 1.0)
        
    def test_sorting(self):
        """Проверка сортировки по времени"""
        unsorted_beatmap = {
            "_beatsPerMinute": 120,
            "_notes": [
                {"_time": 5, "_type": 0, "_cutDirection": 1},
                {"_time": 1, "_type": 0, "_cutDirection": 1},
                {"_time": 3, "_type": 0, "_cutDirection": 1},
            ]
        }
        notes = self.parser.parse(unsorted_beatmap)
        times = [n['time'] for n in notes]
        self.assertEqual(times, sorted(times))


if __name__ == '__main__':
    unittest.main()

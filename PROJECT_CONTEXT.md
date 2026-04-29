# BeatBumper - Контекст проекта

**Дата:** 2026-04-29
**Версия:** 0.1.0-alpha
**Платформа:** Steam Deck (SteamOS / Arch Linux)
**Python:** 3.x с виртуальным окружением

---

## 📋 Текущее состояние

### ✅ Реализовано
- Ядро игры (game_engine.py) с состояниями MENU → PLAYING → PAUSED → RESULTS
- Парсер Beat Saber мап (только красные ноты, фильтрация _type == 0)
- Аудио-движок с компенсацией задержки (audio_latency_ms в конфиге)
- Система судейства: Perfect (±50ms), Good (±100ms), Miss (>100ms)
- Визуальные эффекты: партиклы взрывов, ударные волны
- Подсчет очков с комбо-множителем (+10% за каждые 10 комбо)
- Ранги: SS (100%), S (95%), A (85%), B (70%), C (55%), D (40%), F
- Поддержка геймпада Steam Deck (A=удар, Start=пауза)
- Экран меню со сканированием папки songs/
- Экран результатов с детальной статистикой
- FPS-счетчик в режиме отладки

### ⚠️ Известные проблемы
1. **Ноты не летят после выбора песни** — нужно проверить парсинг сложности
2. **Выход только по Q** — нет маппинга на геймпад
3. **Нет визуального отображения промахов**
4. **Нет выбора сложности в меню**
5. **Конфиг audio_latency_ms требует калибровки**

### 🔧 Последние исправления
- Относительные импорты заменены на абсолютные
- Исправлен Enum Action (вынесен из InputHandler)
- Добавлена отладочная информация при загрузке мап

---

## 🏗️ Архитектура
BeatBumper/
├── main.py # Точка входа, инициализация pygame
├── src/
│ ├── core/
│ │ ├── game_engine.py # Главный цикл, состояния
│ │ ├── note_controller.py # Движение нот, проверка попаданий
│ │ └── score_manager.py # Очки, комбо, ранг
│ ├── parser/
│ │ ├── beatmap_loader.py # Чтение .zip, извлечение аудио
│ │ └── beatmap_parser.py # Парсинг JSON, фильтрация красных нот
│ ├── audio/
│ │ └── audio_manager.py # pygame.mixer, SFX
│ ├── render/
│ │ ├── renderer.py # Отрисовка фона, нот, эффектов
│ │ ├── note_sprite.py # Спрайт красной ноты
│ │ └── effects.py # Particle, Shockwave
│ ├── input/
│ │ └── input_handler.py # Клавиатура + геймпад с Action enum
│ ├── ui/
│ │ ├── menu_screen.py # Сканирование песен, выбор
│ │ ├── game_screen.py # Игровой процесс
│ │ └── results_screen.py # Результаты, ранг
│ └── utils/
│ ├── config.py # Конфиг с автоопределением Steam Deck
│ └── helpers.py # format_time, clamp, lerp, FPSCounter
├── assets/
│ ├── sprites/ # PNG спрайты (пока генерируются кодом)
│ ├── fonts/ # Шрифты (пока используется pygame.font.Font)
│ └── sounds/ # hit.wav, miss.wav (нужно добавить)
├── songs/ # Beat Saber .zip мапы
├── tests/
│ └── test_beatmap_parser.py # Юнит-тесты парсера
├── requirements.txt # pygame, numpy
├── Makefile # run, test, clean, setup
└── config.json # Настройки (автосоздается)

---

## 🎮 Управление

| Действие | Клавиатура | Steam Deck |
|----------|-----------|------------|
| Удар по ноте | ПРОБЕЛ | A |
| Пауза | ESC / P | Start |
| Выход | Q | ❌ не назначен |
| Меню вверх | ↑ | ❌ |
| Меню вниз | ↓ | ❌ |
| Выбор | ENTER | ❌ |
| Полный экран | Alt+Enter | ❌ |

---

## 🔄 Поток данных

songs/*.zip → BeatmapLoader.load_zip()
├── Извлечение Info.dat → название, BPM
├── Поиск аудиофайла → временная папка
└── Поиск сложности → BeatmapParser.parse()
├── Фильтр _type == 0 (только красные)
└── Конвертация beats → секунды
↓
NoteController.load_beatmap()
↓
GameScreen.update()
├── audio_manager.get_adjusted_position()
├── note_controller.update(dt, song_pos)
├── input_handler.is_hit_pressed() → check_hit()
└── score_manager.add_hit(result)

---

## 🐛 Баги и TODO

### Critical
- [ ] **Ноты не отображаются в игре** — проверить:
  - Правильно ли выбрана сложность в beatmap_loader.py?
  - Парсятся ли ноты? (добавить print в beatmap_parser.py)
  - Загружаются ли в NoteController? (вывести len(self.notes))
  - Правильно ли считается note_speed и позиции?
  - Синхронизируется ли audio_manager.get_position()?

- [ ] **Выход с геймпада** — добавить Action.QUIT маппинг на Back/Select

### High Priority
- [ ] Визуальный индикатор Miss (падение ноты вниз)
- [ ] Калибровка audio_latency_ms (меню настройки)
- [ ] Выбор сложности (Easy/Normal/Hard/Expert/Expert+) в меню
- [ ] Добавить звуковые эффекты (assets/sounds/hit.wav, miss.wav)

### Medium Priority
- [ ] Пауза с затемнением и меню (Resume / Restart / Quit)
- [ ] Прогресс-бар песни
- [ ] Сохранение рекордов (scores.json)
- [ ] Навигация по меню геймпадом (стики/D-pad)

### Low Priority
- [ ] Поддержка синих нот
- [ ] Поддержка бомб и стен
- [ ] Тачскрин-управление
- [ ] Скины нот
- [ ] Анимация фона под музыку

---

## 🚀 Быстрый старт

```bash
cd /home/deck/Documents/Projects/BeatBumper

# Активировать виртуальное окружение (если есть)
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Поместить .zip мапы в songs/
# Запустить
python3 main.py

# Тесты
python3 -m pytest tests/ -v

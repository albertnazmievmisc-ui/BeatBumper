# BeatBumper - Контекст проекта

**Дата:** 2026-04-29
**Версия:** 0.2.0-alpha
**Платформа:** Steam Deck (SteamOS / Arch Linux)
**Python:** 3.x с виртуальным окружением

---

## 📋 Текущее состояние

### ✅ Реализовано
- Ядро игры (game_engine.py) с состояниями MENU → PLAYING → PAUSED → RESULTS
- Парсер Beat Saber мап с поддержкой форматов v2, v3, v4.1.0
  - v2: _notes с _type, _lineLayer, _lineIndex, _cutDirection
  - v3: colorNotes с b, x, y, c, d, a
  - v4.1.0: colorNotes + colorNotesData (индексная адресация)
- Поддержка КРАСНЫХ и СИНИХ нот (оба цвета)
- Аудио-движок с компенсацией задержки (audio_latency_ms в конфиге)
- Система судейства: Perfect (±50ms), Good (±100ms), Miss (>100ms), Wrong Color
- Визуальные эффекты: партиклы взрывов, ударные волны
- Подсчет очков с комбо-множителем (+10% за каждые 10 комбо)
- Ранги: SS (100%), S (95%), A (85%), B (70%), C (55%), D (40%), F
- 4 линии для нот (вертикальное распределение по line_index)
- Поддержка геймпада Steam Deck (A=красный удар, X=синий удар, Start=пауза, Back=выход)
- Экран меню с выбором песни и сложности
  - Сканирование папки songs/
  - Выбор сложности (Easy/Normal/Hard/Expert/ExpertPlus)
  - Поддержка Info.dat v2.x и v4.x
- Экран результатов с детальной статистикой
- FPS-счетчик в режиме отладки
- Штраф за удар не тем цветом (Wrong Color)

### ⚠️ Известные проблемы
1. Нет визуального отображения промахов (ноты просто исчезают)
2. Конфиг audio_latency_ms требует калибровки
3. Нет сохранения рекордов (scores.json)
4. Нет поддержки бомб и стен (игнорируются при парсинге)
5. Нет поддержки арок (arcs) — слайдеры из v4 мап
6. Переменный BPM не учитывается (берётся только первый BPM из bpmEvents)

### 🔧 Последние исправления (v0.2.0)
- Добавлены синие ноты — полная поддержка второго цвета
- Парсер v4.1.0 — поддержка colorNotes + colorNotesData
- Выбор сложности в меню — цветовая индикация, отображение мапперов
- Поддержка Info.dat v4 — audio.songFilename, difficultyBeatmaps (плоский список)
- Выход с геймпада — кнопка Back/Select
- 4 игровые линии — ноты распределены по вертикали

---

## 🏗️ Архитектура

BeatBumper/
├── main.py                    # Точка входа, инициализация pygame
├── src/
│   ├── core/
│   │   ├── game_engine.py     # Главный цикл, состояния
│   │   ├── note_controller.py # Движение нот, проверка попаданий (красные/синие)
│   │   └── score_manager.py   # Очки, комбо, ранг
│   ├── parser/
│   │   ├── beatmap_loader.py  # Чтение .zip, извлечение аудио, выбор сложности
│   │   └── beatmap_parser.py  # Парсинг JSON v2/v3/v4.1.0, все цвета нот
│   ├── audio/
│   │   └── audio_manager.py   # pygame.mixer, SFX
│   ├── render/
│   │   ├── renderer.py        # Отрисовка фона, зон удара, нот, эффектов
│   │   ├── note_sprite.py     # Спрайты красных/синих нот со стрелками
│   │   └── effects.py         # Particle, Shockwave
│   ├── input/
│   │   └── input_handler.py   # Клавиатура + геймпад
│   ├── ui/
│   │   ├── menu_screen.py     # Сканирование песен, выбор сложности
│   │   ├── game_screen.py     # Игровой процесс
│   │   └── results_screen.py  # Результаты, ранг
│   └── utils/
│       ├── config.py           # Конфиг с автоопределением Steam Deck
│       └── helpers.py          # format_time, clamp, lerp, FPSCounter
├── assets/
│   ├── sprites/                # PNG спрайты (генерируются кодом)
│   ├── fonts/                  # Шрифты (пока pygame.font.Font)
│   └── sounds/                 # hit.wav, miss.wav (нужно добавить)
├── songs/                      # Beat Saber .zip мапы
├── tests/
│   └── test_beatmap_parser.py  # Юнит-тесты парсера
├── requirements.txt            # pygame, numpy
├── Makefile                    # run, test, clean, setup
├── config.json                 # Настройки (автосоздается)
└── PROJECT_CONTEXT.md          # Этот файл

---

## 🎮 Управление

| Действие | Клавиатура | Steam Deck |
|----------|-----------|------------|
| Удар по красной ноте | ПРОБЕЛ / A | A |
| Удар по синей ноте | Левый Shift / S | X |
| Пауза | ESC / P | Start |
| Выход | Q | Back/Select |
| Меню вверх | ↑ | ❌ |
| Меню вниз | ↓ | ❌ |
| Выбор | ENTER | A |
| Назад | ESC | B |
| Полный экран | Alt+Enter | ❌ |

---

## 🔄 Поток данных

songs/*.zip → BeatmapLoader.load_zip()
├── Определение формата Info.dat (v2/v3/v4)
├── Извлечение аудио (audio.songFilename / _songFilename)
├── Получение списка сложностей
└── Загрузка сложности → BeatmapParser.parse()
    ├── Определение формата (v2/v3/v4)
    ├── v4: colorNotes → colorNotesData[i] (c=0 красные, c=1 синие)
    ├── v3: colorNotes (c, x, y, d)
    ├── v2: _notes (_type, _lineIndex, _lineLayer, _cutDirection)
    └── Возврат: [{time, color, line_index, line_layer, cut_direction}, ...]
        ↓
NoteController.load_beatmap()
├── Note(time, color=RED/BLUE, line_index, line_layer, cut_direction)
└── 4 линии (lane_positions: 0-3)
    ↓
GameScreen.update()
├── audio_manager.get_adjusted_position()
├── note_controller.update(dt, song_pos)
├── is_hit_red_pressed() → check_hit_red()
├── is_hit_blue_pressed() → check_hit_blue()
└── check_hit_by_color() → проверка цвета

---

## 🎨 Форматы битмап

### v4.1.0 (современный)
colorNotes: [{b, r, i}]  b=beat, i=индекс в colorNotesData
colorNotesData: [{x, y, c, d, a}]  c: 0=красный, 1=синий

### v3.x
colorNotes: [{b, x, y, c, d, a}]  данные внутри объекта

### v2.x (старый)
_notes: [{_time, _lineIndex, _lineLayer, _type, _cutDirection}]  _type: 0=красный, 1=синий, 3=бомба

---

## 🐛 Баги и TODO

### Critical
- [ ] Калибровка audio_latency_ms — автоматический тест или меню настройки
- [ ] Добавить звуковые эффекты (assets/sounds/hit.wav, miss.wav)

### High Priority
- [ ] Визуальный индикатор Miss (ноты падают и исчезают)
- [ ] Поддержка бомб (визуальное отображение, -10 очков при ударе)
- [ ] Поддержка стен (визуальное отображение, -5 очков при столкновении)
- [ ] Сохранение рекордов (scores.json)
- [ ] Навигация по меню геймпадом (стики/D-pad)

### Medium Priority
- [ ] Пауза с меню (Resume / Restart / Quit)
- [ ] Прогресс-бар песни
- [ ] Учёт переменного BPM (bpmEvents в v3/v4)
- [ ] Поддержка арок (arcs) — слайдеры между нотами

### Low Priority
- [ ] Тачскрин-управление
- [ ] Скины нот
- [ ] Анимация фона под музыку
- [ ] Поддержка characteristics кроме Standard (Lawless, OneSaber и т.д.)
- [ ] Мультиплеер (local co-op)

---

## 🚀 Быстрый старт

cd /home/deck/Documents/Projects/BeatBumper
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
python3 -m pytest tests/ -v

---

## 📝 Changelog

### v0.2.0-alpha (2026-04-29)
- Синие ноты — полная поддержка второго цвета
- Парсер v4.1.0 — colorNotes + colorNotesData
- 4 игровые линии — вертикальное распределение
- Выбор сложности — меню с цветовой индикацией
- Wrong Color — штраф за удар не тем цветом
- Info.dat v4 — поддержка нового формата
- Выход с геймпада — Back/Select

### v0.1.0-alpha (2026-04-28)
- Базовый геймплей с красными нотами
- Парсер v2/v3 битмап
- Аудио-движок с компенсацией задержки
- Система судейства и рангов
- Интерфейс меню и результатов

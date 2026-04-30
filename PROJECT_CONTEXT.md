# BeatBumper - Контекст проекта

**Дата:** 2026-04-30
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
- Визуализация: ноты движутся СВЕРХУ ВНИЗ
  - Красные ноты — справа (красная дорожка)
  - Синие ноты — слева (синяя дорожка)
  - Линия удара внизу экрана (горизонтальная)
  - Позиции дорожек настраиваются в конфиге (red_lane_position, blue_lane_position)
- Аудио-движок с компенсацией задержки (audio_latency_ms в конфиге)
- Система судейства: Perfect (±50ms), Good (±100ms), Miss (>100ms), Wrong Color
- Визуальные эффекты:
  - Партиклы взрывов при попадании (больше для Perfect)
  - Ударные волны (Shockwave)
  - Свечение дорожки при нажатии кнопки (ButtonPressEffect)
  - Частицы при нажатии (даже если нет ноты)
  - Всплывающие тексты на позиции ноты: PERFECT!, Good, MISS, WRONG!
- Подсчет очков с комбо-множителем (+10% за каждые 10 комбо)
- Ранги: SS (100%), S (95%), A (85%), B (70%), C (55%), D (40%), F
- Поддержка геймпада Steam Deck:
  - RT (правый триггер) — удар по красным нотам
  - LT (левый триггер) — удар по синим нотам
  - Start — пауза
  - Back/Select — выход
  - A — выбор в меню
  - B — назад в меню
- Клавиатурное управление:
  - Стрелка вправо / D — красные ноты
  - Стрелка влево / A — синие ноты
  - ESC / P — пауза
  - Q — выход
- Экран меню с выбором песни и сложности
  - Сканирование папки songs/
  - Выбор сложности (Easy/Normal/Hard/Expert/ExpertPlus)
  - Поддержка Info.dat v2.x и v4.x
- Экран результатов с детальной статистикой
- FPS-счетчик в режиме отладки
- Штраф за удар не тем цветом (Wrong Color)

### ⚠️ Известные проблемы
1. Нет визуального отображения промахов (ноты просто исчезают, но есть текст MISS)
2. Конфиг audio_latency_ms требует калибровки
3. Нет сохранения рекордов (scores.json)
4. Нет поддержки бомб и стен (игнорируются при парсинге)
5. Нет поддержки арок (arcs) — слайдеры из v4 мап
6. Переменный BPM не учитывается (берётся только первый BPM из bpmEvents)

### 🔧 Последние исправления (v0.2.0)
- Добавлены синие ноты — полная поддержка второго цвета
- Визуализация изменена: ноты летят СВЕРХУ ВНИЗ (красные справа, синие слева)
- Управление на триггеры: RT для красных, LT для синих
- Визуальные эффекты при нажатии кнопок (даже мимо нот)
- Всплывающие тексты результатов на позиции ноты
- Парсер v4.1.0 — поддержка colorNotes + colorNotesData
- Выбор сложности в меню — цветовая индикация, отображение мапперов
- Поддержка Info.dat v4 — audio.songFilename, difficultyBeatmaps (плоский список)
- Выход с геймпада — кнопка Back/Select
- Позиции дорожек вынесены в конфиг (red_lane_position, blue_lane_position, lane_width, lane_alpha)

---

## 🏗️ Архитектура

BeatBumper/
├── main.py                    # Точка входа, инициализация pygame
├── src/
│   ├── core/
│   │   ├── game_engine.py     # Главный цикл, состояния (MENU/PLAYING/PAUSED/RESULTS)
│   │   ├── note_controller.py # Движение нот сверху вниз, красные справа/синие слева
│   │   └── score_manager.py   # Очки, комбо, ранг
│   ├── parser/
│   │   ├── beatmap_loader.py  # Чтение .zip, извлечение аудио, выбор сложности, Info.dat v2/v4
│   │   └── beatmap_parser.py  # Парсинг JSON v2/v3/v4.1.0, все цвета нот (+ colorNotesData)
│   ├── audio/
│   │   └── audio_manager.py   # pygame.mixer, SFX, компенсация задержки
│   ├── render/
│   │   ├── renderer.py        # Отрисовка фона, дорожек, линии удары, нот, эффектов
│   │   ├── note_sprite.py     # Спрайты красных/синих нот со стрелками (↑ синие, ↓ красные)
│   │   └── effects.py         # Particle, Shockwave, ButtonPressEffect, EffectsManager
│   ├── input/
│   │   └── input_handler.py   # Клавиатура + геймпад (триггеры RT/LT, оси 4/5)
│   ├── ui/
│   │   ├── menu_screen.py     # Сканирование песен, выбор сложности (2 состояния)
│   │   ├── game_screen.py     # Игровой процесс + FloatingText для результатов
│   │   └── results_screen.py  # Результаты, ранг
│   └── utils/
│       ├── config.py           # Конфиг: позиции дорожек, аудио, автоопределение Steam Deck
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
├── config.json                 # Настройки дорожек, аудио, экрана (автосоздается)
└── PROJECT_CONTEXT.md          # Этот файл

---

## 🎮 Управление

| Действие | Клавиатура | Steam Deck |
|----------|-----------|------------|
| Удар по красной ноте | Стрелка вправо / D | RT (правый триггер) |
| Удар по синей ноте | Стрелка влево / A | LT (левый триггер) |
| Пауза | ESC / P | Start |
| Выход | Q | Back/Select |
| Меню вверх | ↑ | ❌ (добавить D-pad) |
| Меню вниз | ↓ | ❌ (добавить D-pad) |
| Выбор | ENTER | A |
| Назад | ESC | B |
| Полный экран | Alt+Enter | ❌ |

---

## 🔄 Поток данных

songs/*.zip → BeatmapLoader.load_zip()
├── Определение формата Info.dat (v2/v3/v4)
├── Извлечение аудио (audio.songFilename / _songFilename)
├── Получение списка сложностей (difficultyBeatmaps / _difficultyBeatmapSets)
└── Загрузка выбранной сложности → BeatmapParser.parse()
    ├── Определение формата (v2/v3/v4)
    ├── v4: colorNotes[i] → colorNotesData[i] (c=0 красные, c=1 синие)
    ├── v3: colorNotes (c, x, y, d)
    ├── v2: _notes (_type, _lineIndex, _lineLayer, _cutDirection)
    └── Возврат: [{time, color, line_index, line_layer, cut_direction}, ...]
        ↓
NoteController.load_beatmap()
├── Note(time, color=RED/BLUE, line_index, line_layer, cut_direction)
├── RED → red_x (config.red_lane_x, по умолчанию 58% ширины)
├── BLUE → blue_x (config.blue_lane_x, по умолчанию 42% ширины)
└── Движение: Y увеличивается (сверху вниз) к hit_line_y
    ↓
GameScreen.update()
├── audio_manager.get_adjusted_position()
├── note_controller.update(dt, song_pos) — обновление позиций
├── renderer.effects.update(dt) — обновление эффектов
├── input_handler.is_hit_red_pressed() → 
│   ├── effects.create_button_press_red() — ВСЕГДА (визуальный отклик)
│   └── note_controller.check_hit_red() → HitResult
├── input_handler.is_hit_blue_pressed() →
│   ├── effects.create_button_press_blue() — ВСЕГДА
│   └── note_controller.check_hit_blue() → HitResult
├── FloatingText на позиции ноты (PERFECT!/Good/MISS/WRONG!)
└── score_manager.add_hit(result) — WRONG_COLOR считается как MISS

---

## 🎨 Форматы битмап

### v4.1.0 (современный)
colorNotes: [{b, r, i}] — b=beat, r=rotation, i=индекс в colorNotesData
colorNotesData: [{x, y, c, d, a}] — c: 0=красный, 1=синий
bombNotes + bombNotesData — бомбы (игнорируются)
obstacles + obstaclesData — стены (игнорируются)
arcs — слайдеры (игнорируются)

### v3.x
colorNotes: [{b, x, y, c, d, a}] — все данные внутри объекта

### v2.x (старый)
_notes: [{_time, _lineIndex, _lineLayer, _type, _cutDirection}]
_type: 0=красный, 1=синий, 3=бомба

---

## ⚙️ Конфигурация (config.json)

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| screen_width | 1280 | Ширина экрана |
| screen_height | 720 | Высота экрана |
| fullscreen | false | Полноэкранный режим |
| target_fps | 60 | Целевой FPS |
| debug_mode | false | Режим отладки (FPS-счетчик) |
| note_speed | 600 | Скорость падения нот (пикселей/сек) |
| hit_line_y | screen_height - 150 | Y-позиция линии удары |
| red_lane_position | 0.58 | Позиция красной дорожки (0.0-1.0 от ширины) |
| blue_lane_position | 0.42 | Позиция синей дорожки (0.0-1.0 от ширины) |
| lane_width | 100 | Ширина дорожки в пикселях |
| lane_alpha | 15 | Прозрачность дорожки (0-255) |
| audio_latency_ms | -50 | Компенсация задержки аудио (мс) |
| music_volume | 0.8 | Громкость музыки (0.0-1.0) |
| sfx_volume | 0.7 | Громкость звуковых эффектов (0.0-1.0) |
| audio_buffer_size | 2048 | Размер буфера аудио |

---

## 🐛 Баги и TODO

### Critical
- [ ] Калибровка audio_latency_ms — автоматический тест или меню настройки
- [ ] Добавить звуковые эффекты (assets/sounds/hit.wav, miss.wav)

### High Priority
- [ ] Визуальный индикатор Miss (ноты падают и исчезают с анимацией)
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
source .venv/bin/activate  # если есть venv
pip install -r requirements.txt
python3 main.py             # запуск игры
python3 -m pytest tests/ -v # тесты

---

## 📝 Changelog

### v0.2.0-alpha (2026-04-30)
- Визуализация: ноты сверху вниз, красные справа, синие слева
- Управление: RT для красных, LT для синих
- Визуальные эффекты нажатия кнопок (свечение дорожки, частицы)
- Всплывающие тексты результатов на позиции ноты (FloatingText)
- Парсер v4.1.0 (colorNotes + colorNotesData)
- Поддержка синих нот
- Выбор сложности в меню
- Info.dat v4 поддержка
- Конфигурация дорожек в config.json

### v0.1.0-alpha (2026-04-28)
- Базовый геймплей с красными нотами
- Парсер v2/v3 битмап
- Аудио-движок с компенсацией задержки
- Система судейства и рангов
- Интерфейс меню и результатов
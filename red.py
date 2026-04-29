#!/usr/bin/env python3
"""
Исправление ВСЕХ импортов на абсолютные с учетом структуры пакетов
"""

import re
from pathlib import Path
from collections import defaultdict


def build_module_tree(base_dir: Path) -> dict:
    """Строим дерево модулей: {имя_файла: полный.путь.к.модулю}"""
    module_map = {}

    for py_file in base_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        rel_path = py_file.relative_to(base_dir)
        parts = list(rel_path.parts[:-1]) + [rel_path.stem]

        # Полный путь для импорта
        full_module = ".".join(parts)

        # Имя файла без расширения
        file_stem = rel_path.stem
        module_map[file_stem] = full_module

        # Также добавляем с путем относительно src
        if len(parts) > 1:
            # Например: core.game_engine -> game_engine
            pass

    return module_map


def fix_file(file_path: Path, module_map: dict) -> bool:
    """Исправляет импорты в одном файле"""

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    modified = False

    # Паттерны и их замена
    fixes = [
        # from ..module import X
        (
            re.compile(r"from \.\.(\w+) import", re.MULTILINE),
            lambda m: f"from {module_map.get(m.group(1), m.group(1))} import",
        ),
        # from ..sub.module import X
        (
            re.compile(r"from \.\.([\w.]+) import", re.MULTILINE),
            lambda m: f"from {m.group(1)} import",
        ),
        # from .module import X
        (
            re.compile(r"from \.(\w+) import", re.MULTILINE),
            lambda m: f"from {module_map.get(m.group(1), m.group(1))} import",
        ),
        # from .sub.module import X
        (
            re.compile(r"from \.([\w.]+) import", re.MULTILINE),
            lambda m: f"from {m.group(1)} import",
        ),
    ]

    for pattern, replacement in fixes:
        new_content = pattern.sub(replacement, content)
        if new_content != content:
            modified = True
            content = new_content

    # Отдельно обрабатываем случай "from note_controller import"
    # когда файл в той же директории
    current_dir = file_path.parent
    for neighbor in current_dir.glob("*.py"):
        if neighbor.stem == "__init__":
            continue
        # Ищем импорт соседа без указания пакета
        pattern = re.compile(rf"from {neighbor.stem} import", re.MULTILINE)
        if pattern.search(content):
            full_module = module_map.get(neighbor.stem, neighbor.stem)
            content = pattern.sub(f"from {full_module} import", content)
            modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return modified


def main():
    src_dir = Path("/home/deck/Documents/Projects/BeatBumper/src")

    if not src_dir.exists():
        print(f"❌ {src_dir} не найден")
        return

    print("🔧 Строим карту модулей...")
    module_map = build_module_tree(src_dir)
    print(f"📋 Найдено модулей: {len(module_map)}")
    for name, path in sorted(module_map.items()):
        print(f"   {name} -> {path}")

    print("\n🔧 Исправляем импорты...")
    fixed_count = 0

    for py_file in src_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        if fix_file(py_file, module_map):
            print(f"  ✅ {py_file.relative_to(src_dir)}")
            fixed_count += 1

    print(f"\n✨ Исправлено файлов: {fixed_count}")

    # Финальная проверка
    print("\n🔍 Проверяем оставшиеся относительные импорты...")
    pattern = re.compile(r"from \.\.?(\w+)")
    issues = 0

    for py_file in src_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                match = pattern.search(line)
                if match:
                    # Проверяем что это не from module.submodule (абсолютный)
                    if not line.startswith(f"from {match.group(1)}"):
                        print(
                            f"  ⚠️  {py_file.relative_to(src_dir)}:{i}: {line.strip()}"
                        )
                        issues += 1

    if issues == 0:
        print("  ✅ Все чисто!")
    else:
        print(f"  ⚠️  Осталось {issues} проблемных импортов")

    print("\n🚀 Можно запускать: python3 main.py")


if __name__ == "__main__":
    main()

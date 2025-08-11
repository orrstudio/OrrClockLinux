"""
Скрипт для автоматического обновления отладочных принтов на использование логгера.
Запуск: python3 scripts/update_debug_prints.py
"""

import os
import re
import sys
from pathlib import Path

# Папки для обработки
SOURCE_DIRS = [
    'logic',
    'ui',
    'data',
    'utils'
]

# Шаблон для поиска отладочных принтов
DEBUG_PRINT_PATTERN = re.compile(r'print\(\s*[fF]?["\']\s*\[?DEBUG\]?[^\'\"]*[\'\"]\)')

# Шаблон для поиска обычных принтов
PRINT_PATTERN = re.compile(r'print\([^)]*\)')

def process_file(file_path):
    """Обработка одного файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Пропускаем файлы, которые уже используют logger
        if 'from utils.logger import' in content:
            return False
            
        # Заменяем отладочные принты
        new_content = DEBUG_PRINT_PATTERN.sub(
            lambda m: 'logger.debug(' + m.group(0)[6:-1] + ')', 
            content
        )
        
        # Если файл изменился, сохраняем
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
            
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
    
    return False

def main():
    """Основная функция"""
    project_root = Path(__file__).parent.parent
    updated_files = 0
    
    for dir_name in SOURCE_DIRS:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            continue
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(root, file)
                    if process_file(file_path):
                        print(f"Обновлен: {file_path}")
                        updated_files += 1
    
    print(f"\nГотово! Обновлено файлов: {updated_files}")
    
    # Добавляем импорт логгера в __init__.py если его там нет
    init_file = project_root / 'utils' / '__init__.py'
    if init_file.exists():
        with open(init_file, 'r+', encoding='utf-8') as f:
            content = f.read()
            if 'from .logger import' not in content:
                f.seek(0, 0)
                f.write('from .logger import logger, Logger\n\n' + content)
                print("\nДобавлен импорт логгера в utils/__init__.py")

if __name__ == "__main__":
    main()

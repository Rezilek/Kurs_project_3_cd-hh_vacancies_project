#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов проекта
"""

import subprocess
import sys
import os


def run_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ ПРОЕКТА HH VACANCIES")
    print("=" * 60)

    # Запускаем pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])

    print("=" * 60)
    if result.returncode == 0:
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✅")
    else:
        print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ! ❌")

    return result.returncode


if __name__ == '__main__':
    sys.exit(run_tests())
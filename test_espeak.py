#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы espeak с русским языком
"""
import os
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

def test_espeak():
    """
    Тестирование espeak с русским языком
    """
    # Тестовый текст
    text = "Привет! Это тестовое сообщение для проверки работы espeak с русским языком."
    
    # Создаем временную директорию
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Создаем временный текстовый файл
    temp_text_file = os.path.join(temp_dir, "temp_text.txt")
    with open(temp_text_file, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Создаем файл для вывода
    output_file = os.path.join(temp_dir, "test_espeak.wav")
    
    # Тестируем мужской голос
    logger.info("Тестирование espeak с мужским голосом")
    cmd_male = f"espeak -v ru -m -f {temp_text_file} -w {output_file}"
    logger.debug(f"Запуск команды: {cmd_male}")
    
    result_male = subprocess.run(cmd_male, shell=True, capture_output=True, text=True)
    
    if result_male.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        logger.info(f"Успешно создан файл с мужским голосом: {output_file}")
        # Удаляем файл
        os.remove(output_file)
    else:
        logger.error(f"Ошибка при использовании espeak с мужским голосом: {result_male.stderr}")
    
    # Тестируем женский голос
    logger.info("Тестирование espeak с женским голосом")
    cmd_female = f"espeak -v ru+f2 -f {temp_text_file} -w {output_file}"
    logger.debug(f"Запуск команды: {cmd_female}")
    
    result_female = subprocess.run(cmd_female, shell=True, capture_output=True, text=True)
    
    if result_female.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        logger.info(f"Успешно создан файл с женским голосом: {output_file}")
        # Удаляем файл
        os.remove(output_file)
    else:
        logger.error(f"Ошибка при использовании espeak с женским голосом: {result_female.stderr}")
    
    # Удаляем временный файл
    if os.path.exists(temp_text_file):
        os.remove(temp_text_file)

if __name__ == "__main__":
    test_espeak()
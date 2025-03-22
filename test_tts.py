#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы tts_converter.py
"""
import os
import logging
from app.utils.tts_converter import convert_text_to_speech
from config import DEFAULT_LANGUAGE, DEFAULT_VOICE_TYPE, DEFAULT_TTS_ENGINE, DEFAULT_AUDIO_FORMAT

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

def test_tts():
    """
    Тестирование конвертации текста в речь
    """
    # Тестовый текст
    text = "Привет! Это тестовое сообщение для проверки работы конвертера текста в речь."
    
    # Тестируем gtts
    logger.info("Тестирование Google TTS")
    file_path = convert_text_to_speech(
        text=text,
        language=DEFAULT_LANGUAGE,
        voice_type=DEFAULT_VOICE_TYPE,
        tts_engine='gtts',
        audio_format=DEFAULT_AUDIO_FORMAT
    )
    
    if file_path and os.path.exists(file_path):
        logger.info(f"Google TTS успешно создал файл: {file_path}")
        # Удаляем файл
        os.remove(file_path)
    else:
        logger.error("Google TTS не смог создать файл")
    
    # Тестируем pyttsx3
    logger.info("Тестирование pyttsx3")
    file_path = convert_text_to_speech(
        text=text,
        language=DEFAULT_LANGUAGE,
        voice_type=DEFAULT_VOICE_TYPE,
        tts_engine='pyttsx3',
        audio_format=DEFAULT_AUDIO_FORMAT
    )
    
    if file_path and os.path.exists(file_path):
        logger.info(f"pyttsx3 успешно создал файл: {file_path}")
        # Удаляем файл
        os.remove(file_path)
    else:
        logger.error("pyttsx3 не смог создать файл")
    
    # Тестируем espeak
    logger.info("Тестирование espeak")
    # Создаем временный текстовый файл
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_text_file = os.path.join(temp_dir, "temp_text.txt")
    with open(temp_text_file, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Создаем файл для вывода
    output_file = os.path.join(temp_dir, "test_espeak.wav")
    
    # Тестируем мужской голос
    logger.info("Тестирование espeak с мужским голосом")
    cmd_male = f"espeak -v {DEFAULT_LANGUAGE} -f {temp_text_file} -w {output_file}"
    logger.debug(f"Запуск команды: {cmd_male}")
    
    import subprocess
    result_male = subprocess.run(cmd_male, shell=True, capture_output=True, text=True)
    
    if result_male.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        logger.info(f"Успешно создан файл с мужским голосом: {output_file}")
        # Удаляем файл
        os.remove(output_file)
    else:
        logger.error(f"Ошибка при использовании espeak с мужским голосом: {result_male.stderr}")
    
    # Тестируем женский голос
    logger.info("Тестирование espeak с женским голосом")
    voice_param = f"{DEFAULT_LANGUAGE}+f2"
    cmd_female = f"espeak -v {voice_param} -f {temp_text_file} -w {output_file}"
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
    test_tts()
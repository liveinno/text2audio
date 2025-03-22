#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки функциональности бота
"""
import os
import logging
from config import TEMP_DIR, DEFAULT_LANGUAGE, DEFAULT_VOICE_TYPE, DEFAULT_TTS_ENGINE, DEFAULT_AUDIO_FORMAT
from app.utils.text_splitter import split_text
from app.utils.tts_converter import convert_text_to_speech
from app.utils.audio_processor import process_audio
from app.db.database import init_db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """
    Основная функция для тестирования бота
    """
    # Создаем директории
    os.makedirs("db", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Инициализация базы данных
    init_db()
    
    # Тестовый текст
    test_text = "Привет! Это тестовый текст для проверки работы бота. Он должен быть преобразован в аудио."
    
    logger.info("Начинаем тестирование...")
    
    # Разбиение текста на части
    text_parts = split_text(test_text)
    logger.info(f"Текст разбит на {len(text_parts)} частей")
    
    # Конвертация текста в аудио
    audio_files = []
    for i, part in enumerate(text_parts):
        logger.info(f"Конвертация части {i+1}/{len(text_parts)}")
        try:
            audio_file = convert_text_to_speech(
                part, 
                language=DEFAULT_LANGUAGE,
                voice_type=DEFAULT_VOICE_TYPE,
                tts_engine=DEFAULT_TTS_ENGINE
            )
            
            # Обработка аудиофайла
            processed_audio = process_audio(
                audio_file,
                title=f"Часть {i+1}",
                output_format=DEFAULT_AUDIO_FORMAT
            )
            audio_files.append(processed_audio)
            logger.info(f"Аудиофайл создан: {processed_audio}")
        except Exception as e:
            logger.error(f"Ошибка при конвертации текста: {e}")
    
    logger.info("Тестирование завершено!")
    logger.info(f"Созданные аудиофайлы: {audio_files}")

if __name__ == '__main__':
    main()
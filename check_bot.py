#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности бота
"""
import os
import sys
import logging
from dotenv import load_dotenv
import telegram
from app.utils.tts_converter import convert_text_to_speech

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

def check_env_file():
    """
    Проверка наличия и корректности файла .env
    """
    if not os.path.exists('.env'):
        logger.error("Файл .env не найден")
        print("Файл .env не найден. Создаем пример файла...")
        with open('.env', 'w') as f:
            f.write("TELEGRAM_TOKEN=your_telegram_token\n")
            f.write("ADMIN_USER_IDS=your_user_id\n")
            f.write("DEFAULT_TTS_ENGINE=gtts\n")
            f.write("DEFAULT_VOICE_TYPE=female\n")
            f.write("DEFAULT_LANGUAGE=ru\n")
            f.write("DEFAULT_AUDIO_FORMAT=mp3\n")
        print("Файл .env создан. Пожалуйста, заполните его правильными значениями.")
        return False
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие необходимых переменных
    required_vars = [
        'TELEGRAM_TOKEN',
        'ADMIN_USER_IDS',
        'DEFAULT_TTS_ENGINE',
        'DEFAULT_VOICE_TYPE',
        'DEFAULT_LANGUAGE',
        'DEFAULT_AUDIO_FORMAT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"В файле .env отсутствуют следующие переменные: {', '.join(missing_vars)}")
        print(f"В файле .env отсутствуют следующие переменные: {', '.join(missing_vars)}")
        return False
    
    return True

def check_telegram_token():
    """
    Проверка валидности токена Telegram
    """
    token = os.getenv('TELEGRAM_TOKEN')
    try:
        bot = telegram.Bot(token=token)
        bot_info = bot.get_me()
        logger.info(f"Бот успешно авторизован: {bot_info.first_name} (@{bot_info.username})")
        print(f"Бот успешно авторизован: {bot_info.first_name} (@{bot_info.username})")
        return True
    except Exception as e:
        logger.error(f"Ошибка при авторизации бота: {e}")
        print(f"Ошибка при авторизации бота: {e}")
        return False

def check_tts():
    """
    Проверка работоспособности TTS
    """
    # Создаем директории, если они не существуют
    os.makedirs('temp', exist_ok=True)
    
    # Тестовый текст
    text = "Привет! Это тестовое сообщение для проверки работы бота."
    
    # Проверяем Google TTS
    logger.info("Проверка Google TTS...")
    try:
        file_path = convert_text_to_speech(
            text=text,
            language=os.getenv('DEFAULT_LANGUAGE', 'ru'),
            voice_type=os.getenv('DEFAULT_VOICE_TYPE', 'female'),
            tts_engine='gtts',
            audio_format=os.getenv('DEFAULT_AUDIO_FORMAT', 'mp3')
        )
        
        if file_path and os.path.exists(file_path):
            logger.info(f"Google TTS успешно создал файл: {file_path}")
            print(f"Google TTS успешно создал файл: {file_path}")
            # Удаляем файл
            os.remove(file_path)
        else:
            logger.error("Google TTS не смог создать файл")
            print("Google TTS не смог создать файл")
            return False
    except Exception as e:
        logger.error(f"Ошибка при проверке Google TTS: {e}")
        print(f"Ошибка при проверке Google TTS: {e}")
        return False
    
    # Проверяем pyttsx3
    logger.info("Проверка pyttsx3...")
    try:
        file_path = convert_text_to_speech(
            text=text,
            language=os.getenv('DEFAULT_LANGUAGE', 'ru'),
            voice_type=os.getenv('DEFAULT_VOICE_TYPE', 'female'),
            tts_engine='pyttsx3',
            audio_format=os.getenv('DEFAULT_AUDIO_FORMAT', 'mp3')
        )
        
        if file_path and os.path.exists(file_path):
            logger.info(f"pyttsx3 успешно создал файл: {file_path}")
            print(f"pyttsx3 успешно создал файл: {file_path}")
            # Удаляем файл
            os.remove(file_path)
        else:
            logger.warning("pyttsx3 не смог создать файл, но это не критично, так как есть fallback на Google TTS")
            print("pyttsx3 не смог создать файл, но это не критично, так как есть fallback на Google TTS")
    except Exception as e:
        logger.warning(f"Ошибка при проверке pyttsx3: {e}")
        print(f"Ошибка при проверке pyttsx3: {e}")
        print("Это не критично, так как есть fallback на Google TTS")
    
    return True

def check_directories():
    """
    Проверка наличия необходимых директорий
    """
    directories = ['logs', 'temp', 'db']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Создана директория: {directory}")
            print(f"Создана директория: {directory}")
    
    return True

def main():
    """
    Основная функция проверки
    """
    print("Проверка работоспособности бота...")
    
    # Проверка наличия и корректности файла .env
    if not check_env_file():
        return False
    
    # Проверка наличия необходимых директорий
    if not check_directories():
        return False
    
    # Проверка валидности токена Telegram
    if not check_telegram_token():
        return False
    
    # Проверка работоспособности TTS
    if not check_tts():
        return False
    
    print("Все проверки пройдены успешно!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
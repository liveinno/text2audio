"""
Конфигурационный файл для приложения
"""
import os
from pathlib import Path
from decouple import config

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Настройки Telegram-бота
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN', default='')
ADMIN_USER_IDS = list(map(int, config('ADMIN_USER_IDS', default='').split(',')))

# Настройки базы данных
DATABASE_URL = config('DATABASE_URL', default='sqlite:///soundbot.db')

# Настройки TTS
DEFAULT_TTS_ENGINE = config('DEFAULT_TTS_ENGINE', default='gtts')  # Используем gtts по умолчанию, так как он более надежен для русского языка
DEFAULT_VOICE_TYPE = config('DEFAULT_VOICE_TYPE', default='female')
DEFAULT_LANGUAGE = config('DEFAULT_LANGUAGE', default='ru')
SUPPORTED_LANGUAGES = ['ru', 'en', 'fr', 'de', 'es', 'it']

# Настройки аудио
AUDIO_BITRATE = config('AUDIO_BITRATE', default='128k')
AUDIO_SAMPLE_RATE = int(config('AUDIO_SAMPLE_RATE', default='44100'))
DEFAULT_AUDIO_FORMAT = config('DEFAULT_AUDIO_FORMAT', default='mp3')

# Максимальная длина текста для конвертации
MAX_TEXT_LENGTH = int(config('MAX_TEXT_LENGTH', default='4000'))

# Настройки обработки текста
LANGUAGE_CONFIDENCE_THRESHOLD = 0.7
CHARS_PER_MINUTE_PROCESSING = 1000
LONG_PROCESSING_THRESHOLD_MINUTES = 5

# Настройки файлов
MAX_FILE_SIZE_MB = 10

# Создаем временную директорию, если она не существует
os.makedirs(TEMP_DIR, exist_ok=True)
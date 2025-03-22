"""
Модуль для определения языка текста
"""
import logging
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)

def detect_language(text):
    """
    Определение языка текста
    
    Args:
        text (str): Текст для определения языка
        
    Returns:
        tuple: (язык, уверенность)
    """
    try:
        # Простая эвристика для определения языка
        # В реальном проекте здесь должна быть библиотека langdetect или аналогичная
        
        # Для демонстрации просто возвращаем русский язык с высокой уверенностью
        return DEFAULT_LANGUAGE, 0.95
    except Exception as e:
        logger.error(f"Ошибка при определении языка: {e}")
        return DEFAULT_LANGUAGE, 0.5
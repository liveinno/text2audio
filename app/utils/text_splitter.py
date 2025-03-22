"""
Модуль для разбиения текста на части
"""
import logging
import re
from config import MAX_TEXT_LENGTH

logger = logging.getLogger(__name__)

def split_text(text, max_length=MAX_TEXT_LENGTH):
    """
    Разбиение текста на части по максимальной длине
    
    Args:
        text (str): Исходный текст
        max_length (int): Максимальная длина части
        
    Returns:
        list: Список частей текста
    """
    # Если текст короче максимальной длины, возвращаем его как есть
    if len(text) <= max_length:
        return [text]
    
    # Разбиваем текст на предложения
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    parts = []
    current_part = ""
    
    for sentence in sentences:
        # Если предложение слишком длинное, разбиваем его на части
        if len(sentence) > max_length:
            if current_part:
                parts.append(current_part)
                current_part = ""
            
            # Разбиваем предложение на части
            for i in range(0, len(sentence), max_length):
                part = sentence[i:i + max_length]
                parts.append(part)
        else:
            # Если добавление предложения превысит максимальную длину,
            # сохраняем текущую часть и начинаем новую
            if len(current_part) + len(sentence) + 1 > max_length:
                parts.append(current_part)
                current_part = sentence
            else:
                # Добавляем пробел, если текущая часть не пуста
                if current_part:
                    current_part += " "
                current_part += sentence
    
    # Добавляем последнюю часть, если она не пуста
    if current_part:
        parts.append(current_part)
    
    return parts
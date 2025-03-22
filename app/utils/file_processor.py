"""
Модуль для обработки файлов
"""
import os
import logging
from config import TEMP_DIR

logger = logging.getLogger(__name__)

def is_supported_file(file_name):
    """
    Проверка, поддерживается ли формат файла
    
    Args:
        file_name (str): Имя файла
        
    Returns:
        bool: True, если формат поддерживается, иначе False
    """
    # Получаем расширение файла
    _, ext = os.path.splitext(file_name)
    ext = ext.lower()
    
    # Поддерживаемые форматы
    supported_formats = ['.txt', '.docx', '.pdf']
    
    return ext in supported_formats

def process_file(file_path):
    """
    Обработка файла и извлечение текста
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        str: Извлеченный текст
    """
    # Получаем расширение файла
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    try:
        # Обработка в зависимости от формата
        if ext == '.txt':
            return process_txt_file(file_path)
        elif ext == '.docx':
            return process_docx_file(file_path)
        elif ext == '.pdf':
            return process_pdf_file(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {ext}")
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        raise

def process_txt_file(file_path):
    """
    Обработка текстового файла
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        str: Извлеченный текст
    """
    try:
        # Пробуем открыть файл с разными кодировками
        encodings = ['utf-8', 'cp1251', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                return text
            except UnicodeDecodeError:
                continue
        
        # Если ни одна кодировка не подошла
        raise UnicodeDecodeError("Не удалось определить кодировку файла")
    except Exception as e:
        logger.error(f"Ошибка при обработке текстового файла {file_path}: {e}")
        raise

def process_docx_file(file_path):
    """
    Обработка файла DOCX
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        str: Извлеченный текст
    """
    try:
        # Для демонстрации просто возвращаем текст
        return "Текст из DOCX файла (заглушка)"
    except Exception as e:
        logger.error(f"Ошибка при обработке DOCX файла {file_path}: {e}")
        raise

def process_pdf_file(file_path):
    """
    Обработка файла PDF
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        str: Извлеченный текст
    """
    try:
        # Для демонстрации просто возвращаем текст
        return "Текст из PDF файла (заглушка)"
    except Exception as e:
        logger.error(f"Ошибка при обработке PDF файла {file_path}: {e}")
        raise
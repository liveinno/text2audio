"""
Модуль для управления очередью задач
"""
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Очередь задач (в реальном проекте должна быть в базе данных)
task_queue = []

def add_to_queue(user_id, text, source_type):
    """
    Добавление задачи в очередь
    
    Args:
        user_id (int): ID пользователя
        text (str): Текст для конвертации
        source_type (str): Тип источника (text/file)
        
    Returns:
        str: ID задачи
    """
    task_id = str(uuid.uuid4())
    
    task = {
        'id': task_id,
        'user_id': user_id,
        'text': text,
        'source_type': source_type,
        'status': 'pending',
        'created_at': datetime.now(),
        'position': len(task_queue) + 1
    }
    
    task_queue.append(task)
    
    logger.info(f"Задача {task_id} добавлена в очередь для пользователя {user_id}")
    
    return task_id

def get_queue_position(task_id):
    """
    Получение позиции задачи в очереди
    
    Args:
        task_id (str): ID задачи
        
    Returns:
        int: Позиция в очереди (0, если задача не найдена)
    """
    for i, task in enumerate(task_queue):
        if task['id'] == task_id:
            return i + 1
    
    return 0

def is_queue_full():
    """
    Проверка, заполнена ли очередь
    
    Returns:
        bool: True, если очередь заполнена, иначе False
    """
    # Максимальный размер очереди (в реальном проекте должен быть в конфигурации)
    max_queue_size = 100
    
    return len(task_queue) >= max_queue_size

def can_make_request(user_id):
    """
    Проверка, может ли пользователь сделать запрос
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        bool: True, если пользователь может сделать запрос, иначе False
    """
    # В реальном проекте здесь должна быть проверка лимитов запросов
    return True

def update_request_counter(user_id):
    """
    Обновление счетчика запросов пользователя
    
    Args:
        user_id (int): ID пользователя
    """
    # В реальном проекте здесь должно быть обновление счетчика в базе данных
    pass

def get_user_settings(user_id):
    """
    Получение настроек пользователя
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        dict: Настройки пользователя
    """
    # Импортируем здесь, чтобы избежать циклических импортов
    from app.db.database import get_db, get_user_settings as db_get_user_settings
    
    # Получаем настройки из базы данных
    db = get_db()
    settings = db_get_user_settings(db, user_id)
    
    # Преобразуем объект настроек в словарь
    return {
        'tts_engine': settings.tts_engine,
        'voice_type': settings.voice_type,
        'language': settings.language,
        'audio_format': settings.audio_format
    }

def cancel_task(task_id):
    """
    Отмена задачи
    
    Args:
        task_id (str): ID задачи
        
    Returns:
        bool: True, если задача успешно отменена, иначе False
    """
    global task_queue
    
    for i, task in enumerate(task_queue):
        if task['id'] == task_id:
            task_queue.pop(i)
            logger.info(f"Задача {task_id} отменена")
            return True
    
    return False
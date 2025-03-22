"""
Обработчик команды /cancel и callback-запросов для отмены и подтверждения задач
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import config
from app.db.database import get_db, get_user_settings, update_task_status, get_user_tasks
from app.utils.queue_manager import add_to_queue, get_queue_position, can_make_request, update_request_counter, cancel_task
from app.utils.text_splitter import split_text
from app.utils.tts_converter import convert_text_to_speech
from app.utils.audio_processor import process_audio
import os
import logging

logger = logging.getLogger(__name__)

def cancel_command(update: Update, context: CallbackContext):
    """
    Обработчик команды /cancel
    
    Args:
        update (Update): Объект обновления Telegram
        context (CallbackContext): Контекст обработчика
    """
    user = update.effective_user
    
    # Получаем сессию базы данных
    db = get_db()
    
    # Получаем активные задачи пользователя
    tasks = get_user_tasks(db, user.id, status='processing')
    pending_tasks = get_user_tasks(db, user.id, status='pending')
    tasks.extend(pending_tasks)
    
    if not tasks:
        # Если нет активных задач, отправляем сообщение
        update.message.reply_text(
            "У вас нет активных задач для отмены."
        )
        return
    
    if len(tasks) == 1:
        # Если только одна активная задача, отменяем ее
        task = tasks[0]
        success = cancel_task(task.task_id)
        
        if success:
            update.message.reply_text(
                f"Задача успешно отменена."
            )
        else:
            update.message.reply_text(
                "Не удалось отменить задачу. Возможно, она уже завершена."
            )
    else:
        # Если несколько активных задач, предлагаем выбрать
        show_cancel_menu(update, context, tasks)
    
    # Логируем действие
    # Функция add_log отсутствует в database.py, поэтому закомментируем эту строку
    # add_log(db, user.id, "cancel", "Пользователь отменил задачу")

def show_cancel_menu(update: Update, context: CallbackContext, tasks):
    """
    Показывает меню отмены задач
    
    Args:
        update (Update): Объект обновления Telegram
        context (CallbackContext): Контекст обработчика
        tasks (list): Список задач
    """
    # Создаем клавиатуру с кнопками
    keyboard = []
    for task in tasks:
        task_info = f"Задача {task['task_id'][:8]}... "
        if task['file_name']:
            task_info += f"(Файл: {task['file_name']})"
        else:
            task_info += f"(Текст: {task['text_length']} символов)"
        
        keyboard.append([InlineKeyboardButton(
            task_info,
            callback_data=f"cancel_task_{task['task_id']}"
        )])
    keyboard.append([InlineKeyboardButton("Отменить все", callback_data="cancel_all")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с выбором задачи для отмены
    update.message.reply_text(
        "Выберите задачу для отмены:",
        reply_markup=reply_markup
    )

def cancel_callback(update: Update, context: CallbackContext):
    """
    Обработчик колбэков на кнопки отмены задач и подтверждения обработки
    
    Args:
        update (Update): Объект обновления Telegram
        context (CallbackContext): Контекст обработчика
    """
    query = update.callback_query
    query.answer()
    
    user = query.from_user
    data = query.data
    
    if data.startswith("cancel_task_"):
        # Отменяем выбранную задачу
        task_id = data.replace("cancel_task_", "")
        success = cancel_task(task_id)
        
        if success:
            query.edit_message_text(
                f"Задача успешно отменена."
            )
        else:
            query.edit_message_text(
                "Не удалось отменить задачу. Возможно, она уже завершена."
            )
    
    elif data == "cancel_all":
        # Получаем сессию базы данных
        db = get_db()
        
        # Отменяем все задачи пользователя
        tasks = get_user_tasks(db, user.id, status='processing')
        pending_tasks = get_user_tasks(db, user.id, status='pending')
        tasks.extend(pending_tasks)
        
        canceled_count = 0
        for task in tasks:
            if cancel_task(task.task_id):
                canceled_count += 1
        
        query.edit_message_text(
            f"Отменено задач: {canceled_count} из {len(tasks)}."
        )
    
    elif data == "cancel_processing":
        # Отмена обработки длинного текста
        if "pending_text" in context.user_data:
            del context.user_data["pending_text"]
            query.edit_message_text(
                "Обработка текста отменена."
            )
        else:
            query.edit_message_text(
                "Нет текста для обработки."
            )
    
    elif data == "confirm_processing":
        # Подтверждение обработки длинного текста
        if "pending_text" not in context.user_data:
            query.edit_message_text(
                "Нет текста для обработки."
            )
            return
        
        text = context.user_data["pending_text"]
        del context.user_data["pending_text"]
        
        query.edit_message_text(
            "Начинаю обработку текста..."
        )
        
        # Добавление задачи в очередь
        task_id = add_to_queue(user.id, text, "text")
        position = get_queue_position(task_id)
        
        if position > 0:
            query.message.reply_text(
                f"Ваш запрос добавлен в очередь (позиция: {position}). "
                f"Вы получите уведомление, когда обработка начнется."
            )
        else:
            # Обновление счетчика запросов
            update_request_counter(user.id)
            
            # Получение настроек пользователя из базы данных
            db = get_db()
            user_settings_obj = get_user_settings(db, user.id)
            user_settings = {
                'tts_engine': user_settings_obj.tts_engine,
                'voice_type': user_settings_obj.voice_type,
                'language': user_settings_obj.language,
                'audio_format': user_settings_obj.audio_format
            }
            
            # Разбиение текста на части
            text_parts = split_text(text)
            
            # Конвертация текста в аудио
            audio_files = []
            for i, part in enumerate(text_parts):
                part_label = f"Часть {i+1} из {len(text_parts)}" if len(text_parts) > 1 else None
                audio_file = convert_text_to_speech(
                    part, 
                    language=user_settings.get("language", config.DEFAULT_LANGUAGE),
                    voice_type=user_settings.get("voice_type", config.DEFAULT_VOICE_TYPE),
                    tts_engine=user_settings.get("tts_engine", config.DEFAULT_TTS_ENGINE)
                )
                
                # Обработка аудиофайла (форматирование, добавление метаданных)
                processed_audio = process_audio(
                    audio_file,
                    title=part_label,
                    output_format=user_settings.get("audio_format", config.DEFAULT_AUDIO_FORMAT)
                )
                audio_files.append(processed_audio)
            
            # Отправка аудиофайлов пользователю
            for audio_file in audio_files:
                with open(audio_file, "rb") as audio:
                    query.message.reply_audio(
                        audio=audio,
                        title=f"Аудиокнига {audio_files.index(audio_file) + 1}/{len(audio_files)}"
                    )
                
                # Удаление временного файла
                os.remove(audio_file)
            
            query.message.reply_text("Обработка завершена!")
    
    # Логируем действие
    # Функция add_log отсутствует в database.py, поэтому закомментируем эту строку
    # action = "cancel" if data.startswith("cancel") else "confirm"
    # add_log(db, user.id, action, f"Пользователь выполнил действие: {data}")
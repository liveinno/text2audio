"""
Обработчик текстовых сообщений и файлов
"""
import os
import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
import config
from app.utils.file_processor import process_file, is_supported_file
from app.utils.text_splitter import split_text
from app.utils.lang_detector import detect_language
from app.utils.queue_manager import add_to_queue, get_queue_position, is_queue_full, can_make_request, update_request_counter, get_user_settings
from app.utils.tts_converter import convert_text_to_speech
from app.utils.audio_processor import process_audio
from app.db.database import get_db, get_user_settings as db_get_user_settings

logger = logging.getLogger(__name__)

def process_text(update: Update, context: CallbackContext):
    """
    Обработка текстовых сообщений
    """
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверка ограничений по количеству запросов
    if not can_make_request(user_id):
        update.message.reply_text(
            "Вы превысили лимит запросов. Попробуйте повторить попытку позже."
        )
        return
    
    # Проверка длины текста
    if len(text) > config.MAX_TEXT_LENGTH:
        update.message.reply_text(
            f"Текст слишком длинный (превышает {config.MAX_TEXT_LENGTH} символов). "
            "Пожалуйста, разделите его на несколько частей."
        )
        return
    
    # Проверка очереди
    if is_queue_full():
        update.message.reply_text(
            "Сервис временно загружен. Пожалуйста, повторите запрос через несколько минут."
        )
        return
    
    # Определение языка текста
    language, confidence = detect_language(text)
    
    # Если язык не определен с достаточной уверенностью
    if confidence < config.LANGUAGE_CONFIDENCE_THRESHOLD:
        keyboard = [
            [{"text": lang, "callback_data": f"settings_language_{lang}"} for lang in config.SUPPORTED_LANGUAGES[:3]],
            [{"text": lang, "callback_data": f"settings_language_{lang}"} for lang in config.SUPPORTED_LANGUAGES[3:]]
        ]
        update.message.reply_text(
            "Не удалось однозначно определить язык текста. Пожалуйста, выберите язык вручную:",
            reply_markup={"inline_keyboard": keyboard}
        )
        # Сохраняем текст в контексте для последующей обработки
        context.user_data["pending_text"] = text
        return
    
    # Расчет предполагаемого времени обработки
    estimated_time = len(text) / config.CHARS_PER_MINUTE_PROCESSING
    
    # Если время обработки превышает порог
    if estimated_time > config.LONG_PROCESSING_THRESHOLD_MINUTES:
        keyboard = [
            [
                {"text": "Подтвердить", "callback_data": "confirm_processing"},
                {"text": "Отмена", "callback_data": "cancel_processing"}
            ]
        ]
        update.message.reply_text(
            f"Обнаружен очень большой объём текста. Предварительная оценка времени обработки "
            f"составляет примерно {int(estimated_time)} минут. Продолжить обработку?",
            reply_markup={"inline_keyboard": keyboard}
        )
        # Сохраняем текст в контексте для последующей обработки
        context.user_data["pending_text"] = text
        return
    
    # Добавление задачи в очередь
    task_id = add_to_queue(user_id, text, "text")
    position = get_queue_position(task_id)
    
    if position > 0:
        update.message.reply_text(
            f"Ваш запрос добавлен в очередь (позиция: {position}). "
            f"Вы получите уведомление, когда обработка начнется."
        )
    else:
        update.message.reply_text("Начинаю обработку текста...")
        
        # Обновление счетчика запросов
        update_request_counter(user_id)
        
        # Получение настроек пользователя из базы данных
        db = get_db()
        user_settings_obj = db_get_user_settings(db, user_id)
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
                update.message.reply_audio(
                    audio=audio,
                    title=f"Аудиокнига {audio_files.index(audio_file) + 1}/{len(audio_files)}"
                )
            
            # Удаление временного файла
            os.remove(audio_file)
        
        update.message.reply_text("Обработка завершена!")

def process_document(update: Update, context: CallbackContext):
    """
    Обработка документов (файлов)
    """
    user_id = update.effective_user.id
    document = update.message.document
    
    # Проверка ограничений по количеству запросов
    if not can_make_request(user_id):
        update.message.reply_text(
            "Вы превысили лимит запросов. Попробуйте повторить попытку позже."
        )
        return
    
    # Проверка размера файла
    if document.file_size > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        update.message.reply_text(
            f"Файл слишком большой (превышает {config.MAX_FILE_SIZE_MB} МБ). "
            "Пожалуйста, загрузите файл меньшего размера."
        )
        return
    
    # Проверка формата файла
    file_name = document.file_name
    if not is_supported_file(file_name):
        update.message.reply_text(
            "Неподдерживаемый формат файла. Пожалуйста, используйте форматы .txt или .docx."
        )
        return
    
    # Проверка очереди
    if is_queue_full():
        update.message.reply_text(
            "Сервис временно загружен. Пожалуйста, повторите запрос через несколько минут."
        )
        return
    
    # Скачивание файла
    file = context.bot.get_file(document.file_id)
    file_path = os.path.join(config.TEMP_DIR, file_name)
    file.download(file_path)
    
    # Обработка файла и извлечение текста
    try:
        text = process_file(file_path)
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        update.message.reply_text(
            "Не удалось конвертировать файл. Пожалуйста, проверьте исходный документ или используйте формат .docx."
        )
        # Удаление временного файла
        os.remove(file_path)
        return
    
    # Проверка длины текста
    if len(text) > config.MAX_TEXT_LENGTH:
        update.message.reply_text(
            f"Текст в файле слишком длинный (превышает {config.MAX_TEXT_LENGTH} символов). "
            "Пожалуйста, разделите его на несколько частей."
        )
        # Удаление временного файла
        os.remove(file_path)
        return
    
    # Определение языка текста
    language, confidence = detect_language(text)
    
    # Если язык не определен с достаточной уверенностью
    if confidence < config.LANGUAGE_CONFIDENCE_THRESHOLD:
        keyboard = [
            [{"text": lang, "callback_data": f"settings_language_{lang}"} for lang in config.SUPPORTED_LANGUAGES[:3]],
            [{"text": lang, "callback_data": f"settings_language_{lang}"} for lang in config.SUPPORTED_LANGUAGES[3:]]
        ]
        update.message.reply_text(
            "Не удалось однозначно определить язык текста. Пожалуйста, выберите язык вручную:",
            reply_markup={"inline_keyboard": keyboard}
        )
        # Сохраняем текст в контексте для последующей обработки
        context.user_data["pending_text"] = text
        # Удаление временного файла
        os.remove(file_path)
        return
    
    # Расчет предполагаемого времени обработки
    estimated_time = len(text) / config.CHARS_PER_MINUTE_PROCESSING
    
    # Если время обработки превышает порог
    if estimated_time > config.LONG_PROCESSING_THRESHOLD_MINUTES:
        keyboard = [
            [
                {"text": "Подтвердить", "callback_data": "confirm_processing"},
                {"text": "Отмена", "callback_data": "cancel_processing"}
            ]
        ]
        update.message.reply_text(
            f"Обнаружен очень большой объём текста. Предварительная оценка времени обработки "
            f"составляет примерно {int(estimated_time)} минут. Продолжить обработку?",
            reply_markup={"inline_keyboard": keyboard}
        )
        # Сохраняем текст в контексте для последующей обработки
        context.user_data["pending_text"] = text
        # Удаление временного файла
        os.remove(file_path)
        return
    
    # Добавление задачи в очередь
    task_id = add_to_queue(user_id, text, "file")
    position = get_queue_position(task_id)
    
    if position > 0:
        update.message.reply_text(
            f"Ваш запрос добавлен в очередь (позиция: {position}). "
            f"Вы получите уведомление, когда обработка начнется."
        )
    else:
        update.message.reply_text("Начинаю обработку файла...")
        
        # Обновление счетчика запросов
        update_request_counter(user_id)
        
        # Получение настроек пользователя из базы данных
        db = get_db()
        user_settings_obj = db_get_user_settings(db, user_id)
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
                update.message.reply_audio(
                    audio=audio,
                    title=f"Аудиокнига {audio_files.index(audio_file) + 1}/{len(audio_files)}"
                )
            
            # Удаление временного файла
            os.remove(audio_file)
        
        # Удаление исходного файла
        os.remove(file_path)
        
        update.message.reply_text("Обработка завершена!")
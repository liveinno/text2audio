#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной модуль бота для конвертации текста в аудиокниги
"""
import logging
import threading
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import config
from app.handlers import (
    start_command,
    help_command,
    settings_command,
    settings_callback,
    reset_command,
    cancel_command,
    cancel_callback,
    process_text,
    process_document
)
from app.db.database import init_db, get_db, get_user_settings
from app.utils.queue_manager import task_queue, cancel_task
from app.utils.tts_converter import convert_text_to_speech
from app.utils.audio_processor import process_audio
import os

# Создаем директорию для логов
os.makedirs("logs", exist_ok=True)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
    level=logging.DEBUG,
    filename='logs/bot.log',
    filemode='a'
)

logger = logging.getLogger(__name__)

def process_queue(updater):
    """
    Обработка задач из очереди
    
    Args:
        updater (Updater): Экземпляр Updater для отправки сообщений
    """
    logger.debug("Запуск функции process_queue")
    while True:
        try:
            # Логируем состояние очереди
            logger.debug(f"Текущее состояние очереди: {len(task_queue)} задач")
            
            # Если очередь не пуста
            if task_queue:
                # Получаем первую задачу
                task = task_queue[0]
                
                # Логируем начало обработки
                logger.info(f"Начало обработки задачи {task['id']} для пользователя {task['user_id']}")
                logger.debug(f"Содержимое задачи: {task}")
                
                # Получаем настройки пользователя
                db = get_db()
                logger.debug(f"База данных получена: {db}")
                
                user_settings_obj = get_user_settings(db, task['user_id'])
                logger.debug(f"Настройки пользователя получены: {user_settings_obj}")
                
                user_settings = {
                    'tts_engine': user_settings_obj.tts_engine,
                    'voice_type': user_settings_obj.voice_type,
                    'language': user_settings_obj.language,
                    'audio_format': user_settings_obj.audio_format
                }
                logger.debug(f"Настройки пользователя преобразованы: {user_settings}")
                
                try:
                    # Конвертируем текст в речь
                    logger.debug(f"Начинаем конвертацию текста в речь для задачи {task['id']}")
                    logger.debug(f"Параметры конвертации: язык={user_settings['language']}, тип голоса={user_settings['voice_type']}, движок={user_settings['tts_engine']}, формат={user_settings['audio_format']}")
                    
                    audio_file = convert_text_to_speech(
                        task['text'],
                        language=user_settings['language'],
                        voice_type=user_settings['voice_type'],
                        tts_engine=user_settings['tts_engine'],
                        audio_format=user_settings['audio_format']
                    )
                    
                    # Проверяем, что аудиофайл был успешно создан
                    if audio_file is None:
                        logger.error(f"Не удалось конвертировать текст в речь для задачи {task['id']}")
                        updater.bot.send_message(
                            chat_id=task['user_id'],
                            text="Произошла ошибка при конвертации текста в речь. Пожалуйста, попробуйте еще раз."
                        )
                        continue
                    
                    # Обрабатываем аудиофайл
                    logger.debug(f"Начинаем обработку аудиофайла для задачи {task['id']}")
                    
                    processed_audio = process_audio(
                        audio_file,
                        title=f"Аудиокнига {task['id']}",
                        output_format=user_settings['audio_format']
                    )
                    
                    # Проверяем, что аудиофайл был успешно обработан
                    if processed_audio is None:
                        logger.error(f"Не удалось обработать аудиофайл для задачи {task['id']}")
                        updater.bot.send_message(
                            chat_id=task['user_id'],
                            text="Произошла ошибка при обработке аудиофайла. Пожалуйста, попробуйте еще раз."
                        )
                        # Удаляем исходный аудиофайл, если он существует
                        if os.path.exists(audio_file):
                            try:
                                os.remove(audio_file)
                                logger.debug(f"Исходный аудиофайл {audio_file} удален")
                            except Exception as e:
                                logger.error(f"Ошибка при удалении исходного аудиофайла {audio_file}: {e}")
                        continue
                    
                    # Отправляем аудиофайл пользователю
                    logger.debug(f"Начинаем отправку аудиофайла пользователю {task['user_id']}")
                    
                    # Проверяем, что файл существует и не содержит ':Zone.Identifier'
                    if os.path.exists(processed_audio) and ':Zone.Identifier' not in processed_audio:
                        try:
                            with open(processed_audio, 'rb') as audio:
                                updater.bot.send_audio(
                                    chat_id=task['user_id'],
                                    audio=audio,
                                    caption="Ваш текст был успешно преобразован в аудио!"
                                )
                            logger.debug(f"Аудиофайл успешно отправлен пользователю {task['user_id']}")
                            
                            # Удаляем временные файлы
                            try:
                                # Удаляем обработанный аудиофайл
                                if os.path.exists(processed_audio):
                                    os.remove(processed_audio)
                                    logger.debug(f"Обработанный аудиофайл {processed_audio} удален")
                                
                                # Удаляем исходный аудиофайл
                                if os.path.exists(audio_file):
                                    os.remove(audio_file)
                                    logger.debug(f"Исходный аудиофайл {audio_file} удален")
                            except Exception as e:
                                logger.error(f"Ошибка при удалении временных файлов: {e}")
                                
                        except Exception as e:
                            logger.error(f"Ошибка при отправке аудиофайла: {e}")
                            updater.bot.send_message(
                                chat_id=task['user_id'],
                                text=f"Произошла ошибка при отправке аудиофайла: {str(e)}"
                            )
                            
                            # Удаляем временные файлы в случае ошибки
                            try:
                                if os.path.exists(processed_audio):
                                    os.remove(processed_audio)
                                if os.path.exists(audio_file):
                                    os.remove(audio_file)
                            except Exception as e:
                                logger.error(f"Ошибка при удалении временных файлов: {e}")
                    else:
                        logger.error(f"Файл {processed_audio} не существует или имеет неверный формат")
                        updater.bot.send_message(
                            chat_id=task['user_id'],
                            text="Произошла ошибка при обработке аудиофайла. Пожалуйста, попробуйте еще раз."
                        )
                        
                        # Удаляем исходный аудиофайл, если он существует
                        try:
                            if os.path.exists(audio_file):
                                os.remove(audio_file)
                                logger.debug(f"Исходный аудиофайл {audio_file} удален")
                        except Exception as e:
                            logger.error(f"Ошибка при удалении исходного аудиофайла: {e}")
                    
                    # Логируем успешное завершение
                    logger.info(f"Задача {task['id']} для пользователя {task['user_id']} успешно обработана")
                    
                except Exception as e:
                    # В случае ошибки отправляем сообщение пользователю
                    logger.debug(f"Произошла ошибка при обработке задачи {task['id']}: {e}")
                    logger.debug(f"Трассировка стека: ", exc_info=True)
                    
                    updater.bot.send_message(
                        chat_id=task['user_id'],
                        text=f"Произошла ошибка при обработке вашего текста: {str(e)}"
                    )
                    
                    # Логируем ошибку
                    logger.error(f"Ошибка при обработке задачи {task['id']}: {e}")
                
                finally:
                    # Удаляем задачу из очереди
                    logger.debug(f"Удаляем задачу {task['id']} из очереди")
                    task_queue.pop(0)
                    logger.debug(f"Задача {task['id']} удалена из очереди")
            else:
                # Если очередь пуста, логируем это
                logger.debug("Очередь пуста, ожидаем новые задачи")
            
            # Пауза между проверками очереди
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике очереди: {e}")
            logger.debug(f"Трассировка стека: ", exc_info=True)
            time.sleep(5)  # Пауза в случае ошибки

def clean_temp_directory():
    """
    Очистка временной директории от всех файлов
    """
    logger.info("Очистка временной директории")
    try:
        # Проверяем, что директория существует
        if os.path.exists(config.TEMP_DIR):
            # Получаем список файлов в директории
            files = os.listdir(config.TEMP_DIR)
            # Удаляем все файлы, кроме .gitkeep
            for file in files:
                if file != '.gitkeep':
                    file_path = os.path.join(config.TEMP_DIR, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            logger.debug(f"Удален файл: {file_path}")
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла {file_path}: {e}")
        logger.info("Очистка временной директории завершена")
    except Exception as e:
        logger.error(f"Ошибка при очистке временной директории: {e}")

def main():
    """
    Основная функция запуска бота
    """
    # Создаем директорию для базы данных
    os.makedirs("db", exist_ok=True)
    
    # Очистка временной директории от служебных файлов
    clean_temp_directory()
    
    # Инициализация базы данных
    init_db()
    
    # Создание экземпляра Updater и передача ему токена бота
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    
    # Получение диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher
    
    # Регистрация обработчиков команд
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("settings", settings_command))
    dispatcher.add_handler(CommandHandler("reset", reset_command))
    dispatcher.add_handler(CommandHandler("cancel", cancel_command))
    
    # Регистрация обработчиков callback-запросов
    dispatcher.add_handler(CallbackQueryHandler(settings_callback, pattern=r'^(settings_|set_)'))
    dispatcher.add_handler(CallbackQueryHandler(cancel_callback, pattern=r'^(cancel|confirm)_'))
    
    # Регистрация обработчиков сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_text))
    dispatcher.add_handler(MessageHandler(Filters.document, process_document))
    
    # Запуск бота
    updater.start_polling()
    
    # Запуск обработчика очереди в отдельном потоке
    queue_thread = threading.Thread(target=process_queue, args=(updater,))
    queue_thread.daemon = True
    queue_thread.start()
    
    # Логируем запуск обработчика очереди
    logger.info("Обработчик очереди запущен")
    
    # Остановка бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
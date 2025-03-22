"""
Обработчик команды /reset
"""
from telegram import Update
from telegram.ext import CallbackContext
from app.db.database import get_db, reset_user_settings, get_user_settings
from app.handlers.settings_handler import (
    TTS_ENGINE_NAMES, VOICE_TYPE_NAMES, LANGUAGE_NAMES, AUDIO_FORMAT_NAMES
)

def reset_command(update: Update, context: CallbackContext):
    """
    Обработчик команды /reset
    
    Args:
        update (Update): Объект обновления Telegram
        context (CallbackContext): Контекст обработчика
    """
    user = update.effective_user
    
    # Получаем сессию базы данных
    db = get_db()
    
    # Сбрасываем настройки пользователя к значениям по умолчанию
    reset_user_settings(db, user.id)
    
    # Получаем обновленные настройки
    settings = get_user_settings(db, user.id)
    
    # Отправляем сообщение об успешном сбросе настроек
    update.message.reply_text(
        "✅ Настройки успешно сброшены к значениям по умолчанию!\n\n"
        f"TTS-движок: {TTS_ENGINE_NAMES.get(settings.tts_engine, settings.tts_engine)}\n"
        f"Тип голоса: {VOICE_TYPE_NAMES.get(settings.voice_type, settings.voice_type)}\n"
        f"Язык: {LANGUAGE_NAMES.get(settings.language, settings.language)}\n"
        f"Формат аудио: {AUDIO_FORMAT_NAMES.get(settings.audio_format, settings.audio_format)}\n\n"
        "Теперь вы можете отправить мне текст или файл для озвучивания."
    )
    
    # Логируем событие
    # Функция add_log отсутствует в database.py, поэтому закомментируем эту строку
    # add_log(db, user.id, "reset", "Пользователь сбросил настройки")
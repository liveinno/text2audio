"""
Обработчик команды настроек
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import DEFAULT_TTS_ENGINE, DEFAULT_VOICE_TYPE, DEFAULT_LANGUAGE, DEFAULT_AUDIO_FORMAT
from app.db.database import get_db, get_user_settings as db_get_user_settings, update_user_settings
from app.utils.queue_manager import get_user_settings

logger = logging.getLogger(__name__)

# Константы для настроек
TTS_ENGINE_NAMES = {
    'gtts': 'Google TTS (онлайн)',
    'pyttsx3': 'pyttsx3 (оффлайн, высокое качество)',
    'espeak': 'eSpeak (оффлайн)',
    'festival': 'Festival (оффлайн)'
}

VOICE_TYPE_NAMES = {
    'male': 'Мужской',
    'female': 'Женский'
}

LANGUAGE_NAMES = {
    'ru': 'Русский',
    'en': 'Английский',
    'fr': 'Французский',
    'de': 'Немецкий',
    'es': 'Испанский',
    'it': 'Итальянский'
}

AUDIO_FORMAT_NAMES = {
    'mp3': 'MP3',
    'ogg': 'OGG'
}

def settings_command(update: Update, context: CallbackContext):
    """
    Обработчик команды /settings
    """
    user_id = update.effective_user.id
    
    # Получение настроек пользователя из базы данных
    db = get_db()
    user_settings = db_get_user_settings(db, user_id)
    
    # Создание клавиатуры
    keyboard = [
        [
            InlineKeyboardButton("TTS движок", callback_data="settings_tts_engine"),
            InlineKeyboardButton("Тип голоса", callback_data="settings_voice_type")
        ],
        [
            InlineKeyboardButton("Язык", callback_data="settings_language"),
            InlineKeyboardButton("Формат аудио", callback_data="settings_audio_format")
        ],
        [
            InlineKeyboardButton("Сбросить настройки", callback_data="settings_reset")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Формирование текста сообщения
    tts_engine_name = TTS_ENGINE_NAMES.get(user_settings.tts_engine, DEFAULT_TTS_ENGINE)
    voice_type_name = VOICE_TYPE_NAMES.get(user_settings.voice_type, DEFAULT_VOICE_TYPE)
    language_name = LANGUAGE_NAMES.get(user_settings.language, DEFAULT_LANGUAGE)
    audio_format_name = AUDIO_FORMAT_NAMES.get(user_settings.audio_format, DEFAULT_AUDIO_FORMAT)
    
    message = f"""
*Текущие настройки:*

🔊 *TTS движок:* {tts_engine_name}
🗣 *Тип голоса:* {voice_type_name}
🌐 *Язык:* {language_name}
🎵 *Формат аудио:* {audio_format_name}

Выберите настройку для изменения:
"""
    
    # Отправка сообщения
    update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def settings_callback(update: Update, context: CallbackContext):
    """
    Обработчик колбэков от кнопок настроек
    """
    query = update.callback_query
    query.answer()
    
    # Получение данных колбэка
    callback_data = query.data
    
    # Обработка колбэка
    if callback_data == "settings_tts_engine":
        show_tts_engine_settings(update, context)
    elif callback_data == "settings_voice_type":
        show_voice_type_settings(update, context)
    elif callback_data == "settings_language":
        show_language_settings(update, context)
    elif callback_data == "settings_audio_format":
        show_audio_format_settings(update, context)
    elif callback_data == "settings_reset":
        reset_settings(update, context)
    elif callback_data.startswith("set_tts_engine_"):
        set_tts_engine(update, context, callback_data.replace("set_tts_engine_", ""))
    elif callback_data.startswith("set_voice_type_"):
        set_voice_type(update, context, callback_data.replace("set_voice_type_", ""))
    elif callback_data.startswith("set_language_"):
        set_language(update, context, callback_data.replace("set_language_", ""))
    elif callback_data.startswith("set_audio_format_"):
        set_audio_format(update, context, callback_data.replace("set_audio_format_", ""))
    elif callback_data == "settings_back":
        show_settings_menu(update, context)

def show_tts_engine_settings(update: Update, context: CallbackContext):
    """
    Показать настройки TTS движка
    """
    query = update.callback_query
    
    # Создание клавиатуры
    keyboard = []
    for engine, name in TTS_ENGINE_NAMES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_tts_engine_{engine}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data="settings_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Обновление сообщения
    query.edit_message_text(
        "Выберите TTS движок:",
        reply_markup=reply_markup
    )

def show_voice_type_settings(update: Update, context: CallbackContext):
    """
    Показать настройки типа голоса
    """
    query = update.callback_query
    
    # Создание клавиатуры
    keyboard = []
    for voice_type, name in VOICE_TYPE_NAMES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_voice_type_{voice_type}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data="settings_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Обновление сообщения
    query.edit_message_text(
        "Выберите тип голоса:",
        reply_markup=reply_markup
    )

def show_language_settings(update: Update, context: CallbackContext):
    """
    Показать настройки языка
    """
    query = update.callback_query
    
    # Создание клавиатуры
    keyboard = []
    for language, name in LANGUAGE_NAMES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_language_{language}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data="settings_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Обновление сообщения
    query.edit_message_text(
        "Выберите язык:",
        reply_markup=reply_markup
    )

def show_audio_format_settings(update: Update, context: CallbackContext):
    """
    Показать настройки формата аудио
    """
    query = update.callback_query
    
    # Создание клавиатуры
    keyboard = []
    for audio_format, name in AUDIO_FORMAT_NAMES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_audio_format_{audio_format}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data="settings_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Обновление сообщения
    query.edit_message_text(
        "Выберите формат аудио:",
        reply_markup=reply_markup
    )

def show_settings_menu(update: Update, context: CallbackContext):
    """
    Показать основное меню настроек
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Получение настроек пользователя
    db = get_db()
    user_settings = db_get_user_settings(db, user_id)
    
    # Создание клавиатуры
    keyboard = [
        [
            InlineKeyboardButton("TTS движок", callback_data="settings_tts_engine"),
            InlineKeyboardButton("Тип голоса", callback_data="settings_voice_type")
        ],
        [
            InlineKeyboardButton("Язык", callback_data="settings_language"),
            InlineKeyboardButton("Формат аудио", callback_data="settings_audio_format")
        ],
        [
            InlineKeyboardButton("Сбросить настройки", callback_data="settings_reset")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Формирование текста сообщения
    tts_engine_name = TTS_ENGINE_NAMES.get(user_settings.tts_engine, DEFAULT_TTS_ENGINE)
    voice_type_name = VOICE_TYPE_NAMES.get(user_settings.voice_type, DEFAULT_VOICE_TYPE)
    language_name = LANGUAGE_NAMES.get(user_settings.language, DEFAULT_LANGUAGE)
    audio_format_name = AUDIO_FORMAT_NAMES.get(user_settings.audio_format, DEFAULT_AUDIO_FORMAT)
    
    message = f"""
*Текущие настройки:*

🔊 *TTS движок:* {tts_engine_name}
🗣 *Тип голоса:* {voice_type_name}
🌐 *Язык:* {language_name}
🎵 *Формат аудио:* {audio_format_name}

Выберите настройку для изменения:
"""
    
    # Обновление сообщения
    query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def set_tts_engine(update: Update, context: CallbackContext, tts_engine):
    """
    Установка TTS движка
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Обновление настроек пользователя
    db = get_db()
    update_user_settings(db, user_id, tts_engine=tts_engine)
    
    # Возврат к основным настройкам
    show_settings_menu(update, context)

def set_voice_type(update: Update, context: CallbackContext, voice_type):
    """
    Установка типа голоса
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Обновление настроек пользователя
    db = get_db()
    update_user_settings(db, user_id, voice_type=voice_type)
    
    # Возврат к основным настройкам
    show_settings_menu(update, context)

def set_language(update: Update, context: CallbackContext, language):
    """
    Установка языка
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Обновление настроек пользователя
    db = get_db()
    update_user_settings(db, user_id, language=language)
    
    # Возврат к основным настройкам
    show_settings_menu(update, context)

def set_audio_format(update: Update, context: CallbackContext, audio_format):
    """
    Установка формата аудио
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Обновление настроек пользователя
    db = get_db()
    update_user_settings(db, user_id, audio_format=audio_format)
    
    # Возврат к основным настройкам
    show_settings_menu(update, context)

def reset_settings(update: Update, context: CallbackContext):
    """
    Сброс настроек
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Сброс настроек пользователя
    db = get_db()
    update_user_settings(db, user_id, 
                        tts_engine=DEFAULT_TTS_ENGINE,
                        voice_type=DEFAULT_VOICE_TYPE,
                        language=DEFAULT_LANGUAGE,
                        audio_format=DEFAULT_AUDIO_FORMAT)
    
    # Возврат к основным настройкам
    show_settings_menu(update, context)
"""
Обработчик команды /start
"""
import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def start_command(update: Update, context: CallbackContext):
    """
    Обработчик команды /start
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Приветственное сообщение
    welcome_message = f"""
Привет, {user.first_name}! 👋

Я бот для конвертации текста в аудиокниги. Отправь мне текст или документ, и я преобразую его в аудио.

*Основные команды:*
/start - Показать это сообщение
/help - Получить справку
/settings - Настройки конвертации

*Поддерживаемые форматы документов:*
- TXT (текстовые файлы)
- DOCX (документы Word)
- PDF (PDF-документы)

*Как пользоваться:*
1. Отправь мне текст сообщением
2. Или отправь документ в поддерживаемом формате
3. Дождись завершения конвертации
4. Получи аудиофайл

Настрой параметры конвертации с помощью команды /settings
"""
    
    # Отправляем приветственное сообщение
    update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")
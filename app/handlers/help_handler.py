"""
Обработчик команды /help
"""
import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def help_command(update: Update, context: CallbackContext):
    """
    Обработчик команды /help
    """
    user = update.effective_user
    
    # Справочное сообщение
    help_message = """
*Справка по использованию бота*

*Основные команды:*
/start - Начать работу с ботом
/help - Показать эту справку
/settings - Настройки конвертации

*Возможности бота:*
• Конвертация текста в аудио
• Конвертация документов в аудио
• Настройка параметров конвертации

*Поддерживаемые форматы документов:*
• TXT - текстовые файлы
• DOCX - документы Microsoft Word
• PDF - документы PDF

*Ограничения:*
• Максимальный размер текста: 4000 символов
• Максимальный размер файла: 20 МБ

*Как пользоваться:*
1. Отправьте текст сообщением или загрузите документ
2. Бот автоматически определит язык текста
3. Текст будет преобразован в аудио с учетом ваших настроек
4. Вы получите аудиофайл, который можно прослушать или скачать

*Настройки:*
Используйте команду /settings для настройки параметров конвертации:
• Язык текста
• Тип голоса (мужской/женский)
• Формат аудио (MP3/OGG)

*Проблемы и ошибки:*
Если возникли проблемы, попробуйте:
• Проверить формат и размер файла
• Убедиться, что текст не содержит специальных символов
• Перезапустить бота командой /start
"""
    
    # Отправляем справочное сообщение
    update.message.reply_text(
        help_message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"Пользователь {user.id} ({user.username}) запросил справку")
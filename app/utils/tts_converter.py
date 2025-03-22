"""
Модуль для конвертации текста в речь
"""
import os
import logging
import uuid
import gtts
import subprocess
from config import (
    DEFAULT_TTS_ENGINE, DEFAULT_VOICE_TYPE, DEFAULT_LANGUAGE,
    DEFAULT_AUDIO_FORMAT, TEMP_DIR
)

# Импортируем pyttsx3 с обработкой ошибок
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pyttsx3 не установлен. Некоторые функции будут недоступны.")

logger = logging.getLogger(__name__)

def convert_text_to_speech(text, language=DEFAULT_LANGUAGE, voice_type=DEFAULT_VOICE_TYPE, 
                          tts_engine=DEFAULT_TTS_ENGINE, audio_format=DEFAULT_AUDIO_FORMAT):
    """
    Конвертация текста в речь
    
    Args:
        text (str): Текст для конвертации
        language (str): Язык текста
        voice_type (str): Тип голоса (male/female)
        tts_engine (str): Движок TTS
        audio_format (str): Формат аудио
        
    Returns:
        str: Путь к аудиофайлу
    """
    try:
        # Создаем директорию для временных файлов, если она не существует
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        # Генерируем имя файла
        file_name = f"tts_{uuid.uuid4()}.{audio_format}"
        file_path = os.path.join(TEMP_DIR, file_name)
        
        # Конвертация с помощью выбранного движка
        if tts_engine == 'gtts':
            # Google TTS (онлайн)
            tts = gtts.gTTS(text=text, lang=language, slow=False)
            tts.save(file_path)
            logger.debug(f"Использован движок Google TTS для конвертации текста")
        
        elif tts_engine == 'pyttsx3':
            # pyttsx3 (оффлайн, высокое качество)
            if PYTTSX3_AVAILABLE:
                try:
                    # Пробуем разные драйверы
                    try:
                        # Сначала пробуем без указания драйвера
                        engine = pyttsx3.init()
                    except Exception as e1:
                        logger.warning(f"Ошибка при инициализации без драйвера: {e1}")
                        try:
                            # Пробуем с драйвером espeak
                            engine = pyttsx3.init(driverName="espeak")
                        except Exception as e2:
                            logger.warning(f"Ошибка при инициализации с драйвером espeak: {e2}")
                            try:
                                # Пробуем с драйвером sapi5 (для Windows)
                                engine = pyttsx3.init(driverName="sapi5")
                            except Exception as e3:
                                logger.warning(f"Ошибка при инициализации с драйвером sapi5: {e3}")
                                try:
                                    # Пробуем с драйвером nsss (для macOS)
                                    engine = pyttsx3.init(driverName="nsss")
                                except Exception as e4:
                                    logger.error(f"Ошибка при инициализации с драйвером nsss: {e4}")
                                    logger.error("Не удалось инициализировать pyttsx3 с известными драйверами")
                                    raise Exception("Не удалось инициализировать pyttsx3 с известными драйверами")
                    
                    # Настройка голоса
                    voices = engine.getProperty('voices')
                    
                    # Собираем кандидатов, поддерживающих требуемый язык
                    candidates = []
                    
                    # Для русского языка явно ищем голос "russian"
                    if language == 'ru':
                        for voice in voices:
                            if 'russian' in voice.id.lower() or 'ru' in voice.id.lower():
                                candidates.append(voice)
                                logger.debug(f"Найден русский голос: {voice.id}")
                    
                    # Если русских голосов не нашлось, ищем по стандартному алгоритму
                    if not candidates:
                        for voice in voices:
                            langs = []
                            for lang in voice.languages:
                                if isinstance(lang, bytes):
                                    try:
                                        langs.append(lang.decode('utf-8').lower())
                                    except Exception:
                                        langs.append(str(lang).lower())
                                else:
                                    langs.append(str(lang).lower())
                            
                            # Если хотя бы один язык начинается с требуемого кода (например, "ru")
                            if any(l.startswith(language) for l in langs):
                                candidates.append(voice)
                                logger.debug(f"Найден голос с языком {language}: {voice.id}")
                    
                    selected_voice = None
                    if candidates:
                        if voice_type == 'female':
                            for v in candidates:
                                # Используем voice.name для определения "женщины"
                                v_name = v.name.lower() if hasattr(v, 'name') else ''
                                if ('female' in v_name) or ('zira' in v_name) or ('helena' in v_name):
                                    selected_voice = v.id
                                    logger.debug(f"Найден женский голос для языка {language}: {v.name}")
                                    break
                        elif voice_type == 'male':
                            for v in candidates:
                                v_name = v.name.lower() if hasattr(v, 'name') else ''
                                if ('male' in v_name) or ('david' in v_name) or ('mark' in v_name):
                                    selected_voice = v.id
                                    logger.debug(f"Найден мужской голос для языка {language}: {v.name}")
                                    break
                        
                        # Если нужного пола не найдено, используем первого кандидата
                        if selected_voice is None:
                            selected_voice = candidates[0].id
                            logger.warning(f"Не найден голос для языка {language} и пола {voice_type}, используем первый доступный")
                    else:
                        # Если кандидатов по языку не нашлось, пробуем использовать espeak напрямую
                        logger.warning(f"Не найден голос с языком {language} в pyttsx3, пробуем использовать espeak напрямую")
                        # Закрываем текущий движок pyttsx3
                        engine.stop()
                        
                        try:
                            # Проверяем, установлен ли espeak
                            import subprocess
                            
                            # Определяем параметры для espeak
                            voice_param = f"{language}+f2" if voice_type == "female" else language
                            
                            # Создаем временный текстовый файл
                            temp_text_file = os.path.join(os.path.dirname(file_path), "temp_text.txt")
                            with open(temp_text_file, "w", encoding="utf-8") as f:
                                f.write(text)
                            
                            # Запускаем espeak для конвертации текста в речь
                            cmd = f"espeak -v {voice_param} -f {temp_text_file} -w {file_path}"
                            logger.debug(f"Запуск команды: {cmd}")
                            
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                            
                            # Удаляем временный файл
                            if os.path.exists(temp_text_file):
                                os.remove(temp_text_file)
                            
                            if result.returncode == 0 and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                logger.debug(f"Успешно использован espeak для конвертации текста")
                                return file_path
                            else:
                                logger.warning(f"Ошибка при использовании espeak: {result.stderr}")
                                # Если espeak не сработал, используем fallback на Google TTS
                                logger.warning(f"Используем Google TTS как последний вариант")
                                tts = gtts.gTTS(text=text, lang=language, slow=False)
                                tts.save(file_path)
                                logger.debug(f"Fallback на Google TTS из-за отсутствия подходящего голоса")
                                return file_path
                        except Exception as e:
                            logger.error(f"Ошибка при использовании espeak: {e}")
                            # Fallback на gTTS
                            logger.warning(f"Используем Google TTS как последний вариант")
                            tts = gtts.gTTS(text=text, lang=language, slow=False)
                            tts.save(file_path)
                            logger.debug(f"Fallback на Google TTS из-за ошибки espeak")
                            return file_path
                    
                    # Устанавливаем голос, если нашли
                    if selected_voice:
                        engine.setProperty('voice', selected_voice)
                    
                    # Устанавливаем скорость речи
                    engine.setProperty('rate', 150)  # Нормальная скорость
                    
                    # Сохраняем в файл
                    engine.save_to_file(text, file_path)
                    engine.runAndWait()
                    # Добавляем небольшую задержку перед завершением работы с engine
                    import time
                    time.sleep(0.5)
                    
                    logger.debug(f"Использован движок pyttsx3 для конвертации текста")
                except Exception as e:
                    logger.error(f"Ошибка при использовании pyttsx3: {e}")
                    # Проверяем, был ли создан файл, несмотря на ошибку
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        logger.debug(f"Файл {file_path} был создан, несмотря на ошибку. Используем его.")
                    else:
                        # Fallback на gTTS
                        logger.debug(f"Файл не был создан или пуст. Fallback на Google TTS.")
                        tts = gtts.gTTS(text=text, lang=language, slow=False)
                        tts.save(file_path)
                        logger.debug(f"Fallback на Google TTS из-за ошибки pyttsx3")
            else:
                logger.error("pyttsx3 не установлен, используем Google TTS")
                # Fallback на gTTS
                tts = gtts.gTTS(text=text, lang=language, slow=False)
                tts.save(file_path)
                logger.debug(f"Fallback на Google TTS из-за отсутствия pyttsx3")
        
        elif tts_engine == 'espeak':
            # eSpeak (оффлайн)
            try:
                gender = 'm1' if voice_type == 'male' else 'f2'
                cmd = f"espeak -v{language}+{gender} -w {file_path} \"{text}\""
                subprocess.run(cmd, shell=True, check=True)
                logger.debug(f"Использован движок eSpeak для конвертации текста")
            except Exception as e:
                logger.error(f"Ошибка при использовании eSpeak: {e}")
                # Fallback на gTTS
                tts = gtts.gTTS(text=text, lang=language, slow=False)
                tts.save(file_path)
                logger.debug(f"Fallback на Google TTS из-за ошибки eSpeak")
        
        elif tts_engine == 'festival':
            # Festival (оффлайн)
            try:
                # Создаем временный текстовый файл
                text_file = os.path.join(TEMP_DIR, f"text_{uuid.uuid4()}.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # Конвертируем текст в речь с помощью Festival
                cmd = f"text2wave -o {file_path} {text_file}"
                subprocess.run(cmd, shell=True, check=True)
                
                # Удаляем временный файл
                if os.path.exists(text_file):
                    os.remove(text_file)
                
                logger.debug(f"Использован движок Festival для конвертации текста")
            except Exception as e:
                logger.error(f"Ошибка при использовании Festival: {e}")
                # Fallback на gTTS
                tts = gtts.gTTS(text=text, lang=language, slow=False)
                tts.save(file_path)
                logger.debug(f"Fallback на Google TTS из-за ошибки Festival")
        
        else:
            # Для неизвестных движков используем gTTS
            logger.warning(f"Неизвестный движок TTS: {tts_engine}, используем Google TTS")
            tts = gtts.gTTS(text=text, lang=language, slow=False)
            tts.save(file_path)
            logger.debug(f"Использован движок Google TTS (по умолчанию)")
        
        # Проверяем, что файл был успешно создан
        if os.path.exists(file_path) and ':Zone.Identifier' not in file_path:
            logger.debug(f"Текст успешно конвертирован в речь, файл: {file_path}")
            return file_path
        else:
            logger.error(f"Файл {file_path} не был создан или имеет неверный формат")
            return None
    except Exception as e:
        logger.error(f"Ошибка при конвертации текста в речь: {e}")
        return None
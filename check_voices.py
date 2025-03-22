#!/usr/bin/env python3
"""
Скрипт для проверки доступных голосов pyttsx3
"""
import pyttsx3

def check_voices():
    """
    Проверка доступных голосов pyttsx3
    """
    try:
        # Инициализируем движок с явным указанием драйвера
        try:
            # Сначала пробуем без указания драйвера
            engine = pyttsx3.init()
        except Exception as e1:
            print(f"Ошибка при инициализации без драйвера: {e1}")
            try:
                # Пробуем с драйвером espeak
                engine = pyttsx3.init(driverName="espeak")
            except Exception as e2:
                print(f"Ошибка при инициализации с драйвером espeak: {e2}")
                try:
                    # Пробуем с драйвером sapi5 (для Windows)
                    engine = pyttsx3.init(driverName="sapi5")
                except Exception as e3:
                    print(f"Ошибка при инициализации с драйвером sapi5: {e3}")
                    try:
                        # Пробуем с драйвером nsss (для macOS)
                        engine = pyttsx3.init(driverName="nsss")
                    except Exception as e4:
                        print(f"Ошибка при инициализации с драйвером nsss: {e4}")
                        print("Не удалось инициализировать pyttsx3 с известными драйверами")
                        return
        
        # Получаем голоса
        voices = engine.getProperty('voices')
        
        print(f"Найдено {len(voices)} голосов:")
        
        for i, voice in enumerate(voices):
            print(f"\nГолос #{i+1}:")
            print(f"ID: {voice.id}")
            print(f"Имя: {voice.name}")
            print(f"Язык: {voice.languages}")
            print(f"Пол: {'Мужской' if 'male' in voice.id.lower() else 'Женский' if 'female' in voice.id.lower() else 'Неизвестно'}")
            print(f"Возраст: {voice.age}")
        
        # Добавляем задержку перед завершением работы с engine
        import time
        time.sleep(0.5)
            
    except Exception as e:
        print(f"Ошибка при проверке голосов: {e}")

if __name__ == "__main__":
    check_voices()
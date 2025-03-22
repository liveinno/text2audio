#!/bin/bash

# Скрипт для установки всех необходимых движков TTS

echo "Установка зависимостей для TTS..."

# Проверяем, запущен ли скрипт с правами администратора
if [ "$EUID" -ne 0 ]; then
  echo "Пожалуйста, запустите скрипт с правами администратора (sudo)"
  exit 1
fi

# Обновляем список пакетов
echo "Обновление списка пакетов..."
apt-get update

# Устанавливаем espeak и связанные пакеты
echo "Установка espeak и связанных пакетов..."
apt-get install -y espeak espeak-data espeak-ng espeak-ng-data

# Устанавливаем mbrola (если доступно)
echo "Установка mbrola..."
apt-get install -y mbrola || echo "Пакет mbrola не найден, пропускаем..."

# Устанавливаем festival (если доступно)
echo "Установка festival..."
apt-get install -y festival festvox-ru || echo "Пакет festival или festvox-ru не найден, пропускаем..."

# Устанавливаем python-зависимости
echo "Установка python-зависимостей..."
pip install --upgrade pyttsx3 gtts

echo "Установка завершена!"
echo "Теперь вы можете запустить бота с помощью команды: ./run.sh"
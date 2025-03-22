#!/bin/bash

# Скрипт для запуска бота в фоновом режиме

# Создаем необходимые директории
mkdir -p logs
mkdir -p temp
mkdir -p db

# Проверка работоспособности бота
echo "Проверка работоспособности бота..."
python3 check_bot.py

# Если проверка прошла успешно, запускаем бота в фоновом режиме
if [ $? -eq 0 ]; then
    echo "Проверка прошла успешно. Запускаем бота в фоновом режиме..."
    nohup python3 main.py > logs/nohup.log 2>&1 &
    echo "Бот запущен в фоновом режиме. PID: $!"
    echo "Логи доступны в файле logs/nohup.log"
else
    echo "Ошибка при проверке бота. Запуск отменен."
    exit 1
fi
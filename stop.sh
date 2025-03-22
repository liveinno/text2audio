#!/bin/bash

# Скрипт для остановки бота

# Находим PID процесса бота
PID=$(ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "Бот не запущен"
    exit 0
fi

echo "Останавливаем бота (PID: $PID)..."
kill $PID

# Проверяем, остановился ли процесс
sleep 2
if ps -p $PID > /dev/null; then
    echo "Бот не остановился. Принудительно завершаем процесс..."
    kill -9 $PID
    sleep 1
fi

if ps -p $PID > /dev/null; then
    echo "Не удалось остановить бота"
    exit 1
else
    echo "Бот успешно остановлен"
    exit 0
fi
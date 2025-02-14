source venv/bin/activate

if ! python3 -c "import telethon" &> /dev/null; then
    echo "🔹 Встановлюю Telethon..."
    pip install telethon
fi

echo "🚀 Запускаю скрипт..."
sleep 3

python app.py
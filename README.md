# 📌 Телеграм-бот на Telethon

## 📜 Опис
Ця програма автоматично підключається до каналів Telegram, відстежує нові повідомлення та залишає коментарі під ними. Використовує бібліотеку **Telethon** для роботи з Telegram API.

---

## ⚙️ Встановлення

### 1️⃣ Встановлення залежностей
Спочатку потрібно встановити **Python 3.8+** та необхідні бібліотеки:
```bash
pip install -r requirements.txt
```

### 2️⃣ Створення необхідних папок
Створити папки `images`, `sessions` та `logs`. Додати в них необхідні файли.

### 3️⃣ Налаштування API Telegram

📌 Для роботи потрібні **API ID** та **API Hash**, які можна отримати у [my.telegram.org](https://my.telegram.org/apps).

Додати в папку `sessions` файли з самою сессією `session_name.session` та файл з інформацією про акаунт `session_name.json`. 

Приклад файлу `session_name.json`:
```json
{
    "app_id": app_id,
    "app_hash": "app_hash",
    "session_file": "session_name",
    "sdk": "Windows 11",
    "device": "HP ProBook 450 G8",
    "app_version": "5.4.1 x64",
}
```
## 🔧 Конфігурація
Всі основні налаштування знаходяться у файлі `config.py`. Ти можеш змінити:
- `CHANNELS_LIST` – список каналів, які бот буде моніторити.
- `INVITE_LINKS` – список запрошувальних посилань до каналів, які бот буде моніторити.
- `COMMENT_TEXTS` – список текстів для коментарів.
- `COMMENT_IMAGES` – список назв картинок для коментарів з папки `images`.

Приклад `config.py`:
```python
CHANNELS_LIST = ["@test1", "@test2", "@test3"]
INVITE_LINKS = ["https://t.me/+Z8s8QzZ3_NVjNDgy"]
COMMENT_TEXTS = [
    "Дякую!", 
    "Цікава інформація!", 
    "Гарний пост!"
    ]
COMMENT_IMAGES = [
    "image1.png",
    ...
    ]
```
---

## 📂 Структура проекту
```
/project_root
│-- app.py           # Головний файл запуску бота
│-- config.py        # Файл конфігурації (список каналів, налаштування бота)
│-- requirements.txt # Список необхідних залежностей
│-- run.sh           # Bash-скрипт для запуску на macOS/Linux
│-- run.bat          # Скрипт для запуску на Windows
│-- /sessions/       # Папка для збереження сесій Telegram
│-- /images/         # Папка для збереження фотографій для коментарів
│-- /logs/           # Папка для збереження логів
```

---

## 🚀 Запуск програми

### 🔹 У Windows:
Відкрий командний рядок (`cmd`), перейди в папку зі скриптом і виконай команду:
```bash
python app.py
```
Або:

Запустіть `run.bat`


### 🔹 У macOS/Linux:
```bash
chmod +x run.sh
./run.sh
```
Або без скрипта:
```bash
python3 app.py
```

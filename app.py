import json
import logging
from random import choice
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import SessionRevokedError, PhoneNumberBannedError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import GetFullChannelRequest

import asyncio
import os
from config import *
import random
from time import sleep
from asyncio import sleep as async_sleep

# 🔹 Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)

# На початку файлу після імпортів
commented_messages = {}

# Основна логіка бота
async def run_bot(session_data, channels_list=None, comment_texts=None, comment_images=None, invite_links=None, messages_mode=1):
    session_name = session_data['session_file']
    api_id = session_data['app_id']
    api_hash = session_data['app_hash']
    if session_data['device']:
        device_model = session_data['device']
    else:
        device_model = None
    if session_data['sdk']:
        system_version = session_data['sdk']
    else:
        system_version = None
    if session_data['app_version']:
        app_version = session_data['app_version']
    else:
        app_version = None
    logging.info(f"🔄 Запускаємо сесію {session_name}...")
    client = TelegramClient(
        f"sessions/{session_name}", 
        api_id, api_hash, 
        device_model=device_model, 
        system_version=system_version, 
        app_version=app_version)
    channels_list = [channel.strip("@") for channel in channels_list]
    try:
        await client.start() 
        logging.info(f"✅ Авторизація успішна: {session_name}")

        channel_entities = []
        for username in channels_list:
            try:
                channel_entity = await client.get_entity(username)
                channel_entities.append(channel_entity)
                full_channel = await client(GetFullChannelRequest(channel_entity))
                # Перевіряємо наявність групи для коментарів
                if hasattr(full_channel, "full_chat") and full_channel.full_chat.linked_chat_id:
                    await client(JoinChannelRequest(full_channel.full_chat.linked_chat_id))
                    logging.info(f"Канал {username} приєднався до групи для коментарів: {full_channel.full_chat.linked_chat_id}")
                else:
                    logging.info(f"Канал {username} не має окремої групи для коментарів")
            except Exception as e:
                logging.error(f"Помилка при отриманні каналів: {e}")
                if 'No user has' in str(e) and 'as username' in str(e) and channel_entities == None:
                    logging.error("Не знайдено каналів для коментування. Скрипт завершено.")
                    continue

        # Ініціалізуємо словник для кожного каналу
        for channel in channel_entities:
            commented_messages[channel.id] = set()

        if channels_list:
            for channel in channels_list:
                try:
                    await client(JoinChannelRequest(channel))
                    logging.info(f"📢 Успішно приєдналися до @{channel}")
                except Exception as e:
                    if "banned" in str(e):
                        logging.warning(f"❌ Вас заблоковано у каналі @{channel}")
                    else:
                        logging.warning(f"⚠ Не вдалося приєднатися до @{channel}: {e}")
        if invite_links:
            for invite_link in invite_links:
                try:
                    chat_hash = invite_link.split("+")[-1]  # Отримуємо хеш-запрошення
                    await client(ImportChatInviteRequest(chat_hash))
                    logging.info(f"✅ Акаунт приєднався за запрошувальним посиланням {invite_link}")
                except Exception as e:
                    if "user is already a participant" in str(e):
                        logging.info(f"ℹ️ Акаунт вже є учасником цієї групи за посиланням {invite_link}")
                    elif "Invite hash expired" in str(e):
                        logging.error(f"❌ Запрошувальне посилання {invite_link} не дійсне.")
                    else:
                        logging.error(f"❌ Акаунт не може приєднатися за запрошувальним посиланням {invite_link}")
        else:
            logging.error("Не знайдено каналів для коментування. Скрипт завершено.")
            exit()
        # Обробка нових повідомлень у каналі
        @client.on(events.NewMessage(chats=channels_list))
        async def handler(event):
            logging.info(f"📩 Новий пост у @{event.chat.username}: {event.message.text[:50]}...")
            
            # Додаємо випадкову затримку перед коментуванням
            delay = random.uniform(1, 10)
            await async_sleep(delay)
            
            for entity in channel_entities:
                print(entity)
                if entity.id == event.message.peer_id.channel_id:
                    try:
                        # Перевіряємо чи не коментували цей пост раніше
                        if event.message.id in commented_messages.get(entity.id, set()):
                            logging.info(f"Пост вже було прокоментовано, пропускаємо...")
                            continue
                            
                        chat_id = event.chat_id
                        message = event.message
                        comment_text = choice(comment_texts)
                        image = choice(comment_images)
                        
                        # Додаємо обмеження на кількість коментарів
                        if len(commented_messages.get(entity.id, set())) >= 10:
                            logging.info(f"Досягнуто ліміт коментарів для каналу {event.chat.username}")
                            continue
                            
                        if messages_mode == 1:
                            await client.send_message(entity=chat_id, message=comment_text, comment_to=message)
                            logging.info(f"💬 Коментар {comment_text[:50]}... додано до поста {event.message.text[:50]}... в каналі {event.chat.username}")
                        elif messages_mode == 2:
                            await client.send_file(entity=chat_id, file=f"images/{image}", caption=comment_text, comment_to=message)
                            logging.info(f"💬 Коментар {comment_text[:50]}... + картинка {image} додано до поста {event.message.text[:50]}... в каналі {event.chat.username}")
                        elif messages_mode == 3:
                            await client.send_file(entity=chat_id, file=f"images/{image}", comment_to=message)
                            logging.info(f"💬 Коментар картинка {image} додано до поста {event.message.text[:50]}... в каналі {event.chat.username}")
                        commented_messages[entity.id].add(event.message.id)
                    except Exception as e:
                        if "the peer was invalid" in str(e):
                            logging.error(f"❌ В каналі {event.chat.username} не можна залишити коментарі!")
                            continue
                        elif "channel specified is private" in str(e):
                            logging.error(f"❌ Канал {event.chat.username} є приватним")
                            logging.error(f"❌ Видаляємо канал з списку")
                            channel_entities.remove(entity)
                            CHANNELS_LIST.remove(entity.username)
                            continue
                        else:
                            logging.error(f"⚠ Помилка при коментуванні: {e}")
                            continue
        logging.info("🚀 Бот запущений! Очікуємо нові повідомлення...")
        await client.run_until_disconnected()

    except (SessionRevokedError, PhoneNumberBannedError):
        logging.error(f"❌ Сесія {session_name} заблокована! Переходимо до наступної...")
        return False
    except Exception as e:
        logging.error(f"⚠ Помилка в сесії {session_name}: {e}")
        if "user has been deleted/deactivated" in str(e):
            logging.error(f"❌ Акаунт {session_name} видалено! Переходимо до наступної...")
        return False
    finally:
        logging.info("🔴 Вихід з сесії")
        await client.disconnect()

    return True

async def get_sessions():
    json_files = [f for f in os.listdir("sessions") if f.endswith(".json")]
    return json_files


# Основна функція для перемикання акаунтів
async def main():
    sessions = await get_sessions()
    for session in sessions:        
        messages_mode = int(input("Оберіть варіант для коментування повідомлень: 1 - Тільки текст, 2 - Текст + картинка, 3 - Тільки Картинка "))
        with open(f"sessions/{session}", "r") as f:
            session_data = json.load(f)
        success = await run_bot(
            session_data,  
            CHANNELS_LIST,  
            COMMENT_TEXTS, 
            COMMENT_IMAGES,
            INVITE_LINKS,
            messages_mode
            )

        if success:
            break  # Якщо акаунт працює, не переключаємось на інші

if __name__ == "__main__":
    asyncio.run(main())

import json
import logging
from random import choice
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import SessionRevokedError, PhoneNumberBannedError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

import asyncio
import os
from config import *

# 🔹 Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)


# Основна логіка бота
async def run_bot(session_name, api_id, api_hash, channels_list=None, comment_texts=None, comment_images=None, invite_links=None, messages_mode=1):
    logging.info(f"🔄 Запускаємо сесію {session_name}...")
    client = TelegramClient(f"sessions/{session_name}", api_id, api_hash)
    channels_list = [channel.strip("@") for channel in channels_list]
    try:
        await client.start()
        logging.info(f"✅ Авторизація успішна: {session_name}")

        try:
            channel_entities = None
            channel_entities = [await client.get_entity(username) for username in channels_list]
            commented_messages = {entity.id: set() for entity in channel_entities}
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            if 'No user has' in str(e) and 'as username' in str(e) and channel_entities == None:
                logging.error("Не знайдено каналів для коментування. Скрипт завершено.")
                exit()

        if channels_list:
            for channel in channels_list:
                try:
                    await client(JoinChannelRequest(channel))
                    logging.info(f"📢 Успішно приєдналися до @{channel}")
                except Exception as e:
                    if "you were banned" in str(e):
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

        # Обробка нових повідомлень у каналі
        @client.on(events.NewMessage(chats=channels_list))
        async def handler(event):
            logging.info(f"📩 Новий пост у @{event.chat.username}: {event.message.text[:50]}...")
            for entity in channel_entities:
                if entity.id == event.message.peer_id.channel_id:
                    if not event.message.out and event.message.id not in commented_messages[entity.id]:
                        try:
                            chat_id = event.chat_id
                            message = event.message
                            comment_text = choice(comment_texts)
                            image = choice(comment_images)
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
                            else:
                                logging.error(f"⚠ Помилка ƒпри коментуванні: {e}")

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
        print("🔴 Вихід з сесії")
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
            session_data["session_file"], 
            session_data["app_id"], 
            session_data["app_hash"],  
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

import asyncio
import openai
import json
import os
from telethon import TelegramClient, events
import random

#######################################################
#                          ЧАСТЬ КОДА КОТОРУЮ НУЖНО НАСТРОИТЬ                         #
api_id = '' #ВАШ api_id из Telegram API
api_hash = '' #ВАШ api_hash из Telegram API
openai.api_key = '' #сгенерировать ключ через generator.py
prompt = '' #промпт по которому будет отвечать ИИ
#                                                                                                                                             #
#######################################################




session_name = 'user_session'
client_tg = TelegramClient(session_name, api_id, api_hash)
openai.api_base = "http://127.0.0.1:1337/"
history_dir = 'chat_history'
if not os.path.exists(history_dir):
    os.makedirs(history_dir)
contacts_file = os.path.join(history_dir, "contacts.json")
def load_history(user_id):
    file_path = f"{history_dir}/{user_id}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return [
            {"role": "system", "content": prompt}
        ]
def save_history(user_id, history):
    file_path = f"{history_dir}/{user_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
def update_contacts(user_id, username):
    contacts = {}
    if os.path.exists(contacts_file):
        with open(contacts_file, "r", encoding="utf-8") as f:
            contacts = json.load(f)
    if str(user_id) not in contacts:
        contacts[str(user_id)] = username
        with open(contacts_file, "w", encoding="utf-8") as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
def get_ai_answer(history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )
    return response['choices'][0]['message']['content'].strip()
paused = False
@client_tg.on(events.NewMessage(incoming=True))
async def on_message(event):
    if event.is_private and not event.out:
        user_id = event.sender_id
        user_msg = event.raw_text
        sender = await event.get_sender()
        name = sender.first_name or ""
        if sender.last_name:
            name += " " + sender.last_name
        name = name.strip() or str(user_id)
        update_contacts(user_id, name)
        if event.media or event.voice or event.video_note or event.gif or event.sticker or event.photo or event.video or event.document:
            await event.reply("Извините, медиа не просматриваю)")
            return
        history = load_history(user_id)
        history.append({"role": "user", "content": user_msg})
        print(f"Получено сообщение от {user_id} ({name}): {user_msg}")
        if paused:
            print("Режим паузы включен: AI не отвечает, сообщение сохранено.")
            save_history(user_id, history)
            return
        try:
            delay = random.uniform(1, 10)
            print(f"Протупливаю {delay:.2f} секунд перед ответом") #Добавляет живность ответа
            await asyncio.sleep(delay)
            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(None, get_ai_answer, history)
            
            history.append({"role": "assistant", "content": reply})
            save_history(user_id, history)
            if len(history) > 20:
                history = history[:1] + history[-18:]
                save_history(user_id, history)
            await event.reply(reply)
        except openai.OpenAIError as e:
            print(f"Ошибка OpenAI API: {e}")
            await event.reply("Ошибка API")
        except Exception as e:
            print(f"Другая ошибка: {e}")
            await event.reply("ИИ не отвечает. Проблемы...")
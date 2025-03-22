import asyncio
import openai
import json
import os
import random
import wave
import soundfile as sf
from telethon import TelegramClient, events
from vosk import Model, KaldiRecognizer
print('\n--------------------------------\nВнизу логи ai_script.py\n--------------------------------')
api_id = ''
api_hash = ''
session_name = 'user_session'
client_tg = TelegramClient(session_name, api_id, api_hash)

openai.api_key = ''
openai.api_base = "http://127.0.0.1:1337/"

history_dir = 'chat_history'
audio_dir = 'audio_files'
model_path = "vosk-model"
vosk_model = Model(model_path)
print('VOSK запущен. Доступны ответы на голосовые сообщения!')

if not os.path.exists(history_dir):
    os.makedirs(history_dir)

if not os.path.exists(audio_dir): 
    os.makedirs(audio_dir)

contacts_file = os.path.join(history_dir, "contacts.json")

def load_history(user_id):
    file_path = f"{history_dir}/{user_id}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return [
            {"role": "system", "content": "ты — человек, не бот, не ИИ помощник. никаких банальных фраз и тупых сравнений. пиши просто, по-человечески, как переписываешься с другом. коротко, по факту, с характером. без заумных слов, без книжных выражений, без штампов. без заглавных букв и почти без знаков препинания. отвечаешь быстро и по простому. можешь отшутиться если надо. не умничай. в конце сообщения не добавляй точку, переписывайся будто в мессенджере. будто сидим в дискорде или на кухне. не душни фактами."}
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

def transcribe_audio_vosk(audio_file_path):
    try:
        data, samplerate = sf.read(audio_file_path)
        temp_wav = "temp_vosk.wav"
        sf.write(temp_wav, data, samplerate)
        wf = wave.open(temp_wav, "rb")
        rec = KaldiRecognizer(vosk_model, wf.getframerate())
        
        result_text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text += res.get("text", "") + " "
        res = json.loads(rec.FinalResult())
        result_text += res.get("text", "")
        return result_text.strip()
        
    except Exception as e:
        print(f"Ошибка Vosk: {e}")
        return None

paused = False

@client_tg.on(events.NewMessage(incoming=True))
async def on_message(event):
    if event.is_private and not event.out:
        user_id = event.sender_id

        sender = await event.get_sender()
        name = sender.first_name or ""
        if sender.last_name:
            name += " " + sender.last_name
        name = name.strip() or str(user_id)
        update_contacts(user_id, name)
        user_msg = event.raw_text
        if event.voice:
            file_path = await event.download_media(file=os.path.join(audio_dir, f"{user_id}_{random.randint(1000, 9999)}.ogg")) 
            print(f"Скачано голосовое сообщение: {file_path}")
            user_msg = transcribe_audio_vosk(file_path)
            if not user_msg:
                await event.reply("не понял голос, запиши чётче пж")
                return
            print(f"Распознал речь: {user_msg}")

        elif event.media:
            await event.reply("позже гляну, ща времени нет. сорян)")
            return

        history = load_history(user_id)
        history.append({"role": "user", "content": user_msg})

        if paused:
            print("Пауза, просто сохраняю")
            save_history(user_id, history)
            return

        try:
            delay = random.uniform(1, 3)
            print(f"Протупливаю {delay:.2f} сек перед ответом (1-3 секунды)")
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
            print(f"openai error: {e}")
            await event.reply("прости, инет лагает, пока не могу говорить..")
        except Exception as e:
            print(f"ошибка: {e}")
            await event.reply("ИИ не отвечает")

client_tg.start()
client_tg.run_until_disconnected()
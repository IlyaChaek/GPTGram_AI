import time
import re
import random
import os
import subprocess

print('Генератор ключей и данных\n-----------------------------------\n')

class CryptographicState:
    def __init__(self):
        self.gen_state = 0
        self.crypt_key = 0
        self.buffer = [''] * 64

def initialize_cryptographic_state(state, seed):
    state.gen_state = seed
    state.crypt_key = 0xDEADBEEF

def next_cryptographic_state(state):
    state.gen_state = (state.gen_state * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
    return state.gen_state

def xorshift_key_derivation(state):
    state.crypt_key ^= (state.crypt_key << 13)
    state.crypt_key ^= (state.crypt_key >> 17)
    state.crypt_key ^= (state.crypt_key << 5)
    state.crypt_key ^= (state.crypt_key >> 11) & 0xFFFFFFFF

def modular_character_expansion(state, value):
    exponent = (value % 62)
    if exponent < 10:
        return chr(ord('0') + exponent)
    exponent -= 10
    if exponent < 26:
        return chr(ord('A') + exponent)
    return chr(ord('a') + (exponent - 26))

def generate_openai_key(state):
    state.buffer[0] = 's'
    state.buffer[1] = 'k'
    state.buffer[2] = '-'
    for i in range(3, 23):
        xorshift_key_derivation(state)
        state.buffer[i] = modular_character_expansion(state, next_cryptographic_state(state))
    state.buffer[23] = 'T'
    state.buffer[24] = '3'
    state.buffer[25] = 'B'
    state.buffer[26] = 'l'
    state.buffer[27] = 'e'
    state.buffer[28] = 'n'
    state.buffer[29] = 'k'
    state.buffer[30] = 'A'
    state.buffer[31] = 'I'
    for i in range(32, 52):
        xorshift_key_derivation(state)
        state.buffer[i] = modular_character_expansion(state, next_cryptographic_state(state))
    state.buffer[52] = '\0'

def random_system_version():
    return f"{random.randint(1, 10)}.{random.randint(0, 20)}.{random.randint(0, 100)}-ModSys"

def random_device_model():
    models = [
        "iPhone 14 Pro", "Samsung Galaxy S21", "Xiaomi Redmi Note 10 Pro", "OnePlus 9", 
        "Google Pixel 9", "Huawei P40", "Realme GT Neo 6", "Xiaomi Redmi 9A"
    ]
    return random.choice(models)

def random_app_version():
    return f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}"

def update_ai_bot_file(api_key, api_id, api_hash, sys_ver, dev_model, app_ver, file_path='ai_bot.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r"openai\.api_key\s*=\s*''", f"openai.api_key = '{api_key}'", content)
    content = re.sub(r"api_id\s*=\s*''", f"api_id = '{api_id}'", content)
    content = re.sub(r"api_hash\s*=\s*''", f"api_hash = '{api_hash}'", content)
    
    # Вшиваем новые данные:
    content = re.sub(r'system_version\s*=\s*["\'].*?["\']', f'system_version = "{sys_ver}"', content)
    content = re.sub(r'device_model\s*=\s*["\'].*?["\']', f'device_model = "{dev_model}"', content)
    content = re.sub(r'app_version\s*=\s*["\'].*?["\']', f'app_version = "{app_ver}"', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[+] Данные успешно вставлены в {file_path}")

def create_bat_file():
    bat_content = """@echo GPTGram by MOCKBA_123, Thanks for Using my Project
python client.py
pause
"""
    with open("run_client.bat", "w", encoding="utf-8") as bat_file:
        bat_file.write(bat_content)
    print("[+] run_client.bat успешно создан!")

def main():
    state = CryptographicState()
    seed = int(time.time())
    initialize_cryptographic_state(state, seed)

    keys = []
    for _ in range(5):
        generate_openai_key(state)
        key = ''.join(state.buffer).rstrip('\0')
        keys.append(key)

    print("\n-----------------------------\n".join(keys))
    selected_key = random.choice(keys)

    os.system('cls' if os.name == 'nt' else 'clear')
    api_id = input("Введите ваш api_id для Telegram API: ")
    api_hash = input("Введите ваш api_hash для Telegram API: ")

    # Генерация данных
    sys_ver = random_system_version()
    dev_model = random_device_model()
    app_ver = random_app_version()
    print(f"Сгенерировано: Версия ОС={sys_ver},\nМодель телефона={dev_model},\nВерсия приложения Telegram={app_ver}\nКлюч OpenAI: {selected_key}\n\nУспешно!")

    update_ai_bot_file(selected_key, api_id, api_hash, sys_ver, dev_model, app_ver)

    create_bat_file()
    
    subprocess.run(["run_client.bat"], shell=True)

if __name__ == "__main__":
    main()
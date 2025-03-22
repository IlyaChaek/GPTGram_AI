import time
import re
import random
import os
import subprocess

<<<<<<< HEAD

=======
>>>>>>> d41a5c2b0463ca3c15b09ff4dac1e0fabf35b62d
print('Генератор ключей для ChatGPT\n-----------------------------------\n')

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

def update_ai_bot_file(api_key, api_id, api_hash, file_path='ai_bot.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем строку с пустым ключом
    content = re.sub(r"openai\.api_key\s*=\s*''", f"openai.api_key = '{api_key}'", content)
    content = re.sub(r"api_id\s*=\s*''", f"api_id = '{api_id}'", content)
    content = re.sub(r"api_hash\s*=\s*''", f"api_hash = '{api_hash}'", content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[+] Ключ {api_key} и параметры API успешно вставлены в {file_path}")

def create_bat_file():
<<<<<<< HEAD
    bat_content = """@echo GPTGram by MOCKBA_123, Thanks for Using my Project
=======
    bat_content = """@echo off
>>>>>>> d41a5c2b0463ca3c15b09ff4dac1e0fabf35b62d
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
    
<<<<<<< HEAD
    os.system('cls' if os.name == 'nt' else 'clear')
=======
    # Запрашиваем у пользователя api_id и api_hash
>>>>>>> d41a5c2b0463ca3c15b09ff4dac1e0fabf35b62d
    api_id = input("Введите ваш api_id для Telegram API: ")
    api_hash = input("Введите ваш api_hash для Telegram API: ")
    
    update_ai_bot_file(selected_key, api_id, api_hash)
    
    # Создание bat файла
    create_bat_file()
    
    # Запуск .bat файла
    subprocess.run(["run_client.bat"], shell=True)

if __name__ == "__main__":
    main()

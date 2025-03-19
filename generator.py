import time
import re
import random

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

def update_ai_bot_file(api_key, file_path='ai_bot.py'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Заменяем строку с пустым ключом
    content = re.sub(r"openai\.api_key\s*=\s*''", f"openai.api_key = '{api_key}'", content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Ключ {api_key} успешно вставлен в {file_path}")

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
    update_ai_bot_file(selected_key)

if __name__ == "__main__":
    main()

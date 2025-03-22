import tkinter as tk
from tkinter import messagebox
from threading import Thread
import asyncio
import sys
import json
import os
import subprocess
import shutil
import customtkinter as ctk

# Настройки шрифта и темы
DEFAULT_FONT = ("Aptos", 20)  # Aptos 20 без bold

# Темы с расширенными настройками
DARK_THEME = {
    "bg_color": "#282828",
    "fg_color": "#ffffff",
    "button_color": "#FF69B4",
    "button_hover_color": "#FF1493",
    "header_color": "#3c3c3c"
}
LIGHT_THEME = {
    "bg_color": "#f0f0f0",
    "fg_color": "#000000",
    "button_color": "#FF69B4",
    "button_hover_color": "#FF1493",
    "header_color": "#d0d0d0"
}

# Для вывода логов в консоль и в текстовую область
class DualOutput:
    def __init__(self, log_func):
        self.log_func = log_func

    def write(self, message):
        if message.strip():
            self.log_func(message)
            sys.__stdout__.write(f'{message}\n')
            sys.__stdout__.flush()

    def flush(self):
        sys.__stdout__.flush()

class TelegramBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Telegram Bot by MOCKBA_123")
        try:
            self.root.iconbitmap("icon.ico")
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")
        self.bot_thread = None
        self.bot_running = False
        self.endpoint_process = None
        self.logs_visible = True
        self.ai_bot = None  

        # Начальная тема – тёмная
        self.current_theme = "Dark"
        self.theme_data = DARK_THEME.copy()
        ctk.set_appearance_mode("Dark")
        self.root.configure(bg=self.theme_data["bg_color"])

        # Хедер с названием
        self.header_label = ctk.CTkLabel(self.root, text="AI Telegram Bot", font=("Aptos", 24),
                                           fg_color=self.theme_data["header_color"],
                                           text_color=self.theme_data["fg_color"],
                                           corner_radius=12, pady=10)
        self.header_label.pack(padx=10, pady=(10,0), fill="x")

        # Основной фрейм с скруглением
        self.main_frame = ctk.CTkFrame(root, corner_radius=12, fg_color=self.theme_data["bg_color"])
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Контейнер для кнопок
        self.control_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.theme_data["bg_color"])
        self.control_frame.pack(padx=10, pady=10)

        # Кнопки управления с заданными параметрами
        self.start_button = ctk.CTkButton(self.control_frame, text="Запустить бота",
                                          command=self.start_bot, width=180, corner_radius=12,
                                          font=DEFAULT_FONT, fg_color=self.theme_data["button_color"],
                                          hover_color=self.theme_data["button_hover_color"])
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self.control_frame, text="Остановить бота",
                                         command=self.stop_bot, width=180, corner_radius=12,
                                         font=DEFAULT_FONT, state="disabled",
                                         fg_color=self.theme_data["button_color"],
                                         hover_color=self.theme_data["button_hover_color"])
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.history_button = ctk.CTkButton(self.control_frame, text="История",
                                            command=self.show_history, width=180, corner_radius=12,
                                            font=DEFAULT_FONT,
                                            fg_color=self.theme_data["button_color"],
                                            hover_color=self.theme_data["button_hover_color"])
        self.history_button.grid(row=0, column=2, padx=10, pady=10)

        self.pause_button = ctk.CTkButton(self.control_frame, text="Пауза AI",
                                          command=self.toggle_pause, width=180, corner_radius=12,
                                          font=DEFAULT_FONT,
                                          fg_color=self.theme_data["button_color"],
                                          hover_color=self.theme_data["button_hover_color"])
        self.pause_button.grid(row=0, column=3, padx=10, pady=10)

        # Дополнительные кнопки
        self.refresh_button = ctk.CTkButton(self.control_frame, text="Обновить данные",
                                            command=self.refresh_data, width=180, corner_radius=12,
                                            font=DEFAULT_FONT,
                                            fg_color=self.theme_data["button_color"],
                                            hover_color=self.theme_data["button_hover_color"])
        self.refresh_button.grid(row=1, column=0, padx=10, pady=10)

        self.reset_context_button = ctk.CTkButton(self.control_frame, text="Сбросить контекст",
                                                  command=self.reset_chat_context, width=180, corner_radius=12,
                                                  font=DEFAULT_FONT,
                                                  fg_color=self.theme_data["button_color"],
                                                  hover_color=self.theme_data["button_hover_color"])
        self.reset_context_button.grid(row=1, column=1, padx=10, pady=10)

        self.clear_audio_button = ctk.CTkButton(self.control_frame, text="Очистить аудио",
                                                command=self.clear_audio_files, width=180, corner_radius=12,
                                                font=DEFAULT_FONT,
                                                fg_color=self.theme_data["button_color"],
                                                hover_color=self.theme_data["button_hover_color"])
        self.clear_audio_button.grid(row=1, column=2, padx=10, pady=10)

        # Кнопка смены темы
        self.theme_toggle_button = ctk.CTkButton(self.control_frame, text="Сменить тему",
                                                 command=self.toggle_theme, width=180, corner_radius=12,
                                                 font=DEFAULT_FONT,
                                                 fg_color=self.theme_data["button_color"],
                                                 hover_color=self.theme_data["button_hover_color"])
        self.theme_toggle_button.grid(row=1, column=3, padx=10, pady=10)

        # Текстовая область логов – заменил стандартный scrolledtext на CTkTextbox
        self.log_area = ctk.CTkTextbox(self.main_frame, width=600, height=300, font=("Aptos", 16),
                                       fg_color=self.theme_data["bg_color"],
                                       text_color=self.theme_data["fg_color"],
                                       corner_radius=12)
        self.log_area.pack(pady=10)

        # Кнопки под логами
        self.toggle_log_button = ctk.CTkButton(self.main_frame, text="Скрыть логи",
                                               command=self.toggle_logs, width=180, corner_radius=12,
                                               font=DEFAULT_FONT,
                                               fg_color=self.theme_data["button_color"],
                                               hover_color=self.theme_data["button_hover_color"])
        self.toggle_log_button.pack(pady=5)

        self.copy_logs_button = ctk.CTkButton(self.main_frame, text="Копировать логи",
                                              command=self.copy_logs, width=180, corner_radius=12,
                                              font=DEFAULT_FONT,
                                              fg_color=self.theme_data["button_color"],
                                              hover_color=self.theme_data["button_hover_color"])
        self.copy_logs_button.pack(pady=5)

        self.restart_endpoint_button = ctk.CTkButton(self.main_frame, text="Перезапуск Endpoint",
                                                     command=self.restart_endpoint, width=180, corner_radius=12,
                                                     font=DEFAULT_FONT,
                                                     fg_color=self.theme_data["button_color"],
                                                     hover_color=self.theme_data["button_hover_color"])
        self.restart_endpoint_button.pack(pady=5)

        sys.stdout = DualOutput(self.log)

        self.contacts_file = os.path.join("chat_history", "contacts.json")
        self.contacts = {}
        self.load_contacts()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_theme(self):
        # Переключение между темами и обновление цветов для всех элементов
        if self.current_theme == "Dark":
            self.current_theme = "Light"
            ctk.set_appearance_mode("Light")
            self.theme_data = LIGHT_THEME.copy()
        else:
            self.current_theme = "Dark"
            ctk.set_appearance_mode("Dark")
            self.theme_data = DARK_THEME.copy()

        # Обновляем цвета основного окна и всех виджетов
        self.root.configure(bg=self.theme_data["bg_color"])
        self.header_label.configure(fg_color=self.theme_data["header_color"],
                                    text_color=self.theme_data["fg_color"])
        self.main_frame.configure(fg_color=self.theme_data["bg_color"])
        self.control_frame.configure(fg_color=self.theme_data["bg_color"])
        self.log_area.configure(fg_color=self.theme_data["bg_color"],
                                text_color=self.theme_data["fg_color"],
                                bg_color=self.theme_data["bg_color"])
        print(f"Переключена тема на {self.current_theme}")

    def restart_endpoint(self):
        if self.endpoint_process:
            try:
                print("Перезапускаю Endpoint...")
                self.endpoint_process.terminate()
                self.endpoint_process.wait(timeout=5)
                print("Endpoint остановлен")
            except Exception as e:
                print(f"Ошибка при остановке Endpoint: {e}")
            self.endpoint_process = None
        self.launch_endpoint()

    def log(self, message):
        if self.logs_visible:
            self.log_area.insert("end", f"{message.strip()}\n")
            self.log_area.see("end")

    def toggle_logs(self):
        if self.logs_visible:
            self.log_area.pack_forget()
            self.toggle_log_button.configure(text="Показать логи")
            self.logs_visible = False
        else:
            self.log_area.pack(pady=10)
            self.toggle_log_button.configure(text="Скрыть логи")
            self.logs_visible = True

    def copy_logs(self):
        logs = self.log_area.get("0.0", "end")
        self.root.clipboard_clear()
        self.root.clipboard_append(logs)
        messagebox.showinfo("Логи", "Логи скопированы в буфер обмена!")

    def load_contacts(self):
        if os.path.exists(self.contacts_file):
            try:
                with open(self.contacts_file, 'r', encoding='utf-8') as f:
                    self.contacts = json.load(f)
                print("Контакты успешно загружены.")
            except Exception as e:
                print(f"Ошибка при загрузке контактов: {e}")

    def save_contacts(self):
        try:
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(self.contacts, f, ensure_ascii=False, indent=2)
            print("Контакты успешно сохранены.")
        except Exception as e:
            print(f"Ошибка при сохранении контактов: {e}")

    def show_history(self):
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("История общения")
        history_window.geometry("600x600")
        history_window.configure(bg=self.theme_data["bg_color"])

        contact_listbox = tk.Listbox(history_window, height=15, width=40,
                                     bg=self.theme_data["bg_color"], fg=self.theme_data["fg_color"],
                                     font=("Aptos", 16))
        for user_id, username in self.contacts.items():
            contact_listbox.insert(tk.END, f"{username} ({user_id})")
        contact_listbox.pack(padx=10, pady=10)

        def on_contact_select(event):
            selected = contact_listbox.curselection()
            if selected:
                user_info = contact_listbox.get(selected[0])
                user_id = user_info.split(" (")[1][:-1]
                self.show_user_history(user_id)

        contact_listbox.bind("<<ListboxSelect>>", on_contact_select)

    def show_user_history(self, user_id):
        user_history_window = ctk.CTkToplevel(self.root)
        user_history_window.title(f"История общения с {user_id}")
        user_history_window.geometry("400x400")
        user_history_window.configure(bg=self.theme_data["bg_color"])

        history = self.load_user_history(user_id)

        history_text = ctk.CTkTextbox(user_history_window, width=350, height=300, font=("Aptos", 16),
                                      fg_color=self.theme_data["bg_color"],
                                      text_color=self.theme_data["fg_color"],
                                      corner_radius=12)
        history_text.insert("end", "\n".join([f"{entry['role']}: {entry['content']}" for entry in history]))
        history_text.configure(state="disabled")
        history_text.pack(padx=10, pady=10)

    def load_user_history(self, user_id):
        file_path = os.path.join("chat_history", f"{user_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке истории для {user_id}: {e}")
        return []

    def launch_endpoint(self):
        if not self.endpoint_process:
            try:
                self.endpoint_process = subprocess.Popen(
                    ["python", "ChatGPT-Endpoint/endpoint.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                Thread(target=self.stream_endpoint_output, daemon=True).start()
                print("Endpoint запущен")
            except Exception as e:
                print(f"Ошибка при запуске Endpoint: {e}")

    def stream_endpoint_output(self):
        for line in self.endpoint_process.stdout:
            decoded_line = line.decode('utf-8').strip()
            if decoded_line and not decoded_line.startswith("LOG (VoskAPI:"):
                print(decoded_line)
        for err in self.endpoint_process.stderr:
            decoded_err = err.decode('utf-8').strip()
            if decoded_err:
                print(f"[STDERR] {decoded_err}")

    def start_bot(self):
        if not self.bot_running:
            self.bot_running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.launch_endpoint()
            print("ИИ скрипт запущен!")
            self.bot_thread = Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

    def run_bot(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.bot_main())
        except Exception as e:
            print(f"Ошибка запуска бота: {e}")
            self.bot_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    async def bot_main(self):
        import ai_bot 
        self.ai_bot = ai_bot 
        await ai_bot.client_tg.start()
        print("Бот подключился к Telegram!")
        await ai_bot.client_tg.run_until_disconnected()
        print("Бот отключился от Telegram!")

    def stop_bot(self):
        print("Останавливаю бота и закрываю программу...")
        try:
            if self.ai_bot:
                self.ai_bot.client_tg.disconnect()
        except Exception as e:
            print(f"Ошибка при отключении: {e}")
        if self.endpoint_process:
            try:
                self.endpoint_process.terminate()
                self.endpoint_process.wait(timeout=5)
                print("Endpoint остановлен")
            except Exception as e:
                print(f"Ошибка при остановке Endpoint: {e}")
        self.root.destroy()
        os._exit(0)

    def toggle_pause(self):
        if self.ai_bot:
            self.ai_bot.paused = not self.ai_bot.paused
            if self.ai_bot.paused:
                self.pause_button.configure(text="Возобновить AI")
                print("Режим паузы включен: AI не отвечает автоматически.")
            else:
                self.pause_button.configure(text="Пауза AI")
                print("Режим паузы выключен: AI отвечает автоматически.")

    def refresh_data(self):
        self.load_contacts()
        print("Данные клиента обновлены!")

    def reset_chat_context(self):
        folder = "chat_history"
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")
            print("Контекст диалога сброшен (chat_history очищен)!")
        else:
            print("Папка chat_history не существует.")

    def clear_audio_files(self):
        folder = "audio_files"
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")
            print("Аудио файлы очищены (audio_files очищен)!")
        else:
            print("Папка audio_files не существует.")

    def on_closing(self):
        self.stop_bot()

if __name__ == "__main__":
    root = ctk.CTk()
    app = TelegramBotApp(root)
    root.mainloop()

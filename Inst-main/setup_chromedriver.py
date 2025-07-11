#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для налаштування та тестування ChromeDriver
"""

import os
import sys
import platform
import subprocess
import requests
import zipfile
import tempfile
import shutil
from pathlib import Path


def get_chrome_version():
    """Отримання версії Chrome"""
    try:
        if platform.system() == "Windows":
            # Спроба через реєстр
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                # Альтернативний спосіб через командний рядок
                try:
                    result = subprocess.run([
                        'reg', 'query', 
                        'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', 
                        '/v', 'version'
                    ], capture_output=True, text=True, check=True)
                    
                    for line in result.stdout.split('\n'):
                        if 'version' in line:
                            return line.split()[-1]
                except:
                    pass
                
                # Спроба через виконання Chrome
                try:
                    chrome_path = None
                    possible_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            chrome_path = path
                            break
                    
                    if chrome_path:
                        result = subprocess.run([chrome_path, '--version'], 
                                              capture_output=True, text=True, check=True)
                        return result.stdout.strip().split()[-1]
                except:
                    pass
                    
        else:  # Linux/Mac
            try:
                result = subprocess.run(['google-chrome', '--version'], 
                                      capture_output=True, text=True, check=True)
                return result.stdout.strip().split()[-1]
            except:
                try:
                    result = subprocess.run(['chromium-browser', '--version'], 
                                          capture_output=True, text=True, check=True)
                    return result.stdout.strip().split()[-1]
                except:
                    pass
    except Exception as e:
        print(f"Помилка отримання версії Chrome: {e}")
    
    return None


def get_platform_info():
    """Отримання інформації про платформу"""
    system = platform.system()
    machine = platform.machine()
    
    if system == "Windows":
        if machine.endswith('64'):
            return "win64", "chromedriver-win64.zip", "chromedriver.exe"
        else:
            return "win32", "chromedriver-win32.zip", "chromedriver.exe"
    elif system == "Linux":
        if machine.endswith('64'):
            return "linux64", "chromedriver-linux64.zip", "chromedriver"
        else:
            return "linux32", "chromedriver-linux32.zip", "chromedriver"
    elif system == "Darwin":  # macOS
        if machine == "arm64":
            return "mac-arm64", "chromedriver-mac-arm64.zip", "chromedriver"
        else:
            return "mac-x64", "chromedriver-mac-x64.zip", "chromedriver"
    
    raise Exception(f"Непідтримувана платформа: {system} {machine}")


def download_chromedriver(version, platform_name, filename):
    """Завантаження ChromeDriver"""
    try:
        # URL для Chrome for Testing
        base_url = "https://storage.googleapis.com/chrome-for-testing-public"
        download_url = f"{base_url}/{version}/{platform_name}/{filename}"
        
        print(f"Завантаження з: {download_url}")
        
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        return response.content
        
    except Exception as e:
        print(f"Помилка завантаження: {e}")
        
        # Спроба з альтернативним URL (старі версії)
        try:
            # Для старих версій Chrome
            major_version = version.split('.')[0]
            alt_url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{platform_name.replace('-', '_')}.zip"
            
            print(f"Спроба альтернативного URL: {alt_url}")
            
            response = requests.get(alt_url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e2:
            print(f"Альтернативний URL також не працює: {e2}")
            raise e


def install_chromedriver(chrome_version=None):
    """Встановлення ChromeDriver"""
    try:
        # Отримання версії Chrome
        if not chrome_version:
            chrome_version = get_chrome_version()
        
        if not chrome_version:
            print("❌ Не вдалося визначити версію Chrome")
            print("Переконайтесь, що Google Chrome встановлений")
            return False
        
        print(f"📋 Версія Chrome: {chrome_version}")
        
        # Отримання інформації про платформу
        platform_name, filename, executable_name = get_platform_info()
        print(f"🖥️ Платформа: {platform_name}")
        
        # Завантаження ChromeDriver
        print("⬇️ Завантаження ChromeDriver...")
        zip_content = download_chromedriver(chrome_version, platform_name, filename)
        
        # Створення тимчасової директорії
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, filename)
            
            # Збереження zip файлу
            with open(zip_path, 'wb') as f:
                f.write(zip_content)
            
            # Розпакування
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Пошук виконуваного файлу
            driver_path = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == executable_name or (file.startswith('chromedriver') and 
                                                 (file.endswith('.exe') or platform.system() != "Windows")):
                        driver_path = os.path.join(root, file)
                        break
                if driver_path:
                    break
            
            if not driver_path:
                print("❌ Не знайдено виконуваний файл ChromeDriver")
                return False
            
            # Створення постійного розташування
            install_dir = os.path.join(os.path.expanduser('~'), '.chromedriver')
            os.makedirs(install_dir, exist_ok=True)
            
            final_path = os.path.join(install_dir, executable_name)
            
            # Копіювання файлу
            shutil.copy2(driver_path, final_path)
            
            # Встановлення прав виконання (для Unix систем)
            if platform.system() != "Windows":
                os.chmod(final_path, 0o755)
            
            print(f"✅ ChromeDriver встановлено: {final_path}")
            
            # Тестування
            if test_chromedriver(final_path):
                print("✅ ChromeDriver працює правильно!")
                
                # Додавання до PATH (опціонально)
                add_to_path = input("Додати до системного PATH? (y/n): ").lower().strip()
                if add_to_path == 'y':
                    add_chromedriver_to_path(install_dir)
                
                return True
            else:
                print("❌ ChromeDriver не працює правильно")
                return False
        
    except Exception as e:
        print(f"❌ Помилка встановлення: {e}")
        return False


def test_chromedriver(driver_path):
    """Тестування ChromeDriver"""
    try:
        print("🧪 Тестування ChromeDriver...")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")  # Без графічного інтерфейсу
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Простий тест
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"📝 Заголовок сторінки: {title}")
        return "Google" in title
        
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False


def add_chromedriver_to_path(install_dir):
    """Додавання ChromeDriver до PATH"""
    try:
        if platform.system() == "Windows":
            # Для Windows - додавання до PATH користувача
            import winreg
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            if install_dir not in current_path:
                new_path = f"{current_path};{install_dir}" if current_path else install_dir
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"✅ {install_dir} додано до PATH")
                print("⚠️ Перезапустіть командний рядок для застосування змін")
            else:
                print("ℹ️ Директорія вже в PATH")
            
            winreg.CloseKey(key)
            
        else:
            # Для Unix систем
            shell_rc = None
            shell = os.environ.get('SHELL', '/bin/bash')
            
            if 'bash' in shell:
                shell_rc = os.path.expanduser('~/.bashrc')
            elif 'zsh' in shell:
                shell_rc = os.path.expanduser('~/.zshrc')
            elif 'fish' in shell:
                shell_rc = os.path.expanduser('~/.config/fish/config.fish')
            
            if shell_rc:
                export_line = f'export PATH="$PATH:{install_dir}"'
                
                # Перевірка, чи вже додано
                try:
                    with open(shell_rc, 'r') as f:
                        content = f.read()
                    
                    if install_dir not in content:
                        with open(shell_rc, 'a') as f:
                            f.write(f'\n# ChromeDriver\n{export_line}\n')
                        print(f"✅ {install_dir} додано до {shell_rc}")
                        print(f"⚠️ Виконайте: source {shell_rc} або перезапустіть термінал")
                    else:
                        print("ℹ️ Директорія вже в PATH")
                        
                except Exception as e:
                    print(f"⚠️ Не вдалося автоматично додати до PATH: {e}")
                    print(f"Додайте вручну: {export_line}")
            else:
                print(f"⚠️ Невизначений shell, додайте вручну: export PATH=\"$PATH:{install_dir}\"")
        
    except Exception as e:
        print(f"❌ Помилка додавання до PATH: {e}")


def clean_old_drivers():
    """Очищення старих драйверів"""
    try:
        # Очищення webdriver-manager кешу
        wdm_cache = os.path.expanduser('~/.wdm')
        if os.path.exists(wdm_cache):
            shutil.rmtree(wdm_cache)
            print("🗑️ Очищено кеш webdriver-manager")
        
        # Очищення нашого кешу
        our_cache = os.path.expanduser('~/.chromedriver')
        if os.path.exists(our_cache):
            response = input(f"Видалити існуючі драйвери з {our_cache}? (y/n): ").lower().strip()
            if response == 'y':
                shutil.rmtree(our_cache)
                print("🗑️ Очищено старі драйвери")
        
    except Exception as e:
        print(f"⚠️ Помилка очищення: {e}")


def main():
    """Основна функція"""
    print("🚗 Налаштування ChromeDriver для Instagram Bot")
    print("=" * 50)
    
    # Перевірка Chrome
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✅ Chrome знайдено: {chrome_version}")
    else:
        print("❌ Chrome не знайдено!")
        print("Встановіть Google Chrome: https://www.google.com/chrome/")
        return
    
    # Перевірка Selenium
    try:
        import selenium
        print(f"✅ Selenium: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium не встановлено!")
        print("Встановіть: pip install selenium")
        return
    
    print("\nВиберіть дію:")
    print("1. Встановити ChromeDriver")
    print("2. Тестувати існуючий ChromeDriver")
    print("3. Очистити старі драйвери")
    print("4. Показати інформацію про систему")
    
    choice = input("\nВаш вибір (1-4): ").strip()
    
    if choice == "1":
        clean_old_drivers()
        install_chromedriver(chrome_version)
    elif choice == "2":
        driver_path = input("Шлях до ChromeDriver (або Enter для системного): ").strip()
        if not driver_path:
            # Пошук у системному PATH
            import shutil as sh
            driver_path = sh.which('chromedriver')
            if not driver_path:
                print("❌ ChromeDriver не знайдено в PATH")
                return
        
        if test_chromedriver(driver_path):
            print("✅ ChromeDriver працює!")
        else:
            print("❌ ChromeDriver не працює")
    elif choice == "3":
        clean_old_drivers()
    elif choice == "4":
        platform_name, filename, executable_name = get_platform_info()
        print(f"\nℹ️ Інформація про систему:")
        print(f"Операційна система: {platform.system()}")
        print(f"Архітектура: {platform.machine()}")
        print(f"Платформа ChromeDriver: {platform_name}")
        print(f"Файл для завантаження: {filename}")
        print(f"Виконуваний файл: {executable_name}")
        print(f"Версія Chrome: {chrome_version}")
    else:
        print("❌ Невірний вибір")


if __name__ == "__main__":
    main()
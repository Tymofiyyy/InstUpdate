#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Bot - Мобільна автоматизація
Головний файл для запуску програми

Автор: Instagram Bot Team
Версія: 1.0.0
Дата: 2025
"""

import sys
import os
import logging
import argparse
from pathlib import Path
import traceback

# Додавання поточної директорії до шляху
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from config import Config
    from utils import setup_logging, create_directories
    from gui import InstagramBotGUI
    from instagram_bot import InstagramBot
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    print("Переконайтесь, що всі необхідні файли присутні в директорії")
    sys.exit(1)

def check_requirements():
    """Перевірка необхідних залежностей"""
    required_packages = [
        'selenium',
        'requests',
        'PIL',
        'cv2',
        'numpy',
        'matplotlib',
        'pytesseract'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            # Спеціальні випадки для пакетів з різними назвами
            if package == 'PIL':
                try:
                    __import__('Pillow')
                except ImportError:
                    missing_packages.append('Pillow')
            elif package == 'cv2':
                try:
                    __import__('opencv-python')
                except ImportError:
                    missing_packages.append('opencv-python')
            else:
                missing_packages.append(package)
    
    if missing_packages:
        print("❌ Відсутні необхідні пакети:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nВстановіть їх командою:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_chromedriver():
    """Перевірка наявності ChromeDriver"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Спроба створити драйвер
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.quit()
            return True
        except Exception:
            print("❌ ChromeDriver не знайдено або не працює")
            print("Завантажте ChromeDriver з https://chromedriver.chromium.org/")
            print("І додайте його до PATH або в директорію проекту")
            return False
            
    except Exception as e:
        print(f"❌ Помилка перевірки ChromeDriver: {e}")
        return False

def setup_environment():
    """Налаштування середовища"""
    try:
        # Створення необхідних директорій
        create_directories()
        
        # Налаштування логування
        setup_logging()
        
        # Завантаження конфігурації
        config_file = current_dir / "data" / "config.json"
        if config_file.exists():
            Config.load_config(config_file)
            
        logging.info("🚀 Instagram Bot запущено")
        logging.info(f"📁 Робоча директорія: {current_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка налаштування середовища: {e}")
        traceback.print_exc()
        return False

def run_gui():
    """Запуск графічного інтерфейсу"""
    try:
        print("🎨 Запуск графічного інтерфейсу...")
        app = InstagramBotGUI()
        app.run()
        
    except Exception as e:
        logging.error(f"Помилка GUI: {e}")
        traceback.print_exc()
        print(f"❌ Помилка запуску GUI: {e}")

def run_cli(args):
    """Запуск через командний рядок"""
    try:
        print("⚡ Запуск через командний рядок...")
        
        if not args.username or not args.password:
            print("❌ Вкажіть ім'я користувача та пароль")
            return False
            
        if not args.target:
            print("❌ Вкажіть цільового користувача")
            return False
            
        # Створення бота
        bot = InstagramBot(args.username, args.password, args.proxy)
        
        # Повідомлення для відповідей
        messages = Config.DEFAULT_STORY_REPLIES
        if args.messages:
            messages = args.messages.split(',')
            
        # Запуск автоматизації
        success = bot.run_automation(args.target, messages)
        
        if success:
            print("✅ Автоматизація завершена успішно!")
            return True
        else:
            print("❌ Автоматизація завершена з помилками!")
            return False
            
    except Exception as e:
        logging.error(f"Помилка CLI: {e}")
        traceback.print_exc()
        print(f"❌ Помилка CLI: {e}")
        return False
    finally:
        if 'bot' in locals():
            bot.close()

def main():
    """Головна функція"""
    # Парсинг аргументів командного рядка
    parser = argparse.ArgumentParser(
        description="Instagram Bot - Мобільна автоматизація",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади використання:

  Графічний інтерфейс:
    python run.py

  Командний рядок:
    python run.py --cli --username myuser --password mypass --target targetuser
    
  З проксі:
    python run.py --cli --username myuser --password mypass --target targetuser --proxy 127.0.0.1:8080
    
  З кастомними повідомленнями:
    python run.py --cli --username myuser --password mypass --target targetuser --messages "Nice!,Cool!,Amazing!"
        """
    )
    
    parser.add_argument('--cli', action='store_true', 
                       help='Запуск через командний рядок')
    parser.add_argument('--username', type=str, 
                       help='Ім\'я користувача Instagram')
    parser.add_argument('--password', type=str, 
                       help='Пароль Instagram')
    parser.add_argument('--target', type=str, 
                       help='Цільовий користувач')
    parser.add_argument('--proxy', type=str, 
                       help='Проксі сервер (ip:port:username:password)')
    parser.add_argument('--messages', type=str, 
                       help='Повідомлення для сторіс (через кому)')
    parser.add_argument('--headless', action='store_true', 
                       help='Запуск в headless режимі')
    parser.add_argument('--debug', action='store_true', 
                       help='Режим відладки')
    parser.add_argument('--check', action='store_true', 
                       help='Перевірка системи')
    
    args = parser.parse_args()
    
    # Налаштування рівня логування
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        Config.LOGGING['level'] = 'DEBUG'
    
    # Налаштування headless режиму
    if args.headless:
        Config.HEADLESS = True
    
    print("🤖 Instagram Bot - Мобільна автоматизація")
    print("=" * 50)
    
    # Перевірка системи
    if args.check:
        print("🔍 Перевірка системи...")
        
        print("📦 Перевірка залежностей...")
        if not check_requirements():
            return 1
        print("✅ Всі залежності встановлені")
        
        print("🌐 Перевірка ChromeDriver...")
        if not check_chromedriver():
            return 1
        print("✅ ChromeDriver працює")
        
        print("✅ Система готова до роботи!")
        return 0
    
    # Перевірка залежностей
    if not check_requirements():
        return 1
    
    # Перевірка ChromeDriver
    if not check_chromedriver():
        return 1
    
    # Налаштування середовища
    if not setup_environment():
        return 1
    
    try:
        if args.cli:
            # Запуск через командний рядок
            success = run_cli(args)
            return 0 if success else 1
        else:
            # Запуск GUI
            run_gui()
            return 0
            
    except KeyboardInterrupt:
        print("\n⏹️ Програма зупинена користувачем")
        return 0
    except Exception as e:
        logging.error(f"Критична помилка: {e}")
        traceback.print_exc()
        print(f"❌ Критична помилка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
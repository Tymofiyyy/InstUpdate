import random
import time
import requests
import sqlite3
import json
import cv2
import numpy as np
from PIL import Image
import pytesseract
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from config import Config
import logging
from datetime import datetime, timedelta
import hashlib
import base64
import threading
import re

class ProxyManager:
    """Менеджер проксі серверів"""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.failed_proxies = set()
        self.load_proxies()
        
    def load_proxies(self):
        """Завантаження списку проксі"""
        try:
            with open(Config.DATA_DIR / "proxies.txt", 'r') as f:
                self.proxies = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            self.proxies = Config.PROXY_SERVERS.copy()
            
    def get_proxy(self):
        """Отримання робочого проксі"""
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available_proxies:
            self.failed_proxies.clear()  # Очистка списку невдалих проксі
            available_proxies = self.proxies.copy()
            
        if available_proxies:
            self.current_proxy = random.choice(available_proxies)
            return self.current_proxy
            
        return None
        
    def mark_proxy_failed(self, proxy):
        """Позначення проксі як невдалого"""
        self.failed_proxies.add(proxy)
        
    def test_proxy(self, proxy):
        """Тестування проксі"""
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'https://{proxy}'
            }
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False

class DolphinAntyManager:
    """Менеджер для роботи з Dolphin Anty"""
    
    def __init__(self):
        self.api_endpoint = Config.get_dolphin_config().get("api_endpoint", "http://localhost:3001")
        self.profiles = {}
        self.logger = logging.getLogger("DolphinAntyManager")
        
    def create_profile(self, username, proxy=None):
        """Створення профілю в Dolphin Anty"""
        try:
            profile_name = Config.create_dolphin_profile_name(username)
            
            # Перевірка чи профіль вже існує
            existing_profile = self.get_profile(profile_name)
            if existing_profile:
                self.logger.info(f"Профіль {profile_name} вже існує")
                return existing_profile
            
            # Налаштування профілю
            profile_settings = self._create_profile_settings(username, proxy)
            
            # API запит для створення профілю
            url = f"{self.api_endpoint}/v1.0/browser_profiles"
            response = requests.post(url, json=profile_settings, timeout=30)
            
            if response.status_code == 201:
                profile_data = response.json()
                self.profiles[username] = profile_data
                self.logger.info(f"✅ Створено Dolphin профіль: {profile_name}")
                return profile_data
            else:
                self.logger.error(f"❌ Помилка створення профілю: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Помилка API Dolphin: {e}")
            return None
            
    def _create_profile_settings(self, username, proxy):
        """Створення налаштувань профілю"""
        dolphin_config = Config.get_dolphin_config()
        profile_settings = dolphin_config.get("profile_settings", {})
        
        # Випадковий пристрій
        device = Config.get_random_device()
        
        # Основні налаштування профілю
        settings = {
            "name": Config.create_dolphin_profile_name(username),
            "tags": ["instagram", "automation"],
            "platform": profile_settings.get("platform", "windows"),
            "browserType": "anty",
            "mainWebsite": "instagram.com",
            "useragent": {
                "mode": "manual",
                "value": device['user_agent']
            },
            "webrtc": {
                "mode": dolphin_config.get("webrtc_mode", "altered"),
                "fillBasedOnIp": True
            },
            "canvas": {
                "mode": dolphin_config.get("canvas_mode", "noise")
            },
            "webgl": {
                "mode": dolphin_config.get("webgl_mode", "noise")
            },
            "clientRects": {
                "mode": dolphin_config.get("client_rect_mode", "noise")
            },
            "timezone": {
                "mode": "auto",
                "value": "Europe/Kiev"
            },
            "locale": {
                "mode": "auto",
                "value": "en-US"
            },
            "geolocation": {
                "mode": "auto",
                "latitude": 50.4501,
                "longitude": 30.5234
            },
            "cpu": {
                "mode": "manual",
                "value": profile_settings.get("cpu", "4")
            },
            "memory": {
                "mode": "manual", 
                "value": profile_settings.get("memory", "8")
            },
            "screen": {
                "mode": "manual",
                "resolution": f"{device['width']}x{device['height']}",
                "scale": device['pixel_ratio']
            },
            "mediaDevices": {
                "mode": profile_settings.get("media_devices", "default")
            },
            "ports": {
                "mode": "protect",
                "blacklist": "3389,5900,5800,7070,6568,5938"
            }
        }
        
        # Додавання проксі якщо є
        if proxy:
            proxy_parts = proxy.split(':')
            if len(proxy_parts) >= 2:
                settings["proxy"] = {
                    "mode": "http",
                    "host": proxy_parts[0],
                    "port": int(proxy_parts[1]),
                    "username": proxy_parts[2] if len(proxy_parts) > 2 else "",
                    "password": proxy_parts[3] if len(proxy_parts) > 3 else ""
                }
        
        return settings
        
    def get_profile(self, profile_name):
        """Отримання існуючого профілю"""
        try:
            url = f"{self.api_endpoint}/v1.0/browser_profiles"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                profiles = response.json().get("data", [])
                for profile in profiles:
                    if profile.get("name") == profile_name:
                        return profile
            
            return None
            
        except Exception as e:
            self.logger.error(f"Помилка отримання профілю: {e}")
            return None
            
    def start_profile(self, username):
        """Запуск профілю"""
        try:
            profile_name = Config.create_dolphin_profile_name(username)
            
            # Отримання профілю
            profile = self.get_profile(profile_name)
            if not profile:
                self.logger.error(f"Профіль {profile_name} не знайдено")
                return None
            
            profile_id = profile.get("id")
            
            # Запуск профілю
            url = f"{self.api_endpoint}/v1.0/browser_profiles/{profile_id}/start"
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                automation_data = response.json()
                self.logger.info(f"✅ Запущено Dolphin профіль: {profile_name}")
                return automation_data
            else:
                self.logger.error(f"❌ Помилка запуску профілю: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Помилка запуску профілю: {e}")
            return None
            
    def stop_profile(self, username):
        """Зупинка профілю"""
        try:
            profile_name = Config.create_dolphin_profile_name(username)
            
            # Отримання профілю
            profile = self.get_profile(profile_name)
            if not profile:
                return True  # Профіль не існує, вважаємо зупиненим
            
            profile_id = profile.get("id")
            
            # Зупинка профілю
            url = f"{self.api_endpoint}/v1.0/browser_profiles/{profile_id}/stop"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"⏹️ Зупинено Dolphin профіль: {profile_name}")
                return True
            else:
                self.logger.warning(f"⚠️ Помилка зупинки профілю: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Помилка зупинки профілю: {e}")
            return False
            
    def delete_profile(self, username):
        """Видалення профілю"""
        try:
            profile_name = Config.create_dolphin_profile_name(username)
            
            # Спочатку зупиняємо профіль
            self.stop_profile(username)
            time.sleep(2)
            
            # Отримання профілю
            profile = self.get_profile(profile_name)
            if not profile:
                return True  # Профіль не існує
            
            profile_id = profile.get("id")
            
            # Видалення профілю
            url = f"{self.api_endpoint}/v1.0/browser_profiles/{profile_id}"
            response = requests.delete(url, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"🗑️ Видалено Dolphin профіль: {profile_name}")
                return True
            else:
                self.logger.error(f"❌ Помилка видалення профілю: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Помилка видалення профілю: {e}")
            return False
            
    def get_running_profiles(self):
        """Отримання списку запущених профілів"""
        try:
            url = f"{self.api_endpoint}/v1.0/browser_profiles/running"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("data", [])
            
            return []
            
        except Exception as e:
            self.logger.error(f"Помилка отримання запущених профілів: {e}")
            return []
            
    def cleanup_profiles(self, username_list=None):
        """Очищення профілів"""
        try:
            if username_list:
                # Очищення конкретних профілів
                for username in username_list:
                    self.delete_profile(username)
            else:
                # Очищення всіх профілів з префіксом
                prefix = Config.get_dolphin_config().get("profile_prefix", "instagram_")
                url = f"{self.api_endpoint}/v1.0/browser_profiles"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    profiles = response.json().get("data", [])
                    for profile in profiles:
                        if profile.get("name", "").startswith(prefix):
                            profile_id = profile.get("id")
                            delete_url = f"{self.api_endpoint}/v1.0/browser_profiles/{profile_id}"
                            requests.delete(delete_url, timeout=30)
                            
            self.logger.info("✅ Очищення профілів завершено")
            
        except Exception as e:
            self.logger.error(f"Помилка очищення профілів: {e}")

class TargetDistributor:
    """Розподіл таргетів між акаунтами"""
    
    def __init__(self):
        self.distributions = {}
        self.target_config = Config.get_target_distribution_config()
        self.logger = logging.getLogger("TargetDistributor")
        
    def distribute_targets(self, targets, accounts):
        """Розподіл таргетів між акаунтами"""
        try:
            if not targets or not accounts:
                self.logger.warning("Немає таргетів або акаунтів для розподілу")
                return
                
            strategy = self.target_config.get("strategy", "round_robin")
            avoid_duplicates = self.target_config.get("avoid_duplicates", True)
            min_targets = self.target_config.get("min_targets_per_account", 1)
            
            self.logger.info(f"🎯 Розподіл {len(targets)} таргетів між {len(accounts)} акаунтами")
            self.logger.info(f"📋 Стратегія: {strategy}")
            
            # Очищення попереднього розподілу
            self.distributions = {}
            
            # Ініціалізація списків для кожного акаунта
            for account in accounts:
                self.distributions[account] = []
            
            if strategy == "round_robin":
                self._distribute_round_robin(targets, accounts)
            elif strategy == "random":
                self._distribute_random(targets, accounts)
            elif strategy == "sequential":
                self._distribute_sequential(targets, accounts)
            else:
                # За замовчуванням round_robin
                self._distribute_round_robin(targets, accounts)
            
            # Валідація мінімальної кількості таргетів
            self._ensure_minimum_targets(min_targets)
            
            # Логування результатів
            self._log_distribution_results()
            
        except Exception as e:
            self.logger.error(f"❌ Помилка розподілу таргетів: {e}")
            
    def _distribute_round_robin(self, targets, accounts):
        """Рівномірний розподіл по колу"""
        for i, target in enumerate(targets):
            account_index = i % len(accounts)
            account = accounts[account_index]
            self.distributions[account].append(target)
            
    def _distribute_random(self, targets, accounts):
        """Випадковий розподіл"""
        targets_copy = targets.copy()
        random.shuffle(targets_copy)
        
        targets_per_account = len(targets_copy) // len(accounts)
        remainder = len(targets_copy) % len(accounts)
        
        start_idx = 0
        for i, account in enumerate(accounts):
            # Додаткові таргети для перших акаунтів якщо є залишок
            extra = 1 if i < remainder else 0
            end_idx = start_idx + targets_per_account + extra
            
            self.distributions[account] = targets_copy[start_idx:end_idx]
            start_idx = end_idx
            
    def _distribute_sequential(self, targets, accounts):
        """Послідовний розподіл"""
        targets_per_account = len(targets) // len(accounts)
        remainder = len(targets) % len(accounts)
        
        start_idx = 0
        for i, account in enumerate(accounts):
            extra = 1 if i < remainder else 0
            end_idx = start_idx + targets_per_account + extra
            
            self.distributions[account] = targets[start_idx:end_idx]
            start_idx = end_idx
            
    def _ensure_minimum_targets(self, min_targets):
        """Забезпечення мінімальної кількості таргетів для кожного акаунта"""
        if min_targets <= 0:
            return
            
        # Знаходження акаунтів з недостатньою кількістю таргетів
        accounts_need_more = []
        accounts_have_extra = []
        
        for account, targets in self.distributions.items():
            if len(targets) < min_targets:
                accounts_need_more.append(account)
            elif len(targets) > min_targets:
                accounts_have_extra.append(account)
        
        # Перерозподіл таргетів
        for account_need in accounts_need_more:
            while len(self.distributions[account_need]) < min_targets and accounts_have_extra:
                # Знаходимо акаунт з найбільшою кількістю таргетів
                donor_account = max(accounts_have_extra, 
                                  key=lambda x: len(self.distributions[x]))
                
                if len(self.distributions[donor_account]) > min_targets:
                    # Переносимо таргет
                    target = self.distributions[donor_account].pop()
                    self.distributions[account_need].append(target)
                    
                    # Якщо у донора залишилось мінімум, видаляємо його зі списку
                    if len(self.distributions[donor_account]) <= min_targets:
                        accounts_have_extra.remove(donor_account)
                else:
                    break
                    
    def _log_distribution_results(self):
        """Логування результатів розподілу"""
        total_distributed = sum(len(targets) for targets in self.distributions.values())
        
        self.logger.info("📊 Результати розподілу таргетів:")
        for account, targets in self.distributions.items():
            preview = ', '.join(targets[:3])
            if len(targets) > 3:
                preview += f"... (всього {len(targets)})"
            self.logger.info(f"  👤 {account}: {len(targets)} таргетів - {preview}")
        
        self.logger.info(f"✅ Розподілено {total_distributed} таргетів")
        
    def get_targets_for_account(self, username):
        """Отримання таргетів для конкретного акаунта"""
        return self.distributions.get(username, [])
        
    def get_distribution_stats(self):
        """Статистика розподілу"""
        if not self.distributions:
            return {}
            
        target_counts = [len(targets) for targets in self.distributions.values()]
        
        return {
            "total_accounts": len(self.distributions),
            "total_targets": sum(target_counts),
            "min_targets_per_account": min(target_counts) if target_counts else 0,
            "max_targets_per_account": max(target_counts) if target_counts else 0,
            "avg_targets_per_account": sum(target_counts) / len(target_counts) if target_counts else 0,
            "distribution": dict(self.distributions)
        }
        
    def save_distribution(self, filename=None):
        """Збереження розподілу у файл"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = Config.DATA_DIR / f"target_distribution_{timestamp}.json"
            
            distribution_data = {
                "timestamp": datetime.now().isoformat(),
                "config": self.target_config,
                "stats": self.get_distribution_stats(),
                "distributions": self.distributions
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(distribution_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"💾 Розподіл збережено: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка збереження розподілу: {e}")
            return False
            
    def load_distribution(self, filename):
        """Завантаження розподілу з файлу"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                distribution_data = json.load(f)
                
            self.distributions = distribution_data.get("distributions", {})
            self.logger.info(f"📁 Розподіл завантажено: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка завантаження розподілу: {e}")
            return False

class CaptchaSolver:
    """Розв'язувач капчі"""
    
    def __init__(self):
        self.api_key = Config.CAPTCHA_SOLVER.get("api_key")
        self.service = Config.CAPTCHA_SOLVER.get("service", "2captcha")
        self.timeout = Config.CAPTCHA_SOLVER.get("timeout", 120)
        
    def solve_text_captcha(self, image_path):
        """Розв'язування текстової капчі"""
        try:
            # Спочатку спробуємо локальне розпізнавання
            local_result = self.solve_local_captcha(image_path)
            if local_result:
                return local_result
                
            # Якщо локальне не спрацювало, використовуємо сервіс
            if self.api_key:
                return self.solve_service_captcha(image_path)
                
        except Exception as e:
            logging.error(f"Помилка при розв'язуванні капчі: {e}")
            
        return None
        
    def solve_local_captcha(self, image_path):
        """Локальне розпізнавання капчі"""
        try:
            # Завантаження та обробка зображення
            image = cv2.imread(image_path)
            
            # Конвертація в сірий
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Зменшення шуму
            denoised = cv2.medianBlur(gray, 3)
            
            # Бінаризація
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Морфологічні операції
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Розпізнавання тексту
            text = pytesseract.image_to_string(
                cleaned,
                config='--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            ).strip()
            
            # Фільтрація результату
            if len(text) >= 4 and text.isalnum():
                return text
                
        except Exception as e:
            logging.error(f"Помилка локального розпізнавання: {e}")
            
        return None
        
    def solve_service_captcha(self, image_path):
        """Розв'язування через сервіс"""
        if self.service == "2captcha":
            return self.solve_2captcha(image_path)
        elif self.service == "anticaptcha":
            return self.solve_anticaptcha(image_path)
        elif self.service == "deathbycaptcha":
            return self.solve_deathbycaptcha(image_path)
            
        return None
        
    def solve_2captcha(self, image_path):
        """Розв'язування через 2captcha"""
        try:
            # Завантаження зображення
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
                
            # Відправка капчі
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                'method': 'base64',
                'key': self.api_key,
                'body': image_data
            }
            
            response = requests.post(submit_url, data=submit_data, timeout=30)
            
            if response.text.startswith('OK|'):
                captcha_id = response.text.split('|')[1]
                
                # Очікування результату
                result_url = f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}"
                
                for _ in range(self.timeout // 5):
                    time.sleep(5)
                    result = requests.get(result_url, timeout=30)
                    
                    if result.text.startswith('OK|'):
                        return result.text.split('|')[1]
                    elif result.text != 'CAPCHA_NOT_READY':
                        break
                        
        except Exception as e:
            logging.error(f"Помилка 2captcha: {e}")
            
        return None

class AntiDetection:
    """Клас для обходу детекції ботів"""
    
    def __init__(self):
        self.mouse_movements = []
        self.typing_patterns = []
        
    def human_typing(self, element, text):
        """Імітація людського введення тексту"""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            
            # Випадкова затримка між символами
            delay = random.uniform(
                Config.HUMAN_DELAY_MIN,
                Config.HUMAN_DELAY_MAX
            )
            time.sleep(delay)
            
            # Випадкові помилки та виправлення
            if random.random() < 0.05:  # 5% шанс помилки
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.2))
                
    def random_mouse_movement(self, driver):
        """Рандомні рухи миші"""
        try:
            action = ActionChains(driver)
            
            # Генерація випадкових координат
            x = random.randint(100, 300)
            y = random.randint(100, 400)
            
            # Рух миші
            action.move_by_offset(x, y)
            action.perform()
            
            time.sleep(random.uniform(0.1, 0.5))
            
            # Повернення в початкову позицію
            action.move_by_offset(-x, -y)
            action.perform()
            
        except Exception as e:
            logging.error(f"Помилка руху миші: {e}")
            
    def random_scroll(self, driver):
        """Рандомний скрол"""
        try:
            scroll_amount = random.randint(-300, 300)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logging.error(f"Помилка скролу: {e}")
            
    def simulate_reading(self, driver, duration=None):
        """Імітація читання сторінки"""
        if not duration:
            duration = random.uniform(2, 8)
            
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Рандомний скрол
            if random.random() < 0.3:
                self.random_scroll(driver)
                
            # Рандомний рух миші
            if random.random() < 0.2:
                self.random_mouse_movement(driver)
                
            time.sleep(random.uniform(0.5, 2))
            
    def change_viewport(self, driver):
        """Зміна розміру вікна"""
        try:
            device = Config.get_random_device()
            driver.set_window_size(device['width'], device['height'])
            
        except Exception as e:
            logging.error(f"Помилка зміни viewport: {e}")

class DatabaseManager:
    """Менеджер бази даних"""
    
    def __init__(self):
        self.db_path = Config.DATABASE["path"]
        self.init_database()
        
    def init_database(self):
        """Ініціалізація бази даних"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблиця акаунтів
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        proxy TEXT,
                        browser_type TEXT DEFAULT 'chrome',
                        status TEXT DEFAULT 'active',
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        followers_count INTEGER DEFAULT 0,
                        following_count INTEGER DEFAULT 0,
                        posts_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблиця дій
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_username TEXT NOT NULL,
                        action_type TEXT NOT NULL,
                        target_username TEXT,
                        success BOOLEAN DEFAULT FALSE,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        details TEXT,
                        FOREIGN KEY (account_username) REFERENCES accounts (username)
                    )
                ''')
                
                # Таблиця сесій
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_username TEXT NOT NULL,
                        session_data TEXT NOT NULL,
                        browser_type TEXT DEFAULT 'chrome',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        FOREIGN KEY (account_username) REFERENCES accounts (username)
                    )
                ''')
                
                # Таблиця статистики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_username TEXT NOT NULL,
                        date DATE NOT NULL,
                        likes_count INTEGER DEFAULT 0,
                        comments_count INTEGER DEFAULT 0,
                        follows_count INTEGER DEFAULT 0,
                        stories_count INTEGER DEFAULT 0,
                        messages_count INTEGER DEFAULT 0,
                        FOREIGN KEY (account_username) REFERENCES accounts (username),
                        UNIQUE(account_username, date)
                    )
                ''')
                
                # Таблиця розподілу таргетів
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS target_distributions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        account_username TEXT NOT NULL,
                        target_username TEXT NOT NULL,
                        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed BOOLEAN DEFAULT FALSE,
                        processed_at TIMESTAMP,
                        success BOOLEAN,
                        FOREIGN KEY (account_username) REFERENCES accounts (username)
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка ініціалізації БД: {e}")
            
    def add_account(self, username, password, proxy=None, browser_type="chrome"):
        """Додавання акаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO accounts (username, password, proxy, browser_type)
                    VALUES (?, ?, ?, ?)
                ''', (username, password, proxy, browser_type))
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Помилка додавання акаунта: {e}")
            return False
            
    def get_account(self, username):
        """Отримання акаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM accounts WHERE username = ?
                ''', (username,))
                return cursor.fetchone()
                
        except Exception as e:
            logging.error(f"Помилка отримання акаунта: {e}")
            return None
            
    def get_all_accounts(self):
        """Отримання всіх акаунтів"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM accounts')
                return cursor.fetchall()
                
        except Exception as e:
            logging.error(f"Помилка отримання акаунтів: {e}")
            return []
            
    def update_account_status(self, username, status):
        """Оновлення статусу акаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE accounts SET status = ?, last_activity = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (status, username))
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Помилка оновлення статусу: {e}")
            return False
            
    def log_action(self, account_username, action_type, target_username=None, success=True, details=None):
        """Логування дії"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO actions (account_username, action_type, target_username, success, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (account_username, action_type, target_username, success, details))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка логування дії: {e}")
            
    def save_target_distribution(self, session_id, distributions):
        """Збереження розподілу таргетів"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for account_username, targets in distributions.items():
                    for target in targets:
                        cursor.execute('''
                            INSERT INTO target_distributions 
                            (session_id, account_username, target_username)
                            VALUES (?, ?, ?)
                        ''', (session_id, account_username, target))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка збереження розподілу таргетів: {e}")
            
    def get_targets_for_account(self, account_username, session_id):
        """Отримання таргетів для акаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT target_username FROM target_distributions
                    WHERE account_username = ? AND session_id = ? AND processed = FALSE
                ''', (account_username, session_id))
                
                results = cursor.fetchall()
                return [row[0] for row in results]
                
        except Exception as e:
            logging.error(f"Помилка отримання таргетів: {e}")
            return []
            
    def mark_target_processed(self, account_username, target_username, session_id, success=True):
        """Позначення таргета як обробленого"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE target_distributions 
                    SET processed = TRUE, processed_at = CURRENT_TIMESTAMP, success = ?
                    WHERE account_username = ? AND target_username = ? AND session_id = ?
                ''', (success, account_username, target_username, session_id))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка позначення таргета: {e}")
            
    def get_today_actions(self, account_username):
        """Отримання дій за сьогодні"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT action_type, COUNT(*) as count
                    FROM actions
                    WHERE account_username = ? AND DATE(timestamp) = DATE('now')
                    GROUP BY action_type
                ''', (account_username,))
                return dict(cursor.fetchall())
                
        except Exception as e:
            logging.error(f"Помилка отримання дій: {e}")
            return {}
            
    def save_followers_count(self, username, count):
        """Збереження кількості підписників"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE accounts SET followers_count = ? WHERE username = ?
                ''', (count, username))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка збереження кількості підписників: {e}")
            
    def get_followers_count(self, username):
        """Отримання кількості підписників"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT followers_count FROM accounts WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logging.error(f"Помилка отримання кількості підписників: {e}")
            return None
            
    def cleanup_old_data(self, days=30):
        """Очищення старих даних"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Видалення старих дій
                cursor.execute('''
                    DELETE FROM actions
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                # Видалення старих сесій
                cursor.execute('''
                    DELETE FROM sessions
                    WHERE expires_at < datetime('now')
                ''')
                
                # Видалення старих розподілів таргетів
                cursor.execute('''
                    DELETE FROM target_distributions
                    WHERE assigned_at < datetime('now', '-{} days')
                '''.format(days))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка очищення даних: {e}")

class SecurityManager:
    """Менеджер безпеки"""
    
    def __init__(self):
        self.action_limits = Config.SECURITY
        self.db = DatabaseManager()
        
    def can_perform_action(self, username, action_type):
        """Перевірка можливості виконання дії"""
        try:
            today_actions = self.db.get_today_actions(username)
            
            # Перевірка лімітів
            if action_type == 'like' and today_actions.get('like', 0) >= self.action_limits['max_actions_per_day']:
                return False
                
            if action_type == 'comment' and today_actions.get('comment', 0) >= Config.MAX_COMMENTS_PER_SESSION:
                return False
                
            if action_type == 'follow' and today_actions.get('follow', 0) >= Config.MAX_FOLLOWS_PER_SESSION:
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Помилка перевірки лімітів: {e}")
            return False
            
    def get_recommended_delay(self, action_type):
        """Отримання рекомендованої затримки"""
        base_delays = {
            'like': (2, 5),
            'comment': (10, 20),
            'follow': (15, 30),
            'story_reply': (5, 10)
        }
        
        min_delay, max_delay = base_delays.get(action_type, (1, 3))
        
        # Додавання випадковості
        multiplier = random.uniform(0.8, 1.5)
        
        return (min_delay * multiplier, max_delay * multiplier)

class MessageManager:
    """Менеджер повідомлень"""
    
    def __init__(self):
        self.messages = []
        self.load_messages()
        
    def load_messages(self):
        """Завантаження повідомлень"""
        try:
            with open(Config.DATA_DIR / "messages.txt", 'r', encoding='utf-8') as f:
                self.messages = [line.strip() for line in f.readlines() if line.strip()]
                
            if not self.messages:
                self.messages = Config.DEFAULT_STORY_REPLIES.copy()
                
        except FileNotFoundError:
            self.messages = Config.DEFAULT_STORY_REPLIES.copy()
            
    def get_random_message(self):
        """Отримання випадкового повідомлення"""
        return random.choice(self.messages) if self.messages else "Nice! 😊"
        
    def add_message(self, message):
        """Додавання повідомлення"""
        if message not in self.messages:
            self.messages.append(message)
            self.save_messages()
            
    def remove_message(self, message):
        """Видалення повідомлення"""
        if message in self.messages:
            self.messages.remove(message)
            self.save_messages()
            
    def save_messages(self):
        """Збереження повідомлень"""
        try:
            with open(Config.DATA_DIR / "messages.txt", 'w', encoding='utf-8') as f:
                for message in self.messages:
                    f.write(message + '\n')
                    
        except Exception as e:
            logging.error(f"Помилка збереження повідомлень: {e}")

class SessionManager:
    """Менеджер сесій для різних браузерів"""
    
    def __init__(self):
        self.active_sessions = {}
        self.dolphin_manager = DolphinAntyManager()
        self.logger = logging.getLogger("SessionManager")
        
    def create_session(self, username, browser_type, account_data):
        """Створення сесії для акаунта"""
        try:
            session_id = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session_info = {
                'session_id': session_id,
                'username': username,
                'browser_type': browser_type.lower(),
                'account_data': account_data,
                'created_at': datetime.now(),
                'status': 'created'
            }
            
            if browser_type.lower() == 'dolphin anty':
                # Для Dolphin Anty створюємо профіль
                profile_data = self.dolphin_manager.create_profile(
                    username, 
                    account_data.get('proxy')
                )
                if profile_data:
                    session_info['dolphin_profile'] = profile_data
                    session_info['status'] = 'profile_created'
                else:
                    raise Exception("Не вдалося створити Dolphin профіль")
            
            self.active_sessions[username] = session_info
            self.logger.info(f"✅ Сесія створена для {username} ({browser_type})")
            
            return session_info
            
        except Exception as e:
            self.logger.error(f"❌ Помилка створення сесії для {username}: {e}")
            return None
            
    def start_session(self, username):
        """Запуск сесії"""
        try:
            if username not in self.active_sessions:
                self.logger.error(f"Сесія для {username} не знайдена")
                return None
                
            session_info = self.active_sessions[username]
            browser_type = session_info['browser_type']
            
            if browser_type == 'dolphin anty':
                # Запуск Dolphin профілю
                automation_data = self.dolphin_manager.start_profile(username)
                if automation_data:
                    session_info['automation_data'] = automation_data
                    session_info['status'] = 'running'
                    self.logger.info(f"🚀 Dolphin сесія запущена для {username}")
                    return automation_data
                else:
                    raise Exception("Не вдалося запустити Dolphin профіль")
            else:
                # Для Chrome просто позначаємо як запущену
                session_info['status'] = 'running'
                self.logger.info(f"🚀 Chrome сесія запущена для {username}")
                return {'browser_type': 'chrome'}
                
        except Exception as e:
            self.logger.error(f"❌ Помилка запуску сесії для {username}: {e}")
            return None
            
    def stop_session(self, username):
        """Зупинка сесії"""
        try:
            if username not in self.active_sessions:
                return True
                
            session_info = self.active_sessions[username]
            browser_type = session_info['browser_type']
            
            if browser_type == 'dolphin anty':
                # Зупинка Dolphin профілю
                success = self.dolphin_manager.stop_profile(username)
                if success:
                    session_info['status'] = 'stopped'
                    self.logger.info(f"⏹️ Dolphin сесія зупинена для {username}")
                return success
            else:
                # Для Chrome просто позначаємо як зупинену
                session_info['status'] = 'stopped'
                self.logger.info(f"⏹️ Chrome сесія зупинена для {username}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Помилка зупинки сесії для {username}: {e}")
            return False
            
    def cleanup_session(self, username, delete_profile=False):
        """Очищення сесії"""
        try:
            if username in self.active_sessions:
                session_info = self.active_sessions[username]
                browser_type = session_info['browser_type']
                
                # Спочатку зупиняємо
                self.stop_session(username)
                
                if browser_type == 'dolphin anty' and delete_profile:
                    # Видалення Dolphin профілю
                    self.dolphin_manager.delete_profile(username)
                
                # Видалення з активних сесій
                del self.active_sessions[username]
                self.logger.info(f"🧹 Сесія очищена для {username}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Помилка очищення сесії для {username}: {e}")
            return False

class BrowserSwitcher:
    """Клас для перемикання між браузерами"""
    
    def __init__(self):
        self.current_browser = None
        self.session_manager = SessionManager()
        self.logger = logging.getLogger("BrowserSwitcher")
        
    def set_browser(self, browser_type):
        """Встановлення типу браузера"""
        supported_browsers = ["chrome", "dolphin anty"]
        browser_type = browser_type.lower()
        
        if browser_type not in supported_browsers:
            self.logger.error(f"Непідтримуваний браузер: {browser_type}")
            return False
            
        self.current_browser = browser_type
        self.logger.info(f"🌐 Встановлено браузер: {browser_type}")
        return True
        
    def get_current_browser(self):
        """Отримання поточного браузера"""
        return self.current_browser
        
    def is_dolphin_available(self):
        """Перевірка доступності Dolphin Anty"""
        try:
            dolphin_config = Config.get_dolphin_config()
            api_endpoint = dolphin_config.get("api_endpoint", "http://localhost:3001")
            
            response = requests.get(f"{api_endpoint}/v1.0/browser_profiles", timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.warning(f"Dolphin Anty недоступний: {e}")
            return False
            
    def get_available_browsers(self):
        """Отримання списку доступних браузерів"""
        browsers = ["chrome"]
        
        if self.is_dolphin_available():
            browsers.append("dolphin anty")
            
        return browsers
        
    def validate_browser_choice(self, browser_type):
        """Валідація вибору браузера"""
        available = self.get_available_browsers()
        
        if browser_type.lower() not in available:
            self.logger.error(f"Браузер {browser_type} недоступний. Доступні: {', '.join(available)}")
            return False
            
        return True

class AccountValidator:
    """Валідатор акаунтів та їх налаштувань"""
    
    def __init__(self):
        self.logger = logging.getLogger("AccountValidator")
        
    def validate_account_credentials(self, username, password):
        """Валідація облікових даних"""
        errors = []
        
        # Перевірка username
        if not username or len(username.strip()) == 0:
            errors.append("Username не може бути порожнім")
        elif len(username) < 3:
            errors.append("Username занадто короткий (мінімум 3 символи)")
        elif len(username) > 30:
            errors.append("Username занадто довгий (максимум 30 символів)")
        
        # Перевірка на недозволені символи
        if not re.match("^[a-zA-Z0-9._]+$", username):
            errors.append("Username містить недозволені символи")
        
        # Перевірка password
        if not password or len(password.strip()) == 0:
            errors.append("Password не може бути порожнім")
        elif len(password) < 6:
            errors.append("Password занадто короткий (мінімум 6 символів)")
        
        return len(errors) == 0, errors
        
    def validate_proxy_format(self, proxy_string):
        """Валідація формату проксі"""
        if not proxy_string:
            return True, []  # Проксі опціонально
            
        errors = []
        parts = proxy_string.split(':')
        
        if len(parts) < 2:
            errors.append("Неправильний формат проксі (очікується ip:port або ip:port:user:pass)")
            return False, errors
        
        # Перевірка IP
        ip = parts[0]
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}'
                        
        if not re.match(ip_pattern, ip):
            errors.append("Неправильний формат IP адреси")
        else:
            # Перевірка діапазону IP
            ip_parts = ip.split('.')
            for part in ip_parts:
                if not (0 <= int(part) <= 255):
                    errors.append("IP адреса поза допустимим діапазоном")
                    break
        
        # Перевірка порту
        try:
            port = int(parts[1])
            if not (1 <= port <= 65535):
                errors.append("Порт поза допустимим діапазоном (1-65535)")
        except ValueError:
            errors.append("Порт повинен бути числом")
        
        return len(errors) == 0, errors

def setup_logging():
    """Налаштування логування"""
    log_format = Config.LOGGING["format"]
    log_level = getattr(logging, Config.LOGGING["level"])
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(Config.LOGS_DIR / "app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def create_directories():
    """Створення необхідних директорій"""
    directories = [
        Config.LOGS_DIR,
        Config.SESSIONS_DIR,
        Config.TEMP_DIR,
        Config.DATA_DIR
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)

def generate_device_fingerprint():
    """Генерація відбитка пристрою"""
    device = Config.get_random_device()
    user_agent = device['user_agent']
    
    # Створення унікального відбитка
    fingerprint_data = {
        'user_agent': user_agent,
        'screen_resolution': f"{device['width']}x{device['height']}",
        'pixel_ratio': device['pixel_ratio'],
        'timezone': random.choice(['Europe/Kiev', 'Europe/Moscow', 'Europe/Warsaw']),
        'language': 'uk-UA',
        'platform': 'iPhone' if 'iPhone' in user_agent else 'Android'
    }
    
    # Хешування відбитка
    fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
    fingerprint_hash = hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    return fingerprint_hash, fingerprint_data

# Глобальні менеджери
_user_agent_rotator = None
_proxy_rotator = None
_performance_monitor = None
_error_handler = None

def get_user_agent_rotator():
    """Отримання глобального ротатора User-Agent"""
    global _user_agent_rotator
    if _user_agent_rotator is None:
        from utils import UserAgentRotator
        _user_agent_rotator = UserAgentRotator()
    return _user_agent_rotator

def get_proxy_rotator():
    """Отримання глобального ротатора проксі"""
    global _proxy_rotator
    if _proxy_rotator is None:
        from utils import ProxyRotator
        _proxy_rotator = ProxyRotator()
    return _proxy_rotator

def initialize_utils():
    """Ініціалізація всіх утиліт"""
    logging.info("🔧 Ініціалізація утиліт...")
    
    # Створення директорій
    create_directories()
    
    # Налаштування логування
    setup_logging()
    
    logging.info("✅ Утиліти ініціалізовано")

def finalize_utils():
    """Фінальне очищення утиліт"""
    logging.info("🧹 Фінальне очищення...")
    logging.info("✅ Очищення завершено")

if __name__ == "__main__":
    # Тестування утиліт
    initialize_utils()
    
    print("🧪 Тестування утиліт Instagram Bot...")
    
    # Тест Dolphin Anty Manager
    dolphin = DolphinAntyManager()
    print(f"🐬 Dolphin Anty доступний: {BrowserSwitcher().is_dolphin_available()}")
    
    # Тест розподілу таргетів
    distributor = TargetDistributor()
    test_targets = ["user1", "user2", "user3", "user4", "user5"]
    test_accounts = ["account1", "account2"]
    
    distributor.distribute_targets(test_targets, test_accounts)
    print("🎯 Тест розподілу таргетів:")
    for account, targets in distributor.distributions.items():
        print(f"  {account}: {targets}")
    
    # Тест валідації
    validator = AccountValidator()
    valid, errors = validator.validate_account_credentials("test_user", "password123")
    print(f"✅ Валідація акаунта: {valid}")
    if errors:
        print(f"❌ Помилки: {errors}")
    
    finalize_utils()
    print("🎉 Тестування завершено!")

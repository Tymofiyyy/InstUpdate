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
                        FOREIGN KEY (account_username) REFERENCES accounts (username),
                        UNIQUE(account_username, date)
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Помилка ініціалізації БД: {e}")
            
    def add_account(self, username, password, proxy=None):
        """Додавання акаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO accounts (username, password, proxy)
                    VALUES (?, ?, ?)
                ''', (username, password, proxy))
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

class ParallelBotManager:
    """Менеджер для паралельної роботи кількох ботів"""
    
    def __init__(self, max_parallel=5):
        self.max_parallel = max_parallel
        self.active_bots = {}
        self.bot_threads = {}
        self.results = {}
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        self.logger = logging.getLogger('ParallelBotManager')
        self.resource_monitor = ResourceMonitor()
        
    def add_bot(self, account_data):
        """Додавання бота до черги"""
        username = account_data['username']
        
        with self.lock:
            if username in self.active_bots:
                self.logger.warning(f"Бот {username} вже активний")
                return False
                
            self.active_bots[username] = {
                'account_data': account_data,
                'status': 'pending',
                'start_time': None,
                'end_time': None,
                'actions_completed': 0,
                'errors': []
            }
            
        return True
        
    def run_bots(self, target_users, messages, actions_config=None):
        """Запуск ботів паралельно з управлінням ресурсами"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        total_accounts = len(self.active_bots)
        self.logger.info(f"🚀 Запуск {total_accounts} ботів (макс. паралельно: {self.max_parallel})")
        
        # Створюємо пул потоків
        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            futures = {}
            
            # Розбиваємо акаунти на батчі
            accounts_list = list(self.active_bots.items())
            
            for i in range(0, len(accounts_list), self.max_parallel):
                batch = accounts_list[i:i + self.max_parallel]
                
                # Запускаємо батч
                for username, bot_info in batch:
                    if self.resource_monitor.can_start_new_bot():
                        future = executor.submit(
                            self._run_single_bot,
                            username,
                            bot_info['account_data'],
                            target_users,
                            messages,
                            actions_config
                        )
                        futures[future] = username
                        
                        # Затримка між запусками
                        time.sleep(Config.PARALLEL_SETTINGS['account_start_delay'])
                    else:
                        self.logger.warning(f"⚠️ Недостатньо ресурсів для {username}")
                        bot_info['status'] = 'skipped'
                        bot_info['errors'].append("Insufficient resources")
                
                # Чекаємо завершення батча перед запуском наступного
                if i + self.max_parallel < len(accounts_list):
                    self.logger.info(f"⏳ Очікування завершення батча перед наступним...")
                    for future in as_completed(futures):
                        username = futures[future]
                        try:
                            result = future.result()
                            self._process_bot_result(username, result)
                        except Exception as e:
                            self._handle_bot_error(username, e)
                    
                    # Очищуємо futures для наступного батча
                    futures.clear()
                    
                    # Пауза між батчами
                    batch_delay = Config.MULTI_USER_CONFIG['batch_processing']['batch_delay']
                    self.logger.info(f"⏰ Пауза між батчами: {batch_delay} сек")
                    time.sleep(batch_delay)
            
            # Обробка останнього батча
            for future in as_completed(futures):
                username = futures[future]
                try:
                    result = future.result()
                    self._process_bot_result(username, result)
                except Exception as e:
                    self._handle_bot_error(username, e)
        
        # Генерація звіту
        return self._generate_report()
        
    def _run_single_bot(self, username, account_data, target_users, messages, actions_config):
        """Запуск одного бота в окремому потоці"""
        from instagram_bot import InstagramBot
        
        bot = None
        try:
            # Оновлення статусу
            with self.lock:
                self.active_bots[username]['status'] = 'running'
                self.active_bots[username]['start_time'] = datetime.now()
            
            # Створення та запуск бота
            bot = InstagramBot(
                account_data['username'],
                account_data['password'],
                account_data.get('proxy'),
                account_data.get('browser_type', 'Chrome')
            )
            
            # Встановлення обмежень ресурсів
            self.resource_monitor.set_bot_limits(username, bot)
            
            # Запуск автоматизації
            success = bot.run_automation_multiple_users(
                target_users,
                messages,
                actions_config
            )
            
            # Збір статистики
            stats = self._collect_bot_stats(bot)
            
            return {
                'success': success,
                'stats': stats,
                'errors': []
            }
            
        except Exception as e:
            self.logger.error(f"❌ Помилка бота {username}: {e}")
            return {
                'success': False,
                'stats': {},
                'errors': [str(e)]
            }
        finally:
            # Закриття бота
            if bot:
                try:
                    bot.close()
                except:
                    pass
            
            # Оновлення статусу
            with self.lock:
                self.active_bots[username]['status'] = 'completed'
                self.active_bots[username]['end_time'] = datetime.now()
                
    def _process_bot_result(self, username, result):
        """Обробка результату роботи бота"""
        with self.lock:
            bot_info = self.active_bots[username]
            bot_info['success'] = result['success']
            bot_info['stats'] = result.get('stats', {})
            bot_info['errors'].extend(result.get('errors', []))
            
            if result['success']:
                self.logger.info(f"✅ Бот {username} завершив успішно")
            else:
                self.logger.error(f"❌ Бот {username} завершив з помилками")
                
    def _handle_bot_error(self, username, error):
        """Обробка помилки бота"""
        with self.lock:
            bot_info = self.active_bots[username]
            bot_info['status'] = 'error'
            bot_info['success'] = False
            bot_info['errors'].append(str(error))
            bot_info['end_time'] = datetime.now()
            
        self.logger.error(f"❌ Критична помилка для {username}: {error}")
        
    def _collect_bot_stats(self, bot):
        """Збір статистики роботи бота"""
        stats = {
            'likes': 0,
            'comments': 0,
            'follows': 0,
            'stories': 0,
            'messages': 0,
            'total_actions': 0
        }
        
        # Тут можна додати логіку збору статистики з бота
        # Наприклад, через його внутрішні лічильники
        
        return stats
        
    def _generate_report(self):
        """Генерація детального звіту"""
        report = {
            'summary': {
                'total_accounts': len(self.active_bots),
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'total_time': (datetime.now() - self.start_time).total_seconds()
            },
            'accounts': {},
            'statistics': {
                'total_likes': 0,
                'total_comments': 0,
                'total_follows': 0,
                'total_stories': 0,
                'total_messages': 0
            }
        }
        
        with self.lock:
            for username, bot_info in self.active_bots.items():
                # Підрахунок статусів
                if bot_info['status'] == 'completed' and bot_info.get('success'):
                    report['summary']['successful'] += 1
                elif bot_info['status'] == 'error' or not bot_info.get('success'):
                    report['summary']['failed'] += 1
                elif bot_info['status'] == 'skipped':
                    report['summary']['skipped'] += 1
                
                # Збір статистики
                stats = bot_info.get('stats', {})
                for key in ['likes', 'comments', 'follows', 'stories', 'messages']:
                    report['statistics'][f'total_{key}'] += stats.get(key, 0)
                
                # Інформація про акаунт
                report['accounts'][username] = {
                    'status': bot_info['status'],
                    'success': bot_info.get('success', False),
                    'start_time': bot_info['start_time'].isoformat() if bot_info['start_time'] else None,
                    'end_time': bot_info['end_time'].isoformat() if bot_info['end_time'] else None,
                    'duration': (bot_info['end_time'] - bot_info['start_time']).total_seconds() 
                               if bot_info['start_time'] and bot_info['end_time'] else None,
                    'stats': stats,
                    'errors': bot_info['errors']
                }
        
        # Розрахунок показників
        report['summary']['success_rate'] = (
            report['summary']['successful'] / report['summary']['total_accounts'] * 100
            if report['summary']['total_accounts'] > 0 else 0
        )
        
        report['summary']['avg_time_per_account'] = (
            report['summary']['total_time'] / report['summary']['total_accounts']
            if report['summary']['total_accounts'] > 0 else 0
        )
        
        # Виведення звіту
        self._print_report(report)
        
        # Збереження звіту
        self._save_report(report)
        
        return report
        
    def _print_report(self, report):
        """Виведення звіту в консоль"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 ЗВІТ ПАРАЛЕЛЬНОЇ РОБОТИ БОТІВ")
        self.logger.info("=" * 60)
        
        summary = report['summary']
        self.logger.info(f"👥 Всього акаунтів: {summary['total_accounts']}")
        self.logger.info(f"✅ Успішно: {summary['successful']}")
        self.logger.info(f"❌ З помилками: {summary['failed']}")
        self.logger.info(f"⏭️ Пропущено: {summary['skipped']}")
        self.logger.info(f"📈 Успішність: {summary['success_rate']:.1f}%")
        self.logger.info(f"⏱️ Загальний час: {summary['total_time']:.1f} сек")
        self.logger.info(f"⏳ Середній час на акаунт: {summary['avg_time_per_account']:.1f} сек")
        
        self.logger.info("\n📊 СТАТИСТИКА ДІЙ:")
        stats = report['statistics']
        self.logger.info(f"❤️ Лайків: {stats['total_likes']}")
        self.logger.info(f"💬 Коментарів: {stats['total_comments']}")
        self.logger.info(f"👥 Підписок: {stats['total_follows']}")
        self.logger.info(f"📱 Сторіс: {stats['total_stories']}")
        self.logger.info(f"📩 Повідомлень: {stats['total_messages']}")
        
        self.logger.info("=" * 60)
        
    def _save_report(self, report):
        """Збереження звіту у файл"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = Config.DATA_DIR / f"parallel_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"💾 Звіт збережено: {filename}")
            
        except Exception as e:
            self.logger.error(f"Помилка збереження звіту: {e}")
            
    def stop_all_bots(self):
        """Зупинка всіх активних ботів"""
        self.logger.warning("⏹️ Зупинка всіх ботів...")
        
        with self.lock:
            for username in self.active_bots:
                if self.active_bots[username]['status'] == 'running':
                    # Тут можна додати логіку примусової зупинки
                    self.active_bots[username]['status'] = 'stopped'
                    
        self.logger.info("✅ Всі боти зупинені")


class ResourceMonitor:
    """Моніторинг ресурсів для паралельних ботів"""
    
    def __init__(self):
        self.cpu_limit = Config.PARALLEL_SETTINGS.get('cpu_limit_per_account', 25)
        self.memory_limit = Config.PARALLEL_SETTINGS.get('memory_limit_per_account', 1024)
        self.active_processes = {}
        
    def can_start_new_bot(self):
        """Перевірка можливості запуску нового бота"""
        try:
            import psutil
            
            # Перевірка CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 80:
                logging.warning(f"⚠️ Високе навантаження CPU: {cpu_percent}%")
                return False
            
            # Перевірка пам'яті
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                logging.warning(f"⚠️ Високе використання пам'яті: {memory.percent}%")
                return False
            
            # Перевірка вільної пам'яті
            available_mb = memory.available / 1024 / 1024
            if available_mb < self.memory_limit:
                logging.warning(f"⚠️ Недостатньо вільної пам'яті: {available_mb:.0f} MB")
                return False
            
            return True
            
        except ImportError:
            # Якщо psutil не встановлено, дозволяємо запуск
            return True
        except Exception as e:
            logging.error(f"Помилка перевірки ресурсів: {e}")
            return True
            
    def set_bot_limits(self, username, bot):
        """Встановлення обмежень для бота"""
        try:
            import psutil
            
            # Тут можна додати логіку обмеження ресурсів для процесу
            # Наприклад, через nice/ionice на Linux або Job Objects на Windows
            
            self.active_processes[username] = {
                'bot': bot,
                'start_time': datetime.now(),
                'cpu_limit': self.cpu_limit,
                'memory_limit': self.memory_limit
            }
            
        except:
            pass
            
    def monitor_resources(self):
        """Моніторинг використання ресурсів"""
        try:
            import psutil
            
            stats = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'active_bots': len(self.active_processes)
            }
            
            return stats
            
        except:
            return {}


class BatchProcessor:
    """Обробка користувачів батчами"""
    
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
        self.processed = 0
        self.total = 0
        self.start_time = datetime.now()
        
    def process_users_in_batches(self, users, process_func, randomize=True):
        """Обробка користувачів батчами з прогресом"""
        self.total = len(users)
        
        if randomize:
            users = users.copy()
            random.shuffle(users)
            
        results = []
        
        for i in range(0, len(users), self.batch_size):
            batch = users[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(users) + self.batch_size - 1) // self.batch_size
            
            logging.info(f"📦 Обробка батча {batch_num}/{total_batches}")
            
            for user in batch:
                try:
                    result = process_func(user)
                    results.append(result)
                    self.processed += 1
                    
                    # Прогрес
                    progress = (self.processed / self.total) * 100
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    eta = (elapsed / self.processed) * (self.total - self.processed) if self.processed > 0 else 0
                    
                    logging.info(f"📊 Прогрес: {self.processed}/{self.total} ({progress:.1f}%) - ETA: {eta:.0f} сек")
                    
                except Exception as e:
                    logging.error(f"Помилка обробки {user}: {e}")
                    results.append(None)
                    
            # Пауза між батчами
            if i + self.batch_size < len(users):
                delay = random.uniform(
                    Config.MULTI_USER_CONFIG['batch_processing']['batch_delay'] * 0.8,
                    Config.MULTI_USER_CONFIG['batch_processing']['batch_delay'] * 1.2
                )
                logging.info(f"⏳ Пауза між батчами: {delay:.0f} сек")
                time.sleep(delay)
                
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

import os
import json
from pathlib import Path

class Config:
    """Конфігурація бота з підтримкою багатьох користувачів"""
    
    # Основні налаштування
    HEADLESS = False  # Запуск в headless режимі
    TIMEOUT = 10  # Таймаут для операцій
    
    # Затримки (в секундах)
    MIN_DELAY = 1
    MAX_DELAY = 3
    HUMAN_DELAY_MIN = 0.1
    HUMAN_DELAY_MAX = 0.3
    
    # === НОВІ НАЛАШТУВАННЯ ДЛЯ БАГАТЬОХ КОРИСТУВАЧІВ ===
    
    # Затримки між користувачами (секунди)
    MIN_USER_DELAY = 30   # Мінімальна затримка між користувачами
    MAX_USER_DELAY = 60   # Максимальна затримка між користувачами
    
    # Лімити безпеки
    MAX_USERS_PER_SESSION = 50     # Максимум користувачів за одну сесію
    MAX_USERS_PER_DAY = 100        # Максимум користувачів за день
    MAX_DAILY_ACTIONS = 500        # Максимум дій за день
    
    # Налаштування пакетної обробки
    BATCH_SIZE = 10               # Розмір пакету для обробки
    BATCH_DELAY = 300             # Затримка між пакетами (5 хвилин)
    
    # Кількість дій за замовчуванням
    MAX_LIKES_PER_SESSION = 50
    MAX_COMMENTS_PER_SESSION = 10
    MAX_FOLLOWS_PER_SESSION = 20
    DEFAULT_POSTS_COUNT = 2        # Кількість постів для лайку за замовчуванням
    
    # Шляхи до файлів
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "logs"
    SESSIONS_DIR = BASE_DIR / "sessions"
    TEMP_DIR = BASE_DIR / "temp"
    DATA_DIR = BASE_DIR / "data"
    
    # Створення директорій
    for directory in [LOGS_DIR, SESSIONS_DIR, TEMP_DIR, DATA_DIR]:
        directory.mkdir(exist_ok=True)
    
    # User Agents для мобільних пристроїв
    USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-N975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
    ]
    
    # Проксі сервери
    PROXY_SERVERS = [
        # Додайте ваші проксі сервери тут
        # Формат: "ip:port:username:password"
        # Приклад: "192.168.1.1:8080:user:pass"
    ]
    
    # Налаштування капчі
    CAPTCHA_SOLVER = {
        "service": "2captcha",  # 2captcha, anticaptcha, deathbycaptcha
        "api_key": "",  # Ваш API ключ
        "timeout": 120
    }
    
    # Налаштування для обходу детекції
    ANTI_DETECTION = {
        "mouse_movements": True,
        "random_scrolling": True,
        "typing_delays": True,
        "human_pauses": True,
        "viewport_changes": True
    }
    
    # === НАЛАШТУВАННЯ ЛЮДЯНОСТІ ===
    HUMAN_BEHAVIOR = {
        "typing_variations": True,          # Варіативність швидкості друку
        "thinking_pauses": True,           # Паузи для "роздумів"
        "typo_corrections": True,          # Помилки та виправлення
        "emoji_additions": True,           # Додавання емодзі
        "random_long_pauses": True,        # Випадкові довгі паузи
        "micro_pauses": True,              # Мікро-паузи між діями
        
        # Налаштування для сторіс
        "story_reply_thinking_time": (1.5, 3.5),  # Час "роздумів" перед відповіддю
        "story_reply_reading_time": (0.8, 2.0),   # Час "перечитування" перед відправкою
        "story_emoji_probability": 0.3,           # Ймовірність додавання емодзі
        
        # Швидкість друку (секунди на символ)
        "typing_speed": {
            "normal": (0.05, 0.15),
            "punctuation": (0.2, 0.4),
            "capital": (0.1, 0.2),
            "after_word": (0.05, 0.15),
            "between_words_pause": 0.15  # Ймовірність паузи між словами
        }
    }
    
    # === НАЛАШТУВАННЯ ПАРАЛЕЛЬНОЇ РОБОТИ ===
    PARALLEL_SETTINGS = {
        "max_parallel_accounts": 10,        # Максимум паралельних акаунтів
        "account_start_delay": 2,          # Затримка між запусками акаунтів (сек)
        "browser_isolation": True,         # Ізоляція браузерів
        "separate_profiles": True,         # Окремі профілі для кожного акаунта
        "resource_monitoring": True,       # Моніторинг ресурсів
        "cpu_limit_per_account": 25,       # Максимум CPU на акаунт (%)
        "memory_limit_per_account": 1024,  # Максимум RAM на акаунт (MB)
        
        # Розподіл навантаження
        "load_balancing": {
            "enabled": True,
            "strategy": "round_robin",  # round_robin, least_loaded, random
            "check_interval": 30        # Інтервал перевірки навантаження (сек)
        }
    }
    
    # === НАЛАШТУВАННЯ БРАУЗЕРІВ ===
    BROWSER_SETTINGS = {
        "Chrome": {
            "executable_path": None,  # Автоматичний пошук
            "version": "latest",
            "mobile_emulation": True,
            "disable_images": False,
            "disable_javascript": False
        },
        "Dolphin Anty": {
            "api_endpoint": "http://localhost:3001",
            "profile_prefix": "instagram_",
            "auto_create_profiles": True,
            "fingerprint_protection": True,
            "webrtc_mode": "altered",
            "canvas_mode": "noise",
            "webgl_mode": "noise",
            "client_rect_mode": "noise",
            "profile_settings": {
                "platform": "windows",
                "browser_version": "latest",
                "screen_resolution": "1920x1080",
                "timezone": "auto",
                "language": "en-US,en;q=0.9",
                "geolocation": "auto",
                "cpu": "4",
                "memory": "8",
                "do_not_track": True,
                "media_devices": "default"
            }
        }
    }
    
    # === СЕЛЕКТОРИ ДЛЯ INSTAGRAM (ОНОВЛЕНІ ДЛЯ 2025) ===
    SELECTORS = {
        "login": {
            "username": [
                "input[name='username']",
                "input[aria-label*='username']",
                "input[placeholder*='username']",
                "input[autocomplete='username']"
            ],
            "password": [
                "input[name='password']",
                "input[type='password']",
                "input[aria-label*='password']",
                "input[autocomplete='current-password']"
            ],
            "submit": [
                "button[type='submit']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Log In')]",
                "//button[contains(text(), 'Увійти')]",
                "//div[@role='button' and contains(text(), 'Log')]",
                "//button[contains(@class, 'login') or contains(@class, 'Login')]"
            ]
        },
        "posts": {
            "container": [
                "article div div div div a",
                "div[role='button'] img[src*='instagram']",
                "article a[href*='/p/']",
                "div[style*='padding-bottom'] a"
            ],
            "like_button": [
                "svg[aria-label='Like']",
                "svg[aria-label='Подобається']",
                "button svg[aria-label*='Like']",
                "div[role='button'] svg[aria-label*='Like']"
            ],
            "unlike_button": [
                "svg[aria-label='Unlike']",
                "svg[aria-label='Не подобається']",
                "button svg[aria-label*='Unlike']"
            ],
            "comment_button": [
                "svg[aria-label='Comment']",
                "svg[aria-label='Коментувати']",
                "button svg[aria-label*='Comment']"
            ],
            "share_button": [
                "svg[aria-label='Share']",
                "svg[aria-label='Поділитися']",
                "button svg[aria-label*='Share']"
            ]
        },
        "stories": {
            "container": [
                "div[role='menu']",
                "div[style*='scroll'] div[role='button']",
                "section div[role='button']"
            ],
            "story_item": [
                "div[role='menu'] div div div",
                "div[style*='border-radius'] img",
                "canvas[style*='border-radius']"
            ],
            "username": [
                "span",
                "div span",
                "button span"
            ],
            "like_button": [
                "svg[aria-label='Like']",
                "svg[aria-label='Подобається']",
                "button[aria-label*='Like']"
            ],
            "reply_input": [
                "textarea[placeholder*='Send message']",
                "textarea[placeholder*='Reply']",
                "textarea[placeholder*='Відповісти']",
                "div[contenteditable='true']"
            ],
            "send_button": [
                "button[type='submit']",
                "//button[contains(text(), 'Send')]",
                "//div[@role='button' and contains(text(), 'Send')]"
            ]
        },
        "profile": {
            "followers": [
                "a[href*='/followers/'] span",
                "//a[contains(@href, 'followers')]//span"
            ],
            "following": [
                "a[href*='/following/'] span",
                "//a[contains(@href, 'following')]//span"
            ],
            "posts_count": [
                "span",
                "div span:first-child"
            ]
        },
        "dialogs": {
            "not_now": [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Не зараз')]",
                "//div[@role='button' and contains(text(), 'Not Now')]"
            ],
            "save_info": [
                "//button[contains(text(), 'Save Info')]",
                "//button[contains(text(), 'Зберегти')]"
            ],
            "turn_on_notifications": [
                "//button[contains(text(), 'Turn on Notifications')]",
                "//button[contains(text(), 'Увімкнути сповіщення')]"
            ],
            "close": [
                "svg[aria-label='Close']",
                "svg[aria-label='Закрити']",
                "button[aria-label='Close']",
                "//button[@aria-label='Close']"
            ]
        },
        "captcha": [
            "div[role='dialog'] img",
            ".captcha-image",
            "img[alt*='captcha']",
            "img[src*='captcha']",
            "img[src*='challenge']"
        ]
    }
    
    # === ПОВІДОМЛЕННЯ ЗА ЗАМОВЧУВАННЯМ ===
    DEFAULT_STORY_REPLIES = [
        "😍",
        "🔥",
        "❤️",
        "Круто!",
        "Класно!",
        "Супер!",
        "Гарно!",
        "Топ!",
        "Wow!",
        "Nice!",
        "Amazing!",
        "Perfect!",
        "Love it!",
        "Beautiful!",
        "Дуже цікаво!",
        "Топ контент!",
        "Красиво!",
        "💯",
        "🙌",
        "👏",
        "⭐",
        "💫",
        "✨"
    ]
    
    # === НАЛАШТУВАННЯ БАГАТЬОХ КОРИСТУВАЧІВ ===
    MULTI_USER_CONFIG = {
        # Стратегії обробки
        "processing_strategy": "sequential",  # sequential, parallel, batch
        
        # Налаштування пакетної обробки
        "batch_processing": {
            "enabled": True,
            "batch_size": 10,
            "batch_delay": 300,  # 5 хвилин між пакетами
            "randomize_order": True
        },
        
        # Налаштування прогресу
        "progress_reporting": {
            "enabled": True,
            "detailed_logs": True,
            "save_statistics": True
        },
        
        # Обробка помилок
        "error_handling": {
            "max_retries": 2,
            "retry_delay": 60,  # 1 хвилина між спробами
            "skip_failed_users": True,
            "continue_on_errors": True
        },
        
        # Статистика
        "statistics": {
            "track_success_rate": True,
            "save_detailed_logs": True,
            "export_reports": True
        },
        
        # Розподіл таргетів
        "target_distribution": {
            "enabled": True,
            "strategy": "round_robin",  # round_robin, random, sequential
            "avoid_duplicates": True,
            "min_targets_per_account": 1,
            "balance_load": True
        }
    }
    
    # Налаштування бази даних
    DATABASE = {
        "type": "sqlite",
        "path": str(DATA_DIR / "instagram_bot_multi.db"),
        "backup_frequency": 24  # годин
    }
    
    # Налаштування сесій
    SAVE_SESSIONS = False  # Не зберігати сесії для безпеки
    ALWAYS_FRESH_LOGIN = True  # Завжди входити заново
    CLOSE_ALL_DIALOGS = True  # Закривати всі діалоги після входу
    
    # Налаштування для відладки
    DEBUG_MODE = True  # Детальне логування
    SCREENSHOTS_ON_ERROR = True  # Скріншоти при помилках
    SLOW_MODE = True  # Повільний режим для складних випадків
    
    # === БЕЗПЕКА ТА ЛІМИТИ ===
    SECURITY = {
        "max_actions_per_hour": 30,
        "max_actions_per_day": 200,
        "cooldown_after_limit": 3600,  # секунд
        "randomize_actions": True,
        
        # Нові лімити для багатьох користувачів
        "max_users_per_hour": 20,
        "max_users_per_session": 50,
        "user_processing_timeout": 600,  # 10 хвилин на користувача
        "session_timeout": 7200,  # 2 години загального часу роботи
        
        # Додаткові перевірки
        "check_account_limits": True,
        "enforce_daily_limits": True,
        "auto_stop_on_errors": True
    }
    
    # Налаштування логування
    LOGGING = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_rotation": True,
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
        
        # Додаткові налаштування для багатьох користувачів
        "multi_user_format": "%(asctime)s - [USER: %(user)s] - %(levelname)s - %(message)s",
        "separate_user_logs": False,  # Окремі файли для кожного користувача
        "progress_logging": True
    }
    
    # Налаштування GUI
    GUI = {
        "theme": "dark",
        "window_size": "1400x900",
        "resizable": True,
        "auto_save": True,
        "language": "uk",  # українська мова
        
        # Нові налаштування GUI
        "multi_user_features": {
            "show_progress_bar": True,
            "show_user_count": True,
            "auto_validate_users": True,
            "save_user_lists": True,
            "batch_processing_ui": True
        },
        
        "colors": {
            "success": "#4caf50",
            "warning": "#ff9800", 
            "error": "#f44336",
            "info": "#2196f3",
            "accent": "#9c27b0"
        }
    }
    
    # Налаштування для мобільної емуляції
    MOBILE_DEVICES = {
        "iPhone_12": {
            "width": 390,
            "height": 844,
            "pixel_ratio": 3.0,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        },
        "iPhone_13": {
            "width": 390,
            "height": 844,
            "pixel_ratio": 3.0,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        },
        "Samsung_Galaxy_S21": {
            "width": 384,
            "height": 854,
            "pixel_ratio": 2.75,
            "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
        },
        "Google_Pixel_5": {
            "width": 393,
            "height": 851,
            "pixel_ratio": 2.75,
            "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"
        }
    }
    
    # === ВАЛІДАЦІЯ КОРИСТУВАЧІВ ===
    USER_VALIDATION = {
        "check_username_format": True,
        "min_username_length": 1,
        "max_username_length": 30,
        "allowed_characters": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._",
        "remove_at_symbol": True,
        "remove_duplicates": True,
        "case_sensitive": False
    }
    
    # === СТАТИСТИКА ТА ЗВІТНІСТЬ ===
    REPORTING = {
        "generate_reports": True,
        "report_format": "json",  # json, csv, html
        "include_timestamps": True,
        "include_user_details": True,
        "include_action_details": True,
        "save_screenshots": False,  # Скріншоти успішних дій
        "export_path": str(DATA_DIR / "reports")
    }
    
    @classmethod
    def load_config(cls, config_file=None):
        """Завантаження конфігурації з файлу"""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # Оновлення налаштувань
                for key, value in config_data.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
                        
            except Exception as e:
                print(f"Помилка при завантаженні конфігурації: {e}")
                
    @classmethod
    def save_config(cls, config_file=None):
        """Збереження конфігурації в файл"""
        if not config_file:
            config_file = cls.DATA_DIR / "config.json"
            
        try:
            config_data = {
                "HEADLESS": cls.HEADLESS,
                "TIMEOUT": cls.TIMEOUT,
                "MIN_DELAY": cls.MIN_DELAY,
                "MAX_DELAY": cls.MAX_DELAY,
                "MIN_USER_DELAY": cls.MIN_USER_DELAY,
                "MAX_USER_DELAY": cls.MAX_USER_DELAY,
                "MAX_USERS_PER_SESSION": cls.MAX_USERS_PER_SESSION,
                "MAX_USERS_PER_DAY": cls.MAX_USERS_PER_DAY,
                "DEFAULT_POSTS_COUNT": cls.DEFAULT_POSTS_COUNT,
                "MAX_LIKES_PER_SESSION": cls.MAX_LIKES_PER_SESSION,
                "MAX_COMMENTS_PER_SESSION": cls.MAX_COMMENTS_PER_SESSION,
                "MAX_FOLLOWS_PER_SESSION": cls.MAX_FOLLOWS_PER_SESSION,
                "CAPTCHA_SOLVER": cls.CAPTCHA_SOLVER,
                "ANTI_DETECTION": cls.ANTI_DETECTION,
                "MULTI_USER_CONFIG": cls.MULTI_USER_CONFIG,
                "SECURITY": cls.SECURITY,
                "GUI": cls.GUI,
                "USER_VALIDATION": cls.USER_VALIDATION,
                "REPORTING": cls.REPORTING,
                "HUMAN_BEHAVIOR": cls.HUMAN_BEHAVIOR,
                "PARALLEL_SETTINGS": cls.PARALLEL_SETTINGS,
                "BROWSER_SETTINGS": cls.BROWSER_SETTINGS
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Помилка при збереженні конфігурації: {e}")
            
    @classmethod
    def get_random_user_agent(cls):
        """Отримання випадкового User Agent"""
        import random
        return random.choice(cls.USER_AGENTS)
        
    @classmethod
    def get_random_device(cls):
        """Отримання випадкового мобільного пристрою"""
        import random
        device_name = random.choice(list(cls.MOBILE_DEVICES.keys()))
        return cls.MOBILE_DEVICES[device_name]
        
    @classmethod
    def get_proxy(cls):
        """Отримання проксі сервера"""
        import random
        if cls.PROXY_SERVERS:
            return random.choice(cls.PROXY_SERVERS)
        return None
        
    @classmethod
    def get_dolphin_config(cls):
        """Отримання конфігурації Dolphin Anty"""
        return cls.BROWSER_SETTINGS.get("Dolphin Anty", {})
        
    @classmethod
    def get_chrome_config(cls):
        """Отримання конфігурації Chrome"""
        return cls.BROWSER_SETTINGS.get("Chrome", {})
        
    @classmethod
    def create_dolphin_profile_name(cls, username):
        """Створення назви профілю для Dolphin"""
        prefix = cls.get_dolphin_config().get("profile_prefix", "instagram_")
        return f"{prefix}{username}"
        
    @classmethod
    def get_target_distribution_config(cls):
        """Отримання конфігурації розподілу таргетів"""
        return cls.MULTI_USER_CONFIG.get("target_distribution", {})
        
    @classmethod
    def validate_username(cls, username):
        """Валідація юзернейму"""
        if not username:
            return False, "Порожній юзернейм"
            
        # Видалення символу @
        if cls.USER_VALIDATION["remove_at_symbol"]:
            username = username.lstrip('@')
            
        # Перевірка довжини
        if len(username) < cls.USER_VALIDATION["min_username_length"]:
            return False, f"Занадто короткий (мін. {cls.USER_VALIDATION['min_username_length']})"
            
        if len(username) > cls.USER_VALIDATION["max_username_length"]:
            return False, f"Занадто довгий (макс. {cls.USER_VALIDATION['max_username_length']})"
            
        # Перевірка дозволених символів
        allowed = cls.USER_VALIDATION["allowed_characters"]
        for char in username:
            if char not in allowed:
                return False, f"Недозволений символ: {char}"
                
        return True, username
        
    @classmethod
    def parse_users_input(cls, users_input):
        """Парсинг введення користувачів з валідацією"""
        if not users_input:
            return []
            
        # Різні варіанти розділювачів
        separators = [',', ';', '\n', '\t', ' ']
        users = [users_input]
        
        for sep in separators:
            if sep in users_input:
                users = users_input.split(sep)
                break
        
        # Очищення та валідація
        validated_users = []
        errors = []
        
        for user in users:
            user = user.strip()
            if not user:
                continue
                
            is_valid, result = cls.validate_username(user)
            if is_valid:
                if not cls.USER_VALIDATION["case_sensitive"]:
                    result = result.lower()
                validated_users.append(result)
            else:
                errors.append(f"{user}: {result}")
        
        # Видалення дублікатів
        if cls.USER_VALIDATION["remove_duplicates"]:
            validated_users = list(dict.fromkeys(validated_users))
            
        return validated_users, errors
        
    @classmethod
    def get_user_delay(cls):
        """Отримання випадкової затримки між користувачами"""
        import random
        return random.uniform(cls.MIN_USER_DELAY, cls.MAX_USER_DELAY)
        
    @classmethod
    def get_action_delay(cls, action_type="default"):
        """Отримання затримки для конкретної дії"""
        import random
        
        delays = {
            'like': (2, 5),
            'comment': (5, 10),
            'follow': (15, 30),
            'story_reply': (3, 8),
            'direct_message': (10, 15),
            'navigation': (2, 4),
            'default': (cls.MIN_DELAY, cls.MAX_DELAY)
        }
        
        min_delay, max_delay = delays.get(action_type, delays["default"])
        return random.uniform(min_delay, max_delay)
        
    @classmethod
    def get_batch_config(cls):
        """Отримання конфігурації пакетної обробки"""
        return cls.MULTI_USER_CONFIG["batch_processing"]
        
    @classmethod
    def is_within_limits(cls, current_users, current_actions):
        """Перевірка лімітів безпеки"""
        security = cls.SECURITY
        
        # Перевірка кількості користувачів
        if current_users > security["max_users_per_session"]:
            return False, f"Перевищено ліміт користувачів за сесію ({security['max_users_per_session']})"
            
        # Перевірка кількості дій
        if current_actions > security["max_actions_per_day"]:
            return False, f"Перевищено ліміт дій за день ({security['max_actions_per_day']})"
            
        return True, "OK"
        
    @classmethod
    def get_default_actions_config(cls):
        """Конфігурація дій за замовчуванням"""
        return {
            'like_posts': True,
            'like_stories': True,
            'reply_stories': True,
            'send_direct_message': True,  # Fallback
            'posts_count': cls.DEFAULT_POSTS_COUNT
        }
        
    @classmethod
    def get_report_config(cls):
        """Конфігурація звітності"""
        return cls.REPORTING
        
    @classmethod
    def create_user_log_format(cls, username):
        """Створення формату логування для конкретного користувача"""
        base_format = cls.LOGGING["format"]
        return base_format.replace("%(name)s", f"%(name)s-{username}")
        
    @classmethod
    def get_gui_colors(cls):
        """Отримання кольорової схеми GUI"""
        return cls.GUI.get("colors", {})
        
    @classmethod
    def export_user_statistics(cls, username, stats):
        """Експорт статистики користувача"""
        try:
            if not cls.REPORTING["generate_reports"]:
                return False
                
            export_path = Path(cls.REPORTING["export_path"])
            export_path.mkdir(exist_ok=True)
            
            filename = export_path / f"{username}_stats.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Помилка експорту статистики для {username}: {e}")
            return False
            
    @classmethod
    def load_saved_users_lists(cls):
        """Завантаження збережених списків користувачів"""
        try:
            lists_file = cls.DATA_DIR / "saved_user_lists.json"
            if lists_file.exists():
                with open(lists_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
            
    @classmethod
    def save_users_list(cls, list_name, users_list):
        """Збереження списку користувачів"""
        try:
            lists_file = cls.DATA_DIR / "saved_user_lists.json"
            saved_lists = cls.load_saved_users_lists()
            
            saved_lists[list_name] = {
                "users": users_list,
                "created_at": cls._get_current_timestamp(),
                "count": len(users_list)
            }
            
            with open(lists_file, 'w', encoding='utf-8') as f:
                json.dump(saved_lists, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Помилка збереження списку: {e}")
            return False
            
    @classmethod
    def _get_current_timestamp(cls):
        """Отримання поточної мітки часу"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    @classmethod
    def get_version_info(cls):
        """Інформація про версію"""
        return {
            "version": "2.0.0",
            "name": "Instagram Bot Multi-User",
            "features": [
                "Multiple users support",
                "Batch processing", 
                "Enhanced GUI",
                "Advanced validation",
                "Detailed reporting",
                "Improved security",
                "Human-like behavior",
                "Browser switching (Chrome/Dolphin)",
                "Parallel account processing",
                "Target distribution system"
            ],
            "release_date": "2025-01-01"
        }
        
    @classmethod
    def print_config_summary(cls):
        """Виведення резюме конфігурації"""
        print("=" * 50)
        print("📋 КОНФІГУРАЦІЯ INSTAGRAM BOT 2.0")
        print("=" * 50)
        
        version_info = cls.get_version_info()
        print(f"🚀 Версія: {version_info['version']}")
        print(f"📅 Дата релізу: {version_info['release_date']}")
        
        print("\n🔧 Основні налаштування:")
        print(f"  • Headless режим: {'✅' if cls.HEADLESS else '❌'}")
        print(f"  • Таймаут: {cls.TIMEOUT} сек")
        print(f"  • Затримки: {cls.MIN_DELAY}-{cls.MAX_DELAY} сек")
        
        print("\n👥 Налаштування багатьох користувачів:")
        print(f"  • Макс. користувачів за сесію: {cls.MAX_USERS_PER_SESSION}")
        print(f"  • Макс. користувачів за день: {cls.MAX_USERS_PER_DAY}")
        print(f"  • Затримка між користувачами: {cls.MIN_USER_DELAY}-{cls.MAX_USER_DELAY} сек")
        print(f"  • Розмір пакету: {cls.MULTI_USER_CONFIG['batch_processing']['batch_size']}")
        
        print("\n🛡️ Безпека:")
        print(f"  • Макс. дій за день: {cls.SECURITY['max_actions_per_day']}")
        print(f"  • Макс. дій за годину: {cls.SECURITY['max_actions_per_hour']}")
        print(f"  • Рандомізація дій: {'✅' if cls.SECURITY['randomize_actions'] else '❌'}")
        
        print("\n📊 Звітність:")
        print(f"  • Генерація звітів: {'✅' if cls.REPORTING['generate_reports'] else '❌'}")
        print(f"  • Формат звітів: {cls.REPORTING['report_format']}")
        print(f"  • Деталізація: {'✅' if cls.REPORTING['include_user_details'] else '❌'}")
        
        print("\n🌐 Браузери:")
        for browser, settings in cls.BROWSER_SETTINGS.items():
            print(f"  • {browser}: {'✅ Налаштовано' if settings else '❌'}")
        
        print("\n🎯 Розподіл таргетів:")
        target_config = cls.get_target_distribution_config()
        print(f"  • Увімкнено: {'✅' if target_config.get('enabled') else '❌'}")
        print(f"  • Стратегія: {target_config.get('strategy', 'round_robin')}")
        print(f"  • Уникнення дублікатів: {'✅' if target_config.get('avoid_duplicates') else '❌'}")
        
        print("\n🤖 Людяність:")
        print(f"  • Варіації швидкості друку: {'✅' if cls.HUMAN_BEHAVIOR['typing_variations'] else '❌'}")
        print(f"  • Паузи для роздумів: {'✅' if cls.HUMAN_BEHAVIOR['thinking_pauses'] else '❌'}")
        print(f"  • Помилки та виправлення: {'✅' if cls.HUMAN_BEHAVIOR['typo_corrections'] else '❌'}")
        print(f"  • Додавання емодзі: {'✅' if cls.HUMAN_BEHAVIOR['emoji_additions'] else '❌'}")
        
        print("\n💬 Повідомлення за замовчуванням:")
        for i, msg in enumerate(cls.DEFAULT_STORY_REPLIES[:5], 1):
            print(f"  {i}. {msg}")
        print(f"  ... та ще {len(cls.DEFAULT_STORY_REPLIES) - 5} повідомлень")
        
        print("=" * 50)

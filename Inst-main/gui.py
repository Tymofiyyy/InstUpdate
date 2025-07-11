import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import json
import os
from datetime import datetime
import logging
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk
import sys

# Налаштування CustomTkinter для сучасного дизайну
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernInstagramBotGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Instagram Bot Pro - Multi-Account Edition")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        
        # Іконка вікна
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Змінні
        self.accounts = {}  # Словник активних акаунтів
        self.bot_threads = {}  # Потоки для кожного бота
        self.running_bots = {}  # Активні боти
        self.message_queue = queue.Queue()  # Черга повідомлень для GUI
        self.executor = ThreadPoolExecutor(max_workers=10)  # Для паралельної роботи
        
        # Кольорова схема Material Design
        self.colors = {
            'primary': '#1976D2',
            'primary_dark': '#1565C0',
            'primary_light': '#42A5F5',
            'secondary': '#FFC107',
            'accent': '#E91E63',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'info': '#2196F3',
            'bg_dark': '#121212',
            'bg_medium': '#1E1E1E',
            'bg_light': '#2D2D2D',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0'
        }
        
        # Створення інтерфейсу
        self.create_modern_ui()
        
        # Запуск обробника черги повідомлень
        self.process_message_queue()
        
    def create_modern_ui(self):
        """Створення сучасного Material Design інтерфейсу"""
        # Головний контейнер з градієнтом
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True)
        
        # Верхня панель з логотипом
        self.create_header(main_container)
        
        # Бічна панель навігації
        sidebar = self.create_sidebar(main_container)
        sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10)
        
        # Основний контент
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Вкладки з іконками
        self.notebook = ctk.CTkTabview(content_frame, corner_radius=10)
        self.notebook.pack(fill="both", expand=True)
        
        # Створення вкладок
        self.create_multi_account_tab()
        self.create_automation_tab()
        self.create_messages_tab()
        self.create_monitoring_tab()
        self.create_settings_tab()
        
    def create_header(self, parent):
        """Створення стильного заголовку"""
        header_frame = ctk.CTkFrame(parent, height=80, corner_radius=0, fg_color=self.colors['primary_dark'])
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Логотип та назва
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=20, pady=10)
        
        # Емодзі замість іконки
        logo_label = ctk.CTkLabel(logo_frame, text="🤖", font=("Arial", 36))
        logo_label.pack(side="left", padx=(0, 10))
        
        # Назва програми з градієнтом
        title_label = ctk.CTkLabel(logo_frame, text="Instagram Bot Pro", 
                                  font=("Arial", 28, "bold"),
                                  text_color="#FFFFFF")
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(logo_frame, text="Multi-Account Automation", 
                                     font=("Arial", 14),
                                     text_color="#B0BEC5")
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Статистика справа
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=20)
        
        self.active_accounts_label = ctk.CTkLabel(stats_frame, text="👥 Active: 0", 
                                                 font=("Arial", 14))
        self.active_accounts_label.pack(side="left", padx=10)
        
        self.total_actions_label = ctk.CTkLabel(stats_frame, text="⚡ Actions: 0", 
                                               font=("Arial", 14))
        self.total_actions_label.pack(side="left", padx=10)
        
    def create_sidebar(self, parent):
        """Створення бічної панелі з кнопками"""
        sidebar = ctk.CTkFrame(parent, width=200, corner_radius=10)
        sidebar.pack_propagate(False)
        
        # Заголовок
        sidebar_title = ctk.CTkLabel(sidebar, text="Quick Actions", 
                                    font=("Arial", 16, "bold"))
        sidebar_title.pack(pady=(20, 10))
        
        # Кнопки швидких дій
        buttons_data = [
            ("🚀", "Start All", self.start_all_accounts, self.colors['success']),
            ("⏹️", "Stop All", self.stop_all_accounts, self.colors['error']),
            ("➕", "Add Account", self.add_account_dialog, self.colors['info']),
            ("📊", "Statistics", self.show_statistics, self.colors['secondary']),
            ("🔄", "Refresh", self.refresh_all, self.colors['primary']),
            ("⚙️", "Settings", self.open_settings, self.colors['text_secondary'])
        ]
        
        for icon, text, command, color in buttons_data:
            btn = ctk.CTkButton(sidebar, 
                              text=f"{icon} {text}",
                              command=command,
                              height=40,
                              font=("Arial", 14),
                              fg_color=color,
                              hover_color=self.darken_color(color))
            btn.pack(fill="x", padx=10, pady=5)
        
        # Розділювач
        separator = ctk.CTkFrame(sidebar, height=2, fg_color=self.colors['text_secondary'])
        separator.pack(fill="x", padx=20, pady=20)
        
        # Інформація про версію
        version_label = ctk.CTkLabel(sidebar, text="Version 2.0 Pro", 
                                    font=("Arial", 10),
                                    text_color=self.colors['text_secondary'])
        version_label.pack(side="bottom", pady=10)
        
        return sidebar
        
    def create_multi_account_tab(self):
        """Вкладка багатоакаунтності з сучасним дизайном"""
        tab = self.notebook.add("👥 Multi-Account")
        
        # Верхня панель інструментів
        toolbar = ctk.CTkFrame(tab, height=60, corner_radius=10)
        toolbar.pack(fill="x", padx=10, pady=10)
        toolbar.pack_propagate(False)
        
        # Кнопки інструментів
        tools_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        tools_frame.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(tools_frame, text="➕ Add Account", 
                     command=self.add_account_dialog,
                     width=120, height=35).pack(side="left", padx=5)
        
        ctk.CTkButton(tools_frame, text="📁 Import CSV", 
                     command=self.import_accounts_csv,
                     width=120, height=35).pack(side="left", padx=5)
        
        ctk.CTkButton(tools_frame, text="💾 Export", 
                     command=self.export_accounts,
                     width=100, height=35).pack(side="left", padx=5)
        
        # Селектор браузера
        browser_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        browser_frame.pack(side="right", padx=10, pady=10)
        
        ctk.CTkLabel(browser_frame, text="Browser:").pack(side="left", padx=5)
        self.browser_var = tk.StringVar(value="Chrome")
        browser_menu = ctk.CTkOptionMenu(browser_frame, 
                                       values=["Chrome", "Dolphin Anty"],
                                       variable=self.browser_var,
                                       width=120)
        browser_menu.pack(side="left")
        
        # Таблиця акаунтів з сучасним стилем
        accounts_frame = ctk.CTkFrame(tab, corner_radius=10)
        accounts_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Заголовки таблиці
        headers_frame = ctk.CTkFrame(accounts_frame, height=40, fg_color=self.colors['primary'])
        headers_frame.pack(fill="x", padx=1, pady=1)
        headers_frame.pack_propagate(False)
        
        headers = ["Select", "Username", "Status", "Proxy", "Actions", "Last Activity", "Controls"]
        weights = [0.5, 2, 1.5, 2, 1, 2, 2]
        
        for header, weight in zip(headers, weights):
            label = ctk.CTkLabel(headers_frame, text=header, 
                               font=("Arial", 12, "bold"),
                               text_color="white")
            label.pack(side="left", expand=True, fill="x", padx=5)
        
        # Скролований контейнер для рядків
        self.accounts_scroll_frame = ctk.CTkScrollableFrame(accounts_frame, 
                                                           corner_radius=0,
                                                           fg_color=self.colors['bg_medium'])
        self.accounts_scroll_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Додавання тестових акаунтів
        self.add_sample_accounts()
        
    def add_account_row(self, username, password, proxy=""):
        """Додавання рядка акаунта з сучасним дизайном"""
        row_frame = ctk.CTkFrame(self.accounts_scroll_frame, 
                               height=50,
                               corner_radius=5,
                               fg_color=self.colors['bg_light'])
        row_frame.pack(fill="x", padx=5, pady=3)
        row_frame.pack_propagate(False)
        
        # Чекбокс
        var = tk.BooleanVar(value=True)
        checkbox = ctk.CTkCheckBox(row_frame, text="", variable=var, width=30)
        checkbox.pack(side="left", padx=10)
        
        # Username
        username_label = ctk.CTkLabel(row_frame, text=username, 
                                    font=("Arial", 12, "bold"))
        username_label.pack(side="left", expand=True, fill="x", padx=5)
        
        # Статус з кольоровою індикацією
        status_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        status_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        status_indicator = ctk.CTkLabel(status_frame, text="●", 
                                      text_color=self.colors['warning'],
                                      font=("Arial", 16))
        status_indicator.pack(side="left", padx=5)
        
        status_label = ctk.CTkLabel(status_frame, text="Ready", 
                                   font=("Arial", 11))
        status_label.pack(side="left")
        
        # Proxy
        proxy_label = ctk.CTkLabel(row_frame, text=proxy or "No proxy", 
                                 font=("Arial", 11),
                                 text_color=self.colors['text_secondary'])
        proxy_label.pack(side="left", expand=True, fill="x", padx=5)
        
        # Actions counter
        actions_label = ctk.CTkLabel(row_frame, text="0", 
                                   font=("Arial", 12))
        actions_label.pack(side="left", expand=True, fill="x", padx=5)
        
        # Last activity
        activity_label = ctk.CTkLabel(row_frame, text="Never", 
                                    font=("Arial", 11),
                                    text_color=self.colors['text_secondary'])
        activity_label.pack(side="left", expand=True, fill="x", padx=5)
        
        # Кнопки управління
        controls_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        controls_frame.pack(side="left", padx=10)
        
        # Кнопка старту/стопу з анімацією
        start_btn = ctk.CTkButton(controls_frame, text="▶", 
                                width=35, height=35,
                                fg_color=self.colors['success'],
                                command=lambda: self.toggle_account(username))
        start_btn.pack(side="left", padx=2)
        
        # Кнопка налаштувань
        settings_btn = ctk.CTkButton(controls_frame, text="⚙", 
                                   width=35, height=35,
                                   fg_color=self.colors['info'])
        settings_btn.pack(side="left", padx=2)
        
        # Кнопка видалення
        delete_btn = ctk.CTkButton(controls_frame, text="🗑", 
                                 width=35, height=35,
                                 fg_color=self.colors['error'],
                                 command=lambda: self.remove_account(username))
        delete_btn.pack(side="left", padx=2)
        
        # Зберігаємо елементи для оновлення
        self.accounts[username] = {
            'password': password,
            'proxy': proxy,
            'row_frame': row_frame,
            'checkbox': var,
            'status_indicator': status_indicator,
            'status_label': status_label,
            'actions_label': actions_label,
            'activity_label': activity_label,
            'start_btn': start_btn,
            'settings_btn': settings_btn,
            'is_running': False
        }
        
    def create_automation_tab(self):
        """Вкладка автоматизації з покращеним дизайном"""
        tab = self.notebook.add("🚀 Automation")
        
        # Контейнер з двома колонками
        columns_frame = ctk.CTkFrame(tab, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Ліва колонка - Налаштування
        left_column = ctk.CTkFrame(columns_frame, corner_radius=10)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Заголовок лівої колонки
        left_title = ctk.CTkLabel(left_column, text="⚙️ Automation Settings", 
                                font=("Arial", 18, "bold"))
        left_title.pack(pady=10)
        
        # Цільові користувачі
        targets_frame = ctk.CTkFrame(left_column, corner_radius=10)
        targets_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        targets_header = ctk.CTkFrame(targets_frame, height=40, 
                                    fg_color=self.colors['primary'])
        targets_header.pack(fill="x")
        targets_header.pack_propagate(False)
        
        ctk.CTkLabel(targets_header, text="🎯 Target Users", 
                    font=("Arial", 14, "bold"),
                    text_color="white").pack(side="left", padx=10)
        
        self.targets_count_label = ctk.CTkLabel(targets_header, text="Count: 0", 
                                              text_color="white")
        self.targets_count_label.pack(side="right", padx=10)
        
        # Текстове поле для користувачів
        self.targets_text = ctk.CTkTextbox(targets_frame, height=150,
                                         font=("Arial", 12))
        self.targets_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.targets_text.insert("1.0", "user1, user2, user3\n@user4\n@user5")
        
        # Кнопки для targets
        targets_buttons = ctk.CTkFrame(targets_frame, fg_color="transparent")
        targets_buttons.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(targets_buttons, text="📁 Load", width=80,
                     command=self.load_targets_from_file).pack(side="left", padx=2)
        ctk.CTkButton(targets_buttons, text="💾 Save", width=80,
                     command=self.save_targets_to_file).pack(side="left", padx=2)
        ctk.CTkButton(targets_buttons, text="✅ Validate", width=80,
                     command=self.validate_targets).pack(side="left", padx=2)
        ctk.CTkButton(targets_buttons, text="🧹 Clear", width=80,
                     command=lambda: self.targets_text.delete("1.0", "end")).pack(side="left", padx=2)
        
        # Налаштування дій
        actions_frame = ctk.CTkFrame(left_column, corner_radius=10)
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        actions_header = ctk.CTkFrame(actions_frame, height=40,
                                    fg_color=self.colors['primary'])
        actions_header.pack(fill="x")
        
        ctk.CTkLabel(actions_header, text="⚡ Actions Configuration",
                    font=("Arial", 14, "bold"),
                    text_color="white").pack(padx=10, pady=5)
        
        # Чекбокси дій з іконками
        actions_content = ctk.CTkFrame(actions_frame)
        actions_content.pack(fill="x", padx=10, pady=10)
        
        self.like_posts_var = tk.BooleanVar(value=True)
        self.like_stories_var = tk.BooleanVar(value=True)
        self.reply_stories_var = tk.BooleanVar(value=True)
        self.send_dm_var = tk.BooleanVar(value=True)
        
        actions_data = [
            ("❤️ Like Posts", self.like_posts_var),
            ("👍 Like Stories", self.like_stories_var),
            ("💬 Reply to Stories", self.reply_stories_var),
            ("📩 Send DM (Fallback)", self.send_dm_var)
        ]
        
        for text, var in actions_data:
            ctk.CTkCheckBox(actions_content, text=text, variable=var,
                          font=("Arial", 12)).pack(anchor="w", pady=3)
        
        # Кількість постів
        posts_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
        posts_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(posts_frame, text="Posts to like:").pack(side="left")
        self.posts_count_var = tk.IntVar(value=2)
        posts_slider = ctk.CTkSlider(posts_frame, from_=1, to=5,
                                   variable=self.posts_count_var,
                                   width=150)
        posts_slider.pack(side="left", padx=10)
        
        self.posts_count_label = ctk.CTkLabel(posts_frame, text="2")
        self.posts_count_label.pack(side="left")
        
        def update_posts_label(value):
            self.posts_count_label.configure(text=str(int(value)))
        posts_slider.configure(command=update_posts_label)
        
        # Права колонка - Моніторинг
        right_column = ctk.CTkFrame(columns_frame, corner_radius=10)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Заголовок правої колонки
        right_title = ctk.CTkLabel(right_column, text="📊 Real-time Monitoring",
                                 font=("Arial", 18, "bold"))
        right_title.pack(pady=10)
        
        # Логи з кольоровим кодуванням
        logs_frame = ctk.CTkFrame(right_column, corner_radius=10)
        logs_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        logs_header = ctk.CTkFrame(logs_frame, height=40,
                                 fg_color=self.colors['primary'])
        logs_header.pack(fill="x")
        
        ctk.CTkLabel(logs_header, text="📜 Activity Logs",
                    font=("Arial", 14, "bold"),
                    text_color="white").pack(side="left", padx=10)
        
        # Кнопки логів
        logs_buttons = ctk.CTkFrame(logs_header, fg_color="transparent")
        logs_buttons.pack(side="right", padx=10)
        
        ctk.CTkButton(logs_buttons, text="Clear", width=60, height=25,
                     command=self.clear_logs).pack(side="left", padx=2)
        ctk.CTkButton(logs_buttons, text="Export", width=60, height=25,
                     command=self.export_logs).pack(side="left", padx=2)
        
        # Текстове поле логів
        self.logs_text = ctk.CTkTextbox(logs_frame, font=("Consolas", 10))
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Додавання кольорових тегів для логів
        self.setup_log_tags()
        
    def create_messages_tab(self):
     """Вкладка для управління повідомленнями з оптимізованим інтерфейсом"""
     tab = self.notebook.add("💬 Messages")
    
    # Головний контейнер з фіксованою висотою
     main_frame = ctk.CTkFrame(tab, corner_radius=10)
     main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Верхня панель з кнопками управління
     control_panel = ctk.CTkFrame(main_frame, height=40)
     control_panel.pack(fill="x", pady=(0, 10))
     control_panel.pack_propagate(False)
    
    # Кнопки управління з фіксованою шириною
     buttons = [
        ("➕ Add", self.add_message_dialog),
        ("✏️ Edit", self.edit_message_dialog),
        ("🗑 Delete", self.delete_message),
        ("📁 Import", self.import_messages),
        ("💾 Export", self.export_messages),
        ("🎲 Templates", self.show_message_templates)
     ]
    
     for text, command in buttons:
        btn = ctk.CTkButton(control_panel, text=text, command=command,
                          width=70, height=30, font=("Arial", 11))
        btn.pack(side="left", padx=3)
    
    # Основний контент (список + редактор)
     content_frame = ctk.CTkFrame(main_frame)
     content_frame.pack(fill="both", expand=True)
    
    # Ліва частина - список повідомлень (30% ширини)
     list_frame = ctk.CTkFrame(content_frame, width=200, corner_radius=8)
     list_frame.pack(side="left", fill="y", padx=(0, 5))
     list_frame.pack_propagate(False)
    
    # Заголовок списку
     list_header = ctk.CTkFrame(list_frame, height=30, fg_color=self.colors['primary'])
     list_header.pack(fill="x")
     ctk.CTkLabel(list_header, text="📋 Message List", 
                font=("Arial", 12, "bold")).pack(pady=5)
    
    # Скролований список повідомлень
     self.messages_listbox = tk.Listbox(list_frame,
                                     bg=self.colors['bg_medium'],
                                     fg=self.colors['text_primary'],
                                     selectbackground=self.colors['primary'],
                                     font=("Arial", 11),
                                     borderwidth=0,
                                     highlightthickness=0)
     self.messages_listbox.pack(fill="both", expand=True, padx=5, pady=5)
     self.messages_listbox.bind('<<ListboxSelect>>', self.on_message_select)
    
    # Права частина - редактор (70% ширини)
     editor_frame = ctk.CTkFrame(content_frame, corner_radius=8)
     editor_frame.pack(side="right", fill="both", expand=True)
    
    # Заголовок редактора
     editor_header = ctk.CTkFrame(editor_frame, height=30, fg_color=self.colors['primary'])
     editor_header.pack(fill="x")
     ctk.CTkLabel(editor_header, text="✏️ Message Editor", 
                font=("Arial", 12, "bold")).pack(pady=5)
    
    # Редактор повідомлень зі скролом
     self.message_editor = ctk.CTkTextbox(editor_frame,
                                       font=("Arial", 12),
                                       wrap="word",
                                       height=150)  # Фіксована висота
     self.message_editor.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Нижня панель з функціями
     bottom_panel = ctk.CTkFrame(editor_frame, height=80)
     bottom_panel.pack(fill="x", pady=(5, 0))
    
    # Панель швидких емодзі
     emoji_frame = ctk.CTkFrame(bottom_panel)
     emoji_frame.pack(fill="x", padx=5, pady=2)
    
     ctk.CTkLabel(emoji_frame, text="Quick Emojis:").pack(side="left", padx=5)
    
     emojis = ["😊", "❤️", "🔥", "👍", "🎉", "💯", "⭐", "🙌", "👏", "💪"]
     for emoji in emojis:
        btn = ctk.CTkButton(emoji_frame, text=emoji, width=30, height=30,
                          command=lambda e=emoji: self.insert_emoji(e))
        btn.pack(side="left", padx=2)
    
    # Кнопки дій
     action_buttons = ctk.CTkFrame(bottom_panel)
     action_buttons.pack(fill="x", padx=5, pady=5)
    
     ctk.CTkButton(action_buttons, text="💾 Save Message",
                 command=self.save_current_message,
                 width=120, height=30,
                 fg_color=self.colors['success']).pack(side="left", padx=5)
    
     ctk.CTkButton(action_buttons, text="👁️ Preview",
                 command=self.preview_message,
                 width=100, height=30).pack(side="left", padx=5)
    
     ctk.CTkButton(action_buttons, text="🧹 Clear",
                 command=lambda: self.message_editor.delete("1.0", "end"),
                 width=80, height=30).pack(side="left", padx=5)
    
     # Завантаження повідомлень
     self.load_messages()
        
    def create_monitoring_tab(self):
        """Вкладка моніторингу з графіками та статистикою"""
        tab = self.notebook.add("📊 Monitoring")
        
        # Верхня панель зі статистикою
        stats_panel = ctk.CTkFrame(tab, height=120, corner_radius=10)
        stats_panel.pack(fill="x", padx=10, pady=10)
        stats_panel.pack_propagate(False)
        
        # Карточки статистики
        stats_container = ctk.CTkFrame(stats_panel, fg_color="transparent")
        stats_container.pack(expand=True)
        
        stats_data = [
            ("👥", "Active Accounts", "0", self.colors['success']),
            ("⚡", "Total Actions", "0", self.colors['info']),
            ("❤️", "Likes Today", "0", self.colors['accent']),
            ("💬", "Messages Sent", "0", self.colors['secondary']),
            ("📈", "Success Rate", "0%", self.colors['primary'])
        ]
        
        self.stat_labels = {}
        for icon, title, value, color in stats_data:
            card = self.create_stat_card(stats_container, icon, title, value, color)
            card.pack(side="left", padx=10)
            self.stat_labels[title] = card.winfo_children()[2]  # Зберігаємо label зі значенням
        
        # Графіки та детальна статистика
        details_frame = ctk.CTkFrame(tab, corner_radius=10)
        details_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Табличка з детальною інформацією
        self.create_detailed_stats_table(details_frame)
        
    def create_settings_tab(self):
        """Вкладка налаштувань"""
        tab = self.notebook.add("⚙️ Settings")
        
        # Скролований контейнер
        settings_scroll = ctk.CTkScrollableFrame(tab, corner_radius=10)
        settings_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Секція браузера
        browser_section = self.create_settings_section(settings_scroll, 
                                                     "🌐 Browser Settings",
                                                     self.colors['primary'])
        
        # Вибір браузера
        browser_frame = ctk.CTkFrame(browser_section, fg_color="transparent")
        browser_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(browser_frame, text="Default Browser:").pack(side="left", padx=10)
        self.default_browser_var = tk.StringVar(value="Chrome")
        browser_options = ctk.CTkOptionMenu(browser_frame,
                                          values=["Chrome", "Dolphin Anty"],
                                          variable=self.default_browser_var)
        browser_options.pack(side="left", padx=10)
        
        # Headless mode
        self.headless_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(browser_section, text="Run in headless mode (no GUI)",
                       variable=self.headless_var).pack(anchor="w", padx=20, pady=5)
        
        # Секція затримок
        delays_section = self.create_settings_section(settings_scroll,
                                                    "⏱️ Delays & Timing",
                                                    self.colors['info'])
        
        # Слайдери затримок
        delays_data = [
            ("Min delay between actions", 1, 10, 2),
            ("Max delay between actions", 5, 30, 5),
            ("Delay between users", 10, 120, 30),
            ("Human typing speed", 0.05, 0.5, 0.1)
        ]
        
        self.delay_vars = {}
        for label, from_val, to_val, default in delays_data:
            delay_frame = ctk.CTkFrame(delays_section, fg_color="transparent")
            delay_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(delay_frame, text=f"{label}:").pack(side="left", padx=10)
            
            var = tk.DoubleVar(value=default)
            self.delay_vars[label] = var
            
            slider = ctk.CTkSlider(delay_frame, from_=from_val, to=to_val,
                                 variable=var, width=200)
            slider.pack(side="left", padx=10)
            
            value_label = ctk.CTkLabel(delay_frame, text=f"{default}s")
            value_label.pack(side="left", padx=5)
            
            def update_label(val, lbl=value_label):
                lbl.configure(text=f"{val:.2f}s")
            slider.configure(command=update_label)
        
        # Секція безпеки
        security_section = self.create_settings_section(settings_scroll,
                                                      "🔒 Security & Limits",
                                                      self.colors['error'])
        
        # Ліміти
        limits_data = [
            ("Max actions per day", 50, 500, 200),
            ("Max users per session", 10, 100, 50),
            ("Max parallel accounts", 1, 20, 5)
        ]
        
        self.limit_vars = {}
        for label, from_val, to_val, default in limits_data:
            limit_frame = ctk.CTkFrame(security_section, fg_color="transparent")
            limit_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(limit_frame, text=f"{label}:").pack(side="left", padx=10)
            
            var = tk.IntVar(value=default)
            self.limit_vars[label] = var
            
            slider = ctk.CTkSlider(limit_frame, from_=from_val, to=to_val,
                                 variable=var, width=200)
            slider.pack(side="left", padx=10)
            
            value_label = ctk.CTkLabel(limit_frame, text=str(default))
            value_label.pack(side="left", padx=5)
            
            def update_label(val, lbl=value_label):
                lbl.configure(text=str(int(val)))
            slider.configure(command=update_label)
        
        # Кнопки збереження
        buttons_frame = ctk.CTkFrame(settings_scroll, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(buttons_frame, text="💾 Save Settings",
                     command=self.save_settings,
                     fg_color=self.colors['success'],
                     width=150).pack(side="left", padx=10)
        
        ctk.CTkButton(buttons_frame, text="🔄 Reset to Defaults",
                     command=self.reset_settings,
                     fg_color=self.colors['warning'],
                     width=150).pack(side="left", padx=10)
        
    def create_settings_section(self, parent, title, color):
        """Створення секції налаштувань"""
        section = ctk.CTkFrame(parent, corner_radius=10)
        section.pack(fill="x", padx=10, pady=10)
        
        header = ctk.CTkFrame(section, height=40, fg_color=color, corner_radius=10)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text=title,
                    font=("Arial", 14, "bold"),
                    text_color="white").pack(padx=15, pady=5)
        
        return section
        
    def create_stat_card(self, parent, icon, title, value, color):
        """Створення карточки статистики"""
        card = ctk.CTkFrame(parent, width=140, height=80, corner_radius=10)
        card.pack_propagate(False)
        
        # Іконка
        icon_label = ctk.CTkLabel(card, text=icon, font=("Arial", 24))
        icon_label.pack(pady=(10, 0))
        
        # Назва
        title_label = ctk.CTkLabel(card, text=title, 
                                 font=("Arial", 10),
                                 text_color=self.colors['text_secondary'])
        title_label.pack()
        
        # Значення
        value_label = ctk.CTkLabel(card, text=value,
                                 font=("Arial", 16, "bold"),
                                 text_color=color)
        value_label.pack()
        
        return card
        
    def create_detailed_stats_table(self, parent):
        """Створення таблиці з детальною статистикою"""
        # Заголовок
        header = ctk.CTkFrame(parent, height=40, fg_color=self.colors['primary'])
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text="📈 Detailed Statistics",
                    font=("Arial", 14, "bold"),
                    text_color="white").pack(padx=10, pady=5)
        
        # Таблиця
        table_frame = ctk.CTkScrollableFrame(parent, corner_radius=0)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Тестові дані
        test_data = [
            ("account1", "Active", "150", "45", "30", "15", "95%"),
            ("account2", "Active", "120", "35", "25", "10", "92%"),
            ("account3", "Paused", "80", "20", "15", "5", "88%"),
        ]
        
        headers = ["Account", "Status", "Actions", "Likes", "Comments", "DMs", "Success"]
        
        # Заголовки таблиці
        headers_frame = ctk.CTkFrame(table_frame, height=35, fg_color=self.colors['bg_light'])
        headers_frame.pack(fill="x", padx=1, pady=1)
        
        for header in headers:
            ctk.CTkLabel(headers_frame, text=header,
                        font=("Arial", 11, "bold")).pack(side="left", expand=True, fill="x")
        
        # Рядки даних
        for data in test_data:
            row_frame = ctk.CTkFrame(table_frame, height=30)
            row_frame.pack(fill="x", padx=1, pady=1)
            
            for value in data:
                ctk.CTkLabel(row_frame, text=value,
                           font=("Arial", 10)).pack(side="left", expand=True, fill="x")
        
    # === МЕТОДИ ФУНКЦІОНАЛЬНОСТІ ===
    
    def add_sample_accounts(self):
        """Додавання тестових акаунтів"""
        sample_accounts = [
            ("test_account1", "password123", "proxy1.com:8080"),
            ("test_account2", "password456", ""),
            ("test_account3", "password789", "proxy2.com:3128")
        ]
        
        for username, password, proxy in sample_accounts:
            self.add_account_row(username, password, proxy)
            
    def toggle_account(self, username):
        """Перемикання стану акаунта"""
        if username not in self.accounts:
            return
            
        account = self.accounts[username]
        
        if account['is_running']:
            self.stop_single_account(username)
        else:
            self.start_single_account(username)
            
    def start_single_account(self, username):
        """Запуск одного акаунта"""
        account = self.accounts[username]
        
        # Оновлення UI
        account['status_indicator'].configure(text_color=self.colors['success'])
        account['status_label'].configure(text="Running")
        account['start_btn'].configure(text="⏸", fg_color=self.colors['warning'])
        account['is_running'] = True
        
        # Запуск бота в окремому потоці
        def run_bot():
            try:
                # Отримання налаштувань
                targets = self.targets_text.get("1.0", "end").strip()
                messages = self.get_messages()
                
                actions_config = {
                    'like_posts': self.like_posts_var.get(),
                    'like_stories': self.like_stories_var.get(),
                    'reply_stories': self.reply_stories_var.get(),
                    'send_direct_message': self.send_dm_var.get(),
                    'posts_count': self.posts_count_var.get()
                }
                
                # Створення бота з вибраним браузером
                browser_type = self.browser_var.get()
                
                # Імпорт бота
                from instagram_bot import InstagramBot
                
                bot = InstagramBot(
                    username,
                    account['password'],
                    account['proxy'],
                    browser_type=browser_type
                )
                
                self.running_bots[username] = bot
                
                # Підключення логування
                self.setup_bot_logging(bot, username)
                
                # Запуск автоматизації
                success = bot.run_automation_multiple_users(targets, messages, actions_config)
                
                # Оновлення статистики
                self.update_account_stats(username, success)
                
            except Exception as e:
                self.log_message(f"❌ Error for {username}: {e}", "error")
            finally:
                # Оновлення UI після завершення
                self.root.after(0, lambda: self.stop_single_account(username))
        
        # Запуск в ThreadPoolExecutor для паралельної роботи
        self.bot_threads[username] = self.executor.submit(run_bot)
        
        # Оновлення лічильника активних акаунтів
        self.update_active_accounts_count()
        
    def stop_single_account(self, username):
        """Зупинка одного акаунта"""
        if username not in self.accounts:
            return
            
        account = self.accounts[username]
        
        # Зупинка бота
        if username in self.running_bots:
            try:
                self.running_bots[username].close()
                del self.running_bots[username]
            except:
                pass
        
        # Оновлення UI
        account['status_indicator'].configure(text_color=self.colors['warning'])
        account['status_label'].configure(text="Stopped")
        account['start_btn'].configure(text="▶", fg_color=self.colors['success'])
        account['is_running'] = False
        
        # Оновлення активності
        account['activity_label'].configure(text=datetime.now().strftime("%H:%M:%S"))
        
        # Оновлення лічильника
        self.update_active_accounts_count()
        
    def start_all_accounts(self):
        """Запуск всіх вибраних акаунтів"""
        selected_accounts = [username for username, acc in self.accounts.items() 
                           if acc['checkbox'].get() and not acc['is_running']]
        
        if not selected_accounts:
            messagebox.showwarning("Warning", "No accounts selected or all are already running!")
            return
            
        # Перевірка ліміту паралельних акаунтів
        max_parallel = self.limit_vars.get("Max parallel accounts", tk.IntVar(value=5)).get()
        if len(selected_accounts) > max_parallel:
            if not messagebox.askyesno("Warning", 
                f"You selected {len(selected_accounts)} accounts but the limit is {max_parallel}.\n"
                f"Only first {max_parallel} accounts will be started. Continue?"):
                return
            selected_accounts = selected_accounts[:max_parallel]
        
        # Запуск кожного акаунта
        for i, username in enumerate(selected_accounts):
            # Затримка між запусками
            delay = i * 2  # 2 секунди між запусками
            self.root.after(delay * 1000, lambda u=username: self.start_single_account(u))
            
    def stop_all_accounts(self):
        """Зупинка всіх активних акаунтів"""
        active_accounts = [username for username, acc in self.accounts.items() 
                         if acc['is_running']]
        
        if not active_accounts:
            messagebox.showinfo("Info", "No active accounts to stop!")
            return
            
        for username in active_accounts:
            self.stop_single_account(username)
            
        self.log_message("⏹️ All accounts stopped", "info")
        
    def add_account_dialog(self):
        """Діалог додавання нового акаунта"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Account")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрування вікна
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Заголовок
        ctk.CTkLabel(dialog, text="➕ Add Instagram Account",
                    font=("Arial", 18, "bold")).pack(pady=20)
        
        # Поля вводу
        fields_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        fields_frame.pack(padx=30, pady=10)
        
        # Username
        ctk.CTkLabel(fields_frame, text="Username:").pack(anchor="w", pady=(10, 0))
        username_entry = ctk.CTkEntry(fields_frame, width=300, placeholder_text="Enter username")
        username_entry.pack(pady=(0, 10))
        
        # Password
        ctk.CTkLabel(fields_frame, text="Password:").pack(anchor="w")
        password_entry = ctk.CTkEntry(fields_frame, width=300, show="*", placeholder_text="Enter password")
        password_entry.pack(pady=(0, 10))
        
        # Proxy
        ctk.CTkLabel(fields_frame, text="Proxy (optional):").pack(anchor="w")
        proxy_entry = ctk.CTkEntry(fields_frame, width=300, placeholder_text="ip:port:user:pass")
        proxy_entry.pack(pady=(0, 20))
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack()
        
        def add_account():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            proxy = proxy_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required!")
                return
                
            if username in self.accounts:
                messagebox.showerror("Error", "Account already exists!")
                return
                
            self.add_account_row(username, password, proxy)
            self.log_message(f"✅ Account {username} added", "success")
            dialog.destroy()
        
        ctk.CTkButton(buttons_frame, text="Add Account",
                     command=add_account,
                     fg_color=self.colors['success']).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="Cancel",
                     command=dialog.destroy,
                     fg_color=self.colors['error']).pack(side="left", padx=5)
        
    def remove_account(self, username):
        """Видалення акаунта"""
        if messagebox.askyesno("Confirm", f"Remove account {username}?"):
            if username in self.accounts:
                # Зупинка якщо активний
                if self.accounts[username]['is_running']:
                    self.stop_single_account(username)
                    
                # Видалення з UI
                self.accounts[username]['row_frame'].destroy()
                del self.accounts[username]
                
                self.log_message(f"🗑️ Account {username} removed", "warning")
                
    def import_accounts_csv(self):
        """Імпорт акаунтів з CSV"""
        filename = filedialog.askopenfilename(
            title="Import Accounts CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import csv
                imported = 0
                
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2:
                            username = row[0].strip()
                            password = row[1].strip()
                            proxy = row[2].strip() if len(row) > 2 else ""
                            
                            if username and password and username not in self.accounts:
                                self.add_account_row(username, password, proxy)
                                imported += 1
                                
                self.log_message(f"✅ Imported {imported} accounts", "success")
                messagebox.showinfo("Success", f"Imported {imported} accounts!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")
                
    def export_accounts(self):
        """Експорт акаунтів"""
        filename = filedialog.asksaveasfilename(
            title="Export Accounts",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
        )
        
        if filename:
            try:
                if filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Username', 'Password', 'Proxy', 'Status'])
                        
                        for username, account in self.accounts.items():
                            status = "Active" if account['is_running'] else "Inactive"
                            writer.writerow([username, account['password'], 
                                          account['proxy'], status])
                else:
                    data = {}
                    for username, account in self.accounts.items():
                        data[username] = {
                            'password': account['password'],
                            'proxy': account['proxy'],
                            'is_running': account['is_running']
                        }
                        
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                        
                messagebox.showinfo("Success", "Accounts exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
                
    def setup_log_tags(self):
        """Налаштування кольорових тегів для логів"""
        # Тут би були теги для Tkinter Text widget, але CTkTextbox не підтримує теги
        # Тому просто використовуємо як є
        pass
        
    def log_message(self, message, level="info"):
        """Додавання повідомлення до логів"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Емодзі для різних рівнів
        level_emojis = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "debug": "🔍"
        }
        
        emoji = level_emojis.get(level, "📝")
        formatted_message = f"[{timestamp}] {emoji} {message}\n"
        
        # Додавання до логів
        if hasattr(self, 'logs_text'):
            self.logs_text.insert("end", formatted_message)
            self.logs_text.see("end")
            
    def setup_bot_logging(self, bot, username):
        """Налаштування логування для бота"""
        class GUILogHandler(logging.Handler):
            def __init__(self, gui_instance, username):
                super().__init__()
                self.gui = gui_instance
                self.username = username
                
            def emit(self, record):
                message = f"[{self.username}] {record.getMessage()}"
                level = record.levelname.lower()
                
                # Мапінг рівнів логування
                level_map = {
                    'debug': 'debug',
                    'info': 'info',
                    'warning': 'warning',
                    'error': 'error',
                    'critical': 'error'
                }
                
                gui_level = level_map.get(level, 'info')
                
                # Додавання до черги повідомлень
                self.gui.message_queue.put((message, gui_level))
                
        handler = GUILogHandler(self, username)
        handler.setLevel(logging.INFO)
        bot.logger.addHandler(handler)
        
    def process_message_queue(self):
        """Обробка черги повідомлень"""
        try:
            while not self.message_queue.empty():
                message, level = self.message_queue.get_nowait()
                self.log_message(message, level)
        except:
            pass
        finally:
            # Повторний запуск через 100мс
            self.root.after(100, self.process_message_queue)
            
    def update_active_accounts_count(self):
        """Оновлення лічильника активних акаунтів"""
        active_count = sum(1 for acc in self.accounts.values() if acc['is_running'])
        self.active_accounts_label.configure(text=f"👥 Active: {active_count}")
        
        # Оновлення в статистиці
        if hasattr(self, 'stat_labels') and "Active Accounts" in self.stat_labels:
            self.stat_labels["Active Accounts"].configure(text=str(active_count))
            
    def update_account_stats(self, username, success):
        """Оновлення статистики акаунта"""
        if username in self.accounts:
            account = self.accounts[username]
            
            # Оновлення лічильника дій
            current_actions = int(account['actions_label'].cget("text"))
            account['actions_label'].configure(text=str(current_actions + 1))
            
            # Оновлення загальної статистики
            if hasattr(self, 'total_actions_label'):
                current_total = int(self.total_actions_label.cget("text").split(": ")[1])
                self.total_actions_label.configure(text=f"⚡ Actions: {current_total + 1}")
                
    def darken_color(self, color):
        """Затемнення кольору для hover ефекту"""
        # Проста функція затемнення
        if color.startswith("#"):
            # Конвертація hex в RGB, затемнення на 20%, конвертація назад
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = int(r * 0.8)
            g = int(g * 0.8)
            b = int(b * 0.8)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
        
    # === МЕТОДИ ДЛЯ TARGETS ===
    
    def validate_targets(self):
        """Валідація цільових користувачів"""
        content = self.targets_text.get("1.0", "end").strip()
        
        if not content:
            messagebox.showwarning("Warning", "No target users entered!")
            return
            
        # Парсинг користувачів
        users = self.parse_targets(content)
        
        if not users:
            messagebox.showerror("Error", "No valid usernames found!")
            return
            
        # Оновлення лічильника
        self.targets_count_label.configure(text=f"Count: {len(users)}")
        
        # Показ результату
        result = f"✅ Found {len(users)} valid users:\n\n"
        result += "\n".join([f"• @{user}" for user in users[:10]])
        
        if len(users) > 10:
            result += f"\n... and {len(users) - 10} more"
            
        messagebox.showinfo("Validation Result", result)
        
    def parse_targets(self, content):
        """Парсинг цільових користувачів"""
        if not content:
            return []
            
        # Різні розділювачі
        import re
        users = re.split(r'[,;\n\s]+', content)
        
        # Очищення
        cleaned = []
        for user in users:
            user = user.strip().replace('@', '')
            if user and re.match(r'^[a-zA-Z0-9._]+$', user):
                cleaned.append(user)
                
        return list(dict.fromkeys(cleaned))  # Видалення дублікатів
        
    def load_targets_from_file(self):
        """Завантаження targets з файлу"""
        filename = filedialog.askopenfilename(
            title="Load Target Users",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.targets_text.delete("1.0", "end")
                self.targets_text.insert("1.0", content)
                
                # Валідація
                users = self.parse_targets(content)
                self.targets_count_label.configure(text=f"Count: {len(users)}")
                
                self.log_message(f"✅ Loaded {len(users)} target users", "success")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
                
    def save_targets_to_file(self):
        """Збереження targets у файл"""
        content = self.targets_text.get("1.0", "end").strip()
        
        if not content:
            messagebox.showwarning("Warning", "No targets to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Target Users",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                messagebox.showinfo("Success", "Target users saved!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
                
    # === МЕТОДИ ДЛЯ ПОВІДОМЛЕНЬ ===
    
    def load_messages(self):
        """Завантаження повідомлень"""
        try:
            with open('multiline_messages.json', 'r', encoding='utf-8') as f:
                self.original_messages = json.load(f)
        except:
            self.original_messages = [
                "Hi! 😊",
                "Great post! 👍",
                "Amazing content! 🔥",
                """Hello! 😊
Love your content!
Keep it up! 💪"""
            ]
            
        self.refresh_messages_list()
        
    def refresh_messages_list(self):
        """Оновлення списку повідомлень"""
        self.messages_listbox.delete(0, tk.END)
        
        for i, message in enumerate(self.original_messages):
            # Короткий preview
            preview = message.split('\n')[0]
            if len(preview) > 50:
                preview = preview[:47] + "..."
            if '\n' in message:
                preview += " [multi-line]"
                
            self.messages_listbox.insert(tk.END, preview)
            
    def get_messages(self):
        """Отримання списку повідомлень"""
        return self.original_messages if hasattr(self, 'original_messages') else []
        
    def on_message_select(self, event):
        """Вибір повідомлення зі списку"""
        selection = self.messages_listbox.curselection()
        if selection and hasattr(self, 'original_messages'):
            index = selection[0]
            if index < len(self.original_messages):
                self.message_editor.delete("1.0", "end")
                self.message_editor.insert("1.0", self.original_messages[index])
                
    def add_message_dialog(self):
        """Діалог додавання повідомлення"""
        self.message_editor.delete("1.0", "end")
        self.message_editor.focus()
        self.log_message("Enter new message in the editor and click 'Save Message'", "info")
        
    def edit_message_dialog(self):
        """Редагування вибраного повідомлення"""
        selection = self.messages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a message to edit!")
            return
            
        self.editing_index = selection[0]
        self.log_message("Edit the message and click 'Save Message'", "info")
        
    def save_current_message(self):
        """Збереження поточного повідомлення"""
        message = self.message_editor.get("1.0", "end").strip()
        
        if not message:
            messagebox.showwarning("Warning", "Message cannot be empty!")
            return
            
        if hasattr(self, 'editing_index'):
            # Редагування існуючого
            self.original_messages[self.editing_index] = message
            del self.editing_index
        else:
            # Додавання нового
            self.original_messages.append(message)
            
        # Збереження та оновлення
        self.save_messages_to_file()
        self.refresh_messages_list()
        
        self.log_message("✅ Message saved!", "success")
        
    def delete_message(self):
        """Видалення вибраного повідомлення"""
        selection = self.messages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a message to delete!")
            return
            
        if messagebox.askyesno("Confirm", "Delete selected message?"):
            index = selection[0]
            del self.original_messages[index]
            
            self.save_messages_to_file()
            self.refresh_messages_list()
            self.message_editor.delete("1.0", "end")
            
            self.log_message("🗑️ Message deleted", "warning")
            
    def save_messages_to_file(self):
        """Збереження повідомлень у файл"""
        try:
            with open('multiline_messages.json', 'w', encoding='utf-8') as f:
                json.dump(self.original_messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_message(f"Error saving messages: {e}", "error")
            
    def import_messages(self):
        """Імпорт повідомлень з файлу"""
        filename = filedialog.askopenfilename(
            title="Import Messages",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                else:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        messages = content.split('\n\n')
                        
                self.original_messages.extend(messages)
                self.save_messages_to_file()
                self.refresh_messages_list()
                
                self.log_message(f"✅ Imported {len(messages)} messages", "success")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")
                
    def export_messages(self):
        """Експорт повідомлень"""
        if not self.original_messages:
            messagebox.showwarning("Warning", "No messages to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Messages",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.original_messages, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(self.original_messages))
                        
                messagebox.showinfo("Success", f"Exported {len(self.original_messages)} messages!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
                
    def show_message_templates(self):
        """Показ шаблонів повідомлень"""
        templates = {
            "Friendly": [
                "Hey! Love your content! 😊",
                "Amazing post! Keep it up! 👍",
                """Hi there! 👋
Your posts are incredible!
Would love to see more! 💫"""
            ],
            "Business": [
                """Hello! 
I'm reaching out regarding a potential collaboration.
Would you be interested in discussing? 📧""",
                "Great profile! Let's connect for business opportunities 🤝"
            ],
            "Engagement": [
                "This is so inspiring! 🌟",
                "Can't wait for your next post! 🔥",
                "Your content always makes my day! ☀️"
            ]
        }
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Message Templates")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        
        # Заголовок
        ctk.CTkLabel(dialog, text="📝 Message Templates",
                    font=("Arial", 18, "bold")).pack(pady=10)
        
        # Скролований контейнер
        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for category, messages in templates.items():
            # Категорія
            category_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
            category_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(category_frame, text=category,
                        font=("Arial", 14, "bold")).pack(padx=10, pady=5)
            
            for message in messages:
                msg_frame = ctk.CTkFrame(category_frame)
                msg_frame.pack(fill="x", padx=10, pady=5)
                
                # Preview повідомлення
                preview = message.replace('\n', ' ')[:50] + "..." if len(message) > 50 else message
                ctk.CTkLabel(msg_frame, text=preview,
                           font=("Arial", 10)).pack(side="left", padx=10)
                
                # Кнопка використання
                ctk.CTkButton(msg_frame, text="Use",
                            command=lambda m=message: self.use_template(m, dialog),
                            width=60).pack(side="right", padx=10)
                            
    def use_template(self, message, dialog):
        """Використання шаблону повідомлення"""
        self.original_messages.append(message)
        self.save_messages_to_file()
        self.refresh_messages_list()
        
        self.log_message("✅ Template added to messages", "success")
        dialog.destroy()
        
    def insert_emoji(self, emoji):
        """Вставка емодзі в редактор"""
        self.message_editor.insert("insert", emoji)
        
    def preview_message(self):
        """Попередній перегляд повідомлення"""
        message = self.message_editor.get("1.0", "end").strip()
        
        if not message:
            messagebox.showwarning("Warning", "Nothing to preview!")
            return
            
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Message Preview")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        # Заголовок
        ctk.CTkLabel(dialog, text="📱 Instagram Message Preview",
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Рамка повідомлення
        msg_frame = ctk.CTkFrame(dialog, corner_radius=15,
                               fg_color=self.colors['primary_light'])
        msg_frame.pack(padx=20, pady=10, anchor="w")
        
        # Текст повідомлення
        ctk.CTkLabel(msg_frame, text=message,
                    font=("Arial", 12),
                    text_color="white",
                    justify="left").pack(padx=15, pady=10)
        
        # Час
        time_label = ctk.CTkLabel(dialog, text=datetime.now().strftime("%H:%M"),
                                font=("Arial", 10),
                                text_color=self.colors['text_secondary'])
        time_label.pack(anchor="w", padx=25)
        
        # Кнопка закриття
        ctk.CTkButton(dialog, text="Close",
                     command=dialog.destroy).pack(pady=20)
                     
    # === ІНШІ МЕТОДИ ===
    
    def clear_logs(self):
        """Очищення логів"""
        if hasattr(self, 'logs_text'):
            self.logs_text.delete("1.0", "end")
            self.log_message("📋 Logs cleared", "info")
            
    def export_logs(self):
        """Експорт логів"""
        if not hasattr(self, 'logs_text'):
            return
            
        content = self.logs_text.get("1.0", "end").strip()
        
        if not content:
            messagebox.showwarning("Warning", "No logs to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                messagebox.showinfo("Success", "Logs exported!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
                
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            settings = {
                'browser': self.default_browser_var.get(),
                'headless': self.headless_var.get(),
                'delays': {k: v.get() for k, v in self.delay_vars.items()},
                'limits': {k: v.get() for k, v in self.limit_vars.items()}
            }
            
            with open('bot_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
                
            self.log_message("✅ Settings saved", "success")
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            
    def reset_settings(self):
        """Скидання налаштувань"""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            # Скидання змінних
            self.default_browser_var.set("Chrome")
            self.headless_var.set(False)
            
            # Скидання затримок
            defaults_delays = {
                "Min delay between actions": 2,
                "Max delay between actions": 5,
                "Delay between users": 30,
                "Human typing speed": 0.1
            }
            
            for key, value in defaults_delays.items():
                if key in self.delay_vars:
                    self.delay_vars[key].set(value)
                    
            # Скидання лімітів
            defaults_limits = {
                "Max actions per day": 200,
                "Max users per session": 50,
                "Max parallel accounts": 5
            }
            
            for key, value in defaults_limits.items():
                if key in self.limit_vars:
                    self.limit_vars[key].set(value)
                    
            self.log_message("🔄 Settings reset to defaults", "info")
            
    def show_statistics(self):
        """Показ детальної статистики"""
        # Перехід на вкладку моніторингу
        self.notebook.set("📊 Monitoring")
        
    def refresh_all(self):
        """Оновлення всіх даних"""
        self.update_active_accounts_count()
        self.log_message("🔄 Data refreshed", "info")
        
    def open_settings(self):
        """Відкриття налаштувань"""
        self.notebook.set("⚙️ Settings")
        
    def run(self):
        """Запуск програми"""
        self.log_message("🚀 Instagram Bot Pro started", "success")
        self.log_message("👥 Multi-account automation ready", "info")
        self.log_message("🌐 Browser switching enabled (Chrome/Dolphin)", "info")
        
        # Обробка закриття
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()
        
    def on_closing(self):
        """Обробка закриття програми"""
        if self.running_bots:
            if messagebox.askyesno("Confirm", "Active bots are running. Stop all and exit?"):
                self.stop_all_accounts()
                time.sleep(1)  # Даємо час на завершення
                self.executor.shutdown(wait=False)
                self.root.destroy()
        else:
            self.executor.shutdown(wait=False)
            self.root.destroy()


# Спробуємо використати CustomTkinter, якщо не встановлений - використаємо стандартний
try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# Fallback на стару версію якщо CustomTkinter не працює
def start_gui():
    try:
        app = ModernInstagramBotGUI()
        app.run()
    except Exception as e:
        print(f"Error with modern GUI: {e}")
        print("Falling back to classic GUI...")
        # Тут можна запустити стару версію GUI
        from gui import InstagramBotGUI
        app = InstagramBotGUI()
        app.run()

if __name__ == "__main__":
    start_gui()
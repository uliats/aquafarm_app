from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QAction, QMenuBar
)
from PyQt5.QtCore import Qt
import psycopg2
from PyQt5.QtGui import QFont, QIcon

class ManagementWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.initUI()
        self.load_styles()
        self.setup_menu()

    def initUI(self):
        self.setWindowTitle('Управление базой данных')
        self.setGeometry(100, 100, 1200, 800)

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Основной лейаут
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Создаем вкладки для разных таблиц
        self.tabs = QTabWidget()
        
        # Добавляем вкладки
        self.create_aquariums_tab()
        self.create_seafood_tab()
        self.create_users_tab()
        self.create_refrigerators_tab()
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton('Сохранить изменения')
        self.save_button.setIcon(QIcon("icons/save.png"))
        self.save_button.clicked.connect(self.save_changes)
        
        self.refresh_button = QPushButton('Обновить данные')
        self.refresh_button.setIcon(QIcon("icons/refresh.png"))
        self.refresh_button.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(button_layout)

    def load_styles(self):
        # Загрузка стилей из CSS файла
        try:
            with open("management/styles.css", "r") as f:
                self.setStyleSheet(f.read())
        except:
            # Стандартные стили, если файл не найден
            self.setStyleSheet("""
                QTableWidget {
                    font-size: 12px;
                    selection-background-color: #3498db;
                }
                QHeaderView::section {
                    background-color: #2980b9;
                    color: white;
                    padding: 4px;
                }
                QPushButton {
                    padding: 5px;
                    min-width: 80px;
                }
            """)

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Таблицы
        tables_menu = menubar.addMenu('Таблицы')
        tables = {
            'Аквариумы': 0,
            'Морепродукты': 1,
            'Пользователи': 2,
            'Холодильники': 3
        }
        
        for name, index in tables.items():
            action = QAction(name, self)
            action.triggered.connect(lambda _, idx=index: self.tabs.setCurrentIndex(idx))
            tables_menu.addAction(action)

    def create_aquariums_tab(self):
        """Создает вкладку для управления аквариумами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.aquariums_table = QTableWidget()
        self.aquariums_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.aquariums_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.aquariums_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Кнопки для аквариумов
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Добавить')
        add_btn.setIcon(QIcon("icons/add.png"))
        add_btn.clicked.connect(self.add_aquarium)
        
        del_btn = QPushButton('Удалить')
        del_btn.setIcon(QIcon("icons/delete.png"))
        del_btn.clicked.connect(self.delete_aquarium)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.aquariums_table)
        
        self.tabs.addTab(tab, "Аквариумы")
        self.load_aquariums_data()

    def create_seafood_tab(self):
        """Создает вкладку для управления морепродуктами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.seafood_table = QTableWidget()
        self.seafood_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.seafood_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Кнопки для морепродуктов
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Добавить')
        add_btn.setIcon(QIcon("icons/add.png"))
        add_btn.clicked.connect(self.add_seafood)
        
        del_btn = QPushButton('Удалить')
        del_btn.setIcon(QIcon("icons/delete.png"))
        del_btn.clicked.connect(self.delete_seafood)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.seafood_table)
        
        self.tabs.addTab(tab, "Морепродукты")
        self.load_seafood_data()

    def create_users_tab(self):
        """Создает вкладку для управления пользователями"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.users_table = QTableWidget()
        self.users_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Кнопки для пользователей
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Добавить')
        add_btn.setIcon(QIcon("icons/add.png"))
        add_btn.clicked.connect(self.add_user)
        
        del_btn = QPushButton('Удалить')
        del_btn.setIcon(QIcon("icons/delete.png"))
        del_btn.clicked.connect(self.delete_user)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.users_table)
        
        self.tabs.addTab(tab, "Пользователи")
        self.load_users_data()

    def create_refrigerators_tab(self):
        """Создает вкладку для управления холодильниками"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.refrigerators_table = QTableWidget()
        self.refrigerators_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.refrigerators_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Кнопки для холодильников
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Добавить')
        add_btn.setIcon(QIcon("icons/add.png"))
        add_btn.clicked.connect(self.add_refrigerator)
        
        del_btn = QPushButton('Удалить')
        del_btn.setIcon(QIcon("icons/delete.png"))
        del_btn.clicked.connect(self.delete_refrigerator)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.refrigerators_table)
        
        self.tabs.addTab(tab, "Холодильники")
        self.load_refrigerators_data()

    # Методы загрузки данных
    def load_aquariums_data(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT a.aquarium_id, a.тип_аквариума, u.имя_пользователя, 
                       a.объем, a.статус, m.название_вида
                FROM аквариумы a
                LEFT JOIN пользователи u ON a.ответственный_пользователь = u.user_id
                LEFT JOIN морепродукты m ON a.aquarium_id = m.aquarium_id
                ORDER BY a.aquarium_id
            """)
            
            rows = cursor.fetchall()
            self.aquariums_table.setRowCount(len(rows))
            self.aquariums_table.setColumnCount(6)
            self.aquariums_table.setHorizontalHeaderLabels([
                'ID', 'Тип', 'Ответственный', 'Объем', 'Статус', 'Морепродукт'
            ])
            
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col) if col is not None else "")
                    self.aquariums_table.setItem(i, j, item)
            
            self.aquariums_table.hideColumn(0)  # Скрываем ID
            self.aquariums_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def load_seafood_data(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT m.seafood_id, m.название_вида, m.нормальный_вес, 
                       m.нормальный_размер, m.тип_корма, m.норма_корма_на_одну_особь,
                       m.уровень_смертности_группы, a.aquarium_id
                FROM морепродукты m
                LEFT JOIN аквариумы a ON m.aquarium_id = a.aquarium_id
                ORDER BY m.seafood_id
            """)
            
            rows = cursor.fetchall()
            self.seafood_table.setRowCount(len(rows))
            self.seafood_table.setColumnCount(8)
            self.seafood_table.setHorizontalHeaderLabels([
                'ID', 'Название', 'Норма веса', 'Норма размера', 
                'Тип корма', 'Норма корма', 'Смертность', 'ID аквариума'
            ])
            
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col) if col is not None else "")
                    self.seafood_table.setItem(i, j, item)
            
            self.seafood_table.hideColumn(0)  # Скрываем ID
            self.seafood_table.hideColumn(7)  # Скрываем ID аквариума
            self.seafood_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def load_users_data(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT user_id, имя_пользователя, роль_пользователя, логин
                FROM пользователи
                ORDER BY user_id
            """)
            
            rows = cursor.fetchall()
            self.users_table.setRowCount(len(rows))
            self.users_table.setColumnCount(4)
            self.users_table.setHorizontalHeaderLabels([
                'ID', 'Имя', 'Роль', 'Логин'
            ])
            
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    if j == 3:  # Логин - нередактируемый
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.users_table.setItem(i, j, item)
            
            self.users_table.hideColumn(0)  # Скрываем ID
            self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def load_refrigerators_data(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT f.fridge_id, m.название_вида, f.количество, 
                       f.срок_хранения, f.состояние_холодильника, 
                       f.дата_последней_проверки
                FROM холодильники f
                LEFT JOIN морепродукты m ON f.seafood_id = m.seafood_id
                ORDER BY f.fridge_id
            """)
            
            rows = cursor.fetchall()
            self.refrigerators_table.setRowCount(len(rows))
            self.refrigerators_table.setColumnCount(6)
            self.refrigerators_table.setHorizontalHeaderLabels([
                'ID', 'Морепродукт', 'Количество', 'Срок хранения', 'Состояние', 'Последняя проверка'
            ])
            
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col) if col is not None else "")
                    self.refrigerators_table.setItem(i, j, item)
            
            self.refrigerators_table.hideColumn(0)  # Скрываем ID
            self.refrigerators_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    # Методы для добавления записей
    def add_aquarium(self):
        row = self.aquariums_table.rowCount()
        self.aquariums_table.insertRow(row)
        for i in range(self.aquariums_table.columnCount()):
            self.aquariums_table.setItem(row, i, QTableWidgetItem(""))

    def add_seafood(self):
        row = self.seafood_table.rowCount()
        self.seafood_table.insertRow(row)
        for i in range(self.seafood_table.columnCount()):
            self.seafood_table.setItem(row, i, QTableWidgetItem(""))

    def add_user(self):
        row = self.users_table.rowCount()
        self.users_table.insertRow(row)
        for i in range(self.users_table.columnCount()):
            self.users_table.setItem(row, i, QTableWidgetItem(""))

    def add_refrigerator(self):
        row = self.refrigerators_table.rowCount()
        self.refrigerators_table.insertRow(row)
        for i in range(self.refrigerators_table.columnCount()):
            self.refrigerators_table.setItem(row, i, QTableWidgetItem(""))

    # Методы для удаления записей
    def delete_aquarium(self):
        row = self.aquariums_table.currentRow()
        if row >= 0:
            aquarium_id = self.aquariums_table.item(row, 0).text()
            if QMessageBox.question(self, "Подтверждение", 
                                  f"Удалить аквариум ID {aquarium_id}?",
                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.aquariums_table.removeRow(row)

    def delete_seafood(self):
        row = self.seafood_table.currentRow()
        if row >= 0:
            seafood_id = self.seafood_table.item(row, 0).text()
            if QMessageBox.question(self, "Подтверждение", 
                                  f"Удалить морепродукт ID {seafood_id}?",
                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.seafood_table.removeRow(row)

    def delete_user(self):
        row = self.users_table.currentRow()
        if row >= 0:
            user_id = self.users_table.item(row, 0).text()
            if QMessageBox.question(self, "Подтверждение", 
                                  f"Удалить пользователя ID {user_id}?",
                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.users_table.removeRow(row)

    def delete_refrigerator(self):
        row = self.refrigerators_table.currentRow()
        if row >= 0:
            fridge_id = self.refrigerators_table.item(row, 0).text()
            if QMessageBox.question(self, "Подтверждение", 
                                  f"Удалить холодильник ID {fridge_id}?",
                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.refrigerators_table.removeRow(row)

    def save_changes(self):
        """Сохраняет все изменения в базе данных"""
        try:
            cursor = self.db_connection.cursor()
            
            # Сохраняем изменения для каждой таблицы
            self.save_aquariums(cursor)
            self.save_seafood(cursor)
            self.save_users(cursor)
            self.save_refrigerators(cursor)
            
            self.db_connection.commit()
            QMessageBox.information(self, "Успех", "Все изменения сохранены!")
            
        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")
        finally:
            cursor.close()

    def save_aquariums(self, cursor):
        """Сохраняет изменения в таблице аквариумов"""
        for row in range(self.aquariums_table.rowCount()):
            aquarium_id = self.aquariums_table.item(row, 0).text()
            aquarium_type = self.aquariums_table.item(row, 1).text()
            responsible = self.aquariums_table.item(row, 2).text()
            volume = self.aquariums_table.item(row, 3).text()
            status = self.aquariums_table.item(row, 4).text()
            
            if aquarium_id:  # Обновление существующей записи
                cursor.execute("""
                    UPDATE аквариумы 
                    SET тип_аквариума = %s, объем = %s, статус = %s
                    WHERE aquarium_id = %s
                """, (aquarium_type, volume, status, aquarium_id))
            else:  # Новая запись
                cursor.execute("""
                    INSERT INTO аквариумы (тип_аквариума, объем, статус)
                    VALUES (%s, %s, %s)
                    RETURNING aquarium_id
                """, (aquarium_type, volume, status))
                new_id = cursor.fetchone()[0]
                self.aquariums_table.item(row, 0).setText(str(new_id))

    def save_seafood(self, cursor):
        """Сохраняет изменения в таблице морепродуктов"""
        for row in range(self.seafood_table.rowCount()):
            seafood_id = self.seafood_table.item(row, 0).text()
            name = self.seafood_table.item(row, 1).text()
            weight = self.seafood_table.item(row, 2).text()
            size = self.seafood_table.item(row, 3).text()
            food_type = self.seafood_table.item(row, 4).text()
            food_rate = self.seafood_table.item(row, 5).text()
            mortality = self.seafood_table.item(row, 6).text()
            aquarium_id = self.seafood_table.item(row, 7).text()
            
            if seafood_id:  # Обновление существующей записи
                cursor.execute("""
                    UPDATE морепродукты 
                    SET название_вида = %s, нормальный_вес = %s, нормальный_размер = %s,
                        тип_корма = %s, норма_корма_на_одну_особь = %s, 
                        уровень_смертности_группы = %s, aquarium_id = %s
                    WHERE seafood_id = %s
                """, (name, weight, size, food_type, food_rate, mortality, aquarium_id, seafood_id))
            else:  # Новая запись
                cursor.execute("""
                    INSERT INTO морепродукты (
                        название_вида, нормальный_вес, нормальный_размер,
                        тип_корма, норма_корма_на_одну_особь, 
                        уровень_смертности_группы, aquarium_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING seafood_id
                """, (name, weight, size, food_type, food_rate, mortality, aquarium_id))
                new_id = cursor.fetchone()[0]
                self.seafood_table.item(row, 0).setText(str(new_id))

    def save_users(self, cursor):
        """Сохраняет изменения в таблице пользователей"""
        for row in range(self.users_table.rowCount()):
            user_id = self.users_table.item(row, 0).text()
            username = self.users_table.item(row, 1).text()
            role = self.users_table.item(row, 2).text()
            login = self.users_table.item(row, 3).text()
            
            if user_id:  # Обновление существующей записи
                cursor.execute("""
                    UPDATE пользователи 
                    SET имя_пользователя = %s, роль_пользователя = %s
                    WHERE user_id = %s
                """, (username, role, user_id))
            else:  # Новая запись
                cursor.execute("""
                    INSERT INTO пользователи (имя_пользователя, роль_пользователя, логин)
                    VALUES (%s, %s, %s)
                    RETURNING user_id
                """, (username, role, login))
                new_id = cursor.fetchone()[0]
                self.users_table.item(row, 0).setText(str(new_id))

    def save_refrigerators(self, cursor):
        """Сохраняет изменения в таблице холодильников"""
        for row in range(self.refrigerators_table.rowCount()):
            fridge_id = self.refrigerators_table.item(row, 0).text()
            seafood_name = self.refrigerators_table.item(row, 1).text()
            quantity = self.refrigerators_table.item(row, 2).text()
            storage_time = self.refrigerators_table.item(row, 3).text()
            condition = self.refrigerators_table.item(row, 4).text()
            last_check = self.refrigerators_table.item(row, 5).text()
            
            # Получаем seafood_id по названию
            cursor.execute("SELECT seafood_id FROM морепродукты WHERE название_вида = %s", (seafood_name,))
            result = cursor.fetchone()
            seafood_id = result[0] if result else None
            
            if fridge_id:  # Обновление существующей записи
                cursor.execute("""
                    UPDATE холодильники 
                    SET seafood_id = %s, количество = %s, срок_хранения = %s,
                        состояние_холодильника = %s, дата_последней_проверки = %s
                    WHERE fridge_id = %s
                """, (seafood_id, quantity, storage_time, condition, last_check, fridge_id))
            else:  # Новая запись
                cursor.execute("""
                    INSERT INTO холодильники (
                        seafood_id, количество, срок_хранения,
                        состояние_холодильника, дата_последней_проверки
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING fridge_id
                """, (seafood_id, quantity, storage_time, condition, last_check))
                new_id = cursor.fetchone()[0]
                self.refrigerators_table.item(row, 0).setText(str(new_id))

    def refresh_data(self):
        """Обновляет все данные из базы"""
        self.load_aquariums_data()
        self.load_seafood_data()
        self.load_users_data()
        self.load_refrigerators_data()
        QMessageBox.information(self, "Обновление", "Данные успешно обновлены!")
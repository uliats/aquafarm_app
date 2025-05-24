from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QFrame, QSplitter, QStackedWidget, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon
import psycopg2
from operational.add_water_parameters import AddWaterParametersWidget
from operational.add_feeding import AddFeedingWidget
from operational.add_aquarium_state import AddAquariumStateWidget
from operational.add_species_state import AddSpeciesStateWidget

class OperationalWindow(QMainWindow):
    aquarium_selected = pyqtSignal(int)  # Сигнал о выборе аквариума

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.current_aquarium_id = None  # Текущий выбранный аквариум
        self.initUI()
        self.setup_connections()

    def initUI(self):
        self.setWindowTitle('Оперативный персонал')
        self.setGeometry(100, 100, 1200, 800)

        # Загрузка стилей из CSS файла
        with open("operational/styles.css", "r") as f:
            self.setStyleSheet(f.read())

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Основной вертикальный лейаут
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Горизонтальный разделитель (верхняя часть: таблица и кнопки)
        top_splitter = QSplitter(Qt.Horizontal)

        # Таблица аквариумов
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Тип', 'Ответственный', 'Объем (л)', 'Статус', 
            'Вид морепродукта', 'Последняя проверка'
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.hideColumn(0)  # Скрываем ID
        self.table.doubleClicked.connect(self.on_aquarium_double_click)
        top_splitter.addWidget(self.table)

        # Лейаут для кнопок
        button_widget = QWidget(self)
        button_widget.setObjectName("button_widget")
        button_layout = QVBoxLayout(button_widget)
        button_layout.setSpacing(10)

        button_font = QFont()
        button_font.setPointSize(10)

        # Группа действий с аквариумом
        action_group = QGroupBox("Действия с аквариумом")
        action_layout = QVBoxLayout(action_group)
        
        self.button_add_feeding = QPushButton('Кормление', self)
        self.button_add_feeding.setFont(button_font)
        self.button_add_feeding.setIcon(QIcon("icons/feeding.png"))
        action_layout.addWidget(self.button_add_feeding)

        self.button_add_water_parameters = QPushButton('Параметры воды', self)
        self.button_add_water_parameters.setFont(button_font)
        self.button_add_water_parameters.setIcon(QIcon("icons/water.png"))
        action_layout.addWidget(self.button_add_water_parameters)

        self.button_add_aquarium_state = QPushButton('Состояние аквариума', self)
        self.button_add_aquarium_state.setFont(button_font)
        self.button_add_aquarium_state.setIcon(QIcon("icons/aquarium_state.png"))
        action_layout.addWidget(self.button_add_aquarium_state)

        self.button_add_species_state = QPushButton('Состояние особей', self)
        self.button_add_species_state.setFont(button_font)
        self.button_add_species_state.setIcon(QIcon("icons/species_state.png"))
        action_layout.addWidget(self.button_add_species_state)

        button_layout.addWidget(action_group)
        button_layout.addStretch()
        top_splitter.addWidget(button_widget)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(top_splitter)

        # StackedWidget для переключения между формами
        self.stacked_widget = QStackedWidget(self)
        
        # Форма по умолчанию
        self.default_form = QWidget()
        default_layout = QVBoxLayout(self.default_form)
        
        # Информационная панель о выбранном аквариуме
        self.info_panel = QGroupBox("Информация об аквариуме")
        self.info_layout = QFormLayout(self.info_panel)
        
        self.aquarium_type_label = QLabel("Не выбран")
        self.responsible_label = QLabel("Не выбран")
        self.volume_label = QLabel("Не выбран")
        self.status_label = QLabel("Не выбран")
        self.last_check_label = QLabel("Не выбран")
        self.species_label = QLabel("Не выбран")
        
        self.info_layout.addRow("Тип аквариума:", self.aquarium_type_label)
        self.info_layout.addRow("Ответственный:", self.responsible_label)
        self.info_layout.addRow("Объем (л):", self.volume_label)
        self.info_layout.addRow("Статус:", self.status_label)
        self.info_layout.addRow("Последняя проверка:", self.last_check_label)
        self.info_layout.addRow("Морепродукт:", self.species_label)
        
        # Таблица параметров морепродукта
        self.species_table = QTableWidget()
        self.species_table.setColumnCount(6)
        self.species_table.setHorizontalHeaderLabels([
            'Норма веса', 'Норма размера', 'Тип корма', 
            'Норма корма', 'Уровень смертности', 'Оптимальная температура'
        ])
        self.species_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.species_table.setSelectionMode(QTableWidget.SingleSelection)
        
        default_layout.addWidget(self.info_panel)
        default_layout.addWidget(QLabel("Параметры морепродукта:"))
        default_layout.addWidget(self.species_table)
        
        self.stacked_widget.addWidget(self.default_form)
        
        # Виджет параметров воды
        self.add_water_parameters_widget = AddWaterParametersWidget(self.db_connection)
        self.stacked_widget.addWidget(self.add_water_parameters_widget)
        
        # Виджет кормления
        self.add_feeding_widget = AddFeedingWidget(self.db_connection)
        self.stacked_widget.addWidget(self.add_feeding_widget)
        
        # # Виджет состояния аквариума
        self.add_aquarium_state_widget = AddAquariumStateWidget(self.db_connection)
        self.stacked_widget.addWidget(self.add_aquarium_state_widget)
        
        # Виджет состояния особей
        self.add_species_state_widget = AddSpeciesStateWidget(self.db_connection)
        self.stacked_widget.addWidget(self.add_species_state_widget)
        
        main_layout.addWidget(self.stacked_widget)

        self.load_data()

    def setup_connections(self):
        self.aquarium_selected.connect(self.on_aquarium_selected)
        self.button_add_feeding.clicked.connect(self.add_feeding)
        self.button_add_water_parameters.clicked.connect(self.add_water_parameters)
        self.button_add_aquarium_state.clicked.connect(self.add_aquarium_state)
        self.button_add_species_state.clicked.connect(self.add_species_state)

    def load_data(self):
        """Загружает данные об аквариумах из базы данных"""
        cursor = self.db_connection.cursor()

        try:
            # Загружаем основную информацию об аквариумах
            cursor.execute("""
                SELECT 
                    a.aquarium_id, 
                    a.тип_аквариума,
                    u.имя_пользователя, 
                    a.объем,
                    a.статус,
                    COALESCE(m.название_вида, 'Нет данных'),
                    COALESCE(MAX(sa.дата_проверки)::text, 'Нет данных')
                FROM аквариумы a
                JOIN пользователи u ON a.ответственный_пользователь = u.user_id
                LEFT JOIN морепродукты m ON a.aquarium_id = m.aquarium_id
                LEFT JOIN состояние_аквариума sa ON a.aquarium_id = sa.aquarium_id
                GROUP BY a.aquarium_id, u.имя_пользователя, m.название_вида
                ORDER BY a.aquarium_id
            """)
            rows = cursor.fetchall()
            
            self.table.setRowCount(len(rows))
            self.table.setSortingEnabled(False)
            
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.table.setItem(i, j, item)
            
            self.table.setSortingEnabled(True)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить данные: {str(e)}")
        finally:
            cursor.close()

    def on_aquarium_double_click(self, index):
        row = index.row()
        self.current_aquarium_id = int(self.table.item(row, 0).text())
        self.aquarium_selected.emit(self.current_aquarium_id)

    def on_aquarium_selected(self, aquarium_id):
        """Обновляет информацию о выбранном аквариуме"""
        cursor = self.db_connection.cursor()
        
        try:
            # Получаем основную информацию об аквариуме
            cursor.execute("""
                SELECT 
                    a.тип_аквариума, 
                    u.имя_пользователя, 
                    a.объем, 
                    a.статус,
                    COALESCE(MAX(sa.дата_проверки)::text, 'Нет данных') as last_check,
                    COALESCE(m.название_вида, 'Нет данных') as species_name
                FROM аквариумы a
                JOIN пользователи u ON a.ответственный_пользователь = u.user_id
                LEFT JOIN состояние_аквариума sa ON a.aquarium_id = sa.aquarium_id
                LEFT JOIN морепродукты m ON a.aquarium_id = m.aquarium_id
                WHERE a.aquarium_id = %s
                GROUP BY a.тип_аквариума, u.имя_пользователя, a.объем, a.статус, m.название_вида
            """, (aquarium_id,))
            
            aquarium_data = cursor.fetchone()
            
            if aquarium_data:
                self.aquarium_type_label.setText(aquarium_data[0])
                self.responsible_label.setText(aquarium_data[1])
                self.volume_label.setText(str(aquarium_data[2]))
                self.status_label.setText(aquarium_data[3])
                self.last_check_label.setText(aquarium_data[4] if aquarium_data[4] else "Нет данных")
                self.species_label.setText(aquarium_data[5])
            
            # Загружаем информацию о морепродукте в аквариуме
            cursor.execute("""
                SELECT 
                    m.нормальный_вес, m.нормальный_размер, m.тип_корма, 
                    m.норма_корма_на_одну_особь, m.уровень_смертности_группы,
                    o.оптимальная_температура
                FROM морепродукты m
                LEFT JOIN оптимальные_параметры_содержания o ON m.seafood_id = o.seafood_id
                WHERE m.aquarium_id = %s
            """, (aquarium_id,))
            
            species_data = cursor.fetchone()
            self.species_table.setRowCount(1 if species_data else 0)
            
            if species_data:
                for j, col in enumerate(species_data):
                    item = QTableWidgetItem(str(col) if col is not None else "Нет данных")
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.species_table.setItem(0, j, item)
            
            # Переключаемся на основную форму
            self.stacked_widget.setCurrentIndex(0)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить данные: {str(e)}")
        finally:
            cursor.close()

    def get_selected_aquarium_id(self):
        if self.current_aquarium_id is None:
            QMessageBox.warning(self, "Ошибка", 
                              "Сначала выберите аквариум (двойной клик по строке в таблице)")
            return None
        return self.current_aquarium_id

    def add_feeding(self):
        aquarium_id = self.get_selected_aquarium_id()
        if aquarium_id is None:
            return
        
        self.add_feeding_widget.set_aquarium_id(aquarium_id)
        self.stacked_widget.setCurrentIndex(2)  # Индекс 2 для формы кормления

    def add_water_parameters(self):
        aquarium_id = self.get_selected_aquarium_id()
        if aquarium_id is None:
            return
        
        self.add_water_parameters_widget.set_aquarium_id(aquarium_id)
        self.stacked_widget.setCurrentIndex(1)  # Индекс 1 для параметров воды

    def add_aquarium_state(self):
        aquarium_id = self.get_selected_aquarium_id()
        if aquarium_id is None:
            return
        
        self.add_aquarium_state_widget.set_aquarium_id(aquarium_id)
        self.stacked_widget.setCurrentIndex(3)  # Индекс 3 для состояния аквариума

    def add_species_state(self):
        aquarium_id = self.get_selected_aquarium_id()
        if aquarium_id is None:
            return
        
        self.add_species_state_widget.set_aquarium_id(aquarium_id)
        self.stacked_widget.setCurrentIndex(4)  # Индекс 4 для состояния особей

    def setCurrentIndex(self, index):
        """Анимированное переключение между формами"""
        self.stacked_widget.setCurrentIndex(index)
        animation = QPropertyAnimation(self.stacked_widget.widget(index), b"geometry")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        animation.setStartValue(self.stacked_widget.widget(index).geometry().adjusted(0, 20, 0, 0))
        animation.setEndValue(self.stacked_widget.widget(index).geometry())
        animation.start()
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox,
    QRadioButton, QButtonGroup, QSlider, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import psycopg2
from datetime import datetime


class AddAquariumStateWidget(QWidget):
    operation_completed = pyqtSignal()

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.aquarium_id = None
        self.initUI()

    def initUI(self):
        # Основной вертикальный лейаут
        main_layout = QVBoxLayout(self)

        # Группа для состояния фильтра
        filter_group = QGroupBox("Состояние фильтра")
        filter_layout = QVBoxLayout()
        
        self.filter_buttons = QButtonGroup(self)
        self.filter_bad = QRadioButton("Не функционирует (0)")
        self.filter_warning = QRadioButton("Требуется очистка (1)")
        self.filter_good = QRadioButton("Работает нормально (2)")
        self.filter_good.setChecked(True)
        
        self.filter_buttons.addButton(self.filter_bad, 0)
        self.filter_buttons.addButton(self.filter_warning, 1)
        self.filter_buttons.addButton(self.filter_good, 2)
        
        filter_layout.addWidget(self.filter_bad)
        filter_layout.addWidget(self.filter_warning)
        filter_layout.addWidget(self.filter_good)
        filter_group.setLayout(filter_layout)

        # Группа для состояния стекла
        glass_group = QGroupBox("Состояние стекла")
        glass_layout = QVBoxLayout()
        
        self.glass_buttons = QButtonGroup(self)
        self.glass_bad = QRadioButton("Сильные загрязнения (0)")
        self.glass_warning = QRadioButton("Небольшие загрязнения (1)")
        self.glass_good = QRadioButton("Чистое (2)")
        self.glass_good.setChecked(True)
        
        self.glass_buttons.addButton(self.glass_bad, 0)
        self.glass_buttons.addButton(self.glass_warning, 1)
        self.glass_buttons.addButton(self.glass_good, 2)
        
        glass_layout.addWidget(self.glass_bad)
        glass_layout.addWidget(self.glass_warning)
        glass_layout.addWidget(self.glass_good)
        glass_group.setLayout(glass_layout)

        # Слайдер для уровня водорослей
        algae_widget = QWidget()
        algae_layout = QHBoxLayout(algae_widget)
        algae_label = QLabel("Уровень водорослей (0-100%):")
        self.algae_slider = QSlider(Qt.Horizontal)
        self.algae_slider.setRange(0, 100)
        self.algae_spinbox = QDoubleSpinBox()
        self.algae_spinbox.setRange(0, 100)
        self.algae_spinbox.setSuffix("%")
        
        # Связываем слайдер и спинбокс
        self.algae_slider.valueChanged.connect(
            lambda value: self.algae_spinbox.setValue(value))
        self.algae_spinbox.valueChanged.connect(
            lambda value: self.algae_slider.setValue(int(value)))
        
        algae_layout.addWidget(algae_label)
        algae_layout.addWidget(self.algae_slider)
        algae_layout.addWidget(self.algae_spinbox)

        # Слайдер для прозрачности воды
        clarity_widget = QWidget()
        clarity_layout = QHBoxLayout(clarity_widget)
        clarity_label = QLabel("Прозрачность воды (0-100%):")
        self.clarity_slider = QSlider(Qt.Horizontal)
        self.clarity_slider.setRange(0, 100)
        self.clarity_slider.setValue(80)
        self.clarity_spinbox = QDoubleSpinBox()
        self.clarity_spinbox.setRange(0, 100)
        self.clarity_spinbox.setValue(80)
        self.clarity_spinbox.setSuffix("%")
        
        # Связываем слайдер и спинбокс
        self.clarity_slider.valueChanged.connect(
            lambda value: self.clarity_spinbox.setValue(value))
        self.clarity_spinbox.valueChanged.connect(
            lambda value: self.clarity_slider.setValue(int(value)))
        
        clarity_layout.addWidget(clarity_label)
        clarity_layout.addWidget(self.clarity_slider)
        clarity_layout.addWidget(self.clarity_spinbox)

        # Кнопка для добавления данных
        self.add_button = QPushButton('Добавить состояние', self)
        self.add_button.clicked.connect(self.add_state)

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Дата', 'Фильтр', 'Стекло', 'Водоросли', 'Прозрачность', 'Общее состояние'
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 200)
        self.table.setColumnWidth(5, 200)
        self.table.setColumnWidth(6, 200)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Добавляем виджеты в лейаут
        main_layout.addWidget(filter_group)
        main_layout.addWidget(glass_group)
        main_layout.addWidget(algae_widget)
        main_layout.addWidget(clarity_widget)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.table)

    def set_aquarium_id(self, aquarium_id):
        """Устанавливает ID аквариума и обновляет таблицу."""
        self.aquarium_id = aquarium_id
        self.update_table()

    def add_state(self):
        """Добавляет данные о состоянии в базу данных."""
        if self.aquarium_id is None:
            QMessageBox.warning(self, "Ошибка", "Аквариум не выбран.")
            return

        filter_state = self.filter_buttons.checkedId()
        glass_state = self.glass_buttons.checkedId()
        algae_level = float(self.algae_spinbox.value())  # Явное преобразование
        water_clarity = float(self.clarity_spinbox.value())  # Явное преобразование

        # Рассчитываем общее состояние
        overall_state = self.calculate_overall_state(filter_state, glass_state, algae_level, water_clarity)

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO состояние_аквариума 
                (aquarium_id, состояние_фильтра, состояние_стекла, 
                уровень_водорослей, прозрачность_воды)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.aquarium_id, filter_state, glass_state, 
                str(algae_level), str(water_clarity)))  # Преобразуем в строку для Decimal
            self.db_connection.commit()

            self.update_table()
            QMessageBox.information(self, "Успех", 
                                f"Состояние аквариума добавлено!\nОбщая оценка: {overall_state}")
            self.operation_completed.emit()
        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка базы данных", 
                            f"Не удалось добавить данные: {e}")




    def calculate_overall_state(self, filter_state, glass_state, algae_level, water_clarity):
        """Рассчитывает общее состояние аквариума."""
        try:
            # Преобразуем все значения к float для вычислений
            filter_state = float(filter_state)
            glass_state = float(glass_state)
            algae_level = float(algae_level)
            water_clarity = float(water_clarity)
            
            score = 0.0
            
            # Фильтр (макс 30 баллов)
            score += filter_state * 10
            
            # Стекло (макс 20 баллов)
            score += glass_state * 10
            
            # Водоросли (макс 20 баллов)
            score += max(0.0, 20.0 - (algae_level / 5.0))
            
            # Прозрачность (макс 30 баллов)
            score += water_clarity * 0.3
            
            # Определяем уровень состояния
            if score >= 80.0:
                return "Отличное"
            elif score >= 60.0:
                return "Хорошее"
            elif score >= 40.0:
                return "Удовлетворительное"
            else:
                return "Критическое"
                
        except Exception as e:
            print(f"Ошибка расчета состояния: {e}")
            return "Не определено"

    def update_table(self):
        """Обновляет таблицу данными из базы только для выбранного аквариума."""
        if self.aquarium_id is None:
            self.table.setRowCount(0)
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    aquarium_state_id, 
                    дата_проверки,
                    состояние_фильтра,
                    состояние_стекла,
                    уровень_водорослей,
                    прозрачность_воды
                FROM состояние_аквариума
                WHERE aquarium_id = %s
                ORDER BY дата_проверки DESC
            """, (self.aquarium_id,))
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    # Форматируем данные для отображения
                    if j == 1:  # Дата
                        item = QTableWidgetItem(col.strftime("%Y-%m-%d %H:%M"))
                    elif j == 2:  # Фильтр
                        item = QTableWidgetItem(self.format_filter_state(col))
                    elif j == 3:  # Стекло
                        item = QTableWidgetItem(self.format_glass_state(col))
                    elif j in (4, 5):  # Водоросли и прозрачность
                        item = QTableWidgetItem(f"{col}%")
                    else:
                        item = QTableWidgetItem(str(col))
                    
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(i, j, item)
                    
                # Добавляем общее состояние в последнюю колонку
                overall = self.calculate_overall_state(
                    row[2], row[3], row[4], row[5]
                )
                item = QTableWidgetItem(overall)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 6, item)
                
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось загрузить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def format_filter_state(self, state):
        """Форматирует состояние фильтра для отображения."""
        states = {
            0: "Не функционирует",
            1: "Требуется очистка",
            2: "Работает нормально"
        }
        return states.get(state, "Неизвестно")

    def format_glass_state(self, state):
        """Форматирует состояние стекла для отображения."""
        states = {
            0: "Сильные загрязнения",
            1: "Небольшие загрязнения",
            2: "Чистое"
        }
        return states.get(state, "Неизвестно")
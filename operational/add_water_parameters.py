from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QDoubleSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
import psycopg2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime


class AddWaterParametersWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.aquarium_id = None  # Инициализируем переменную для хранения ID аквариума
        self.initUI()

    def initUI(self):
        # Основной вертикальный лейаут
        main_layout = QVBoxLayout(self)

        # Виджеты для ввода данных
        self.temperature_slider = self.create_slider("Температура (°C)", 0, 40, 25)
        self.ph_slider = self.create_slider("pH", 0, 14, 7)
        self.oxygen_slider = self.create_slider("Уровень кислорода (mg/L)", 0, 20, 10)

        # Кнопка для добавления данных
        self.add_button = QPushButton('Добавить данные', self)
        self.add_button.clicked.connect(self.add_data)

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Дата измерения', 'Температура', 'pH', 'Уровень кислорода'
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 200)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Запрещаем редактирование

        # Кнопка для показа графика
        self.show_graph_button = QPushButton('Показать график', self)
        self.show_graph_button.clicked.connect(self.show_graph)

        # Добавляем виджеты в лейаут
        main_layout.addWidget(self.temperature_slider)
        main_layout.addWidget(self.ph_slider)
        main_layout.addWidget(self.oxygen_slider)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.show_graph_button)

    def create_slider(self, label_text, min_value, max_value, default_value):
        """Создает слайдер с меткой."""
        widget = QWidget(self)
        layout = QHBoxLayout(widget)

        label = QLabel(label_text, self)
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(min_value * 10)
        slider.setMaximum(max_value * 10)
        slider.setValue(default_value * 10)

        spin_box = QDoubleSpinBox(self)
        spin_box.setMinimum(min_value)
        spin_box.setMaximum(max_value)
        spin_box.setValue(default_value)
        spin_box.setSingleStep(0.1)

        # Связываем слайдер и спин-бокс
        slider.valueChanged.connect(lambda value: spin_box.setValue(value / 10))
        spin_box.valueChanged.connect(lambda value: slider.setValue(int(value * 10)))

        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(spin_box)

        return widget

    def set_aquarium_id(self, aquarium_id):
        """Устанавливает ID аквариума и обновляет таблицу."""
        self.aquarium_id = aquarium_id
        self.update_table()

    def add_data(self):
        """Добавляет данные в таблицу и базу данных."""
        if self.aquarium_id is None:
            QMessageBox.warning(self, "Ошибка", "Аквариум не выбран.")
            return

        temperature = self.temperature_slider.findChild(QDoubleSpinBox).value()
        ph = self.ph_slider.findChild(QDoubleSpinBox).value()
        oxygen = self.oxygen_slider.findChild(QDoubleSpinBox).value()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO параметры_воды 
                (aquarium_id, температура, pH, уровень_кислорода)
                VALUES (%s, %s, %s, %s)
            """, (self.aquarium_id, temperature, ph, oxygen))
            self.db_connection.commit()

            # Обновляем таблицу
            self.update_table()
            QMessageBox.information(self, "Успех", "Данные успешно добавлены!")
        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось добавить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def update_table(self):
        """Обновляет таблицу данными из базы только для выбранного аквариума."""
        if self.aquarium_id is None:
            self.table.setRowCount(0)  # Очищаем таблицу, если аквариум не выбран
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    parameter_id, 
                    дата_измерения, 
                    температура, 
                    pH, 
                    уровень_кислорода
                FROM параметры_воды
                WHERE aquarium_id = %s
                ORDER BY дата_измерения DESC
            """, (self.aquarium_id,))
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    # Форматируем дату для лучшего отображения
                    if j == 1 and isinstance(col, datetime):
                        item = QTableWidgetItem(col.strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        item = QTableWidgetItem(str(col))
                    
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(i, j, item)
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def show_graph(self):
        """Открывает окно с графиком изменения параметров для выбранного аквариума."""
        if self.aquarium_id is None:
            QMessageBox.warning(self, "Ошибка", "Аквариум не выбран.")
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    дата_измерения, 
                    температура, 
                    pH, 
                    уровень_кислорода
                FROM параметры_воды
                WHERE aquarium_id = %s
                ORDER BY дата_измерения
            """, (self.aquarium_id,))
            data = cursor.fetchall()

            if not data:
                QMessageBox.information(self, "Информация", "Нет данных для построения графика.")
                return

            dates = [row[0] for row in data]
            temperature = [row[1] for row in data]
            ph = [row[2] for row in data]
            oxygen = [row[3] for row in data]

            # Создаем график
            fig, ax = plt.subplots(3, 1, figsize=(10, 8))
            fig.suptitle(f"Параметры воды для аквариума {self.aquarium_id}")

            ax[0].plot(dates, temperature, label="Температура (°C)", color="red")
            ax[0].set_ylabel("Температура")
            ax[0].grid(True)

            ax[1].plot(dates, ph, label="pH", color="blue")
            ax[1].set_ylabel("pH")
            ax[1].grid(True)

            ax[2].plot(dates, oxygen, label="Уровень кислорода (mg/L)", color="green")
            ax[2].set_ylabel("Уровень кислорода")
            ax[2].grid(True)

            plt.tight_layout()
            plt.show()

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось получить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить график: {e}")
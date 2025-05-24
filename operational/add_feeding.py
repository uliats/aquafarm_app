from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QDateEdit, QComboBox
)
from PyQt5.QtCore import Qt, QDate
import psycopg2
from PyQt5.QtCore import pyqtSignal
from datetime import datetime


class AddFeedingWidget(QWidget):
    operation_completed = pyqtSignal()  # Сигнал о завершении операции

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.aquarium_id = None
        self.seafood_id = None
        self.initUI()

    def initUI(self):
        # Основной вертикальный лейаут
        main_layout = QVBoxLayout(self)

        # Виджеты для ввода данных
        self.date_edit = QDateEdit(self)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        # Выбор типа корма (выпадающий список)
        self.food_type_combo = QComboBox(self)
        self.food_type_combo.addItems(["Сухой", "Живой", "Замороженный", "Растительный"])
        
        self.total_feed_spinbox = QDoubleSpinBox(self)
        self.total_feed_spinbox.setMinimum(0)
        self.total_feed_spinbox.setMaximum(999999.99)
        self.total_feed_spinbox.setDecimals(2)
        self.total_feed_spinbox.setSuffix(" г")

        # Кнопка для добавления данных
        self.add_button = QPushButton('Добавить кормление', self)
        self.add_button.clicked.connect(self.add_feeding)

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Дата кормления', 'Тип корма', 'Общий объем', 'Вид морепродукта'
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 200)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Добавляем виджеты в лейаут
        main_layout.addWidget(QLabel("Дата кормления:"))
        main_layout.addWidget(self.date_edit)
        main_layout.addWidget(QLabel("Тип корма:"))
        main_layout.addWidget(self.food_type_combo)
        main_layout.addWidget(QLabel("Общий объем корма:"))
        main_layout.addWidget(self.total_feed_spinbox)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.table)

    def set_aquarium_id(self, aquarium_id):
        """Устанавливает ID аквариума и обновляет таблицу."""
        self.aquarium_id = aquarium_id
        self.load_seafood_info()
        self.update_table()

    def load_seafood_info(self):
        """Загружает информацию о морепродукте в аквариуме"""
        if self.aquarium_id is None:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT seafood_id, название_вида 
                FROM морепродукты 
                WHERE aquarium_id = %s
            """, (self.aquarium_id,))
            
            seafood_data = cursor.fetchone()
            if seafood_data:
                self.seafood_id = seafood_data[0]
                self.seafood_name = seafood_data[1]
            else:
                QMessageBox.warning(self, "Предупреждение", 
                                  "В выбранном аквариуме нет морепродуктов!")
                self.seafood_id = None
                self.seafood_name = "Не определено"
                
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось загрузить данные: {e}")

    def add_feeding(self):
        """Добавляет данные о кормлении в базу данных."""
        if self.aquarium_id is None:
            QMessageBox.warning(self, "Ошибка", "Аквариум не выбран.")
            return
            
        if self.seafood_id is None:
            QMessageBox.warning(self, "Ошибка", 
                              "В выбранном аквариуме нет морепродуктов!")
            return

        feed_date = self.date_edit.date().toString("yyyy-MM-dd")
        food_type = self.food_type_combo.currentText()
        total_feed = self.total_feed_spinbox.value()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO кормления 
                (aquarium_id, seafood_id, дата_кормления, тип_корма, общий_объем_корма)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.aquarium_id, self.seafood_id, feed_date, food_type, total_feed))
            self.db_connection.commit()

            # Обновляем таблицу
            self.update_table()
            
            # Очищаем поля ввода
            self.total_feed_spinbox.setValue(0)
            
            QMessageBox.information(self, "Успех", "Данные о кормлении добавлены!")
            self.operation_completed.emit()
        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось добавить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def update_table(self):
        """Обновляет таблицу данными из базы только для выбранного аквариума."""
        if self.aquarium_id is None:
            self.table.setRowCount(0)
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    k.feeding_id, 
                    k.дата_кормления, 
                    k.тип_корма, 
                    k.общий_объем_корма,
                    m.название_вида
                FROM кормления k
                JOIN морепродукты m ON k.seafood_id = m.seafood_id
                WHERE k.aquarium_id = %s
                ORDER BY k.дата_кормления DESC
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
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось загрузить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")
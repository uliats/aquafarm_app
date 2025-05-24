from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
import psycopg2
from datetime import datetime


class AddSpeciesStateWidget(QWidget):
    operation_completed = pyqtSignal()

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.aquarium_id = None
        self.seafood_id = None
        self.initUI()

    def initUI(self):
        # Основной вертикальный лейаут
        main_layout = QVBoxLayout(self)

        # Форма для ввода данных
        form_group = QGroupBox("Параметры состояния особей")
        form_layout = QFormLayout()

        # Поля для ввода числовых данных
        self.total_count = QSpinBox()
        self.total_count.setRange(0, 9999)
        
        self.damaged_count = QSpinBox()
        self.damaged_count.setRange(0, 9999)
        
        self.abnormal_count = QSpinBox()
        self.abnormal_count.setRange(0, 9999)
        
        self.dead_count = QSpinBox()
        self.dead_count.setRange(0, 9999)
        
        self.avg_size = QDoubleSpinBox()
        self.avg_size.setRange(0, 999.99)
        self.avg_size.setDecimals(2)
        self.avg_size.setSuffix(" см")
        
        self.avg_weight = QDoubleSpinBox()
        self.avg_weight.setRange(0, 9999.99)
        self.avg_weight.setDecimals(2)
        self.avg_weight.setSuffix(" г")

        # Добавляем поля в форму
        form_layout.addRow("Общее количество:", self.total_count)
        form_layout.addRow("С повреждениями:", self.damaged_count)
        form_layout.addRow("С аномальным поведением:", self.abnormal_count)
        form_layout.addRow("Умершие особи:", self.dead_count)
        form_layout.addRow("Средний размер:", self.avg_size)
        form_layout.addRow("Средний вес:", self.avg_weight)
        
        form_group.setLayout(form_layout)

        # Кнопка для добавления данных
        self.add_button = QPushButton('Добавить данные о состоянии', self)
        self.add_button.clicked.connect(self.add_species_state)

        # Таблица для отображения истории
        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Дата', 'Общее', 'Повреждения', 
            'Аномалии', 'Умерло', 'Размер', 'Вес', 'Состояние'
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        [self.table.setColumnWidth(i, 90) for i in range(2, 8)]
        self.table.setColumnWidth(8, 120)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Добавляем виджеты в лейаут
        main_layout.addWidget(form_group)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.table)

    def set_aquarium_id(self, aquarium_id):
        """Устанавливает ID аквариума и загружает seafood_id"""
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
                SELECT seafood_id FROM морепродукты 
                WHERE aquarium_id = %s LIMIT 1
            """, (self.aquarium_id,))
            
            result = cursor.fetchone()
            if result:
                self.seafood_id = result[0]
            else:
                QMessageBox.warning(self, "Ошибка", 
                                  "В аквариуме не найден морепродукт!")
                self.seafood_id = None
                
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось загрузить данные: {e}")

    def add_species_state(self):
        """Добавляет данные о состоянии особей в базу данных."""
        if self.aquarium_id is None or self.seafood_id is None:
            QMessageBox.warning(self, "Ошибка", "Аквариум или морепродукт не определен!")
            return

        # Получаем значения из полей ввода
        total = self.total_count.value()
        damaged = self.damaged_count.value()
        abnormal = self.abnormal_count.value()
        dead = self.dead_count.value()
        avg_size = self.avg_size.value()
        avg_weight = self.avg_weight.value()

        # Проверка корректности данных
        if damaged > total or abnormal > total or dead > total:
            QMessageBox.warning(self, "Ошибка", 
                              "Количество с повреждениями/аномалиями/умерших не может превышать общее количество!")
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO состояние_особей (
                    aquarium_id, seafood_id, 
                    общее_количество, количество_с_повреждениями,
                    количество_с_аномальным_поведением, количество_умерших,
                    средний_текущий_размер, средний_текущий_вес
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.aquarium_id, self.seafood_id,
                total, damaged, abnormal, dead,
                avg_size, avg_weight
            ))
            self.db_connection.commit()

            # Обновляем таблицу и очищаем поля
            self.update_table()
            self.clear_fields()
            
            QMessageBox.information(self, "Успех", "Данные о состоянии особей добавлены!")
            self.operation_completed.emit()
            
        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось добавить данные: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def clear_fields(self):
        """Очищает поля ввода после успешного добавления"""
        self.total_count.setValue(0)
        self.damaged_count.setValue(0)
        self.abnormal_count.setValue(0)
        self.dead_count.setValue(0)
        self.avg_size.setValue(0)
        self.avg_weight.setValue(0)

    def update_table(self):
        """Обновляет таблицу историей состояний"""
        if self.aquarium_id is None or self.seafood_id is None:
            self.table.setRowCount(0)
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    health_id, дата_замера,
                    общее_количество, количество_с_повреждениями,
                    количество_с_аномальным_поведением, количество_умерших,
                    средний_текущий_размер, средний_текущий_вес
                FROM состояние_особей
                WHERE aquarium_id = %s AND seafood_id = %s
                ORDER BY дата_замера DESC
                LIMIT 50
            """, (self.aquarium_id, self.seafood_id))
            
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    # Форматируем дату
                    if j == 1:
                        item = QTableWidgetItem(col.strftime("%Y-%m-%d %H:%M"))
                    # Форматируем размер и вес
                    elif j in (6, 7):
                        item = QTableWidgetItem(f"{col:.2f}")
                    else:
                        item = QTableWidgetItem(str(col))
                    
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(i, j, item)
                
                # Добавляем оценку состояния в последнюю колонку
                status = self.calculate_status(
                    row[2], row[3], row[4], row[5]
                )
                item = QTableWidgetItem(status)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 8, item)
                
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", 
                               f"Не удалось загрузить историю: {e}")

    def calculate_status(self, total, damaged, abnormal, dead):
        """Рассчитывает общую оценку состояния особей"""
        if total == 0:
            return "Нет данных"
        
        healthy = total - damaged - abnormal - dead
        health_percent = (healthy / total) * 100
        
        if dead > total * 0.3:  # Более 30% умерло
            return "Критическое"
        elif health_percent >= 80:
            return "Отличное"
        elif health_percent >= 60:
            return "Хорошее"
        elif health_percent >= 40:
            return "Удовлетворительное"
        else:
            return "Плохое"
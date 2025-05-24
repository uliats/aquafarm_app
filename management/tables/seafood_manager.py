from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
import psycopg2
from PyQt5.QtGui import QIcon

class SeafoodManager(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.initUI()
        self.refresh_data()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('Добавить', self)
        self.add_btn.setIcon(QIcon("icons/add.png"))
        self.add_btn.clicked.connect(self.add_record)
        
        self.delete_btn = QPushButton('Удалить', self)
        self.delete_btn.setIcon(QIcon("icons/delete.png"))
        self.delete_btn.clicked.connect(self.delete_record)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

    def refresh_data(self):
        """Загружает данные из базы"""
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
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels([
                'ID', 'Название', 'Норма веса', 'Норма размера', 
                'Тип корма', 'Норма корма', 'Смертность', 'ID аквариума'
            ])
            
            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col) if col is not None else "")
                    self.table.setItem(i, j, item)
            
            self.table.hideColumn(0)  # Скрываем ID
            self.table.hideColumn(7)  # Скрываем ID аквариума
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def add_record(self):
        """Добавляет новую запись"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i in range(self.table.columnCount()):
            self.table.setItem(row, i, QTableWidgetItem(""))

    def delete_record(self):
        """Удаляет выбранную запись"""
        row = self.table.currentRow()
        if row >= 0:
            seafood_id = self.table.item(row, 0).text()
            if QMessageBox.question(
                self, "Подтверждение", 
                f"Удалить морепродукт ID {seafood_id}?",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                self.table.removeRow(row)

    def save_changes(self):
        """Сохраняет изменения в базе данных"""
        try:
            cursor = self.db_connection.cursor()
            
            for row in range(self.table.rowCount()):
                seafood_id = self.table.item(row, 0).text()
                name = self.table.item(row, 1).text()
                weight = self.table.item(row, 2).text()
                size = self.table.item(row, 3).text()
                food_type = self.table.item(row, 4).text()
                food_rate = self.table.item(row, 5).text()
                mortality = self.table.item(row, 6).text()
                aquarium_id = self.table.item(row, 7).text()
                
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
                    self.table.item(row, 0).setText(str(new_id))
            
            self.db_connection.commit()
        except psycopg2.Error as e:
            self.db_connection.rollback()
            raise Exception(f"Ошибка при сохранении морепродуктов: {e}")
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                            QPushButton, QVBoxLayout, QMessageBox, QDesktopWidget, QFileDialog)
from PyQt5.QtCore import Qt, QFile, QTextStream
from connection import get_db_connection

def load_stylesheet():
    """Загружает CSS стили из файла"""
    try:
        # Определяем путь к файлу стилей относительно расположения скрипта
        base_dir = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(base_dir, "styles", "style.css")
        
        file = QFile(style_path)
        if not file.open(QFile.ReadOnly | QFile.Text):
            print(f"Не удалось открыть файл стилей: {style_path}")
            return ""
            
        stream = QTextStream(file)
        return stream.readAll()
    except Exception as e:
        print(f"Ошибка загрузки стилей: {str(e)}")
        return ""


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

                # Применяем стили после инициализации UI
        self.apply_styles()

    def apply_styles(self):
        """Применяет CSS стили к окну"""
        stylesheet = load_stylesheet()
        if stylesheet:
            self.setStyleSheet(stylesheet)
            # Применяем стили также к дочерним виджетам
            for child in self.findChildren(QWidget):
                child.setStyleSheet(stylesheet)


    def initUI(self):
        self.setWindowTitle('Авторизация')
        self.resize(500, 250)  # Увеличиваем размер окна
        
        # Центрируем окно на экране
        self.center()
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Стилизуем заголовок
        title_label = QLabel('Система управления аквариумами')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        
        self.login_label = QLabel('Логин:')
        self.login_label.setObjectName("loginLabel")
        
        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Введите ваш логин")
        self.login_input.setMinimumHeight(35)
        self.login_input.setObjectName("loginInput")
        
        self.password_label = QLabel('Пароль:')
        self.password_label.setObjectName("passwordLabel")
        
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.setObjectName("passwordInput")
        
        self.login_button = QPushButton('Войти', self)
        self.login_button.setMinimumHeight(40)
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.on_login)
        
        # Добавляем виджеты в layout
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def center(self):
        """Центрирует окно на экране"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        conn = get_db_connection()
        cur = conn.cursor()
        self.db_connection = get_db_connection()  # Сохраняем соединение в атрибуте класса
        cur = self.db_connection.cursor()

        cur.execute("SELECT * FROM пользователи WHERE логин = %s AND пароль_пользователя = %s", (login, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            if user[5]:  # is_operational
                self.open_operational_window()
            elif user[6]:  # is_management
                self.open_management_window()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def open_operational_window(self):
        from operational.mainOperational import OperationalWindow
        self.operational_window = OperationalWindow(self.db_connection)
        self.operational_window.show()
        self.close()

    def open_management_window(self):
        from management.mainManagement import ManagementWindow
        self.management_window = ManagementWindow(self.db_connection)
        self.management_window.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Загружаем и применяем глобальные стили
    app.setStyleSheet(load_stylesheet())
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

    
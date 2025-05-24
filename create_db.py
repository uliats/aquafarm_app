import psycopg2
from psycopg2 import sql

# Параметры подключения к базе данных
DB_NAME = "aquarium_db"
DB_USER = "postgres"
DB_PASSWORD = "1234"  # Замените на ваш пароль
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Создает базу данных и все таблицы"""
    
    try:
        # Подключаемся к серверу PostgreSQL (без указания конкретной базы)
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Создаем базу данных, если она не существует
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_NAME))
        )
        print(f"База данных {DB_NAME} успешно создана")
        
        cursor.close()
        conn.close()
        
        # Теперь подключаемся к созданной базе данных
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Создаем таблицы
        create_tables(cursor)
        
        print("Все таблицы успешно созданы")
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_tables(cursor):
    """Создает все таблицы в базе данных"""
    
    # Таблица пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS пользователи (
        user_id SERIAL PRIMARY KEY,
        имя_пользователя VARCHAR(50),
        роль_пользователя VARCHAR(20),
        логин VARCHAR(50),
        пароль_пользователя VARCHAR(100),
        is_оперативный BOOLEAN DEFAULT FALSE,
        is_менеджмент BOOLEAN DEFAULT FALSE
    )
    """)
    
    # Таблица аквариумов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS аквариумы (
        aquarium_id SERIAL PRIMARY KEY,
        ответственный_пользователь INT REFERENCES пользователи(user_id),
        объем DECIMAL(10,2),
        статус VARCHAR(20) DEFAULT 'Активен',
        тип_аквариума VARCHAR(20) DEFAULT 'Товарный'
    )
    """)
    
    # Таблица состояния аквариума
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS состояние_аквариума (
        aquarium_state_id SERIAL PRIMARY KEY,
        aquarium_id INT REFERENCES аквариумы(aquarium_id),
        дата_проверки TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        состояние_фильтра INT,
        состояние_стекла INT,
        уровень_водорослей DECIMAL(5,2),
        прозрачность_воды DECIMAL(5,2)
    )
    """)
    
    # Таблица морепродуктов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS морепродукты (
        seafood_id SERIAL PRIMARY KEY,
        название_вида VARCHAR(50),
        нормальный_вес DECIMAL(6,2),
        нормальный_размер DECIMAL(5,2),
        тип_корма VARCHAR(50),
        норма_корма_на_одну_особь DECIMAL(6,2),
        уровень_смертности_группы DECIMAL(5,2),
        aquarium_id INT REFERENCES аквариумы(aquarium_id)
    )
    """)
    
    # Таблица оптимальных параметров содержания
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS оптимальные_параметры_содержания (
        optimal_params_id SERIAL PRIMARY KEY,
        seafood_id INT REFERENCES морепродукты(seafood_id),
        оптимальная_температура DECIMAL(5,2),
        допустимое_отклонение_температуры DECIMAL(3,2),
        уровень_кислорода DECIMAL(4,2),
        допустимое_отклонение_кислорода DECIMAL(3,2),
        уровень_pH DECIMAL(3,2),
        допустимое_отклонение_pH DECIMAL(2,2),
        требуемый_объем_воды_на_особь DECIMAL(6,2)
    )
    """)
    
    # Таблица состояния особей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS состояние_особей (
        health_id SERIAL PRIMARY KEY,
        aquarium_id INT REFERENCES аквариумы(aquarium_id),
        seafood_id INT REFERENCES морепродукты(seafood_id),
        дата_замера TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        общее_количество INT,
        количество_с_повреждениями INT,
        количество_с_аномальным_поведением INT,
        количество_умерших INT,
        средний_текущий_размер DECIMAL(5,2),
        средний_текущий_вес DECIMAL(6,2)
    )
    """)
    
    # Таблица готовности продукции
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS готовность_продукции (
        readiness_id SERIAL PRIMARY KEY,
        seafood_id INT REFERENCES морепродукты(seafood_id),
        требуемый_вес_к_продаже DECIMAL(6,2),
        требуемый_размер_к_продаже DECIMAL(5,2)
    )
    """)
    
    # Таблица параметров воды
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS параметры_воды (
        parameter_id SERIAL PRIMARY KEY,
        aquarium_id INT REFERENCES аквариумы(aquarium_id),
        дата_измерения TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        температура DECIMAL(5,2),
        pH DECIMAL(3,2),
        уровень_кислорода DECIMAL(4,2)
    )
    """)
    
    # Таблица кормлений
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS кормления (
        feeding_id SERIAL PRIMARY KEY,
        aquarium_id INT REFERENCES аквариумы(aquarium_id),
        seafood_id INT REFERENCES морепродукты(seafood_id),
        дата_кормления TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        общий_объем_корма DECIMAL(10,2),
        тип_корма VARCHAR(50)
    )
    """)
    
    # Таблица холодильников
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS холодильники (
        fridge_id SERIAL PRIMARY KEY,
        seafood_id INT REFERENCES морепродукты(seafood_id),
        срок_хранения INT,
        количество INT,
        состояние_холодильника VARCHAR(50) DEFAULT 'Рабочее',
        дата_последней_проверки DATE
    )
    """)

if __name__ == "__main__":
    create_database()
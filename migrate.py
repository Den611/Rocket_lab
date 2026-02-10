
from database import Database

print("Connecting to database...")
db = Database()

try:
    with db.connection:
        with db.connection.cursor() as cursor:
            print("Updating 'users' table...")
            # Додаємо колонку дати (текстом YYYY-MM-DD)
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_quiz_date DATE DEFAULT CURRENT_DATE;")
            # Додаємо лічильник
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_quiz_count INTEGER DEFAULT 0;")

    print("✅ Базу даних успішно оновлено! Тепер можна видалити цей файл.")
except Exception as e:
    print(f"❌ Помилка: {e}")
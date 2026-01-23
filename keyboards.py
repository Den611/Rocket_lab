from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_kb_no_family():
    kb = [
        [KeyboardButton(text="🚀 Створити сім'ю"), KeyboardButton(text="🔗 Приєднатися до сім'ї")],
        [KeyboardButton(text="👤 Мій профіль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_main_kb_with_family():
    kb = [
        [KeyboardButton(text="🌌 Кабінет сім'ї"), KeyboardButton(text="🛸 Ангар (Веб)")],
        # Окремі кнопки для Місій та Заводів
        [KeyboardButton(text="📡 Місії"), KeyboardButton(text="🏭 Інфраструктура")],
        [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="❌ Покинути сім'ю")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
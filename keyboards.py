from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_kb_no_family():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Створити сім'ю"), KeyboardButton(text="🔗 Приєднатися до сім'ї")],
            [KeyboardButton(text="ℹ️ Допомога")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію..."
    )

def get_main_kb_with_family():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌌 Кабінет сім'ї"), KeyboardButton(text="🛸 Політ (Веб)")],
            [KeyboardButton(text="📡 Місії"), KeyboardButton(text="🏭 Інфраструктура")],
            [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="🎁 Вітальний бонус")],
            [KeyboardButton(text="🎲 Розваги"), KeyboardButton(text="⚔️ Рейд")],
            # Кнопка Академії вже є тут 👇
            [KeyboardButton(text="👾 Космічний бій"), KeyboardButton(text="🎓 Академія")],
            [KeyboardButton(text="❌ Покинути сім'ю"), KeyboardButton(text="🚀 Навігація")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Панель керування Rocket Lab"
    )

def main_keyboard(user_family_id):
    if user_family_id:
        return get_main_kb_with_family()
    else:
        return get_main_kb_no_family()
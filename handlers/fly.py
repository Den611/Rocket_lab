import json
from aiogram import Router, F, types
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import Database
from keyboards import main_keyboard

router = Router()
db = Database('space.db')

WEB_APP_URL = "https://rocket-lab.onrender.com"


# 1. Відкриваємо Web App через кнопку "🛸 Політ (Веб)"
@router.message(F.text == "🛸 Політ (Веб)")
async def open_webapp(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # Кнопка, яка відкриває сайт всередині Telegram
    builder.button(text="🚀 ВІДКРИТИ ТЕРМІНАЛ", web_app=WebAppInfo(url=WEB_APP_URL))
    builder.button(text="🔙 Назад")
    builder.adjust(1)

    await message.answer(
        "🛸 **СИСТЕМА ПОЛЬОТУ**\n\n"
        "Завантаження інтерфейсу корабля...\n"
        "Натисніть кнопку нижче, щоб відкрити панель керування.",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )


# 2. Кнопка "Назад" повертає головне меню
@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Головне меню", reply_markup=main_keyboard())


# 3. Обробка даних, які приходять з сайту (якщо ви налаштували відправку даних)
@router.message(F.web_app_data)
async def process_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        # Приклад: якщо сайт відправляє 'action': 'game_score' (можна адаптувати під ваші потреби)
        if data.get('action') == 'game_score':
            score = int(data.get('amount', 0))

            fid = db.get_user_family(message.from_user.id)
            if fid:
                db.update_balance(fid, score)
                await message.answer(
                    f"✅ **ДАНІ ОТРИМАНО**\n"
                    f"💰 Зараховано: **{score}** ресурсів.",
                    reply_markup=main_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await message.answer("Помилка: Сім'ю не знайдено.", reply_markup=main_keyboard())

    except Exception as e:
        print(f"Web App Error: {e}")
        await message.answer("Дані отримано, повертаємось в меню.", reply_markup=main_keyboard())
from aiogram import Router, types, F
from aiogram.filters import Command
from database import Database
# ВИПРАВЛЕНИЙ ІМПОРТ 👇
from keyboards import main_keyboard

router = Router()
db = Database('space.db')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "SpaceTraveller"

    db.add_user(user_id, username)
    family_id = db.get_user_family(user_id)

    if family_id:
        info = db.get_family_info(family_id)
        # info: 0=name, ..., 5=planet

        text = (
            f"🟢 **СИСТЕМА ІДЕНТИФІКАЦІЇ: УСПІХ**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пілот: **{username}**\n"
            f"🚀 Екіпаж: **{info[0]}**\n"
            f"📍 Поточна база: **{info[5]}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Очікую ваших вказівок через бортовий комп'ютер 👇"
        )
        # Передаємо family_id, щоб показати повне меню
        await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(family_id))
    else:
        text = (
            f"🌌 **ЛАСКАВО ПРОСИМО ДО ROCKET LAB** 🌌\n\n"
            f"Ви — новий учасник космічної програми. Ваша мета — підкорити Сонячну систему.\n\n"
            f"⚠️ **ВАЖЛИВО:** Одинакам тут не вижити. Вам потрібно:\n"
            f"1️⃣ Створити власну космічну сім'ю (екіпаж).\n"
            f"2️⃣ Або приєднатися до друзів за кодом.\n\n"
            f"👇 **Оберіть дію для початку:**"
        )
        # Передаємо None, бо сім'ї немає
        await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(None))


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Допомога")
async def cmd_help(message: types.Message):
    text = (
        "📘 **БОРТОВИЙ ЖУРНАЛ: ІНСТРУКЦІЯ**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 **МІСІЇ**\n"
        "Літайте за ресурсами. Увага на ризик піратів!\n\n"
        "🎓 **АКАДЕМІЯ**\n"
        "Проходьте тести про космос і заробляйте монети (5 разів на день).\n\n"
        "🏭 **ІНФРАСТРУКТУРА**\n"
        "Будуйте шахти для пасивного доходу.\n\n"
        "⚔️ **ВІЙНА (PvP)**\n"
        "Грабуйте інші сім'ї на Марсі та Юпітері."
    )
    await message.answer(text, parse_mode="Markdown")
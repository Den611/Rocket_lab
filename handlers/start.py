from aiogram import Router, types
from aiogram.filters import Command
from database import Database
from keyboards import get_main_kb_no_family, get_main_kb_with_family

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

        await message.answer(
            f"📡 **ВХІДНИЙ СИГНАЛ...**\n\n"
            f"Вітаю, капітане **{username}**!\n"
            f"Команда **«{info[0]}»** базується на планеті **{info[5]}**.\n\n"
            f"🚀 Ракета готова до старту.\n"
            f"⛏ Шахти працюють.\n\n"
            f"Чекаємо ваших наказів у меню нижче 👇",
            parse_mode="Markdown",
            reply_markup=get_main_kb_with_family()
        )
    else:
        await message.answer(
            f"🌌 **ROCKET LAB: SPACE TYCOON** 🌌\n\n"
            f"Привіт, майбутній підкорювач зірок!\n"
            f"Тут ми будуємо ракети, збираємо команду та летимо від Землі до Юпітера.\n\n"
            f"🛡 **Правила виживання:**\n"
            f"1. **Сім'я** — це твій екіпаж. Грати самому неможливо.\n"
            f"2. **Місії** — вимагають згоди всіх учасників.\n"
            f"3. **Ресурси** — унікальні на кожній планеті.\n\n"
            f"👇 **Почніть свій шлях зараз:**",
            parse_mode="Markdown",
            reply_markup=get_main_kb_no_family()
        )
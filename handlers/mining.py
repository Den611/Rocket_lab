import asyncio
import logging
from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest
from database import Database

router = Router()


async def update_resources_loop(message: types.Message, user_id: int, db: Database):
    """
    Фонове завдання, яке оновлює текст повідомлення кожні 5 секунд,
    зчитуючи дані з обох баз даних (space.db та resourses.db).
    """
    family_id = db.get_user_family(user_id)
    if not family_id:
        return

    while True:
        try:
            # Чекаємо 5 секунд перед наступним оновленням
            await asyncio.sleep(5)

            # Отримуємо свіжі дані (метод get_family_resources робить JOIN з resourses.db)
            # Структура res згідно з вашим кодом у database.py:
            # 0: balance, 1: iron, 2: fuel, 3: regolith, 4: he3,
            # 5: silicon, 6: oxide, 7: hydrogen, 8: helium, 11: planet
            res = db.get_family_resources(family_id)

            if not res:
                break

            new_text = (
                f"🛰 **Бортовий комп'ютер: Ресурси сім'ї**\n"
                f"━━━━━━━━━━━━━━\n"
                f"💰 Кредити: `{res[0]}`\n\n"
                f"⛏ **Матеріали:**\n"
                f"⚙️ Залізо: `{res[1]}` | ⛽ Паливо: `{res[2]}`\n"
                f"💎 Гелій-3: `{res[4]}` | 🌑 Реголіт: `{res[3]}`\n"
                f"🧪 Оксид: `{res[6]}` | 💾 Кремній: `{res[5]}`\n"
                f"🎈 Водень: `{res[7]}` | 🌌 Гелій: `{res[8]}`\n"
                f"━━━━━━━━━━━━━━\n"
                f"📍 Поточна локація: **{res[11]}**\n"
                f"🕒 Оновлено: щойно"
            )

            # Редагуємо існуюче повідомлення
            await message.edit_text(
                text=new_text,
                reply_markup=message.reply_markup,
                parse_mode="Markdown"
            )

        except TelegramBadRequest as e:
            # Якщо текст не змінився або повідомлення видалено користувачем
            if "message is not modified" in str(e):
                continue
            logging.info(f"Цикл оновлення зупинено: {e}")
            break
        except Exception as e:
            logging.error(f"Помилка в циклі оновлення ресурсів: {e}")
            break


@router.callback_query(F.data == "view_resources")
async def show_resources(callback: types.CallbackQuery, db: Database):
    """
    Основний обробник натискання кнопки 'Ресурси'.
    Відправляє повідомлення та запускає фоновий цикл оновлення.
    """
    family_id = db.get_user_family(callback.from_user.id)
    if not family_id:
        await callback.answer("Ви не в сім'ї!", show_alert=True)
        return

    res = db.get_family_resources(family_id)

    initial_text = (
        f"🛰 **Бортовий комп'ютер: Ресурси сім'ї**\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 Кредити: `{res[0]}`\n"
        f"⏳ Завантаження актуальних даних..."
    )

    # Відправляємо нове повідомлення (або редагуємо поточне)
    sent_message = await callback.message.answer(
        text=initial_text,
        parse_mode="Markdown"
    )

    # ЗАПУСК МАГІЇ: створюємо асинхронне завдання, яке працює незалежно
    asyncio.create_task(update_resources_loop(sent_message, callback.from_user.id, db))

    await callback.answer()
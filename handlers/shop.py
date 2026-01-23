from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database

router = Router()
db = Database('space.db')


@router.message(F.text == "🛒 Магазин")
async def open_shop(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!")
        return

    # Отримуємо інформацію про сім'ю
    # 0=name, 1=code, 2=balance, 3=engine, 4=hull, 5=planet
    info = db.get_family_info(family_id)

    balance = info[2]
    eng_lvl = info[3]
    hull_lvl = info[4]

    # Ціна зростає з рівнем
    eng_price = eng_lvl * 500
    hull_price = hull_lvl * 500

    builder = InlineKeyboardBuilder()
    builder.button(text=f"🔥 Двигун v{eng_lvl + 1} (💰{eng_price})", callback_data=f"buy_upg:engine_lvl:{eng_price}")
    builder.button(text=f"🛡 Корпус v{hull_lvl + 1} (💰{hull_price})", callback_data=f"buy_upg:hull_lvl:{hull_price}")
    builder.adjust(1)

    text = (
        f"🛒 **КОСМІЧНИЙ МАГАЗИН**\n"
        f"💰 Ваш баланс: **{balance}**\n\n"
        f"🔧 **Покращення ракети:**\n"
        f"🔥 **Двигун (Рівень {eng_lvl}):** Збільшує швидкість та шанс успіху.\n"
        f"🛡 **Корпус (Рівень {hull_lvl}):** Захищає від аварій.\n"
    )

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("buy_upg:"))
async def process_buy(callback: types.CallbackQuery):
    # data: "buy_upg:type:price"
    parts = callback.data.split(":")
    upg_type = parts[1]  # engine_lvl або hull_lvl
    price = int(parts[2])

    family_id = db.get_user_family(callback.from_user.id)
    balance = db.get_family_resources(family_id)[0]

    if balance >= price:
        # Списуємо гроші через deduct_resources (або update_balance)
        # Оскільки deduct_resources у нас універсальний, використаємо його
        db.deduct_resources(family_id, price)

        # Оновлюємо рівень
        db.update_upgrade(family_id, upg_type)

        await callback.message.edit_text("✅ **Успішна покупка!**\nМодуль встановлено на ракету.")
    else:
        await callback.answer("❌ Недостатньо коштів!", show_alert=True)
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime

router = Router()
db = Database('space.db')

# Ресурси по планетах (Earth -> Moon -> Mars -> Upiter)
PLANET_RESOURCES = {
    "Earth": [
        {"name": "Залізо", "col": "res_iron", "emoji": "⛓", "rate_mod": 1.0},
        {"name": "Паливо", "col": "res_fuel", "emoji": "⛽", "rate_mod": 0.5}
    ],
    "Moon": [
        {"name": "Реголіт", "col": "res_regolith", "emoji": "🌑", "rate_mod": 0.9},
        {"name": "Гелій-3", "col": "res_he3", "emoji": "⚛️", "rate_mod": 0.3}
    ],
    "Mars": [
        {"name": "Кремній", "col": "res_silicon", "emoji": "💾", "rate_mod": 0.8},
        {"name": "Оксид", "col": "res_oxide", "emoji": "🧪", "rate_mod": 0.4}
    ],
    "Upiter": [
        {"name": "Водень", "col": "res_hydrogen", "emoji": "🌫", "rate_mod": 0.7},
        {"name": "Гелій", "col": "res_helium", "emoji": "🎈", "rate_mod": 0.2}
    ]
}


@router.message(F.text == "⛏ Шахта")
async def mining_menu(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!")
        return

    data = db.get_family_resources(family_id)
    # data: ... 9=mine_lvl, 10=last_coll, 11=planet ...

    planet = data[11]
    mine_lvl = data[9]
    last_collection_str = data[10]

    resources = PLANET_RESOURCES.get(planet, PLANET_RESOURCES["Earth"])
    res1 = resources[0]
    res2 = resources[1]

    try:
        last_time = datetime.strptime(last_collection_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        last_time = datetime.now()

    now = datetime.now()
    minutes_passed = (now - last_time).total_seconds() / 60
    base_rate = mine_lvl * 10

    if mine_lvl == 0:
        amount1, amount2 = 0, 0
    else:
        amount1 = int((minutes_passed / 60) * base_rate * res1['rate_mod'])
        amount2 = int((minutes_passed / 60) * base_rate * res2['rate_mod'])

    builder = InlineKeyboardBuilder()

    if mine_lvl == 0:
        price = 500
        builder.button(text=f"🏗 Побудувати станцію (💰{price})", callback_data=f"build_mine:{price}")
    else:
        if amount1 > 0 or amount2 > 0:
            builder.button(
                text=f"📥 Зібрати ({amount1}{res1['emoji']} + {amount2}{res2['emoji']})",
                callback_data=f"collect_res:{amount1}:{res1['col']}:{amount2}:{res2['col']}"
            )
        upgrade_price = (mine_lvl + 1) * 1000
        builder.button(text=f"⬆ Покращити (💰{upgrade_price})", callback_data=f"upgrade_mine:{upgrade_price}")

    builder.adjust(1)

    text = (
        f"🏭 **Видобувна станція: {planet}**\n"
        f"Рівень: {mine_lvl}\n"
        f"Ресурси:\n1. {res1['emoji']} {res1['name']}\n2. {res2['emoji']} {res2['name']}\n\n"
        f"⏳ Накопичено: **{amount1}** і **{amount2}**\n"
        f"💰 Баланс: {data[0]}"
    )

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


# Хендлери кнопок (build_mine, collect_res) залишаються такими ж, як в попередньому коді
# (Якщо треба - скопіюйте блок @router.callback_query з минулої відповіді)
@router.callback_query(F.data.startswith("build_mine:") | F.data.startswith("upgrade_mine:"))
async def process_upgrade(callback: types.CallbackQuery):
    price = int(callback.data.split(":")[1])
    family_id = db.get_user_family(callback.from_user.id)
    data = db.get_family_resources(family_id)
    balance = data[0]
    if balance >= price:
        db.upgrade_mine(family_id, price)
        await callback.message.edit_text("✅ **Готово!** Рівень шахти підвищено.")
    else:
        await callback.answer("Недостатньо грошей!", show_alert=True)


@router.callback_query(F.data.startswith("collect_res:"))
async def process_collect(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    db.collect_resources(family_id=db.get_user_family(callback.from_user.id),
                         res1_col=parts[2], amount1=int(parts[1]),
                         res2_col=parts[4], amount2=int(parts[3]))
    await callback.message.edit_text("✅ **Ресурси зібрано!**")
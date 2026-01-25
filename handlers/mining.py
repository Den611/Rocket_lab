from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime

router = Router()
db = Database('space.db')

BUILD_TIME = 15  # Час будівництва у хвилинах

# Налаштування ресурсів для кожної планети
PLANET_RESOURCES = {
    "Earth": [{"name": "Залізо", "col": "res_iron", "emoji": "⛓", "mod": 1.0},
              {"name": "Паливо", "col": "res_fuel", "emoji": "⛽", "mod": 0.5}],
    "Moon": [{"name": "Реголіт", "col": "res_regolith", "emoji": "🌑", "mod": 0.9},
             {"name": "Гелій-3", "col": "res_he3", "emoji": "⚛️", "mod": 0.3}],
    "Mars": [{"name": "Кремній", "col": "res_silicon", "emoji": "💾", "mod": 0.8},
             {"name": "Оксид", "col": "res_oxide", "emoji": "🧪", "mod": 0.4}],
    "Jupiter": [{"name": "Водень", "col": "res_hydrogen", "emoji": "🌫", "mod": 0.7},
                {"name": "Гелій", "col": "res_helium", "emoji": "🎈", "mod": 0.2}]
}


@router.message(F.text == "🏭 Інфраструктура")
async def mining_menu(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!")
        return

    # 1. Перевірка таймера будівництва
    timers = db.get_timers(family_id)
    if timers[3]:  # upgrade_end_time
        try:
            end_time = datetime.strptime(timers[3], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end_time = datetime.strptime(timers[3], "%Y-%m-%d %H:%M:%S")

        if datetime.now() < end_time:
            rem = int((end_time - datetime.now()).total_seconds() // 60)
            await message.answer(f"🏗 **БУДІВНИЦТВО ТРИВАЄ**\nЗалишилось: {rem} хв.")
            return
        else:
            # Якщо час вийшов, завершуємо
            db.finish_upgrade(family_id)
            await message.answer("✅ **БУДІВНИЦТВО ЗАВЕРШЕНО!**\nВиробництво збільшено.")

    # 2. Отримуємо дані про сім'ю
    data = db.get_family_resources(family_id)
    # data[11] = planet, data[9] = mine_lvl
    planet = data[11]
    mine_lvl = data[9]

    # Визначаємо ресурси поточної планети
    res = PLANET_RESOURCES.get(planet, PLANET_RESOURCES["Earth"])

    # 3. Розрахунок накопичених ресурсів
    try:
        last = datetime.strptime(data[10], "%Y-%m-%d %H:%M:%S")
    except:
        last = datetime.now()

    mins = (datetime.now() - last).total_seconds() / 60

    base = mine_lvl * 10  # Базова ефективність

    # Формула: (Хвилини / 60) * База * Модифікатор ресурсу
    a1 = int((mins / 60) * base * res[0]['mod']) if mine_lvl > 0 else 0
    a2 = int((mins / 60) * base * res[1]['mod']) if mine_lvl > 0 else 0

    price = (mine_lvl + 1) * 800

    # 4. Меню кнопок
    builder = InlineKeyboardBuilder()
    if mine_lvl == 0:
        builder.button(text=f"🏗 Будувати 1-й завод (💰{price})", callback_data=f"build:{price}")
    else:
        if a1 > 0 or a2 > 0:
            # Кнопка збору: передаємо кількість і назви колонок у базу
            builder.button(
                text=f"📥 Зібрати (+{a1} {res[0]['emoji']} / +{a2} {res[1]['emoji']})",
                callback_data=f"col:{a1}:{res[0]['col']}:{a2}:{res[1]['col']}"
            )
        builder.button(text=f"🏭 Розширити ({mine_lvl + 1}-й рівень) 💰{price}", callback_data=f"build:{price}")
    builder.adjust(1)

    stats = (
        f"🏭 **ІНФРАСТРУКТУРА: {planet}**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Рівень заводів: **{mine_lvl}**\n"
        f"Ефективність: **{base}/год**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 **На складі готової продукції:**\n"
        f"{res[0]['emoji']} {res[0]['name']}: **{a1}**\n"
        f"{res[1]['emoji']} {res[1]['name']}: **{a2}**"
    )
    await message.answer(stats, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("build:"))
async def build(cb: types.CallbackQuery):
    price = int(cb.data.split(":")[1])
    fid = db.get_user_family(cb.from_user.id)

    # Перевірка грошей
    if db.get_family_resources(fid)[0] >= price:
        db.deduct_resources(fid, price)
        db.set_upgrade_timer(fid, BUILD_TIME)
        await cb.message.edit_text(
            f"🏗 **РОБОТИ РОЗПОЧАТО!**\nБригада приступила до роботи.\nЗавершення через {BUILD_TIME} хв.")
    else:
        await cb.answer("❌ Брак коштів для будівництва!", show_alert=True)


@router.callback_query(F.data.startswith("col:"))
async def collect(cb: types.CallbackQuery):
    # col:amount1:res1_col:amount2:res2_col
    p = cb.data.split(":")
    amount1 = int(p[1])
    res1_col = p[2]
    amount2 = int(p[3])
    res2_col = p[4]

    family_id = db.get_user_family(cb.from_user.id)

    # Викликаємо метод з бази
    db.collect_resources(family_id, res1_col, amount1, res2_col, amount2)

    await cb.message.edit_text("✅ **РЕСУРСИ ЗІБРАНО!**\nВони додані на склад сім'ї.")
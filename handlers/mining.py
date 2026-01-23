from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime

router = Router()
db = Database('space.db')

BUILD_TIME = 15  # Хвилин

PLANET_RESOURCES = {
    "Earth": [{"name": "Залізо", "col": "res_iron", "emoji": "⛓", "mod": 1.0},
              {"name": "Паливо", "col": "res_fuel", "emoji": "⛽", "mod": 0.5}],
    "Moon": [{"name": "Реголіт", "col": "res_regolith", "emoji": "🌑", "mod": 0.9},
             {"name": "Гелій-3", "col": "res_he3", "emoji": "⚛️", "mod": 0.3}],
    "Mars": [{"name": "Кремній", "col": "res_silicon", "emoji": "💾", "mod": 0.8},
             {"name": "Оксид", "col": "res_oxide", "emoji": "🧪", "mod": 0.4}],
    "Upiter": [{"name": "Водень", "col": "res_hydrogen", "emoji": "🌫", "mod": 0.7},
               {"name": "Гелій", "col": "res_helium", "emoji": "🎈", "mod": 0.2}]
}


@router.message(F.text == "🏭 Інфраструктура")
async def mining_menu(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!")
        return

    # ПЕРЕВІРКА ТАЙМЕРА БУДІВНИЦТВА
    timers = db.get_timers(family_id)
    if timers[3]:  # upgrade_end
        try:
            end_time = datetime.strptime(timers[3], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end_time = datetime.strptime(timers[3], "%Y-%m-%d %H:%M:%S")

        if datetime.now() < end_time:
            rem = int((end_time - datetime.now()).total_seconds() // 60)
            await message.answer(
                f"🏗 **БУДІВЕЛЬНИЙ МАЙДАНЧИК**\n\nТриває будівництво нового заводу.\n⏳ Залишилось: {rem} хв.")
            return
        else:
            # ЗАВЕРШУЄМО БУДІВНИЦТВО І ОНОВЛЮЄМО ЧАС ЗБОРУ (Щоб не було багу)
            db.finish_upgrade(family_id)
            await message.answer("✅ **БУДІВНИЦТВО ЗАВЕРШЕНО!**\nНовий завод запущено.")

    # МЕНЮ ЗАВОДІВ
    data = db.get_family_resources(family_id)
    planet = data[11]
    mine_lvl = data[9]
    res = PLANET_RESOURCES.get(planet, PLANET_RESOURCES["Earth"])

    # Розрахунок зібраного
    try:
        last = datetime.strptime(data[10], "%Y-%m-%d %H:%M:%S")
    except:
        last = datetime.now()
    mins = (datetime.now() - last).total_seconds() / 60

    base = mine_lvl * 10
    a1 = int((mins / 60) * base * res[0]['mod']) if mine_lvl > 0 else 0
    a2 = int((mins / 60) * base * res[1]['mod']) if mine_lvl > 0 else 0

    # Ціна наступного заводу
    next_price = (mine_lvl + 1) * 800

    builder = InlineKeyboardBuilder()
    if mine_lvl == 0:
        builder.button(text=f"🏗 Збудувати 1-й завод (💰{next_price})", callback_data=f"build:{next_price}")
    else:
        if a1 > 0 or a2 > 0:
            builder.button(text=f"📥 Зібрати (+{a1}/+{a2})",
                           callback_data=f"col:{a1}:{res[0]['col']}:{a2}:{res[1]['col']}")

        builder.button(text=f"🏭 Розширити ({mine_lvl + 1}-й завод) 💰{next_price}", callback_data=f"build:{next_price}")
    builder.adjust(1)

    stats = (
        f"📊 **ПРОЕКТНА ДОКУМЕНТАЦІЯ**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 Локація: **{planet}**\n"
        f"🏭 Активні заводи: **{mine_lvl}**\n"
        f"⚡ Ефективність: **{base} од/год**\n"
        f"⏳ Час будівництва: **{BUILD_TIME} хв**\n"
        f"💰 Вартість розширення: **{next_price}**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 На складі готової продукції:\n"
        f"{res[0]['emoji']} {a1} | {res[1]['emoji']} {a2}"
    )

    await message.answer(stats, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("build:"))
async def build(cb: types.CallbackQuery):
    price = int(cb.data.split(":")[1])
    fid = db.get_user_family(cb.from_user.id)

    if db.get_family_resources(fid)[0] >= price:
        db.deduct_resources(fid, price)
        # СТАВИМО ТАЙМЕР
        db.set_upgrade_timer(fid, BUILD_TIME)
        await cb.message.edit_text(
            f"🏗 **РОБОТИ РОЗПОЧАТО!**\n\nБригада приступила до монтажу конструкцій.\nЗавершення через {BUILD_TIME} хв.")
    else:
        await cb.answer("Брак грошей!", show_alert=True)


@router.callback_query(F.data.startswith("col:"))
async def collect(cb: types.CallbackQuery):
    p = cb.data.split(":")
    db.collect_resources(db.get_user_family(cb.from_user.id), p[2], int(p[1]), p[4], int(p[3]))
    await cb.message.edit_text("✅ Ресурси переміщено на склад!")
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime

router = Router()
db = Database('space.db')
BUILD_TIME = 15
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
    fid = db.get_user_family(message.from_user.id)
    if not fid: return

    # Таймер
    tm = db.get_timers(fid)
    if tm[3]:
        try:
            end = datetime.strptime(tm[3], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end = datetime.strptime(tm[3], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < end:
            rem = int((end - datetime.now()).total_seconds() // 60)
            await message.answer(f"🏗 **БУДІВЕЛЬНІ РОБОТИ**\nДо завершення: {rem} хв.")
            return
        else:
            db.finish_upgrade(fid)
            # Тут можна надіслати нове повідомлення про успіх, бо старе вже далеко в чаті
            await message.answer("✅ **БУДІВНИЦТВО ЗАВЕРШЕНО!**")

    # Меню
    d = db.get_family_resources(fid)
    p = d[11];
    l = d[9]
    res = PLANET_RESOURCES.get(p, PLANET_RESOURCES["Earth"])

    try:
        last = datetime.strptime(d[10], "%Y-%m-%d %H:%M:%S")
    except:
        last = datetime.now()
    mins = (datetime.now() - last).total_seconds() / 60
    base = l * 10
    a1 = int((mins / 60) * base * res[0]['mod']) if l > 0 else 0
    a2 = int((mins / 60) * base * res[1]['mod']) if l > 0 else 0
    price = (l + 1) * 800

    kb = InlineKeyboardBuilder()
    if l == 0:
        kb.button(text=f"🏗 Збудувати (💰{price})", callback_data=f"build:{price}")
    else:
        if a1 > 0 or a2 > 0:
            kb.button(text=f"📥 Зібрати (+{a1}/+{a2})", callback_data=f"col:{a1}:{res[0]['col']}:{a2}:{res[1]['col']}")
        kb.button(text=f"🏭 Розширити (Lv.{l + 1}) 💰{price}", callback_data=f"build:{price}")
    kb.adjust(1)

    txt = (
        f"🏭 **ПРОМИСЛОВИЙ СЕКТОР: {p}**\n"
        f"Рівень: **{l}** | Ефективність: **{base}/год**\n"
        f"📦 **Склад:** {res[0]['emoji']} {a1} | {res[1]['emoji']} {a2}"
    )
    await message.answer(txt, reply_markup=kb.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("build:"))
async def build(call: types.CallbackQuery):
    pr = int(call.data.split(":")[1])
    fid = db.get_user_family(call.from_user.id)
    if db.get_family_resources(fid)[0] >= pr:
        db.deduct_resources(fid, pr);
        db.set_upgrade_timer(fid, BUILD_TIME)
        await call.message.edit_text(f"🏗 **РОБОТИ РОЗПОЧАТО**\nБригади приступили до виконання.\nЧас: {BUILD_TIME} хв.")
    else:
        await call.answer("❌ Брак грошей!", show_alert=True)


@router.callback_query(F.data.startswith("col:"))
async def collect(call: types.CallbackQuery):
    p = call.data.split(":")
    db.collect_resources(db.get_user_family(call.from_user.id), p[2], int(p[1]), p[4], int(p[3]))
    # Оновлюємо текст на "Зібрано"
    await call.message.edit_text("✅ **РЕСУРСИ ПЕРЕМІЩЕНО НА СКЛАД**", parse_mode="Markdown")
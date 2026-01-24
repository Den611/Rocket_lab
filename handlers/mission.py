from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from keyboards import get_main_kb_no_family
import asyncio
import random
from datetime import datetime

router = Router()
db = Database('space.db')

FLIGHT_TIME = 10
PLANET_PROGRESSION = {"Earth": "Moon", "Moon": "Mars", "Mars": "Jupiter", "Jupiter": "Earth"}

RES_NAMES = {
    "res_iron": "Залізо", "res_fuel": "Паливо", "res_regolith": "Реголіт",
    "res_he3": "Гелій-3", "res_silicon": "Кремній", "res_oxide": "Оксид",
    "res_hydrogen": "Водень", "res_helium": "Гелій"
}


@router.message(F.text == "📡 Місії")
async def show_missions(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!", reply_markup=get_main_kb_no_family())
        return

    # Перевірка таймера
    timers = db.get_timers(family_id)
    if timers[0]:
        try:
            end_time = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end_time = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S")

        if datetime.now() < end_time:
            remaining = end_time - datetime.now()
            mins = int(remaining.total_seconds() // 60)
            await message.answer(f"🚀 **РАКЕТА В ПОЛЬОТІ!**\nДо прибуття: {mins} хв.")
            return
        else:
            await process_mission_result(message, family_id, timers[2], timers[1])
            db.clear_mission_timer(family_id)
            return

    fam_info = db.get_family_info(family_id)
    current_planet = fam_info[5]
    missions = db.get_missions_by_planet(current_planet)

    if not missions:
        await message.answer("Місій немає.")
        return

    builder = InlineKeyboardBuilder()
    for m in missions:
        # m[0]=id, m[1]=name, m[2]=desc, m[3]=reward, m[4]=is_boss, m[5]=cost
        cost = m[5]
        reward = m[3]
        icon = "👑" if m[4] else "🚀"
        # ВИПРАВЛЕНО ТУТ (було m[7], стало m[5] або змінна cost)
        builder.button(text=f"{icon} {m[1]} (-{cost} | +{reward})", callback_data=f"select_mission:{m[0]}")
    builder.adjust(1)

    emoji = {"Earth": "🌍", "Moon": "🌑", "Mars": "🔴", "Jupiter": "⚡"}.get(current_planet, "🌌")
    await message.answer(f"{emoji} **Орбіта: {current_planet}**\nЧас польоту: {FLIGHT_TIME} хв.",
                         reply_markup=builder.as_markup(), parse_mode="Markdown")


async def process_mission_result(message, family_id, mission_id, launch_id):
    mission = db.get_mission_by_id(mission_id)
    # Шанс успіху 85%
    if random.randint(1, 100) <= 85:
        db.update_launch_status(launch_id, "success")
        db.update_balance(family_id, mission[4])  # reward
        msg = f"✅ **МІСІЯ УСПІШНА!**\n+💰{mission[4]}"
        if mission[6]:  # Boss
            next_p = PLANET_PROGRESSION.get(mission[5])
            if next_p:
                db.move_family_to_planet(family_id, next_p)
                msg += f"\n🌌 **ПЕРЕЛІТ НА {next_p}!**"
        await message.answer(msg, parse_mode="Markdown")
    else:
        db.update_launch_status(launch_id, "failed")
        await message.answer("💥 **АВАРІЯ!** Ресурси втрачено.", parse_mode="Markdown")


@router.callback_query(F.data.startswith("select_mission:"))
async def start_protocol(callback: types.CallbackQuery):
    mission_id = int(callback.data.split(":")[1])
    family_id = db.get_user_family(callback.from_user.id)

    # Тут використовуємо get_mission_by_id, який повертає SELECT *, тому індекси інші
    mission = db.get_mission_by_id(mission_id)
    # mission: 0=id, ..., 7=cost, 8=req_name, 9=req_amt

    res = db.get_family_resources(family_id)

    # Перевірка грошей (mission[7] це cost_money у SELECT *)
    if res[0] < mission[7]:
        await callback.answer("❌ Брак коштів!", show_alert=True)
        return

    req_name = mission[8]
    req_amt = mission[9]
    if req_name and req_amt > 0:
        res_idx = {"res_iron": 1, "res_fuel": 2, "res_regolith": 3, "res_he3": 4, "res_silicon": 5, "res_oxide": 6,
                   "res_hydrogen": 7, "res_helium": 8}
        idx = res_idx.get(req_name)
        if res[idx] < req_amt:
            await callback.answer(f"❌ Брак ресурсу!", show_alert=True)
            return

    launch_id = db.start_launch(family_id, mission_id)
    db.deduct_resources(family_id, mission[7], req_name, req_amt)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ ПІДТВЕРДИТИ", callback_data=f"confirm_launch:{launch_id}")
    await callback.message.answer(f"🚨 **ПІДГОТОВКА**\nВитрати списано. Всі готові?", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_launch:"))
async def confirm_launch(callback: types.CallbackQuery):
    launch_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    family_id = db.get_user_family(user_id)

    total = len(db.get_family_members(family_id))
    current = db.sign_launch(launch_id, user_id)

    if current is False:
        await callback.answer("Вже підтверджено!")
        return

    await callback.message.edit_text(f"⚙️ Готовність: {current}/{total}\n{'🟩' * current}")

    if current >= total:
        conn = db.connection
        cur = conn.cursor()
        m_id = cur.execute("SELECT mission_id FROM launches WHERE id = ?", (launch_id,)).fetchone()[0]
        db.set_mission_timer(family_id, FLIGHT_TIME, launch_id, m_id)
        await callback.message.answer(f"🔥 **ПУСК!** Час польоту: {FLIGHT_TIME} хв.")
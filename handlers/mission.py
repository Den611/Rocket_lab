from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from keyboards import get_main_kb_no_family
import asyncio
import random
from datetime import datetime

router = Router()
db = Database('space.db')

# НОВИЙ МАРШРУТ
PLANET_PROGRESSION = {
    "Earth": "Moon",  # Земля -> Місяць
    "Moon": "Mars",  # Місяць -> Марс
    "Mars": "Upiter",  # Марс -> Юпітер
    "Upiter": "Earth"  # Юпітер -> Кінець (Земля)
}


@router.message(F.text == "📡 Місії")
async def show_missions(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!", reply_markup=get_main_kb_no_family())
        return

    # 1. ПЕРЕВІРКА ТАЙМЕРА
    timers = db.get_timers(family_id)
    # 0=end_time, 1=launch_id, 2=mission_id

    if timers[0]:
        try:
            end_time = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end_time = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S")

        if datetime.now() < end_time:
            # Ще летить
            remaining = end_time - datetime.now()
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            await message.answer(
                f"🚀 **РАКЕТА В ПОЛЬОТІ!**\n\n"
                f"Триває виконання місії.\n"
                f"⏳ До прибуття: **{mins} хв {secs} с**\n"
                f"Очікуйте завершення маневру."
            )
            return
        else:
            # Прилетів! Рахуємо результат
            await process_mission_result(message, family_id, timers[2], timers[1])
            db.clear_mission_timer(family_id)
            return

    # 2. ЯКЩО НЕ ЛЕТИТЬ - ПОКАЗУЄМО МЕНЮ
    fam_info = db.get_family_info(family_id)
    current_planet = fam_info[5]
    missions = db.get_missions_by_planet(current_planet)

    if not missions:
        await message.answer("Місій немає.")
        return

    builder = InlineKeyboardBuilder()
    for m in missions:
        cost = m[5]
        reward = m[3]
        icon = "👑" if m[4] else "🚀"
        builder.button(text=f"{icon} {m[1]} (-{cost} | +{reward})", callback_data=f"select_mission:{m[0]}")
    builder.adjust(1)

    # Емодзі для кожної планети
    emoji_map = {
        "Earth": "🌍",
        "Moon": "🌑",
        "Mars": "🔴",
        "Upiter": "⚡"
    }
    emoji = emoji_map.get(current_planet, "🌌")

    await message.answer(
        f"{emoji} **Орбіта: {current_planet}**\nОберіть місію:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("select_mission:"))
async def start_protocol(callback: types.CallbackQuery):
    mission_id = int(callback.data.split(":")[1])
    family_id = db.get_user_family(callback.from_user.id)
    mission = db.get_mission_by_id(mission_id)

    # Перевірка ресурсів
    res = db.get_family_resources(family_id)
    if res[0] < mission[7]:
        await callback.answer("❌ Брак грошей!", show_alert=True)
        return

    # Ресурси
    req_name = mission[8]
    req_amt = mission[9]
    if req_name and req_amt > 0:
        res_idx = {"res_iron": 1, "res_fuel": 2, "res_regolith": 3, "res_he3": 4, "res_silicon": 5, "res_oxide": 6,
                   "res_hydrogen": 7, "res_helium": 8}
        idx = res_idx.get(req_name)
        if res[idx] < req_amt:
            await callback.answer(f"❌ Брак ресурсу: {RES_NAMES.get(req_name)}!", show_alert=True)
            return

    # Бронь
    launch_id = db.start_launch(family_id, mission_id)
    db.deduct_resources(family_id, mission[7], req_name, req_amt)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ ГОТОВИЙ ДО ЗАПУСКУ", callback_data=f"confirm_launch:{launch_id}")
    await callback.message.answer(f"🚨 **ПІДГОТОВКА**\nВитрачено: 💰{mission[7]}.\nПотрібна згода екіпажу.",
                                  reply_markup=builder.as_markup())
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

    await callback.message.edit_text(f"⚙️ Готовність: {current}/{total}\n{'🟩' * current}{'⬜' * (total - current)}")

    if current >= total:
        conn = db.connection
        cur = conn.cursor()
        m_id = cur.execute("SELECT mission_id FROM launches WHERE id = ?", (launch_id,)).fetchone()[0]

        # ЗАПУСК ТАЙМЕРА
        db.set_mission_timer(family_id, FLIGHT_TIME, launch_id, m_id)

        await callback.message.answer(
            f"🔥 **ПУСК!**\nРакета вийшла на орбіту.\nРозрахунковий час польоту: {FLIGHT_TIME} хв.")
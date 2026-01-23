from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from keyboards import get_main_kb_no_family
import asyncio

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

    fam_info = db.get_family_info(family_id)
    current_planet = fam_info[5]

    missions = db.get_missions_by_planet(current_planet)

    if not missions:
        await message.answer("Місій немає.")
        return

    builder = InlineKeyboardBuilder()
    for m in missions:
        boss_marker = "👑 " if m[4] else ""
        builder.button(text=f"{boss_marker}{m[1]} (💰{m[3]})", callback_data=f"select_mission:{m[0]}")
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
    launch_id = db.start_launch(family_id, mission_id)
    mission_data = db.get_mission_by_id(mission_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Системи в нормі!", callback_data=f"confirm_launch:{launch_id}")

    await callback.message.answer(
        f"🚨 **ПІДГОТОВКА** 🚨\n"
        f"Місія: **{mission_data[1]}**\n"
        f"Нагорода: 💰{mission_data[4]}\n"
        f"Потрібно підтверджень: Всі учасники",
        reply_markup=builder.as_markup(), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_launch:"))
async def confirm_participation(callback: types.CallbackQuery):
    launch_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    family_id = db.get_user_family(user_id)

    members = db.get_family_members(family_id)
    total_members = len(members)
    current_signatures = db.sign_launch(launch_id, user_id)

    if current_signatures is False:
        await callback.answer("Вже підтверджено!", show_alert=True)
        return

    await callback.message.edit_text(
        f"🚨 **ПЕРЕВІРКА** 🚨\nГотовність: {current_signatures}/{total_members}\n"
        f"{'🟢' * current_signatures}{'🔴' * (total_members - current_signatures)}",
        reply_markup=callback.message.reply_markup, parse_mode="Markdown"
    )

    if current_signatures >= total_members:
        await callback.message.answer("🚀 **ЗАПУСК!** Двигуни на повну потужність...")
        await asyncio.sleep(2)

        # Логіка успіху та переходу
        conn = db.connection
        cur = conn.cursor()
        cur.execute("SELECT mission_id FROM launches WHERE id = ?", (launch_id,))
        m_id = cur.fetchone()[0]

        mission_info = db.get_mission_by_id(m_id)
        is_boss = mission_info[6]
        current_planet = mission_info[5]
        reward = mission_info[4]

        db.update_launch_status(launch_id, "success")
        db.update_balance(family_id, reward)

        msg = f"🎉 **Місія успішна!**\nЗароблено: 💰{reward}"

        if is_boss:
            next_planet = PLANET_PROGRESSION.get(current_planet)
            if next_planet:
                db.move_family_to_planet(family_id, next_planet)
                msg += f"\n\n🌌 **ГІПЕРСТРИБОК!**\nВи прибули на орбіту **{next_planet}**!"
            else:
                msg += "\n\n🏆 **ГРУ ПРОЙДЕНО!** Ви підкорили систему!"

        await callback.message.answer(msg, parse_mode="Markdown")
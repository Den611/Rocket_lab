from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime

router = Router()
db = Database('space.db')


@router.message(F.text == "📡 Місії")
async def show_missions(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid: return

    # Перевірка активних польотів
    timers = db.get_timers(fid)
    if timers[0]:
        try:
            end = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S")

        if datetime.now() < end:
            rem = int((end - datetime.now()).total_seconds() // 60)
            # Якщо політ триває - просто повідомляємо
            await message.answer(
                f"🚀 **СТАТУС: У ПОЛЬОТІ**\n⏳ До прибуття: {rem} хв.\n\n_Ви отримаєте сповіщення по завершенню._",
                parse_mode="Markdown")
            return

    # Якщо польотів немає - меню
    fam_info = db.get_family_info(fid)
    planet = fam_info[5]
    missions = db.get_missions_by_planet(planet)

    builder = InlineKeyboardBuilder()
    for m in missions:
        # 0=id, 1=name, 3=reward, 4=boss, 5=cost, 6=time, 7=risk
        icon = "👑" if m[4] else "🌑"
        btn_text = f"{icon} {m[1]} (⏳{m[6]}хв | ☠️{m[7]}%)"
        builder.button(text=btn_text, callback_data=f"sel_mis:{m[0]}")
    builder.adjust(1)

    emoji = {"Earth": "🌍", "Moon": "🌑", "Mars": "🔴", "Jupiter": "⚡"}.get(planet, "🌌")
    await message.answer(
        f"{emoji} **ЦЕНТР УПРАВЛІННЯ ПОЛЬОТАМИ: {planet}**\n"
        f"Оберіть місію зі списку. Зважайте на ризики!",
        reply_markup=builder.as_markup(), parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("sel_mis:"))
async def select_mission(call: types.CallbackQuery):
    mid = int(call.data.split(":")[1])
    fid = db.get_user_family(call.from_user.id)
    mis = db.get_mission_by_id(mid)

    # Перевірка ресурсів... (код ідентичний минулому, але з edit_text в кінці)
    res = db.get_family_resources(fid)
    if res[0] < mis[7]:
        return await call.answer("❌ Брак коштів!", show_alert=True)

    # ... (перевірка ресурсів req_name ...)

    lid = db.start_launch(fid, mid)
    db.deduct_resources(fid, mis[7], mis[8], mis[9])

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ ПІДТВЕРДИТИ ЗАПУСК", callback_data=f"conf_mis:{lid}")

    # ЗМІНЮЄМО повідомлення, а не пишемо нове
    await call.message.edit_text(
        f"📋 **ПІДГОТОВКА ДО ЗАПУСКУ**\n"
        f"🎯 Цілі: **{mis[1]}**\n"
        f"⏳ Час: **{mis[10]} хв**\n"
        f"☠️ Ризик: **{mis[11]}%**\n"
        f"💸 Списано: **{mis[7]}**\n\n"
        f"Очікування підтвердження...",
        reply_markup=builder.as_markup(), parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("conf_mis:"))
async def confirm_launch(call: types.CallbackQuery):
    lid = int(call.data.split(":")[1])
    fid = db.get_user_family(call.from_user.id)

    cur = db.sign_launch(lid, call.from_user.id)
    tot = len(db.get_family_members(fid))

    if cur is False: return await call.answer("Вже підтверджено!")

    # Оновлюємо статус у тому ж повідомленні
    if cur >= tot:
        # Старт
        conn = db.connection;
        c = conn.cursor()
        mid = c.execute("SELECT mission_id FROM launches WHERE id=?", (lid,)).fetchone()[0]
        mis = db.get_mission_by_id(mid)
        db.set_mission_timer(fid, mis[10], lid, mid)

        await call.message.edit_text(
            f"🚀 **ЗАПУСК ПІДТВЕРДЖЕНО!**\n"
            f"Двигуни працюють на повну потужність.\n"
            f"Розрахунковий час прибуття: **{mis[10]} хв**.\n\n"
            f"_Зв'язок завершено._", parse_mode="Markdown"
        )
    else:
        await call.message.edit_text(
            f"⚙️ **ПЕРЕВІРКА СИСТЕМ**\n"
            f"Готовність екіпажу: **{cur}/{tot}**\n"
            f"{'🟩' * cur}{'⬜' * (tot - cur)}", parse_mode="Markdown"
        )
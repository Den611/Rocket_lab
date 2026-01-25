from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime
import random

router = Router()
db = Database('space.db')


@router.message(F.text == "📡 Місії")
async def show_missions(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid: return

    timers = db.get_timers(fid)
    if timers[0]:
        try:
            end = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S.%f")
        except:
            end = datetime.strptime(timers[0], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < end:
            rem = int((end - datetime.now()).total_seconds() // 60)
            await message.answer(f"🚀 **ПОЛІТ ТРИВАЄ**\nПрибуття через: {rem} хв")
            return

    fam = db.get_family_info(fid)
    missions = db.get_missions_by_planet(fam[5])

    kb = InlineKeyboardBuilder()
    for m in missions:
        # 0=id, 1=name, 5=cost, 6=time, 7=risk
        icon = "👑" if m[4] else "🚀"
        kb.button(text=f"{icon} {m[1]} (⏳{m[6]}хв | ☠️{m[7]}%)", callback_data=f"sel_mis:{m[0]}")
    kb.adjust(1)
    await message.answer(f"🌌 **Місії: {fam[5]}**", reply_markup=kb.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("sel_mis:"))
async def select_mission(cb: types.CallbackQuery):
    mid = int(cb.data.split(":")[1])
    fid = db.get_user_family(cb.from_user.id)
    mission = db.get_mission_by_id(mid)
    # 7=cost, 10=time, 11=risk
    res = db.get_family_resources(fid)

    if res[0] < mission[7]:
        return await cb.answer("Брак грошей!", show_alert=True)

    lid = db.start_launch(fid, mid)
    db.deduct_resources(fid, mission[7], mission[8], mission[9])

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ СТАРТ", callback_data=f"conf_mis:{lid}")
    await cb.message.answer(f"📋 **План:** {mission[1]}\n⏳ {mission[10]} хв | ☠️ Ризик {mission[11]}%",
                            reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("conf_mis:"))
async def confirm(cb: types.CallbackQuery):
    lid = int(cb.data.split(":")[1])
    fid = db.get_user_family(cb.from_user.id)
    cur = db.sign_launch(lid, cb.from_user.id)
    tot = len(db.get_family_members(fid))

    if cur >= tot:
        conn = db.connection;
        c = conn.cursor()
        mid = c.execute("SELECT mission_id FROM launches WHERE id=?", (lid,)).fetchone()[0]
        mis = db.get_mission_by_id(mid)
        db.set_mission_timer(fid, mis[10], lid, mid)
        await cb.message.answer(f"🔥 **ПУСК!** Час: {mis[10]} хв.")
    else:
        await cb.message.edit_text(f"Готовність: {cur}/{tot}")
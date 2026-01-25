import asyncio
import random
from database import Database
from aiogram import Bot

PLANET_NEXT = {"Earth": "Moon", "Moon": "Mars", "Mars": "Jupiter", "Jupiter": "Earth"}
db = Database('space.db')


async def start_autocheck(bot: Bot):
    while True:
        try:
            await check_mis(bot)
            await check_upg(bot)
            await check_base(bot)
        except Exception as e:
            print(e)
        await asyncio.sleep(30)


async def notify(bot, fid, txt):
    for uid in db.get_family_user_ids(fid):
        try:
            await bot.send_message(uid, txt, parse_mode="Markdown")
        except:
            pass


async def check_mis(bot):
    for row in db.get_expired_missions():
        fid, mid, lid, planet = row
        db.clear_mission_timer(fid)
        m = db.get_mission_by_id(mid)
        # 4=rew, 11=risk
        fam = db.get_family_info(fid)
        hull = fam[4]

        roll = random.randint(1, 100)
        if roll <= m[11]:  # Pirates
            if random.randint(1, 100) <= hull * 15:
                db.update_balance(fid, m[4])
                await notify(bot, fid, f"⚔️ Пірати відбиті! +💰{m[4]}")
            else:
                loss = int(m[4] * 0.5)
                db.update_balance(fid, m[4] - loss)
                await notify(bot, fid, f"🏴‍☠️ Пірати вкрали 50%! +💰{m[4] - loss}")
        else:
            db.update_balance(fid, m[4])
            msg = f"✅ Успіх! +💰{m[4]}"
            if m[6] and PLANET_NEXT.get(m[5]):
                db.move_family_to_planet(fid, PLANET_NEXT[m[5]])
                msg += f"\n🌌 Переліт на {PLANET_NEXT[m[5]]}!"
            await notify(bot, fid, msg)


async def check_upg(bot):
    for row in db.get_expired_upgrades():
        db.finish_upgrade(row[0])
        await notify(bot, row[0], "✅ Завод готовий!")


async def check_base(bot):
    for row in db.get_all_families_for_events():
        fid, pl, hull, eng, bal = row
        if pl in ["Earth", "Moon"]: continue
        if random.randint(1, 100) <= 5:
            defense = hull + eng
            str_pir = random.randint(3, 10)
            if defense < str_pir:
                lost = int(bal * 0.05)
                db.deduct_resources(fid, lost)
                await notify(bot, fid, f"🚨 Напад на базу! Вкрадено 💰{lost}")
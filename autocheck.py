import asyncio
import random
from database import Database
from aiogram import Bot

# Ланцюжок планет
PLANET_NEXT = {"Earth": "Moon", "Moon": "Mars", "Mars": "Jupiter", "Jupiter": "Earth"}
db = Database('space.db')


async def start_autocheck(bot: Bot):
    while True:
        try:
            await check_mis(bot)
            await check_upg(bot)
            await check_base_events(bot)
        except Exception as e:
            print(f"Authocheck Error: {e}")
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
        fam = db.get_family_info(fid)
        hull = fam[4]

        # Логіка піратів
        roll = random.randint(1, 100)
        msg = ""

        if roll <= m[11]:  # Ризик піратів
            if random.randint(1, 100) <= hull * 15:
                db.update_balance(fid, m[4])
                msg = f"⚔️ **ПІРАТСЬКИЙ НАПАД ВІДБИТО!**\nВаш корпус витримав удар.\n💰 Отримано: **{m[4]}**"
            else:
                loss = int(m[4] * 0.5)
                db.update_balance(fid, m[4] - loss)
                msg = f"🏴‍☠️ **УВАГА! ПОГРАБУВАННЯ!**\nПірати пробили захист і забрали частину вантажу.\n💰 Залишилось: **{m[4] - loss}**"
        else:
            db.update_balance(fid, m[4])
            msg = f"✅ **МІСІЯ ЗАВЕРШЕНА УСПІШНО!**\nРакета повернулася на базу.\n💰 Прибуток: **{m[4]}**"

            # Переліт на нову планету
            if m[6] and PLANET_NEXT.get(m[5]):
                new_p = PLANET_NEXT[m[5]]
                db.move_family_to_planet(fid, new_p)
                msg += f"\n\n🌌 **ГІПЕРСТРИБОК ЗДІЙСНЕНО!**\nНова база: **{new_p}**"

        await notify(bot, fid, msg)


async def check_upg(bot):
    for row in db.get_expired_upgrades():
        fid = row[0]
        db.finish_upgrade(fid)
        await notify(bot, fid, "🏭 **БУДІВНИЦТВО ЗАВЕРШЕНО!**\nНовий цех введено в експлуатацію. Видобуток збільшено.")


async def check_base_events(bot):
    # Напади на базу (тільки Марс/Юпітер)
    for row in db.get_all_families_for_events():
        fid, pl, hull, eng, bal = row
        if pl in ["Earth", "Moon"]: continue

        if random.randint(1, 100) <= 5:  # 5% шанс
            defense = hull + eng
            if defense < random.randint(3, 10):
                lost = int(bal * 0.05)
                db.deduct_resources(fid, lost)
                await notify(bot, fid,
                             f"🚨 **ТРИВОГА! ПРОРИВ ПЕРИМЕТРА!**\nНа базу {pl} напали мародери!\nВтрачено: 💰**{lost}**")
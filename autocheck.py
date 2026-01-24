import asyncio
import random
from database import Database
from aiogram import Bot

# Налаштування (мають співпадати з handler/mission.py)
PLANET_PROGRESSION = {"Earth": "Moon", "Moon": "Mars", "Mars": "Jupiter", "Jupiter": "Earth"}

db = Database('space.db')


async def start_autocheck(bot: Bot):
    print("🔄 Фоновий моніторинг запущено...")

    while True:
        try:
            await check_missions(bot)
            await check_upgrades(bot)
        except Exception as e:
            print(f"⚠️ Помилка в autocheck: {e}")

        # Перевіряємо кожні 30 секунд
        await asyncio.sleep(30)


async def notify_family(bot: Bot, family_id, text):
    users = db.get_family_user_ids(family_id)
    for user_id in users:
        try:
            await bot.send_message(user_id, text, parse_mode="Markdown")
        except:
            pass


# --- ПЕРЕВІРКА МІСІЙ ---
async def check_missions(bot: Bot):
    expired = db.get_expired_missions()
    # row: 0=family_id, 1=mission_id, 2=launch_id, 3=current_planet

    for row in expired:
        family_id, mission_id, launch_id, current_planet = row

        # Очищаємо таймер, щоб не обробляти двічі
        db.clear_mission_timer(family_id)

        mission = db.get_mission_by_id(mission_id)
        # mission: ... 3=reward, 4=reward(дубль?), перевірте індекси в БД
        # У вашій БД get_mission_by_id повертає SELECT *, тому:
        # 0=id, 1=name, 2=desc, 3=diff, 4=reward, 5=planet, 6=is_boss

        mission_name = mission[1]
        reward = mission[4]
        is_boss = mission[6]
        target_planet = mission[5]  # Планета місії

        # Логіка успіху (85%)
        if random.randint(1, 100) <= 85:
            db.update_launch_status(launch_id, "success")
            db.update_balance(family_id, reward)

            msg = (
                f"✅ **МІСІЯ ЗАВЕРШЕНА!**\n\n"
                f"🚀 Ракета успішно повернулася з завдання **«{mission_name}»**.\n"
                f"💰 Отримано нагороду: **{reward}**"
            )

            if is_boss:
                next_p = PLANET_PROGRESSION.get(target_planet)
                if next_p:
                    db.move_family_to_planet(family_id, next_p)
                    msg += f"\n\n🌌 **ГІПЕРСТРИБОК!**\nВи перелетіли на нову базу: **{next_p}**!"

            await notify_family(bot, family_id, msg)

        else:
            db.update_launch_status(launch_id, "failed")
            msg = (
                f"💥 **АВАРІЯ!**\n\n"
                f"Місія **«{mission_name}»** зазнала невдачі при посадці.\n"
                f"Екіпаж врятувався, але час та ресурси втрачено."
            )
            await notify_family(bot, family_id, msg)


# --- ПЕРЕВІРКА БУДІВНИЦТВА ---
async def check_upgrades(bot: Bot):
    expired = db.get_expired_upgrades()
    # row: 0=family_id, 1=planet, 2=mine_lvl

    for row in expired:
        family_id, planet, old_lvl = row

        # Завершуємо будівництво в БД (рівень +1, таймер NULL)
        db.finish_upgrade(family_id)

        msg = (
            f"✅ **БУДІВНИЦТВО ЗАВЕРШЕНО!**\n\n"
            f"🏭 На планеті **{planet}** відкрито новий завод.\n"
            f"Поточний рівень: **{old_lvl + 1}**.\n"
            f"Видобуток відновлено."
        )
        await notify_family(bot, family_id, msg)
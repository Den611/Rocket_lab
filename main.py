import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import navigation, start, family, mission, shop, mining, admin, games, pvp, bonus, webapp, quiz
import autocheck
import threading
from server import run_flask

logging.basicConfig(level=logging.INFO)

async def main():
    threading.Thread(target=run_flask, daemon=True).start()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # --- ПІДКЛЮЧЕННЯ РОУТЕРІВ ---
    dp.include_router(start.router)
    dp.include_router(family.router)
    dp.include_router(mission.router)
    dp.include_router(shop.router)
    dp.include_router(mining.router)
    dp.include_router(admin.router)
    dp.include_router(games.router)
    dp.include_router(pvp.router)
    dp.include_router(bonus.router)
    dp.include_router(webapp.router)

    # Підключаємо новий модуль вікторини
    dp.include_router(quiz.router)

    # Навігація має бути в кінці (якщо там є загальні обробники тексту)
    dp.include_router(navigation.router)

    # --- МЕНЮ КОМАНД ---
    commands = [
        BotCommand(command="start", description="🖥 Головний термінал"),
        BotCommand(command="quiz", description="🎓 Академія (Тест)"),  # Нова команда в меню
        BotCommand(command="help", description="📘 Інструкція пілота"),
    ]
    await bot.set_my_commands(commands)

    # Запуск фонового процесу (перевірка таймерів місій та будівництва)
    asyncio.create_task(autocheck.start_autocheck(bot))

    print("✅ SYSTEM ONLINE: Rocket Lab Bot is running...")

    # Видаляємо вебхук, щоб не було конфліктів при запуску polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 SYSTEM SHUTDOWN")
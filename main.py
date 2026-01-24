import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import start, family, mission, shop, mining, admin
import autocheck


logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Підключаємо роутери
    dp.include_router(start.router)
    dp.include_router(family.router)
    dp.include_router(mission.router)
    dp.include_router(shop.router)
    dp.include_router(mining.router)
    dp.include_router(admin.router)

    # Меню команд
    commands = [
        BotCommand(command="start", description="🚀 Головне меню"),
        BotCommand(command="help", description="ℹ️ Допомога"),
    ]
    await bot.set_my_commands(commands)
    asyncio.create_task(autocheck.start_autocheck(bot))

    print("✅ Бот Space Family запущено!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот зупинений")
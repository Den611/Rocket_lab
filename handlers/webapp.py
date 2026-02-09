import json
from aiogram import Router, F, types
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import Database

# 👇 ІМПОРТУЄМО ВАШЕ ПОВНЕ МЕНЮ З ФАЙЛУ keyboards.py
from keyboards import main_keyboard 

router = Router()
db = Database('space.db')

# ВАШЕ ПОСИЛАННЯ НА ГРУ (з GitHub)
GAME_URL = "https://artemkakoder228.github.io/Game/" 

# 1. Відкриваємо гру
@router.message(F.text == "👾 Космічний бій")
async def open_game(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚀 ЗАПУСТИТИ ДВИГУНИ", web_app=WebAppInfo(url=GAME_URL))
    builder.button(text="🔙 Назад")
    builder.adjust(1)
    
    await message.answer(
        "🎮 **АРКАДНИЙ РЕЖИМ**\n\n"
        "Знищуйте ворогів, щоб заробити кредити!\n"
        "1 збитий ворог = **10 монет**.\n\n"
        "Тисніть кнопку внизу 👇",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )

# 2. Кнопка "Назад" повертає ПОВНЕ меню
@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    # Викликаємо main_keyboard(), щоб показати всі кнопки
    await message.answer("Головне меню", reply_markup=main_keyboard())

# 3. Обробка результатів гри
@router.message(F.web_app_data)
async def process_game_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get('action') == 'game_score':
            score = int(data.get('amount', 0))
            
            # Якщо очок 0 або менше
            if score <= 0:
                await message.answer(
                    "Ви нікого не збили. Спробуйте ще раз!", 
                    reply_markup=main_keyboard() # 👈 Повертаємо повне меню
                )
                return

            fid = db.get_user_family(message.from_user.id)
            if fid:
                db.update_balance(fid, score)
                
                await message.answer(
                    f"🏁 **МІСІЯ ЗАВЕРШЕНА!**\n\n"
                    f"💀 Збито ворогів: **{score // 10}**\n"
                    f"💰 Отримано: **+{score}** монет\n\n"
                    f"_Кошти зараховано на баланс сім'ї._",
                    # 👇 ТУТ ГОЛОВНА ЗМІНА:
                    reply_markup=main_keyboard(), 
                    parse_mode="Markdown"
                )
            else:
                await message.answer(
                    "У вас немає сім'ї, тому ресурси втрачено в космосі.", 
                    reply_markup=main_keyboard() # 👈 Повертаємо повне меню
                )
                
    except Exception as e:
        print(f"Web App Error: {e}")
        # У разі помилки теж повертаємо меню, щоб бот не завис
        await message.answer("Сталася помилка обробки даних.", reply_markup=main_keyboard())
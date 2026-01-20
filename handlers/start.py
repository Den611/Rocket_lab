from aiogram import Router, types
from aiogram.filters import Command
from database import Database
from keyboards import get_main_kb_no_family, get_main_kb_with_family

router = Router()
db = Database('space.db')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    db.add_user(message.from_user.id, message.from_user.username)
    family_id = db.get_user_family(message.from_user.id)

    if family_id:
        await message.answer("З поверненням, космонавте!", reply_markup=get_main_kb_with_family())
    else:
        await message.answer("Вітаю в Space Family! 🌌\nТобі потрібна команда.", reply_markup=get_main_kb_no_family())
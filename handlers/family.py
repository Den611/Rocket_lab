from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from config import WEB_APP_URL
import urllib.parse
from keyboards import get_main_kb_with_family, get_main_kb_no_family

router = Router()
db = Database('space.db')


class FamilyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_code = State()


@router.message(F.text == "🚀 Створити сім'ю")
async def start_create_family(message: types.Message, state: FSMContext):
    await state.set_state(FamilyStates.waiting_for_name)
    await message.answer("Назва команди:")


@router.message(FamilyStates.waiting_for_name)
async def process_family_name(message: types.Message, state: FSMContext):
    db.add_user(message.from_user.id, message.from_user.username or "Cap")
    invite_code = db.create_family(message.from_user.id, message.text)
    await state.clear()
    await message.answer(f"Створено! Код: `{invite_code}`", parse_mode="Markdown",
                         reply_markup=get_main_kb_with_family())


@router.message(F.text == "🔗 Приєднатися до сім'ї")
async def start_join_family(message: types.Message, state: FSMContext):
    await state.set_state(FamilyStates.waiting_for_code)
    await message.answer("Введіть код:")


@router.message(FamilyStates.waiting_for_code)
async def process_join_code(message: types.Message, state: FSMContext):
    db.add_user(message.from_user.id, message.from_user.username or "Recruit")
    if db.join_family(message.from_user.id, message.text.upper().strip()):
        await state.clear()
        await message.answer("Успіх!", reply_markup=get_main_kb_with_family())
    else:
        await message.answer("Помилка.")


@router.message(F.text == "🌌 Кабінет сім'ї")
async def family_info(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id: return
    data = db.get_family_resources(family_id)
    base = db.get_family_info(family_id)

    text = (
        f"🏢 **{base[0]}** (База: {data[11]})\n"
        f"💰 {data[0]}\n\n"
        f"📦 **Склад:**\n"
        f"  🌍 {data[1]} | {data[2]}\n"
        f"  🌑 {data[3]} | {data[4]}\n"
        f"  🔴 {data[5]} | {data[6]}\n"
        f"  ⚡ {data[7]} | {data[8]}\n"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "🛸 Ангар (Веб)")
async def open_webapp_angar(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!")
        return

    res = db.get_family_resources(family_id)
    info = db.get_family_info(family_id)

    # Параметри для передачі на сайт
    params = {
        "uid": message.from_user.id,
        "family": info[0],
        "planet": res[11],  # Це буде "Earth", "Moon", "Mars" або "Jupiter"
        "balance": res[0],
        "iron": res[1], "fuel": res[2],
        "regolith": res[3], "he3": res[4],
        "silicon": res[5], "oxide": res[6],
        "hydrogen": res[7], "helium": res[8],
        "mine_lvl": res[9]
    }

    query_string = urllib.parse.urlencode(params)
    final_url = f"{WEB_APP_URL}?{query_string}"

    builder = InlineKeyboardBuilder()
    builder.button(text="🖥 Відкрити термінал", web_app=WebAppInfo(url=final_url))

    await message.answer(f"🚀 **Доступ до терміналу**\nЛокація: {res[11]}", reply_markup=builder.as_markup())


@router.message(F.text == "❌ Покинути сім'ю")
async def leave_family(message: types.Message):
    db.leave_family(message.from_user.id)
    await message.answer("Ви покинули команду.", reply_markup=get_main_kb_no_family())
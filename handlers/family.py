from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import Database
from keyboards import get_main_kb_with_family, get_main_kb_no_family

router = Router()
db = Database('space.db')

class FamilyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_code = State()

@router.message(F.text == "🚀 Створити сім'ю")
async def start_create_family(message: types.Message, state: FSMContext):
    await state.set_state(FamilyStates.waiting_for_name)
    await message.answer("Придумай назву для своєї команди:")

@router.message(FamilyStates.waiting_for_name)
async def process_family_name(message: types.Message, state: FSMContext):
    name = message.text
    invite_code = db.create_family(message.from_user.id, name)
    await state.clear()
    await message.answer(
        f"Сім'ю **{name}** створено! 🎇\nКод запрошення: `{invite_code}`",
        parse_mode="Markdown", reply_markup=get_main_kb_with_family()
    )

@router.message(F.text == "🔗 Приєднатися до сім'ї")
async def start_join_family(message: types.Message, state: FSMContext):
    await state.set_state(FamilyStates.waiting_for_code)
    await message.answer("Введіть код запрошення (6 символів):")

@router.message(FamilyStates.waiting_for_code)
async def process_join_code(message: types.Message, state: FSMContext):
    code = message.text.upper().strip()
    if db.join_family(message.from_user.id, code):
        await state.clear()
        await message.answer("Успіх! Ти в команді! 🚀", reply_markup=get_main_kb_with_family())
    else:
        await message.answer("Невірний код.")

@router.message(F.text == "🌌 Кабінет сім'ї")
async def family_info(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Ти не в сім'ї!", reply_markup=get_main_kb_no_family())
        return

    info = db.get_family_info(family_id)
    members = db.get_family_members(family_id)

    text = f"🏢 **Сім'я:** {info[0]}\n💰 **Бюджет:** {info[2]}\n🔑 **Код:** `{info[1]}`\n\n👨‍🚀 **Екіпаж:**\n"
    for member in members:
        text += f"- {member[0]} ({member[1]})\n"
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "❌ Покинути сім'ю")
async def leave_family(message: types.Message):
    db.leave_family(message.from_user.id)
    await message.answer("Ти покинув сім'ю.", reply_markup=get_main_kb_no_family())
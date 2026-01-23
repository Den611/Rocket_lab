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
    await message.answer("Придумай назву для своєї космічної команди:")


@router.message(FamilyStates.waiting_for_name)
async def process_family_name(message: types.Message, state: FSMContext):
    name = message.text
    invite_code = db.create_family(message.from_user.id, name)
    await state.clear()
    await message.answer(
        f"Сім'ю **{name}** створено! 🎇\nТвій код: `{invite_code}`",
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

    # 0=bal, 1=iron, 2=fuel, 3=sil, 4=ox, 5=hydro, 6=hel, 7=REGOLITH, 8=HE3, 9=mine, 10=time, 11=planet
    data = db.get_family_resources(family_id)
    base_info = db.get_family_info(family_id)

    text = (
        f"🏢 **Сім'я:** {base_info[0]}\n"
        f"🌍 **Локація:** {data[11]}\n"
        f"💰 **Баланс:** {data[0]}\n\n"
        f"📦 **Склад ресурсів:**\n"
        f"  🌍 Земля: ⛓{data[1]} | ⛽{data[2]}\n"
        f"  🔴 Марс: 💾{data[3]} | 🧪{data[4]}\n"
        f"  ⚡ Юпітер: 🌫{data[5]} | 🎈{data[6]}\n"
        f"  🌑 Місяць: 🌑{data[7]} | ⚛️{data[8]}\n\n"
        f"🏭 **Шахта:** Рівень {data[9]}\n"
        f"🔑 **Код:** `{base_info[1]}`"
    )

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "❌ Покинути сім'ю")
async def leave_family(message: types.Message):
    db.leave_family(message.from_user.id)
    await message.answer("Ти покинув сім'ю.", reply_markup=get_main_kb_no_family())
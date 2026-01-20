from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from keyboards import get_main_kb_no_family

router = Router()
db = Database('space.db')


@router.message(F.text == "📡 Місії")
async def show_missions(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id:
        await message.answer("Спочатку вступи в сім'ю!", reply_markup=get_main_kb_no_family())
        return

    missions = db.get_all_missions()
    if not missions:
        await message.answer("Місій поки немає. Адмін має запустити init_missions.py")
        return

    builder = InlineKeyboardBuilder()
    for m in missions:
        builder.button(text=f"{m[1]} (💰{m[3]})", callback_data=f"select_mission:{m[0]}")
    builder.adjust(1)
    await message.answer("📜 **Центр управління польотами**\nОберіть ціль:", reply_markup=builder.as_markup(),
                         parse_mode="Markdown")


@router.callback_query(F.data.startswith("select_mission:"))
async def start_protocol(callback: types.CallbackQuery):
    mission_id = int(callback.data.split(":")[1])
    family_id = db.get_user_family(callback.from_user.id)
    launch_id = db.start_launch(family_id, mission_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Системи в нормі!", callback_data=f"confirm_launch:{launch_id}")

    await callback.message.answer(
        f"🚨 **УВАГА ВСІМ ЕКІПАЖАМ!** 🚨\n\nПротокол підготовки до запуску!\nСтатус: 🔴 Очікування команди\nПотрібно підтверджень: Всі учасники",
        reply_markup=builder.as_markup(), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_launch:"))
async def confirm_participation(callback: types.CallbackQuery):
    launch_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    family_id = db.get_user_family(user_id)

    members = db.get_family_members(family_id)
    total_members = len(members)
    current_signatures = db.sign_launch(launch_id, user_id)

    if current_signatures is False:
        await callback.answer("Ти вже підтвердив!", show_alert=True)
        return

    await callback.message.edit_text(
        f"🚨 **УВАГА ВСІМ ЕКІПАЖАМ!** 🚨\n\nГотовність: {current_signatures}/{total_members}\n"
        f"{'🟢' * current_signatures}{'🔴' * (total_members - current_signatures)}",
        reply_markup=callback.message.reply_markup, parse_mode="Markdown"
    )

    if current_signatures >= total_members:
        await callback.message.answer(
            "🚀 **3... 2... 1... ПУСК!**\nРакета вийшла на траєкторію!\nПеревірте Веб-додаток.", parse_mode="Markdown")
    else:
        await callback.answer("Готовність прийнято!")
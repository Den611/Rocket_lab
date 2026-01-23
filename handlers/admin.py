from aiogram import Router, F, types
from database import Database

router = Router()
db = Database('space.db')

# 1. Пропустити час (для перевірки місій та будівництва)
@router.message(F.text == "!skip_time_admin_999")
async def admin_skip(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id: return

    db.admin_skip_timers(family_id)
    await message.answer("⏩ **[ADMIN]** Час прискорено! Всі процеси завершено.")

# 2. Додати ресурси (для тестів)
@router.message(F.text == "!add_res_admin_777")
async def admin_rich(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    if not family_id: return

    db.admin_add_resources(family_id)
    await message.answer("🤑 **[ADMIN]** Ресурси нараховано. Ви багаті!")
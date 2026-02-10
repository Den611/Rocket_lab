import random
import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from quiz_data import SPACE_QUESTIONS

router = Router()
db = Database('space.db')


# --- ОКРЕМА ФУНКЦІЯ ДЛЯ ВІДПРАВКИ ПИТАННЯ ---
async def send_new_question(message: types.Message, user_id: int):
    """
    Перевіряє ліміти та надсилає нове питання.
    Викликається при старті тесту та автоматично після відповіді.
    """
    # 1. Перевірка сім'ї
    fid = db.get_user_family(user_id)
    if not fid:
        return await message.answer("❌ Спочатку вступіть у сім'ю, щоб заробляти для неї бонуси!")

    # 2. Перевірка ліміту (5 питань на день)
    can_play, count = db.check_quiz_limit(user_id)

    if not can_play:
        return await message.answer(
            f"🏁 **Тест завершено!**\n"
            f"Ви відповіли на всі 5 питань сьогодні.\n"
            f"Приходьте завтра за новою порцією знань! 🚀",
            parse_mode="Markdown"
        )

    # 3. Вибираємо випадкове питання
    q_data = random.choice(SPACE_QUESTIONS)

    # 4. Формуємо кнопки
    kb = InlineKeyboardBuilder()

    options_with_correctness = []
    for i, opt_text in enumerate(q_data["o"]):
        is_correct = (i == q_data["a"])
        options_with_correctness.append((opt_text, is_correct))

    random.shuffle(options_with_correctness)

    for text, is_correct in options_with_correctness:
        # callback: qz : 1/0 (правильно/ні) : reward
        flag = "1" if is_correct else "0"
        kb.button(text=text, callback_data=f"qz:{flag}:{q_data['r']}")

    kb.adjust(1)

    # 5. Списуємо спробу
    db.increment_quiz_count(user_id)

    await message.answer(
        f"🎓 **ПИТАННЯ ({count + 1}/5)**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"❓ {q_data['q']}\n\n"
        f"💰 Нагорода: **{q_data['r']} монет**",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )


# --- ХЕНДЛЕРИ ---

@router.message(F.text == "🎓 Академія")
@router.message(Command("quiz"))
async def start_quiz_handler(message: types.Message):
    # Запускаємо перше питання
    await send_new_question(message, message.from_user.id)


@router.callback_query(F.data.startswith("qz:"))
async def quiz_answer_handler(call: types.CallbackQuery):
    _, flag, reward = call.data.split(":")
    is_correct = (flag == "1")
    reward = int(reward)
    user_id = call.from_user.id

    # Прибираємо кнопки з попереднього питання
    await call.message.edit_reply_markup(reply_markup=None)

    # Обробка відповіді
    if is_correct:
        fid = db.get_user_family(user_id)
        if fid:
            db.update_balance(fid, reward)

            # Редагуємо старе повідомлення, показуємо результат
            await call.message.edit_text(
                f"✅ **Правильно!** (+{reward} монет)\n"
                f"_{get_question_text(call.message.text)}_",  # Залишаємо текст питання для історії
                parse_mode="Markdown"
            )
        else:
            await call.message.edit_text("❌ Ви не в сім'ї.")
    else:
        await call.message.edit_text(
            f"❌ **Помилка!**\n"
            f"_{get_question_text(call.message.text)}_",
            parse_mode="Markdown"
        )

    # --- АВТОМАТИЧНИЙ ЗАПУСК НАСТУПНОГО ПИТАННЯ ---
    await call.answer()

    # Невелика затримка (1 сек) для комфорту
    await asyncio.sleep(1)

    # Викликаємо функцію відправки нового питання
    # Передаємо call.message, щоб бот знав, куди писати
    await send_new_question(call.message, user_id)


def get_question_text(full_text):
    """Допоміжна функція, щоб витягнути текст питання з повідомлення (для краси)"""
    try:
        # Наше повідомлення має структуру: Заголовок \n Лінія \n ❓ Питання ...
        lines = full_text.split('\n')
        # Повертаємо рядок, що починається з ❓, або просто весь текст
        for line in lines:
            if "❓" in line:
                return line
        return full_text
    except:
        return "Питання"
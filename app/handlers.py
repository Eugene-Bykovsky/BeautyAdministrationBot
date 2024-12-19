from aiogram import Router, F
from aiogram.types import Message, FSInputFile

from app.keyboards import consent_keyboard, start_keyboard

router = Router()


@router.message(F.text == '/start')
async def start_command(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 🙋‍♀️\n"
        "Перед началом использования бота, пожалуйста, ознакомьтесь с "
        "документом "
        "о согласии на обработку персональных данных.\n\n"
        "Нажмите кнопку ниже, чтобы подтвердить согласие:",
        reply_markup=consent_keyboard
    )

    consent_file = FSInputFile(
        "files/soglasie.pdf")  # Преобразуем файл в InputFile
    await message.answer_document(document=consent_file)


@router.message(F.text == 'Согласен с обработкой персональнных данных')
async def consent_given(message:Message):
    await message.answer(
        "Спасибо за ваше согласие! 🎉\n"
        "Теперь вы можете начать записываться на процедуры, выбирать мастеров "
        "и получать всю необходимую информацию.",
        reply_markup=start_keyboard
    )
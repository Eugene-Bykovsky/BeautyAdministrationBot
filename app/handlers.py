from aiogram import Router, F
from aiogram.types import Message

from app.keyboards import start_keyboard

router = Router()


@router.message(F.text == '/start')
async def start_command(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 🙋‍♀️\n"
        "Я бот BeautyCity, и я помогу вам записаться на процедуру, "
        "выбрать мастера, узнать цены и оставить чаевые.\n\n"
        "Нажмите 'Записаться', чтобы начать, или выберите другие доступные "
        "опции из меню. 💅✨",
        reply_markup=start_keyboard
    )

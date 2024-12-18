from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тут нужно добавить")],
        [KeyboardButton(text="Тут нужно добавить")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)
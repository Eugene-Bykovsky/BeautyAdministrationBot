from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


consent_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Согласен с обработкой персональнных данных")],
    ],
    resize_keyboard=True,
)


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Запись через Салон")],
        [KeyboardButton(text="Запись к Любимому мастеру")],
        [KeyboardButton(text="Запись через звонок по телефону")],
    ],
    resize_keyboard=True,
)
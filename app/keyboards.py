from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

consent_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Согласен с обработкой персональнных данных")],
    ],
    resize_keyboard=True,
)


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Запись через Салон", callback_data="book_salon")],
        [InlineKeyboardButton(text="Запись к Любимому мастеру", callback_data="book_master")],
        [InlineKeyboardButton(text="Запись через звонок по телефону", callback_data="book_phone")],
    ]
)


# Клавиатура для возврата
back_to_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться в главное меню")],
    ],
    resize_keyboard=True,
)

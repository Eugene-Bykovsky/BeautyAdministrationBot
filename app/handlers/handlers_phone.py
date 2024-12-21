import requests
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards import back_to_menu_keyboard
from config import API_URL

router = Router()


@router.callback_query(lambda c: c.data == "book_phone")
async def show_phone_list(callback_query: types.CallbackQuery):
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        await callback_query.message.answer(
            f"Произошла ошибка при запросе данных: {e}"
        )
        return

    # Обрабатываем ответ API
    salons = response.json()
    if not salons:
        await callback_query.message.answer("Список салонов пуст.")
        return

    # Создаём клавиатуру с телефонами
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{salon['phone']} - {salon['address']}",
                    callback_data=f"salon_{salon['id']}"
                )
            ]
            for salon in salons
        ]
    )

    await callback_query.message.answer(
        "Выберите салон для записи через звонок:",
        reply_markup=keyboard
    )
    await callback_query.message.answer(
        "Или нажмите, чтобы вернуться на главное меню:",
        reply_markup=back_to_menu_keyboard
    )


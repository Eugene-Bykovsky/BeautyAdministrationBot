from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests

from app.keyboards import back_to_menu_keyboard
from config import API_URL

router = Router()


# FSM States
class FavoriteMasterBookingState(StatesGroup):
    fav_choosing_specialist = State()
    fav_choosing_time = State()
    fav_choosing_service = State()
    fav_entering_phone = State()


@router.callback_query(F.data == "book_master")
async def choose_favorite_master_start(callback: CallbackQuery,
                                       state: FSMContext):
    response = requests.get(f'{API_URL}/specialists')
    specialists = response.json()
    if specialists:
        keyboard_builder = InlineKeyboardBuilder()
        for specialist in specialists:
            button = InlineKeyboardButton(
                text=specialist['name'],
                callback_data=f"fav_choose_time_{specialist['id']}"
            )
            keyboard_builder.row(button)
        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите мастера:", reply_markup=keyboard)
        await callback.message.answer(
            "Или нажмите, чтобы вернуться на главное меню:",
            reply_markup=back_to_menu_keyboard
        )
        await state.set_state(FavoriteMasterBookingState.fav_choosing_specialist)
    else:
        await callback.message.answer("Нет доступных мастеров.")


@router.callback_query(F.data.startswith('fav_choose_time_'))
async def choose_time_favorite_master(callback: CallbackQuery, state: FSMContext):
    specialist_id = int(callback.data.split('_')[-1])
    response = requests.get(f'{API_URL}/schedules', params={"specialist_id": specialist_id})
    schedules = response.json()
    if schedules:
        keyboard_builder = InlineKeyboardBuilder()
        for schedule in schedules:
            if schedule['is_available']:
                button = InlineKeyboardButton(
                    text=f"{schedule['date']} {schedule['time']} (Место: {schedule['salon']})",
                    callback_data=f"fav_choose_service_{schedule['id']}"
                )
                keyboard_builder.row(button)
        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите время:", reply_markup=keyboard)
        await callback.message.answer(
            "Или нажмите, чтобы вернуться на главное меню:",
            reply_markup=back_to_menu_keyboard
        )
        await state.set_state(FavoriteMasterBookingState.fav_choosing_time)
    else:
        await callback.message.answer("Нет доступного времени.")


@router.callback_query(F.data.startswith('fav_choose_service_'))
async def choose_service_favorite_master(callback: CallbackQuery, state: FSMContext):
    schedule_id = int(callback.data.split('_')[-1])
    await state.update_data(schedule_id=schedule_id)
    response = requests.get(f'{API_URL}/services')
    services = response.json()
    if services:
        keyboard_builder = InlineKeyboardBuilder()
        for service in services:
            button = InlineKeyboardButton(
                text=f"{service['title']} ({service['price']} руб.)",
                callback_data=f"fav_confirm_{service['id']}"
            )
            keyboard_builder.row(button)
        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите услугу:", reply_markup=keyboard)
        await callback.message.answer(
            "Или нажмите, чтобы вернуться на главное меню:",
            reply_markup=back_to_menu_keyboard
        )
        await state.set_state(FavoriteMasterBookingState.fav_choosing_service)
    else:
        await callback.message.answer("Список услуг недоступен.")


@router.callback_query(F.data.startswith('fav_confirm_'))
async def confirm_appointment_fav(callback: CallbackQuery, state: FSMContext):
    schedule_id = int(callback.data.split('_')[-1])
    await state.update_data(schedule_id=schedule_id)

    await callback.message.answer("Введите ваш номер телефона:")
    await callback.message.answer(
        "Или нажмите, чтобы вернуться на главное меню:",
        reply_markup=back_to_menu_keyboard
    )
    await state.set_state(FavoriteMasterBookingState.fav_entering_phone)


@router.message(FavoriteMasterBookingState.fav_entering_phone)
async def finalize_booking(message: Message, state: FSMContext):
    phone = message.text
    user_data = await state.get_data()
    payload = {
        "customer": message.from_user.first_name,
        "customer_phone": phone,
        "schedule": user_data['schedule_id']
    }
    response = requests.post(f'{API_URL}/appointments-new/create/',
                             json=payload)
    if response.status_code == 201:
        result = response.json()
        print(result)
        await message.answer(
            f"Успешно записаны! 🎉\n"
            f"Адрес салона: {result['Адрес салона']}\n"
            f"Мастер: {result['Мастер']}\n"
            f"Дата: {result['Дата']}\n"
            f"Время: {result['Время']}"
        )
    else:
        error_message = response.json().get('error', 'Произошла ошибка. '
                                                     'Попробуйте позже.')
        await message.answer(f"Ошибка: {error_message}")
    await state.clear()

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests

router = Router()

base_url = 'http://127.0.0.1:8000/api'


# FSM States
class FavoriteMasterBookingState(StatesGroup):
    choosing_specialist = State()
    choosing_time = State()
    choosing_service = State()
    entering_phone = State()


@router.message(F.text == 'Запись к Любимому мастеру')
async def choose_favorite_master_start(message: Message, state: FSMContext):
    response = requests.get(f'{base_url}/specialists')
    specialists = response.json()
    if specialists:
        keyboard_builder = InlineKeyboardBuilder()
        for specialist in specialists:
            button = InlineKeyboardButton(
                text=specialist['name'],
                callback_data=f"choose_time_fav_{specialist['id']}"
            )
            keyboard_builder.row(button)
        keyboard = keyboard_builder.as_markup()
        await message.answer("Выберите мастера:", reply_markup=keyboard)
        await state.set_state(FavoriteMasterBookingState.choosing_specialist)
    else:
        await message.answer("Нет доступных мастеров.")


@router.callback_query(F.data.startswith('choose_time_fav_'))
async def choose_time_favorite_master(callback: CallbackQuery, state: FSMContext):
    specialist_id = int(callback.data.split('_')[-1])
    response = requests.get(f'{base_url}/schedules', params={"specialist_id": specialist_id})
    schedules = response.json()
    if schedules:
        keyboard_builder = InlineKeyboardBuilder()
        for schedule in schedules:
            if schedule['is_available']:
                button = InlineKeyboardButton(
                    text=f"{schedule['date']} {schedule['time']} (Место: {schedule['salon']})",
                    callback_data=f"choose_service_fav_{schedule['id']}"
                )
                keyboard_builder.row(button)
        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите время:", reply_markup=keyboard)
        await state.set_state(FavoriteMasterBookingState.choosing_time)
    else:
        await callback.message.answer("Нет доступного времени.")


@router.callback_query(F.data.startswith('choose_service_fav_'))
async def choose_service_favorite_master(callback: CallbackQuery, state: FSMContext):
    schedule_id = int(callback.data.split('_')[-1])
    await state.update_data(schedule_id=schedule_id)
    response = requests.get(f'{base_url}/services')
    services = response.json()
    if services:
        keyboard_builder = InlineKeyboardBuilder()
        for service in services:
            button = InlineKeyboardButton(
                text=f"{service['title']} ({service['price']} руб.)",
                callback_data=f"confirm_fav_{service['id']}"
            )
            keyboard_builder.row(button)
        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите услугу:", reply_markup=keyboard)
        await state.set_state(FavoriteMasterBookingState.choosing_service)
    else:
        await callback.message.answer("Список услуг недоступен.")


@router.callback_query(F.data.startswith('confirm_fav_'))
async def confirm_appointment_fav(callback: CallbackQuery, state: FSMContext):
    schedule_id = int(callback.data.split('_')[-1])
    await state.update_data(schedule_id=schedule_id)

    await callback.message.answer("Введите ваш номер телефона:")
    await state.set_state(FavoriteMasterBookingState.entering_phone)


@router.message(FavoriteMasterBookingState.entering_phone)
async def finalize_booking(message: Message, state: FSMContext):
    phone = message.text
    user_data = await state.get_data()
    payload = {
        "customer": message.from_user.first_name,
        "customer_phone": phone,
        "schedule": user_data['schedule_id']
    }
    response = requests.post(f'{base_url}/appointments-new/create/',
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

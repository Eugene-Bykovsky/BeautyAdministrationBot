import requests

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, InlineKeyboardButton, \
    CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards import consent_keyboard, start_keyboard

router = Router()

base_url = 'http://127.0.0.1:8000/api'


# FSM States
class BookingState(StatesGroup):
    choosing_salon = State()
    choosing_service = State()
    choosing_time = State()
    entering_phone = State()


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
async def consent_given(message: Message):
    await message.answer(
        "Спасибо за ваше согласие! 🎉\n"
        "Теперь вы можете начать записываться на процедуры, выбирать мастеров "
        "и получать всю необходимую информацию.",
        reply_markup=start_keyboard
    )


@router.message(F.text == 'Запись через Салон')
async def choose_salon_start(message: Message, state: FSMContext):
    response = requests.get(f'{base_url}/salons')
    salons = response.json()

    if salons:
        keyboard_builder = InlineKeyboardBuilder()
        for salon in salons:
            button = InlineKeyboardButton(
                text=salon['address'],
                callback_data=f"choose_service_{salon['id']}"
            )
            keyboard_builder.row(button)

        keyboard = keyboard_builder.as_markup()
        await message.answer("Выберите салон:", reply_markup=keyboard)
        await state.set_state(BookingState.choosing_salon)
    else:
        await message.answer("Список салонов недоступен.")


@router.callback_query(F.data.startswith('choose_service_'))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    salon_id = int(callback.data.split('_')[-1])
    await state.update_data(salon_id=salon_id)

    response = requests.get(f'{base_url}/services')
    services = response.json()

    if services:
        keyboard_builder = InlineKeyboardBuilder()
        for service in services:
            button = InlineKeyboardButton(
                text=f"{service['title']} ({service['price']} руб.)",
                callback_data=f"choose_time_{service['id']}"
            )
            keyboard_builder.row(button)

        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите услугу:",
                                      reply_markup=keyboard)
        await state.set_state(BookingState.choosing_service)
    else:
        await callback.message.answer("Список услуг недоступен.")


@router.callback_query(F.data.startswith('choose_time_'))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split('_')[-1])
    user_data = await state.get_data()
    salon_id = user_data['salon_id']

    response = requests.get(f'{base_url}/schedules',
                            params={"salon_id": salon_id,
                                    "service_id": service_id})
    schedules = response.json()

    if schedules:
        keyboard_builder = InlineKeyboardBuilder()
        for schedule in schedules:
            if schedule['is_available']:
                button = InlineKeyboardButton(
                    text=f"{schedule['date']} {schedule['time']}",
                    callback_data=f"confirm_{schedule['id']}"
                )
                keyboard_builder.row(button)

        keyboard = keyboard_builder.as_markup()
        await callback.message.answer("Выберите время:", reply_markup=keyboard)
        await state.set_state(BookingState.choosing_time)
    else:
        await callback.message.answer("Нет доступного времени.")


@router.callback_query(F.data.startswith('confirm_'))
async def confirm_appointment(callback: CallbackQuery, state: FSMContext):
    schedule_id = int(callback.data.split('_')[-1])
    await state.update_data(schedule_id=schedule_id)

    await callback.message.answer("Введите ваш номер телефона:")
    await state.set_state(BookingState.entering_phone)


@router.message(BookingState.entering_phone)
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
        await message.answer(
            f"Успешно записаны! 🎉\n"
            f"Адрес салона: {result['Адрес салона']}\n"
            f"Мастер: {result['Мастер']}\n"
            f"Дата: {result['Дата']}\n"
            f"Время: {result['Время']}"
        )
    else:
        error_message = response.json().get('error',
                                            'Произошла ошибка. '
                                            'Попробуйте позже.')
        await message.answer(f"Ошибка: {error_message}")

    await state.clear()

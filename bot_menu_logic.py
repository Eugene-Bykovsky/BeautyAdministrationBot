import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from django.core.management import call_command
from django.db import models

from my_django_project.models import Salon, Specialist, Service

API_TOKEN = 'YOUR_BOT_API_TOKEN'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Логирование
logging.basicConfig(level=logging.INFO)

# Сценарии
SALON, SERVICE, SPECIALIST, DATE_TIME, PHONE = range(5)

# Состояние пользователя
user_state = {}

# Функция для генерации кнопок выбора салона
def salon_keyboard():
    salons = Salon.objects.all()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for salon in salons:
        keyboard.add(KeyboardButton(salon.name))
    return keyboard

# Функция для генерации кнопок выбора услуги
def service_keyboard():
    services = Service.objects.all()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for service in services:
        keyboard.add(KeyboardButton(service.name))
    return keyboard

# Функция для генерации кнопок выбора специалиста
def specialist_keyboard(salon_name):
    salon = Salon.objects.get(name=salon_name)
    specialists = salon.specialists.all()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for specialist in specialists:
        keyboard.add(KeyboardButton(specialist.name))
    return keyboard

# Функция для обработки команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_state[message.from_user.id] = SALON
    await message.answer("Добро пожаловать! Выберите салон:", reply_markup=salon_keyboard())

# Обработка выбора салона
@dp.message_handler(lambda message: message.text in [salon.name for salon in Salon.objects.all()])
async def choose_salon(message: types.Message):
    user_state[message.from_user.id] = SERVICE
    salon_name = message.text
    user_state[message.from_user.id] = salon_name
    await message.answer(f"Вы выбрали салон {salon_name}. Теперь выберите услугу:", reply_markup=service_keyboard())

# Обработка выбора услуги
@dp.message_handler(lambda message: message.text in [service.name for service in Service.objects.all()])
async def choose_service(message: types.Message):
    user_state[message.from_user.id] = SPECIALIST
    service_name = message.text
    user_state[message.from_user.id] = service_name
    salon_name = user_state.get(message.from_user.id, {}).get('salon', '')
    await message.answer(f"Вы выбрали услугу {service_name}. Теперь выберите специалиста:", reply_markup=specialist_keyboard(salon_name))

# Обработка выбора специалиста
@dp.message_handler(lambda message: message.text in [specialist.name for specialist in Specialist.objects.all()])
async def choose_specialist(message: types.Message):
    user_state[message.from_user.id] = DATE_TIME
    specialist_name = message.text
    user_state[message.from_user.id] = specialist_name
    await message.answer("Теперь выберите дату и время для записи. Например, 2024-12-20 14:00.")

# Обработка ввода даты и времени
@dp.message_handler(lambda message: message.text.count('-') == 1 and message.text.count(':') == 1)
async def choose_datetime(message: types.Message):
    user_state[message.from_user.id] = PHONE
    datetime = message.text
    user_state[message.from_user.id] = datetime
    await message.answer("Спасибо за запись! Если вы не смогли записаться онлайн, напишите ваш номер телефона.")

# Обработка ввода номера телефона
@dp.message_handler(lambda message: message.contact is not None, state=PHONE)
async def get_phone(message: types.Message):
    phone = message.contact.phone_number
    await message.answer(f"Ваш номер телефона {phone} принят. Мы с вами свяжемся для подтверждения записи.")
    # Тут можно добавить логику сохранения в базу данных или отправки уведомления
    user_state[message.from_user.id] = None

# Обработка ошибки выбора (если сообщение не подходит под логику)
@dp.message_handler(lambda message: message.text not in [salon.name for salon in Salon.objects.all()] and
                                      message.text not in [service.name for service in Service.objects.all()] and
                                      message.text not in [specialist.name for specialist in Specialist.objects.all()])
async def handle_invalid_choice(message: types.Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

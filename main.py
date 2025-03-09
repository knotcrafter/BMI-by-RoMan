import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен бота не найден! Укажите его в файле .env")

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Храним временные данные пользователей
user_data = {}

# Постоянная клавиатура с кнопкой расчёта
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔄 Начать расчёт BMI")]],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start_command(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Хватит сидеть на диване, {user_name}! 🚀\nПора узнать, в какой вы форме! 💪\nЯ быстро посчитаю ваш BMI и помогу понять, куда двигаться дальше. 😏\nНажимайте 'Начать расчёт BMI' и давайте разбираться!",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "🔄 Начать расчёт BMI")
async def start_bmi(message: Message):
    user_data[message.from_user.id] = {}
    await message.answer("Введите ваш вес (в кг):")


@dp.message()
async def get_weight_or_height(message: Message):
    user_id = message.from_user.id
    text = message.text.replace(",", ".")

    try:
        value = float(text)

        if user_id not in user_data or "weight" not in user_data[user_id]:
            user_data[user_id] = {"weight": value}
            await message.answer("Отлично! Теперь введите ваш рост (в метрах, например 1.75):")
        else:
            user_data[user_id]["height"] = value
            weight = user_data[user_id]["weight"]
            height = user_data[user_id]["height"]

            if height <= 0:
                await message.answer("Рост должен быть положительным числом! Попробуй ещё раз.")
                return

            bmi = weight / (height ** 2)
            category = get_bmi_category(bmi)

            await message.answer(f"📊 Твой BMI: {bmi:.2f}\n{category}", reply_markup=keyboard)
            user_data.pop(user_id, None)

    except ValueError:
        await message.answer("Пожалуйста, введите число в формате 70 (вес) или 1.75 (рост).")


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "😅 Недостаток веса (нужно больше пельменей 🥟)"
    elif 18.5 <= bmi < 24.9:
        return "✅ Норма (так держать! 💪)"
    elif 25 <= bmi < 29.9:
        return "⚠️ Избыточный вес (можно немного подтянуться 🏋️‍♂️)"
    else:
        return "🚨 Ожирение (время подружиться с беговой дорожкой! 🏃)"


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

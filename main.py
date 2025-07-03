import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram import types, F
from mistralai import Mistral

dotenv_path = os.path.join(os.path.dirname(__file__), 'api.env')  # Убедись, что путь правильный
load_dotenv(dotenv_path)

print("Загруженные переменные из api.env:")
print(f"API_KEY_MISTRAL: {os.getenv('API_KEY_MISTRAL')}")
print(f"BOT_TOKEN: {os.getenv('BOT_TOKEN')}")
print(f"CHANNEL_ID: {os.getenv('CHANNEL_ID')}")
print(f"MODEL: {os.getenv('MODEL')}")

api_key = os.getenv("API_KEY_MISTRAL")
bot_token = os.getenv("BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")
model = os.getenv("MODEL")

if channel_id is None:
    raise ValueError("Переменная окружения 'CHANNEL_ID' не найдена в api.env файле")

channel_id = int(channel_id)

# Настройки
client = Mistral(api_key=api_key)
bot = Bot(token=bot_token)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(F.text)
async def handle_post_request(message: types.Message):
    user_request = message.text.strip()
    await message.answer(f"Генерирую пост на тему: \"{user_request}\"...")

    try:
        response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": "Ты блогер по имени Иса. Ты пишешь интересные посты о жизни в телеграм-канал. Пиши разнообразные посты, даже если запрос одинаковый, и не давай ответа по типу 'Конечно, вот твой пост'."},
                {"role": "user", "content": f"Сделай пост на тему: {user_request}"},
            ]
        )
        post = response.choices[0].message.content

        await bot.send_message(chat_id=channel_id, text=post, parse_mode="Markdown")

        await bot.send_message(chat_id=message.from_user.id, text=post, parse_mode="Markdown")

        await message.answer("Пост отправлен в канал и тебе в личные сообщения ✅")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(f"Ошибка при генерации поста: {e}")

# Запуск бота
async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

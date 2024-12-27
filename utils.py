import json
import os
from telebot import types
import logging

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.WARNING,  # Изменено на WARNING
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s') # Добавлено filename и lineno


BOT_TOKEN = os.environ.get('BOT_TOKEN')
if BOT_TOKEN is None:
    logging.critical("Переменная окружения BOT_TOKEN не установлена!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)


def load_data():
    try:
        with open("data.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Файл data.json не найден.")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка разбора JSON в файле data.json: {e}")
        return None


def send_photo(message, image_path, caption, reply_markup=None):
    try:
        with open(image_path, 'rb') as f:
            bot.send_photo(message.chat.id, f, caption=caption, reply_markup=reply_markup)
    except FileNotFoundError:
        logging.error(f"Фото {image_path} не найдено.")
        bot.send_message(message.chat.id, "Извини, что-то пошло не так. Попробуй ещё раз.")
    except Exception as e:
        logging.exception(f"Ошибка при отправке фото: {e}")
        bot.send_message(message.chat.id, "Извини, что-то пошло не так. Попробуй ещё раз.")


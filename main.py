import json
import traceback
from telebot import types
import telebot
import os
from result_module import show_result

print(f"Текущая директория: {os.path.abspath(__file__)}")  # Проверяем директорию

BOT_TOKEN = "YOUR_TOKEN" #!!!
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
data = None


def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Данные успешно загружены из data.json")
        return data
    except FileNotFoundError:
        print("Ошибка: файл data.json не найден")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка: Неверный формат JSON в файле data.json, детали: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при загрузке данных: {e}")
        traceback.print_exc()
        return None


def start_quiz(message, bot):
    print(f"start_quiz: Начало обработки команды /start для чата {message.chat.id}")
    chat_id = message.chat.id
    global data
    if not data:
        data = load_data()
        if not data:
            bot.send_message(chat_id, "Ошибка загрузки данных викторины.")
            print(f"start_quiz: Данные не загружены, завершение обработки команды /start для чата {message.chat.id}")
            return
    user_states[chat_id] = {
        "current_question": 0,
        "answers": [],
        "points": {}
    }
    ask_question(message, bot)
    print(f"start_quiz: Успешное завершение обработки команды /start для чата {message.chat.id}")


def ask_question(message, bot):
    chat_id = message.chat.id
    user_data = user_states.get(chat_id)

    if not user_data:
        bot.send_message(chat_id, "Используйте /start для начала викторины.")
        return

    try:
        question = data["questions"][user_data["current_question"]]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for answer in question['answers']:
            keyboard.add(answer['text'])
        bot.send_message(chat_id, question["question"], reply_markup=keyboard)
        bot.register_next_step_handler(message, process_answer, bot)
    except Exception as e:
        print(f"Ошибка в ask_question: {e}")
        traceback.print_exc()


def process_answer(message, bot):
    chat_id = message.chat.id
    user_data = user_states.get(chat_id)

    if not user_data:
        bot.send_message(chat_id, "Используйте /start для начала викторины.")
        return

    answer = message.text
    current_question = user_data["current_question"]

    try:
        question = data["questions"][current_question]
        for a in question["answers"]:
            if a["text"] == answer:
                animal = a.get("animal", None)
                points = a.get("points", 0)
                if animal in user_data["points"]:
                    user_data["points"][animal] += points
                else:
                    user_data["points"][animal] = points

                user_data["answers"].append((current_question, answer))
                user_data["current_question"] += 1
                if user_data["current_question"] < len(data["questions"]):
                    ask_question(message, bot)
                else:
                    show_result(message, user_data["points"], data, bot)
                    del user_states[chat_id]
                return
        bot.send_message(chat_id, "Пожалуйста, выберите один из предложенных вариантов.")  # Исправлен отступ


    except Exception as e:
        print(f"Ошибка в process_answer: {e}")
        traceback.print_exc()


@bot.message_handler(commands=['start'])
def handle_start(message):
    print(f"handle_start: Начало обработки команды /start для чата {message.chat.id}")
    start_quiz(message, bot)
    print(f"handle_start: Завершение обработки команды /start для чата {message.chat.id}")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"handle_message: Начало обработки сообщения: {message.text} для чата {message.chat.id}")
    if message.text != "/start":
        bot.send_message(message.chat.id, "Не понимаю вашего запроса. Используйте /start для начала викторины")
    print(f"handle_message: Завершение обработки сообщения: {message.text} для чата {message.chat.id}")


try:
    print("Начало infinity_polling")
    bot.infinity_polling(timeout=60)

except Exception as e:
    print(f"Ошибка в infinity_polling: {e}")
    traceback.print_exc()

print("Завершение работы бота")

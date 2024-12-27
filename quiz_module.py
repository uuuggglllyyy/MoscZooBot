import json
from telebot import types
from telebot import TeleBot
from utils import load_data  # Предполагается, что utils.py находится в той же директории

user_states = {}  # Словарь для хранения состояний викторин пользователей
quiz_data = None  # Глобальная переменная, где мы сохраним данные викторины


def start_quiz(message, bot: TeleBot):
    print("Запуск start_quiz")  # Отладочное сообщение
    chat_id = message.chat.id
    global quiz_data
    if not quiz_data:
        quiz_data = load_data()
    if not quiz_data:
        bot.send_message(chat_id, "Ошибка загрузки данных викторины.")
        print("Ошибка загрузки данных викторины.") # Вывод сообщения в консоль
        return

    user_states[chat_id] = {
        "current_question": 0,
        "answers": []
    }
    ask_question(message, bot)


def ask_question(message, bot: TeleBot):
    print("Запуск ask_question")  # Отладочное сообщение
    chat_id = message.chat.id
    user_data = user_states.get(chat_id)

    if not user_data:
        bot.send_message(chat_id, "Используйте /start для начала викторины.")
        return

    if not quiz_data:  # Добавлена проверка quiz_data
        bot.send_message(chat_id, "Данные викторины не загружены.")
        return

    current_question_index = user_data["current_question"]
    if current_question_index >= len(quiz_data["questions"]):
        show_result(message, user_data["answers"], bot)
        del user_states[chat_id]
        return

    question = quiz_data["questions"][current_question_index]
    print(f"Текущий вопрос: {current_question_index}")  # Отладочное сообщение

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for answer in question['answers']:
        keyboard.add(answer['text'])

    try:
        sent_message = bot.send_message(chat_id, question["question"], reply_markup=keyboard)
        bot.register_next_step_handler(sent_message, process_answer, bot)
    except Exception as e:  # Лучше ловить более общее исключение
        bot.reply_to(message, f"Произошла ошибка: {e}")


def process_answer(message, bot: TeleBot):
    print("Запуск process_answer")  # Отладочное сообщение
    chat_id = message.chat.id
    user_data = user_states.get(chat_id)

    if not user_data:
        bot.send_message(chat_id, "Используйте /start для начала викторины.")
        return

    if not quiz_data:  # Добавлена проверка quiz_data
        bot.send_message(chat_id, "Данные викторины не загружены.")
        return
    answer = message.text
    print(f"Получен ответ: {answer}")  # Отладочное сообщение
    current_question_index = user_data["current_question"]

    if current_question_index >= len(quiz_data["questions"]):
        show_result(message, user_data["answers"], bot)
        del user_states[chat_id]
        return

    question = quiz_data["questions"][current_question_index]

    if answer in [a['text'] for a in question['answers']]:
        user_data["answers"].append((current_question_index, answer))
        user_data["current_question"] += 1
        ask_question(message, bot)  # Здесь вызываем снова ask_question
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите один из предложенных вариантов.")


def show_result(message, user_answers, bot: TeleBot):
    chat_id = message.chat.id
    # Ваш код для обработки результатов викторины
    if not quiz_data: # Добавлена проверка quiz_data
        bot.send_message(chat_id, "Данные викторины не загружены. Невозможно показать результаты.")
        return

    correct_answers_count = 0
    for question_index, answer in user_answers:
        question_data = quiz_data['questions'][question_index]
        for option in question_data['answers']:
            if option['text'] == answer and option.get('correct', False):
                correct_answers_count += 1
    bot.send_message(chat_id,
                     f"Викторина окончена. Вы правильно ответили на {correct_answers_count} из {len(quiz_data['questions'])} вопросов.")


# Ваш токен от Telegram бота
TOKEN = "YOUR_TOKEN"
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    start_quiz(message, bot)


# Обработчик для всех текстовых сообщений (можно использовать для тестов)
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text == '/start':
        return
    if message.chat.id in user_states:
         process_answer(message, bot) # Обрабатываем ответ, если пользователь в процессе викторины


bot.polling(none_stop=True)
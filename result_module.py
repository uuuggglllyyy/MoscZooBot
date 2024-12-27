import json
from telebot import types
import telebot
import traceback


def show_result(message: telebot.types.Message, user_points: dict, data: dict, bot: telebot.TeleBot):
    """
    Отображает результат викторины.

    Args:
        message (telebot.types.Message): Объект сообщения.
        user_points (dict): Словарь с баллами пользователей.
        data (dict): Словарь с данными викторины.
        bot (telebot.TeleBot): Объект бота.
    """
    print(f"show_result: начало, chat_id={message.chat.id}")
    try:
      chat_id = message.chat.id
      max_points_animal = max(user_points, key=user_points.get)
      print(f"show_result: max_points_animal={max_points_animal}, chat_id={message.chat.id}")
      animal_data = data["animals"].get(max_points_animal, None)
      print(f"show_result: animal_data={animal_data}, chat_id={message.chat.id}")
      if animal_data:
          description = animal_data.get('description', "Описание отсутствует")
          compatibility = animal_data.get('compatibility', [])
          if compatibility:
              comp_str = f" Ты отлично поладишь с {', '.join(compatibility)}."
          else:
             comp_str = "Это очень уникальное животное."
          caption = f"Ты – {max_points_animal}! {description}\n{comp_str}\n"
          caption += "Стань его опекуном и внеси свой вклад в защиту животных! \n"
          caption += "Программа опеки – это возможность финансово поддержать животное, участвовать в мероприятиях, получать обновления о животном. \n"
          caption += f"Узнай больше о программе и начни свою миссию по защите животных!"

          image_path = animal_data.get("image_path", None)
          print(f"show_result: image_path={image_path}, chat_id={message.chat.id}")
          if image_path:
             try:
                 with open(image_path, 'rb') as photo:
                    bot.send_photo(chat_id, photo, caption = caption)
                    print(f"show_result: photo отправлено, chat_id={message.chat.id}")
             except FileNotFoundError:
                print(f"show_result: FileNotFoundError, chat_id={message.chat.id}")
                bot.send_message(chat_id, "Фотография не найдена")
          opeca_link = data.get("opeca_link", None)
          print(f"show_result: opeca_link={opeca_link}, chat_id={message.chat.id}")
          if opeca_link:
             keyboard = types.InlineKeyboardMarkup()
             url_button = types.InlineKeyboardButton(text="Узнать больше о программе опеки", url=data["opeca_link"])
             keyboard.add(url_button)
             bot.send_message(chat_id, text="Или свяжитесь с нами: @MetalOrDeath", reply_markup = keyboard)
      else:
         bot.send_message(chat_id, "Не удалось определить животное.")
      print(f"show_result: завершено, chat_id={message.chat.id}")
    except Exception as e:
       print(f"Ошибка в show_result: {e}, chat_id={message.chat.id}")
       traceback.print_exc()
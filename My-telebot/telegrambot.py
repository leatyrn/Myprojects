import telebot
import json
import requests
import schedule
from telebot import types
import time
import config


COHERE_API_URL = 'https://api.cohere.ai/v1/chat'

bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
# -------------------------------------------------------- фунції роботи з БД

markup = types.ReplyKeyboardMarkup(                   # клавіатура
    resize_keyboard=True, one_time_keyboard=False)

btn_good = types.KeyboardButton("😊 Все добре")
btn_bad = types.KeyboardButton("😢 Погано")
btn_help = types.KeyboardButton("🆘 Потрібна допомога")

markup.add(btn_good)
markup.add(btn_bad, btn_help)


def first_load_file():  # Фунція яка захищає від помилки: json.decoder.JSONDecodeError 
    try:

        with open('file2.json', 'r', encoding='utf-8') as file:
            return json.load(file)
        
    except json.decoder.JSONDecodeError: # Якщо файл ПОВНІСЮ пустий робм заготовку для майбутній користувачів

        data_for_none = {
            'state' : {}
            
        }

        with open('file2.json', 'w', encoding='utf-8') as file:
            json.dump(data_for_none, file, ensure_ascii=False, indent=4)

start_func = first_load_file() # перший запуск першої фунції

def load_data():
    with open('file2.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data):
    with open('file2.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def generate_text(prompt, chat_id):

    headers = {
        'Authorization': f'Bearer {config.COHERE_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': 'command-r-08-2024',
        'message': prompt,
        'max_tokens': 100,
        'temperature': 0.8,
        'p': 0.75,
        'conversation_id': str(chat_id)
    }

    try:
        response = requests.post(COHERE_API_URL, json = data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()


            return response_data['text']

        else:
            print('Помилка про зверненні до API', response.text)
            return None
    except Exception as e:
        print('Помилка запиту!', e)
        return None
    
# -------------------------------------------------------- фунції бота
def job():
    data = load_data()
    for user_id in data['state']:
        bot.send_message(user_id, 'Привіт! Як твій психологічний стан зараз?', reply_markup=markup)

        data['state'][user_id] = 'waiting_schedule'
    save_data(data)

@bot.message_handler(commands=['start'])
def send_hello(message):

    data = load_data()
    user_id = str(message.chat.id)

    # Реєструємо користувача, якщо його немає
    if user_id not in data['state']:
        data['state'][user_id] = 'start'
        save_data(data)


    bot.reply_to(message, 'Привіт! Це бот який буде тобі допомогати у складні часи')


    bot.send_message(message.chat.id, 'обери варіант свого стану:', reply_markup=markup)
    bot.send_message(message.chat.id, 'Яккщо нічого з цього не підходить напиши: Інше')


@bot.message_handler(func=lambda message: True)
def main(message):
    data = load_data()
    user_id = str(message.chat.id)
    current_state = data['state'].get(user_id)

    if message.text == '😊 Все добре':
        data['state'][user_id] = 'good'
        save_data(data)
        prompt = "Користувач каже, що у нього добре. Напиши коротку, позитивну репліку українською мовою, підтримай його гарний настрій та побажай чудового дня."
        ai_response = generate_text(prompt, user_id)
        bot.reply_to(message, ai_response)

    elif message.text == '😢 Погано':
        data['state'][user_id] = 'bad'
        save_data(data)
        prompt = "Користувач написав, що йому погано. Напиши коротке емпатичне слово співчуття та підтримки українською мовою. Нагадай, що відчувати різні емоції — це нормально."
        ai_response = generate_text(prompt, user_id)
        bot.reply_to(message, ai_response)

    elif message.text == '🆘 Потрібна допомога':
        data['state'][user_id] = 'need_help'
        save_data(data)
        prompt = "Користувач у стані сильного стресу чи тривоги і просить про допомогу. Дай йому одну чітку, дуже коротку психологічну вправу для заземлення українською мовою."
        ai_response = generate_text(prompt, user_id)
        bot.reply_to(message, ai_response)

    elif message.text == 'Інше':
        data['state'][user_id] = 'other'
        save_data(data)
        bot.send_message(
            message.chat.id, 'Що саме сталось? Розкажи детальніше своїми словами.')

    elif current_state == 'waiting_schedule':
        prompt = f"Користувач відповідає на планове запитання про самопочуття: '{message.text}'. Дай йому коротку емпатичну пораду або слова підтримки українською мовою."
        ai_response = generate_text(prompt, user_id)
        bot.reply_to(message, ai_response)
        data['state'][user_id] = 'processed'
        save_data(data)

    elif current_state == 'other':
        prompt = f"Користувач описує свій унікальний стан: '{message.text}'. Дай йому коротку емпатичну пораду українською мовою."
        ai_response = generate_text(prompt, user_id)
        bot.reply_to(message, ai_response)
        data['state'][user_id] = 'processed'
        save_data(data)

    elif current_state == 'processed':
        bot.send_message(message.chat.id,'У вас скинутий стан! Оберіть з поданих варіантів, коли зручно)')

    else:
        bot.reply_to(message, 'Я не знаю такого!')
        

schedule.every().day.at("20:09").do(job)


offset = 0  # Змінна для відстеження оброблених повідомлень

while True:
    try:
        schedule.run_pending()

        # Отримуємо нові повідомлення з урахуванням offset
        updates = bot.get_updates(
            offset=offset, timeout=1, long_polling_timeout=1)

        if updates:
            bot.process_new_updates(updates)
            # Оновлюємо offset на ID останнього повідомлення + 1
            offset = updates[-1].update_id + 1

        time.sleep(1)

    except Exception as e:
        print(f"Помилка: {e}")
        time.sleep(5)













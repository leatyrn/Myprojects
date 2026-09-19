import telebot
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import config

bot = telebot.TeleBot(config.TOKEN)

# Функція для завантаження даних


def load_data(filename='Telegram bot types/tele.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Функція для збереження даних
def save_data(data, filename='Telegram bot types/tele.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_user(message):
    user_id = str(message.chat.id)
    username = message.from_user.username  # @ЮЗ
    first_name = message.from_user.first_name  # Як записаний

    filename = 'Telegram bot types/tele.json'

    # Запобіжник помилці, про пустий json
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print('Файл був пустий!')
        users = {}

    if user_id not in users:  # Якщо Айді користувача немає у БД, додаємо його
        users[user_id] = {'username': username,
                          'first_name': first_name,
                          'state': 'none',
                          'variables': {
                              'value_1': {
                                  'name_of_value': 'value1',
                                  'type': 'str',
                                  'info': 'STR'
                              },
                              'value_2': {
                                  'name_of_value': 'value2',
                                  'type': 'str',
                                  'info': 'STR'
                              }
                          }
                          }

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
        print(
            f'Користувача додано! Данні: \nUser_id: {user_id} \nUsername: {username} \nFirst name: {first_name}')
        print()
    else:
        print(f'Користувач за Айді: {user_id} існує!')
        print()


# ==========================================================================
# ==========================================================================
@bot.message_handler(commands=['start'])
def send_message(message):

    add_user(message)

    text = (
        f"Привіт, *{message.from_user.first_name}*! 👋\n\n"
        "Це міні-бот про *Python*! 🐍\n"
        "Тут ти будеш створювати свої змінні та працювати з ними.\n\n"
        "💡 Для більшої інформації напиши /help"
    )

    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def give_help_info(message):

    add_user(message)

    text = (
        "🤖 *Довідка по роботі з ботом*\n\n"
        "Цей міні-бот допоможе тобі вивчити основи роботи зі змінними у *Python*! 🐍\n\n"
        "🔹 */start* — перезапустити бота та оновити дані\n"
        "🔹 */help* — показати це довідкове вікно\n\n"
        "🔹 */to_work* — для початку роботи з ботом\n\n"
        "🐍 За замовчуванням вам доступно 2 змінні типу «Рядок» 🐍"
    )

    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(commands=['to_work'])
def start_work(message):

    add_user(message)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Створити змінну')
    button2 = KeyboardButton('Видалити змінну')
    button3 = KeyboardButton('Виведення змінних')
    button4 = KeyboardButton('Робота з змінними')
    keyboard.add(button1, button2, button3, button4)

    bot.send_message(
        message.chat.id, 'Вибери потрібну дію за допомогою кнопок нижче:', reply_markup = keyboard)


@bot.message_handler(func = lambda message: True)
def main(message):

    add_user(message)

    users = load_data()
    text = message.text
    user_id = str(message.chat.id)
    current_state = users.get(user_id, {}).get('state', 'none')

    if text == 'Створити змінну':

        users[user_id]['state'] = 'which_number_of_value'

        save_data(users)

        bot.send_message(
            message.chat.id, 'Перше введи з якої змінною працюємо(1 або 2): 🔤')
        return

    elif text == 'Виведення змінних':
        user_vars = users[user_id].get('variables', {})

        text_to_send = '📊 *Твої поточні змінні:*\n\n'

        for var_key, var_data in user_vars.items():
            name = var_data.get('name_of_value')
            v_type = var_data.get('type')
            info = var_data.get('info')

            text_to_send += f"• Ім'я: *{name}*\n  Тип: `{v_type}`\n  Значення: `{info}`\n\n"

        bot.send_message(message.chat.id, text_to_send, parse_mode='Markdown')
        return

    elif text == 'Видалити змінну':
        users[user_id]['state'] = 'delete_variable_number'
        save_data(users)

        bot.send_message(
            message.chat.id,
            '🗑 *Видалення змінної*\n\n'
            'Введи номер змінної, яку хочеш очистити/видалити (*1* або *2*): 🔤',
            parse_mode='Markdown'
        )

        return

    elif text == 'Робота з змінними':
        user_variables = users[user_id].get('variables', {})

        if 'value_1' in user_variables and 'value_2' in user_variables:
            # Перевіряємо їхні типи
            type1 = user_variables['value_1']['type']
            type2 = user_variables['value_2']['type']

            if type1 == 'int' and type2 == 'int':
                # Безпечно перетворюємо на числа
                val1 = int(user_variables['value_1']['info'])
                val2 = int(user_variables['value_2']['info'])

                bot.send_message(
                    message.chat.id,
                    f'🔢 *Круто! Обидві змінні виявилися числами (`int`)*\n\n'
                    f'• Значення першої: `{val1}`\n'
                    f'• Значення другої: `{val2}`\n\n'
                    f'Ось що робить із ними справжній Python:\n'
                    f'➕ Додавання: `{val1} + {val2} = {val1 + val2}`\n'
                    f'➖ Віднімання: `{val1} - {val2} = {val1 - val2}`\n'
                    f'✖️ Множення: `{val1} * {val2} = {val1 * val2}`',
                    parse_mode='Markdown'
                )

            elif type1 == 'str' and type2 == 'str':
                str1 = user_variables['value_1']['info']
                str2 = user_variables['value_2']['info']

                # Конкатенація (склеювання) рядків у Python
                result = str1 + str2

                upper_str1 = str1.upper()
                lower_str1 = str1.lower()

                bot.send_message(
                    message.chat.id,
                    f'🔤 *Круто! Обидві змінні виявилися рядками (`str`)*\n\n'
                    f'• Значення першої: `{str1}`\n'
                    f'• Значення другої: `{str2}`\n\n'
                    f'У Python рядки можна склеювати за допомогою плюса (+):\n'
                    f'🔗 Склеювання: `"{str1}" + "{str2}" = "{result}"`'
                    f'✨ А ось як працюють методи рядків у Python:\n'
                    f'• `.upper()` (усі великі): `"{upper_str1}"`\n'
                    f'• `.lower()` (усі малі): `"{lower_str1}"`',
                    parse_mode='Markdown'
                )

            elif type1 == 'bool' and type2 == 'bool':
                # Оскільки у базі значення зберігаються як рядки, перетворимо їх на справжні булеві значення Python
                bool1 = user_variables['value_1']['info'].lower() == 'true'
                bool2 = user_variables['value_2']['info'].lower() == 'true'

                and_res = bool1 and bool2
                or_res = bool1 or bool2
                not_res = not bool1

                bot.send_message(
                    message.chat.id,
                    f'🟨 *Круто! Обидві змінні виявилися булевими (`bool`)*\n\n'
                    f'• Значення першої: `{bool1}`\n'
                    f'• Значення другої: `{bool2}`\n\n'
                    f'Ось логічні операції в Python:\n'
                    f'• `and` (І): `{bool1} and {bool2} = {and_res}`\n'
                    f'• `or` (АБО): `{bool1} or {bool2} = {or_res}`\n'
                    f'• `not` (НЕ для першої): `not {bool1} = {not_res}`',
                    parse_mode='Markdown'
                )

            else:
                bot.send_message(
                    message.chat.id,
                    f'💥 *Ой! Python видає помилку типу (TypeError)*\n\n'
                    f'• Тип першої змінної: `{type1}`\n'
                    f'• Тип другої змінної: `{type2}`\n\n'
                    f'У Python не можна виконувати математичні чи стандартні операції між різними типами даних напряму. '
                    f'Спершу їх потрібно перетворити (зробити *casting*), наприклад, через `str()` або `int()`!',
                    parse_mode='Markdown'
                )

        else:
            bot.send_message(
                message.chat.id,
                '❌ У тебе створено ще не всі змінні. Спочатку створи обидві через меню!'
            )
        return
# ВИДАЛЕННЯ
# ========================================================================================================
    elif current_state == 'delete_variable_number' and text in ['1', '2']:
        # users[user_id]['temp_var_num'] = text

        var_num = text
        target_key = f'value_{var_num}'

        if target_key in users[user_id]['variables']:
            del users[user_id]['variables'][target_key]

        users[user_id]['state'] = 'none'
        save_data(users)

        bot.send_message(
            message.chat.id,
            f'🗑 Змінну №{var_num} успішно видалено!',
        )
        return
# ========================================================================================================
# СТВОРЕННЯ
# ========================================================================================================
    elif current_state == 'which_number_of_value' and text in ['1', '2']:
        # З якою змінною працюємо, 1 чи 2 users
        users[user_id]['temp_var_num'] = text

        users[user_id]['state'] = 'waiting_for_variable_name'

        save_data(users)

        bot.send_message(message.chat.id, f'Введи назву для змінної {text}: 🔤')
        return

    elif current_state == 'waiting_for_variable_name':
        user_variables = users[user_id].get('variables', {})
        if 'value_1' not in user_variables:
            target_key = 'value_1'
        elif 'value_2' not in user_variables:
            target_key = 'value_2'
        else:
            var_num = users[user_id].get('temp_var_num', '1')
            target_key = f'value_{var_num}'

            # Гарантуємо, що словник для цієї змінної існує (навіть якщо її перед цим видаляли)
            users[user_id]['variables'].setdefault(target_key, {})

            # Тепер безпечно записуємо ім'я
            users[user_id]['variables'][target_key]['name_of_value'] = text

            users[user_id]['state'] = 'waiting_for_type_of_value'

            save_data(users)

            bot.send_message(
                message.chat.id,
                f'✅ Змінну успішно оновлено! Її нове ім’я: *{text}*',
                parse_mode='Markdown',
            )

            bot.send_message(
                message.chat.id,
                f'Введи тип для змінної: {text} Ось так (*str*, *int*, *bool*) 🔤',
                parse_mode='Markdown'
            )
            return

    elif current_state == 'waiting_for_type_of_value' and text in ['str', 'int', 'bool']:

        var_num = users[user_id].get('temp_var_num', '1')
        target_key = f'value_{var_num}'

        users[user_id]['variables'][target_key]['type'] = text

        users[user_id]['state'] = 'waiting_for_info'

        save_data(users)

        bot.send_message(
            message.chat.id,
            f'✅ Тип успішно перезаписано!',
            parse_mode='Markdown'
        )

        bot.send_message(
            message.chat.id,
            "🎯 *Майже готово!*\n\n"
            "Залишилося ввести саме значення для цієї змінної.\n"
            "💡 _Зауваження до введення:_\n"
            "• Для `int` — тільки числа.\n"
            "• Для `bool` — тільки `True` або `False`.\n"
            "• Для `str` — будь-який текст.",
            parse_mode="Markdown",
        )

        return

    elif current_state == 'waiting_for_info':

        var_num = users[user_id].get('temp_var_num', '1')
        target_key = f'value_{var_num}'

        if users[user_id]['variables'][target_key]['type'] == 'int':
            try:
                number = int(text)
                users[user_id]['variables'][target_key]['info'] = number
            except ValueError:
                bot.send_message(message.chat.id,
                                 '❌Ви ввели для типу *int* не число!❌',
                                 parse_mode='Markdown')

        elif users[user_id]['variables'][target_key]['type'] == 'str':
            users[user_id]['variables'][target_key]['info'] = text

        else:
            if text not in ['True', 'False']:
                bot.send_message(message.chat.id,
                                 '❌Для даних типу *bool* потрібно ввести: *False* або *True*❌',
                                 parse_mode='Markdown')
                return
            elif text in ['True', 'False']:
                users[user_id]['variables'][target_key]['info'] = text

        save_data(users)

        bot.send_message(
            message.chat.id,
            '🎉 Змінну успішно створено та збережено!\n'
            'Для подальшої роботи можете написати /to_work'
        )

        users[user_id]['state'] = 'none'

        save_data(users)

        return
# ========================================================================================================
    else:
        if current_state == 'which_number_of_value':
            bot.send_message(
                message.chat.id,
                '❌ Ой, ти ввів щось не те! Зараз потрібно вибрати номер змінної: начни цифру **1** або **2**.',
                parse_mode='Markdown'
            )

        elif current_state == 'waiting_for_type_of_value':
            bot.send_message(
                message.chat.id,
                '❌ Невірний тип! Обери з доступних: *str*, *int* або *bool*.',
                parse_mode='Markdown'
            )

        elif current_state == 'waiting_for_info':
            bot.send_message(
                message.chat.id,
                '❌ Формат не підходить під обраний тип даних. Спробуй ще раз згідно з інструкцією!',
                parse_mode='Markdown'
            )

        else:
            # На випадок, якщо стан 'none', а користувач просто пише текст у чат
            bot.send_message(
                message.chat.id,
                'Я тебе не зовсім зрозумів. Скористайся кнопками нижче або напиши /help 🤖'
            )
        return


bot.polling()

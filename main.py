import telebot
from telebot import types
import random
import time
import threading

bot = telebot.TeleBot('8177309175:AAFXqP8Cqo1-KaVDJFR56K0uKkXPIbmyAiQ')

mutually_exclusive_items = {"Sange and Yasha", "Yasha and Kaya", "Sange and Kaya"}
blinks = ["Blink(Stremght),Blink(Agility), Blink(Intelect)"]

def load_items_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Загрузка массивов
items_core = load_items_from_file('All TXT Files/items_core.txt')
items_offlane = load_items_from_file('All TXT Files/items_offlane.txt')
items_support = load_items_from_file('All TXT Files/items_support.txt')
boots_core = load_items_from_file('All TXT Files/boots_core.txt')
boots_support = load_items_from_file('All TXT Files/boots_support.txt')
early_support = load_items_from_file("All TXT Files/early_support.txt")
early_core = load_items_from_file("All TXT Files/early_core.txt")
heroes = load_items_from_file("All TXT Files/heroes.txt")
heroes_1x6 = load_items_from_file("All TXT Files/heroes_1x6.txt")

# Функция для удаления сообщений
def delete_after_delay(chat_id, message_id, delay):
    time.sleep(delay)
    bot.delete_message(chat_id, message_id)

@bot.message_handler(commands=["game"])
def game_picker(message):
    selected_hero = random.choice(heroes)
    markup = types.InlineKeyboardMarkup(row_width=2)
    roles = ["Carry", "Mid", "Offlane", "Semi-Support", "Full Support"]
    buttons = [types.InlineKeyboardButton(role, callback_data=f"role_{role}_{selected_hero}") for role in roles]
    markup.add(*buttons)

    bot_message = bot.send_message(message.chat.id, f"Вам выпал герой: {selected_hero}\nВыберите роль:", reply_markup=markup, parse_mode="html")
    threading.Thread(target=delete_after_delay, args=(message.chat.id, message.message_id, 2400)).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def role_selected(call):
    _, role, selected_hero = call.data.split("_")

    # Определяем массив предметов в зависимости от роли
    role_items = {
        "Carry": items_core,
        "Mid": items_core,
        "Offlane": items_offlane,
        "Semi-Support": items_support,
        "Full Support": items_support
    }
    
    selected_items = select_items_from_role(role_items[role], 5)

    boots = boots_core if role in ["Carry", "Mid", "Offlane"] else boots_support

    selected_boots = random.choice(boots)

    result_text = (
    f"🎮 <b>Ваш герой:</b> {selected_hero} ({role})  \n\n"
    f"🏃‍♂️ <b>Твой скороход:</b> {selected_boots}  \n"
    f"⚔️ <b>Айтем-билд:</b> {', '.join(selected_items)}  \n\n"
    f"⏳ <i>Сообщение удалится через 40 минут!</i>"
)

    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_text, parse_mode="html")
    threading.Thread(target=delete_after_delay, args=(call.message.chat.id, call.message.message_id, 2400)).start() #2400 - 40 минут

def select_items_from_role(items_list, num_items):
    selected_items = []
    available_items = items_list.copy()

    while len(selected_items) < num_items:
        item = random.choice(available_items)

        # Проверяем на взаимно исключающие предметы
        if item in mutually_exclusive_items:
            available_items = [i for i in available_items if i not in mutually_exclusive_items or i == item]

        # Добавляем условие для Блинков
        if item not in blinks or not any(blink in selected_items for blink in blinks):
            selected_items.append(item)
            available_items.remove(item)

    # Добавляем Блинки в выбранные предметы
    if len(selected_items) < num_items:
        blink_count = num_items - len(selected_items)
        selected_blinks = random.sample(blinks, min(blink_count, len(blinks)))
        selected_items.extend(selected_blinks)

    return selected_items


@bot.message_handler(commands=["1x6"])
def picker_1x6(message):
    selected_hero = random.choice(heroes_1x6)
    skill = random.randint(1, 4)
    bot_message = bot.reply_to(message, f"🎮 <b>Ваш герой:</b> {selected_hero}\n"
                                        f"🔥 Твой легендарный скилл: <u><b>{skill}</b></u>\n\n"
                                        f"⏳ <i>Сообщение удалится через 20 секунд!</i>",
                                        parse_mode="HTML")
    threading.Thread(target=delete_after_delay, args=(message.chat.id, message.message_id, 20)).start()
    threading.Thread(target=delete_after_delay, args=(message.chat.id, bot_message.message_id, 20)).start()

# Команда /roll для случайного числа в диапазоне
@bot.message_handler(commands=['roll'])
def roll(message):
    text = message.text.split()
    try:
        min_val, max_val = (map(int, text[1].split('-')) if len(text) > 1 and '-' in text[1] else (1, 100))
        initial_number = random.randint(min_val, max_val)
        msg = bot.send_message(message.chat.id, f"Выпало число: {initial_number} ({min_val}-{max_val})")
        
        end_time = time.time() + 2
        while time.time() < end_time:
            random_number = random.randint(min_val, max_val)
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                  text=f"Выпало число: {random_number} ({min_val}-{max_val})")
            time.sleep(0.1)
        
        final_number = random.randint(min_val, max_val)
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                              text=f"Выпало число: {final_number} ({min_val}-{max_val})")
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Пожалуйста, введите диапазон в формате /roll X-Y, например, /roll 1-50")

# Команда /hero для случайного героя
@bot.message_handler(commands=["hero", "хиро", "герой"])
def random_hero(message):
    bot_message = bot.send_message(message.chat.id, f"Герой: {random.choice(heroes)}")
    threading.Thread(target=delete_after_delay, args=(message.chat.id, message.message_id, 10)).start()
    threading.Thread(target=delete_after_delay, args=(message.chat.id, bot_message.message_id, 10)).start()

# Команда /early с кнопками выбора для ранних предметов по роли
@bot.message_handler(commands=["early"])
def random_early_item(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("Core", callback_data="early_core"),
        types.InlineKeyboardButton("Support", callback_data="early_support")
    ]
    markup.add(*buttons)
    bot_message = bot.send_message(message.chat.id, "Выберите свою роль для ранней игры:", reply_markup=markup)
    threading.Thread(target=delete_after_delay, args=(message.chat.id, message.message_id, 10)).start()

# Команда /boots с кнопками выбора для ботинок по роли
@bot.message_handler(commands=["boots", "ботинок", "тапок", "педали", "скороходы"])
def random_boots(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("Core", callback_data="boots_core"),
        types.InlineKeyboardButton("Support", callback_data="boots_support")
    ]
    markup.add(*buttons)
    bot_message = bot.send_message(message.chat.id, "Выберите свою роль для ботинок:", reply_markup=markup)
    threading.Thread(target=delete_after_delay, args=(message.chat.id, message.message_id, 10)).start()

# Обработчик callback для кнопок выбора предметов и ботинок
@bot.callback_query_handler(func=lambda call: call.data in ["items_core", "items_offlane", "items_support", "early_core", "early_support", "boots_core", "boots_support"])
def send_random_item_or_boots(call):
    role_items = {
        "boots_core": boots_core,
        "boots_support": boots_support
    }

    selected_items = role_items.get(call.data, [])
    if selected_items:
        chosen_item = random.choice(selected_items)
        result_text = f"Ваш ботинок: {chosen_item}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_text)
    threading.Thread(target=delete_after_delay, args=(call.message.chat.id, call.message.message_id, 10)).start()

bot.infinity_polling()
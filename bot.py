import os
import json
import time
import string
import threading
import subprocess
import http.client
import urllib.parse
import telebot
import pyautogui
import pyscreeze

# --- Constants and Global Variables ---
SENSOR_IDS = [1, 2]   #<====  Replace 1, 2 with your id !!!
BOT_TOKEN = ""  # Replace with your bot token !!!
bot = telebot.TeleBot(BOT_TOKEN)

KEY_MAP = {  # Mapping key names to PyAutoGUI codes
    "alt": "alt", "ctrl": "ctrl", "shift": "shift", "win": "win", "tab": "tab",
    "enter": "enter", "esc": "esc", "space": "space", "up": "up", "down": "down",
    "left": "left", "right": "right",
    "fn": "fn", "home": "home", "return": "enter", "insert": "insert"
}

monitoring_thread = None
monitoring_message_id = None
monitoring_chat_id = None
monitoring_stop_event = threading.Event()
last_hardware_info = ""
selected_special_keys = []
selected_keys = []  # Initialize selected_keys globally
current_stage = "special"
screenshot_counter = 1

# --- Utility Functions ---
def get_hardware_info_from_json(url="http://localhost:8085/data.json"):
    try:
        parsed_url = urllib.parse.urlparse(url)
        conn = http.client.HTTPConnection(parsed_url.netloc) # Use netloc for host:port
        conn.request("GET", parsed_url.path)
        response = conn.getresponse()
        if response.status == 200:
            return json.loads(response.read().decode('utf-8'))
        print(f"HTTP Error: {response.status}")
        return None
    except (ConnectionRefusedError, http.client.RemoteDisconnected, http.client.InvalidURL, json.JSONDecodeError) as e:
        print(f"Error fetching JSON: {e}")
        return None


def find_sensor_values(data, sensor_ids):
    results = []  # Picking up the results here
    def find_recursive(data, sensor_ids):
        if isinstance(data, list):
            for item in data:
                find_recursive(item, sensor_ids)
        elif isinstance(data, dict):
            if "id" in data and data["id"] in sensor_ids:
                if "Value" in data:
                    results.append(f"{data.get('Text', 'Unknown Sensor'):<20}: {data['Value']}")
                else:
                    results.append(f"Sensor {data['id']} found, but 'Value' is missing.")
            if "Children" in data:
                find_recursive(data["Children"], sensor_ids)
    find_recursive(data, sensor_ids)  # Causes an internal function
    return "\n".join(results)  # Returns the formatted string


def get_hardware_info_string(sensor_ids):
    data = get_hardware_info_from_json()
    if data:
        output = find_sensor_values(data, sensor_ids)
        return output or "No data found for specified sensors."
    return "Failed to retrieve hardware information."


def create_keyboard(keys, selected_keys, stage):
    markup = telebot.types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for key in keys:
        if key not in ("continue", "execute"): #Combined conditions
             buttons.append(telebot.types.InlineKeyboardButton(f"✅ {key}" if key in selected_keys else key, callback_data=key))
    if stage == "special":
        buttons.append(telebot.types.InlineKeyboardButton("Continue", callback_data="continue"))
    elif stage == "alphabet":
        buttons.append(telebot.types.InlineKeyboardButton("Execute", callback_data="execute"))
    markup.add(*buttons)
    return markup


def monitor_resources(chat_id, message_id, interval=1):
    global monitoring_stop_event, last_hardware_info
    dots = "."  # Start with one dot
    while not monitoring_stop_event.is_set():
        try:
            hardware_info = get_hardware_info_string(SENSOR_IDS)                    
            message_to_send = f"{hardware_info}{dots}"
            if hardware_info != last_hardware_info:  # Only update if data changed
                bot.edit_message_text(message_to_send, chat_id, message_id)
                last_hardware_info = hardware_info
                if dots == ".":
                    dots = ".."
                elif dots == "..":
                    dots = "."
            time.sleep(interval)
        except telebot.apihelper.ApiException as e:
            print(f"Ошибка обновления ресурсов: {e}")
            break


def process_cmd_command(message):
    try:
        command = message.text
        process = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='cp866', check = True) # Use subprocess.run
        output = f"{process.stdout}\n{process.stderr}"
        bot.send_message(message.chat.id, output)
    except subprocess.CalledProcessError as e:  # Catch specific error
        bot.reply_to(message, f"Command failed: {e.stderr}")  # Show stderr for better diagnostics
    except Exception as e:
        bot.reply_to(message, f"Command execution error: {e}")

def process_winr_command(message):
    try:
        command = message.text.strip()
        os.system(f"start {command}")
        bot.send_message(message.chat.id, f"Executed: {command}")
    except Exception as e:
        bot.reply_to(message, f"Command execution error: {e}")


def take_screenshot(message):
    global screenshot_counter
    try:
        screenshot_path = rf"V:\\foto.kolektzia\\screens\\screen{screenshot_counter}.png"
        pyautogui.screenshot(screenshot_path)
        with open(screenshot_path, 'rb') as screenshot:
            bot.send_photo(message.chat.id, photo=screenshot)
        screenshot_counter += 1
    except Exception as e:
        bot.send_message(message.chat.id, f"Error taking screenshot: {e}")


# --- Keyboard and Menu Functions ---
def create_main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) #reduced row width
    markup.add(telebot.types.KeyboardButton('pc control'))
    return markup


def create_pc_control_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = ("screenshot", "cmd command", "win+r (execute)", "monitoring", "hotkey", "back")
    markup.add(*(telebot.types.KeyboardButton(btn) for btn in btns))
    return markup



# --- Telegram Bot Handlers ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome!", reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: message.text == 'pc control')
def handle_pc_control(message):
    bot.send_message(message.chat.id, "Select an action:", reply_markup=create_pc_control_menu())


@bot.message_handler(func=lambda message: message.text == "back")
def handle_back(message):
    bot.send_message(message.chat.id, "Main menu:", reply_markup=create_main_menu())


@bot.message_handler(commands=['screenshot'])
@bot.message_handler(func=lambda message: message.text == "screenshot")
def screenshot_handler(message):
    take_screenshot(message)


@bot.message_handler(commands=['cmd'])
@bot.message_handler(func=lambda message: message.text == "cmd command")
def cmd_command_handler(message):
    bot.send_message(message.chat.id, "Enter command:")
    bot.register_next_step_handler(message, process_cmd_command)


@bot.message_handler(commands=['winr'])
@bot.message_handler(func=lambda message: message.text == "win+r (execute)")
def winr_command_handler(message):
    bot.send_message(message.chat.id, "Enter the name of the file/program:")
    bot.register_next_step_handler(message, process_winr_command)


@bot.message_handler(commands=['monitoring'])
@bot.message_handler(func=lambda message: message.text == "monitoring")
def handle_monitor_resources(message):
    global monitoring_stop_event
    if not monitoring_stop_event.is_set():
        monitoring_stop_event.set()  # Stop if already running

    msg = bot.send_message(message.chat.id, "Enter the desired refresh interval in seconds (enter the decimal fraction with a dot '.')")
    bot.register_next_step_handler(msg, start_monitoring)  # register with 'msg'


def start_monitoring(message):
    """Runs resource monitoring in a separate thread."""
    global monitoring_thread, monitoring_message_id, monitoring_chat_id, monitoring_stop_event
    try:
        interval = float(message.text)
        if interval <= 0:
            raise ValueError("The interval must be a positive number.")  # Keep error message concise
        monitoring_stop_event.clear()
        if not monitoring_thread or not monitoring_thread.is_alive():  # Simplified condition
            hardware_info = get_hardware_info_string(SENSOR_IDS)                                           
            sent_message = bot.send_message(message.chat.id, hardware_info)
            monitoring_message_id = sent_message.message_id
            monitoring_chat_id = message.chat.id
            monitoring_thread = threading.Thread(target=monitor_resources, args=(
                message.chat.id, sent_message.message_id, interval), daemon=True)  # Use daemon=True directly
            monitoring_thread.start()
        else:
            bot.send_message(message.chat.id, "Monitoring is already running. To stop it, use /stopmonitor.") 
    except ValueError:
        bot.reply_to(message, "Invalid interval. Enter a positive number.")  
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")  


@bot.message_handler(commands=['hotkey'], func=lambda message: True)  # Combined hotkey handler
@bot.message_handler(func=lambda message: message.text == "hotkey")
def keystroke_handler(message):
    global selected_keys, current_stage, selected_special_keys
    selected_keys = []
    current_stage = "special"  # added for clarity
    selected_special_keys = ["ctrl", "shift", "tab", "win", "esc", "fn", "home", "return", "insert", "alt", "continue"] # Reset special keys here for each use
    reply_markup = create_keyboard(selected_special_keys, selected_keys, current_stage)
    bot.send_message(message.chat.id, "Select special keys:", reply_markup=reply_markup)


@bot.message_handler(commands=['keys'])
def handle_virtual_keys(message):
    try:
        keys_text = message.text[6:]
        keys = keys_text.lower().split("+")
        invalid_keys = [key for key in keys if key not in KEY_MAP]
        if invalid_keys:
            return bot.reply_to(message, f"Invalid keys: {', '.join(invalid_keys)}")

        pyautogui_keys = [KEY_MAP[key] for key in keys]
        pyautogui.hotkey(*pyautogui_keys)
        bot.reply_to(message, f"Keys {'+'.join(keys)} pressed.")
    except Exception as e:
        bot.reply_to(message, f"Error pressing keys: {e}")


@bot.callback_query_handler(func=lambda call: True)
def handle_key_callback(call):
    global selected_keys, current_stage, selected_special_keys  
    key = call.data
    if key == "continue":
        current_stage = "alphabet"
        selected_special_keys = selected_keys.copy() # Corrected the copy method
        selected_keys = [] #Clears the list before adding alphabet keys
        alphabet_keys = list(string.ascii_lowercase) + list(string.digits) + ["execute"]
        reply_markup = create_keyboard(alphabet_keys, selected_keys, current_stage)
        bot.edit_message_text("Select alphabet keys:", call.message.chat.id, call.message.message_id, reply_markup=reply_markup)
    elif key == "execute":
        try:
            keys_to_press = [KEY_MAP[key] for key in selected_special_keys] + [KEY_MAP[key] for key in selected_keys if key not in ["continue", "execute"]]
            if keys_to_press:
                pyautogui.hotkey(*keys_to_press)
                bot.answer_callback_query(call.id, text=f"Keys pressed: {', '.join(keys_to_press)}")
            selected_keys = [] # Cleared the list before switching stage
            current_stage = "special"
        except Exception as e:
            bot.answer_callback_query(call.id, text=f"Error: {e}")
    elif current_stage == "special":
        if key in selected_keys:
            selected_keys.remove(key)
        else:
            selected_keys.append(key)
        special_keys = ["ctrl", "shift", "tab", "win", "esc", "fn", "home", "return", "insert", "alt"] + ["continue"] # Moved inside the "if" block so that it is redefined every time this part of the code is executed
        reply_markup = create_keyboard(special_keys, selected_keys, current_stage)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=reply_markup)
    elif current_stage == "alphabet":
        if key in selected_keys:
            selected_keys.remove(key)
        else:
            selected_keys.append(key)
        alphabet_keys = list(string.ascii_lowercase) + list(string.digits) + ["execute"]  # Redefined alphabet_keys to avoid adding execute button multiple times
        reply_markup = create_keyboard(alphabet_keys, selected_keys, current_stage)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=reply_markup)

bot.polling(none_stop=True)
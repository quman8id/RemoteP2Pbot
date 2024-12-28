# RemoteP2Pbot
This is a Telegram bot that allows your phone to communicate with your computer. (PhoneToPC)

## Features

* **Screenshot:** Captures and sends a screenshot of your screen.
* **CMD Commands:** Executes commands in the command prompt.
* **Win+R Execution:** Runs programs or opens files via the Win+R dialog.
* **Resource Monitoring:** Monitors CPU and RAM usage and sends updates to Telegram.  You can specify the update interval.
* **Hotkey Sending:** Sends keystrokes, including combinations with modifier keys (Ctrl, Shift, Alt, Win). Uses an interactive keyboard within Telegram.
* **Interactive Menu:** Provides a user-friendly menu system for navigating the bot's features.

## Prerequisites

* **Python 3.x:** Make sure you have Python 3 installed on your system.
* **OpenHardwareMonitor**: You need to have [Open Hardware Monitor](https://openhardwaremonitor.org/downloads/) running in the background for resource monitoring to work. The bot connects to it locally (port 8085 by default). Make sure to configure the web server within OHM.
**Telegram Bot Token**: You'll need to create a Telegram bot in [@BotFather](https://t.me/botfather) and obtain its token. Replace "YOUR_BOT_TOKEN" in the script with your actual token.
* **Required Libraries:** Install the necessary libraries using pip:

```bash
pip install pyTelegramBotAPI pyautogui pyscreeze json http.client urllib.parse threading string
```

## Setup
**Clone the repository:**
```bash
git clone https://github.com/your-username/telegram-pc-control.git
```
**Install dependencies:** See "Prerequisites" above.

**Configure the bot:**
Replace "YOUR_BOT_TOKEN" at line 20 with your bot's token.

**Modify the screenshot_path** variable if you want to save screenshots to a different location.

**Adjust the sensor IDs** in get_hardware_info_string to monitor different hardware components. The default IDs (49, 57) may not correspond to CPU and RAM on your system. Refer to the OpenHardwareMonitor data.json file for the correct sensor IDs.

**Run the script:**
```bash
python your_script_name.py
```
## Usage
**Commands:**
/start, /help - main menu

Start a conversation with your bot in Telegram. The main menu will appear, allowing you to choose from the available features.
PC Control: Opens a submenu with options for screenshot, CMD, Win+R, monitoring, and hotkeys.
Smart Home: (Not yet implemented) Placeholder for future smart home integration.
/keys [key combination]: Directly send keystrokes. For example, /keys ctrl+alt+delete or /keys win+r. This method can also be used along with the main menu options.
Monitoring Specific Sensors
The script connects to OpenHardwareMonitor on port 8085 and expects a data.json file to be served. To monitor specific sensors, you need to provide their IDs within the get_hardware_info_string function.
Run OpenHardwareMonitor.
Enable the "Web Server" option in the Options menu, and check that the port is 8085 (or change it in the script if needed).
Visit http://localhost:8085/data.json in your web browser to see the available sensor data.
Locate the "id" values for the sensors you want to monitor (e.g., CPU temperature, RAM usage).
Update the sensor_ids list in the get_hardware_info_string function with the IDs you found.

# RemoteP2Pbot
This is a Telegram bot that allows your phone to communicate with your computer. (PhoneToPC)

## Features

* **Screenshot:** Captures and sends a screenshot of your screen.
* **CMD Commands:** Executes commands in the command prompt.
* **Win+R Execution:** Runs programs or opens files via the Win+R dialog.
* **Resource Monitoring:** Monitors CPU, RAM etc. usage and sends updates to Telegram.  You can specify the update interval.
* **Hotkey Sending:** Sends keystrokes, including combinations with modifier keys (Ctrl, Shift, Alt, Win). Uses an interactive keyboard within Telegram.
* **Interactive Menu:** Provides a user-friendly menu system for navigating the bot's features.

## Prerequisites

* **Python 3.x:** Make sure you have Python 3 installed on your system.
* **OpenHardwareMonitor**: You need to have [Open Hardware Monitor](https://openhardwaremonitor.org/downloads/) with the remote web server running. The bot connects to it locally (port 8085 by default).
* **Telegram Bot Token**: You'll need to create a Telegram bot in [@BotFather](https://t.me/botfather) and obtain its token. Replace `"YOUR_BOT_TOKEN"` **(line 15)** in the script with your actual token
* **Required Libraries:** Install the necessary libraries using pip:
```bash
pip install pyTelegramBotAPI pyautogui pyscreeze json http.client urllib.parse threading string
```

## Setup
1. **Clone the repository:**
```bash
git clone https://github.com/quman8id/RemoteP2Pbot.git
```
2. **Install dependencies:** See "Prerequisites" above.

3. **Configure the bot:**
Replace "YOUR_BOT_TOKEN" at line 15 with your bot's token.

4. **Modify the screenshot_path** variable if you want to save screenshots to a different location.

5. **Adjust the sensor IDs** in `SENSOR_IDS` **(line 14)** to monitor different hardware components. Get them from OHM's JSON file.

6. **Run the script:**
```bash
python bot.py
```


## Usage

Start a conversation with your bot in Telegram. The main menu will appear, allowing you to choose from the available features.

***Commands:***
- **`/start, /help`** - main menu
- **`/cmd`** - execute command in cmd
- **`/winr`** - execute file or programm (win+r analog)
- **`/screenshot`** - make a screenshot
- **`/hotkeys`** - send hotkeys to pc
- **`/monitoring`** - output monitoring of pc

## Possible errors

- Connection Error: [WinError 10061] Connection not established because the destination computer rejected the connection request

  - Try turning off VPN

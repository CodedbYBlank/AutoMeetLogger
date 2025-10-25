# Smart Scheduler 

> Your assistant for automatically joining and leaving meetings, with logs sent straight to Telegram 

---

## Features
- Automatically joins and leaves your online meetings
- Sends logs to a Telegram bot in real-time
- Health checks & crash recovery for smooth operation
- Schedule reminders before your meetings 
- style logging and emojis  

---

## 🛠 Requirements
- Python 3.10+
- Libraries:
  ```txt
  pyautogui
  schedule
  requests
  pygetwindow
  pillow
  ```
---

## Install all Python dependencies:

- pip install -r requirements.txt

---

## Setup

- Telegram bot
- Create a Telegram bot and get its token.
- Find your chat ID.
- add your token & chat ID.

```
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
```
---
## Meeting links

- Replace the placeholder links in the meetings dictionary in main.py with your own meeting links.

---

## Assets

- Add screenshots of your meeting app’s join and leave buttons in the assets/ folder:

- join_button.png

- leave_button.png

- Run the scheduler

- python main.py

---
## 🗓 Usage

- It will automatically join your scheduled meetings.

- Logs appear locally (scheduler.log) and in Telegram.

- If a meeting doesn’t join automatically, It will check manually after 20 minutes.

- Get reminders 10 minutes before each meeting.

---

# 📁 Recommended Folder Structure
```
SmartScheduler/
├─ assets/
│  ├─ join_button.png
│  └─ leave_button.png
├─ main.py
├─ requirements.txt
├─ README.md
└─ LICENSE
```
---
## 📝 License

This project is licensed under the MIT License 💌

It is watching over your meetings… in the Best way possible 💫


---

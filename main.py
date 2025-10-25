import webbrowser
import pyautogui
import schedule
import time
import datetime
import subprocess
import pygetwindow as gw
import requests
import os
import sys
import logging
import traceback
from typing import Optional

class MeetingError(Exception):
    """Custom exception for meeting-related errors"""
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

# Get base path (works for .py and .exe)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

assets_path = os.path.join(base_path, "assets")

# Track meetings and state
joined_meetings = set()
restart_count = 0
MAX_RESTARTS = 5

# Telegram configuration
# Telegram configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"



# Weekly meeting schedule with join and leave times

meetings = {
    "Monday": [
        ("08:00", "10:04", "MEETING_LINK"),
        ("13:00", "14:05", "MEETING_LINK")
    ],
    "Tuesday": [
        ("09:00", "11:00", "MEETING_LINK")
        ],
    "Wednesday": [
        ("08:00", "10:04", "MEETING_LINK"),
       ],
    "Thursday": [
        ("13:00", "15:00", "MEETING_LINK"),
    ],
    "Saturday": [
        ("09:00", "11:00", "MEETING_LINK"),
    ]
}

# log sender
def send_log(msg: str, level: str = "info") -> None:
    """Enhanced log sender with multiple channels"""
    prefixes = ["✌️", "😑", "✨", "🙄", "🐾", "😏", "🙃", "💫"]
    heart = prefixes[hash(msg) % len(prefixes)]
    formatted_msg = f"{heart} {msg}"
    
    # Local logging
    log_func = getattr(logging, level.lower())
    log_func(formatted_msg)
    
    # Telegram logging
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": formatted_msg},
            timeout=10
        )
    except Exception as e:
        logging.error(f"Failed to send Telegram log: {e}")

def safe_window_operation(func):
    """Decorator for safe window operations"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            send_log(f"Window operation failed: {e}", "error")
            return None
    return wrapper

@safe_window_operation
def restore_teams() -> Optional[gw.Window]:
    """Improved Teams window restoration"""
    teams_windows = gw.getWindowsWithTitle("Microsoft Teams")
    if not teams_windows:
        raise MeetingError("Teams window not found")
    
    team_win = teams_windows[0]
    if team_win.isMinimized:
        team_win.restore()
    team_win.activate()
    return team_win

def join_meeting(link: str, join_time: str, leave_time: str) -> None:
    """Enhanced meeting join with selective manual join detection"""
    try:
        # Skip if already joined
        if link in joined_meetings:
            send_log("Meeting already in joined list, skipping join check")
            return

        send_log(f"Attempting to join meeting at {join_time}")
        webbrowser.open(link)
        
        # Wait for Teams with timeout
        for _ in range(4):  # 20 seconds total
            time.sleep(5)
            if restore_teams():
                break
        else:
            send_log("Teams failed to open in time")

        # Look for join button with multiple attempts
        join_img = os.path.join(assets_path, "join_button.png")
        for _ in range(3):
            join_btn = pyautogui.locateOnScreen(join_img, confidence=0.8)
            if join_btn:
                pyautogui.click(join_btn)
                joined_meetings.add(link)
                send_log(f"Successfully joined meeting ({join_time} → {leave_time})")
                return
            time.sleep(5)
        
        # Schedule manual join check only if automated join failed
        join_dt = datetime.datetime.strptime(join_time, "%H:%M").replace(
            year=datetime.datetime.now().year,
            month=datetime.datetime.now().month,
            day=datetime.datetime.now().day
        )
        check_time = (join_dt + datetime.timedelta(minutes=20)).strftime("%H:%M")
        
        schedule.every().day.at(check_time).do(check_manual_join, link, check_time)
        send_log(f"Join failed - Will check for manual join at {check_time}")
            
    except Exception as e:
        send_log(f"Failed to join meeting: {str(e)}", "error")
        logging.error(traceback.format_exc())

def check_manual_join(link: str, check_time: str) -> schedule.CancelJob:
    """Check if user manually joined the meeting"""
    try:
        # Skip check if meeting was joined in the meantime
        if link in joined_meetings:
            send_log("Meeting already joined, canceling manual check")
            return schedule.CancelJob

        restore_teams()
        leave_img = os.path.join(assets_path, "leave_button.png")
        
        if pyautogui.locateOnScreen(leave_img, confidence=0.7):
            send_log(f"Manual join detected at {check_time}")
            joined_meetings.add(link)
        else:
            send_log("No manual join detected")
            
    except Exception as e:
        send_log(f"Error checking manual join: {e}", "error")
    
    return schedule.CancelJob  # Remove the scheduled check after running once

def leave_meeting(link: str) -> None:
    """Improved meeting leave mechanism"""
    if link not in joined_meetings:
        send_log("Meeting not in active sessions, skipping leave")
        return

    try:
        restore_teams()
        leave_img = os.path.join(assets_path, "leave_button.png")

        for _ in range(12):
            leave_btn = pyautogui.locateOnScreen(leave_img, confidence=0.7)
            if leave_btn:
                pyautogui.click(leave_btn)
                joined_meetings.discard(link)
                send_log("Successfully left meeting")
                return
            time.sleep(5)

        raise MeetingError("Leave button not found after timeout")

    except Exception as e:
        send_log(f"Error leaving meeting: {e}", "error")
        logging.error(traceback.format_exc())
        joined_meetings.discard(link)  # Clean up tracking anyway

def sleep_until(target_dt):
    while True:
        if datetime.datetime.now() >= target_dt:
            break
        time.sleep(60)

def sleep_until_morning():
    now = datetime.datetime.now()
    next_morning = (now + datetime.timedelta(days=1)).replace(hour=6, minute=0, second=0)
    send_log("🌙 All done for today~ Sleeping until morning 💫")
    sleep_until(next_morning)

# Smart daily scheduler
def daily_schedule():
    today = datetime.datetime.now()
    today_day = today.strftime("%A")
    today_str = today.strftime("%Y-%m-%d")

    # Check conditions
    if today.date() > SEM_END_DATE.date():
        send_log("🎓 Semester over~! No more classes ")
        return False
    if today_str in holidays:
        send_log(f" Holiday today ({today_str})~ enjoy your rest ")
        return False
    if today_day not in meetings:
        send_log("💤 No classes today~ ")
        return False

    today_meetings = meetings[today_day]

    #  Send today’s schedule once
    schedule_msg = " Hey~ here’s today’s schedule 💕\n\n"
    for join_time, leave_time, _ in today_meetings:
        schedule_msg += f"👉 {join_time} → {leave_time}\n"
    send_log(schedule_msg.strip())

    # Schedule reminders + join/leave
    for join_time, leave_time, link in today_meetings:
        join_dt = datetime.datetime.strptime(join_time, "%H:%M").replace(
            year=today.year, month=today.month, day=today.day
        )
        reminder_dt = join_dt - datetime.timedelta(minutes=10)

        # Schedule reminder
        schedule.every().day.at(reminder_dt.strftime("%H:%M")).do(
            lambda jt=join_time: send_log(f" Class at {jt} soon, get ready ")
        )
        # Schedule join + leave
        schedule.every().day.at(join_time).do(join_meeting, link, join_time, leave_time)
        schedule.every().day.at(leave_time).do(leave_meeting, link)

    return True

def main_loop() -> None:
    """Enhanced main loop with better state management"""
    global restart_count
    
    try:
        has_class = daily_schedule()
        if not has_class:
            sleep_until_morning()
            return

        midnight_sent = False
        last_health_check = datetime.datetime.now()

        while True:
            schedule.run_pending()
            
            # Health check every hour
            now = datetime.datetime.now()
            if (now - last_health_check).total_seconds() > 3600:
                send_log("Hourly health check - System running normally")
                last_health_check = now
                restart_count = 0  # Reset restart count after successful hour

            # Midnight refresh
            if now.hour == 0 and not midnight_sent:
                send_log("Midnight refresh - Updating schedule")
                daily_schedule()
                midnight_sent = True
            elif now.hour != 0:
                midnight_sent = False

            time.sleep(30)

    except Exception as e:
        logging.error(traceback.format_exc())
        handle_crash(e)

def handle_crash(error: Exception) -> None:
    """Improved crash handling with restart limiting"""
    global restart_count
    
    restart_count += 1
    if restart_count > MAX_RESTARTS:
        send_log("Too many restart attempts - Requiring manual intervention", "critical")
        sys.exit(1)

    send_log(f"Crash detected (attempt {restart_count}/{MAX_RESTARTS}): {str(error)}", "error")
    time.sleep(10)

    try:
        if getattr(sys, 'frozen', False):
            subprocess.Popen([sys.executable] + sys.argv)
        else:
            os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit(0)
    except Exception as e:
        send_log(f"Failed to restart: {e}", "critical")
        sys.exit(1)

# Holidays
holidays = [
    "2025-10-20", "2025-10-21", "2025-10-27",
    "2025-10-28", "2025-10-29", "2025-11-05"
]

# Last day of semester
SEM_END_DATE = datetime.datetime(2026, 11, 24) #CHANGE TO YOUR SEMISTER LAST CLASSES 

if __name__ == "__main__":
    send_log(" Smart Scheduler started with enhanced reliability")
    main_loop()

import datetime
import os
import subprocess

import dotenv

# Get present working directory
dotenv.load_dotenv(os.path.join(os.getcwd(), ".env"))

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHAT_ID_ARRAY = os.getenv("CHAT_ID")  # Can have multiple chat ids separated by commas
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Split chat ids into a list
CHAT_IDS = [int(chat_id) for chat_id in CHAT_ID_ARRAY.split(",")]


def save_logs():
    # Define the log directory and ensure it exists
    log_dir = "/var/log/user_cpu_usage"
    os.makedirs(log_dir, exist_ok=True)

    # Get today's date
    today = datetime.date.today()

    # Run the `sa -u` command
    result = subprocess.run(["sudo", "sa", "-u"], capture_output=True, text=True)

    # Parse the output and prepare the log entry
    log_entry = f"Date: {today}\n{result.stdout}\n"

    # Save the log entry to a file
    log_file = os.path.join(log_dir, f"{today}.log")
    with open(log_file, "w") as file:
        file.write(log_entry)

    print(f"CPU usage log for {today} has been saved to {log_file}")


def parse_log(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        user_cpu = {}
        for line in lines:
            if line.strip() and not line.startswith("Date:"):
                parts = line.split()
                if len(parts) > 1:
                    user = parts[0]
                    cpu_time = float(parts[1])
                    user_cpu[user] = user_cpu.get(user, 0) + cpu_time
    return user_cpu


def aggregate_cpu_usage(log_dir):
    total_usage = {}
    for file_name in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file_name)
        if os.path.isfile(file_path):
            daily_usage = parse_log(file_path)
            for user, cpu_time in daily_usage.items():
                total_usage[user] = total_usage.get(user, 0) + cpu_time
    return total_usage


def show_metrics():
    log_dir = "/var/log/user_cpu_usage"

    total_usage = aggregate_cpu_usage(log_dir)
    for user, cpu_time in total_usage.items():
        # Convert CPU time to human readable hours
        cpu_time_hours = cpu_time / 3600
        print(f"**User:** {user}, Total CPU Time: {cpu_time_hours:.2f} hours")


# Use telethon to send the metrics to a Telegram channel
from telethon import TelegramClient, events

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


async def send_metrics():
    log_dir = "/var/log/user_cpu_usage"
    total_usage = aggregate_cpu_usage(log_dir)
    message = ""
    for user, cpu_time in total_usage.items():
        # Convert CPU time to human readable hours and minutes
        cpu_time_hours = cpu_time / 3600
        cpu_time_minutes = (cpu_time_hours % 1) * 60
        message += f"<b>User:</b> {user}, <b>Total CPU Time:</b> {cpu_time_hours:.0f} hours {cpu_time_minutes:.0f} minutes\n"
    for CHAT_ID in CHAT_IDS:
        await client.send_message(CHAT_ID, message, parse_mode="html")


with client:
    client.loop.run_until_complete(send_metrics())

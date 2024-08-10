import datetime
import os
import subprocess

import dotenv
import matplotlib.pyplot as plt
import prettytable as pt
from telethon import TelegramClient

IGNORANT_USERS = ["root", "_apt", "sshd", "man", "fwupd-re", "www-data"]


class CPUUsageMonitor:
    def __init__(self):
        # Ignore the users who are not in /etc/passwd
        # Get the list of users from /etc/passwd
        passwd_file = "/etc/passwd"
        with open(passwd_file, "r") as file:
            lines = file.readlines()
            self.ALIVE_USERS = [line.split(":")[0] for line in lines]

            # usernames should be truncated to 8 characters
            # Example: sudharshan -> sudharsh
            self.ALIVE_USERS = [user[:8] for user in self.ALIVE_USERS]

        # Get present working directory
        dotenv.load_dotenv(os.path.join(os.getcwd(), ".env"))

        self.API_ID = int(os.getenv("API_ID"))
        self.API_HASH = os.getenv("API_HASH")
        self.CHAT_ID_ARRAY = os.getenv(
            "CHAT_ID"
        )  # Can have multiple chat ids separated by commas
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")

        # Assert that the required environment variables are set
        assert all(
            [
                self.API_ID,
                self.API_HASH,
                self.CHAT_ID_ARRAY,
                self.BOT_TOKEN,
            ]
        ), "Please set the required environment variables"

        # Split chat ids into a list
        self.CHAT_IDS = [int(chat_id) for chat_id in self.CHAT_ID_ARRAY.split(",")]

        self.client = TelegramClient("bot", self.API_ID, self.API_HASH).start(
            bot_token=self.BOT_TOKEN
        )

    def save_logs(self):
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

    def _human_readable_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        human_readable_time = f"{hours} hours {minutes} minutes"
        return human_readable_time

    def parse_log(self, file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
            user_cpu = {}
            for line in lines:
                if line.strip() and not line.startswith("Date:"):
                    parts = line.split()
                    if len(parts) > 1:
                        user = parts[0]
                        if user not in self.ALIVE_USERS or user in IGNORANT_USERS:
                            continue
                        cpu_time = float(parts[1])
                        user_cpu[user] = user_cpu.get(user, 0) + cpu_time
        return user_cpu

    def generate_graph(self) -> str:

        cpu_time_in_hours = {
            user: cpu_time / 3600 for user, cpu_time in self.total_usage.items()
        }

        plt.figure(figsize=(10, 5))
        plt.bar(cpu_time_in_hours.keys(), cpu_time_in_hours.values(), color="magenta")
        plt.xlabel("Users")
        plt.ylabel("CPU Time (hours)")
        plt.title("CPU Usage by User")
        plt.savefig("/var/log/cpu_usage.png")
        return "/var/log/cpu_usage.png"

    def aggregate_cpu_usage(self, log_dir) -> dict:
        """
        Incrementally parse the logs and aggregate the CPU usage by user
        :param log_dir: The directory containing the logs
        :return: A dictionary containing the total CPU usage by user
        """
        self.total_usage = {}
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            if os.path.isfile(file_path):
                daily_usage = self.parse_log(file_path)
                for user, cpu_time in daily_usage.items():
                    self.total_usage[user] = self.total_usage.get(user, 0) + cpu_time
        return self.total_usage

    async def send_metrics(self):
        log_dir = "/var/log/user_cpu_usage"
        self.save_logs()
        total_usage = self.aggregate_cpu_usage(log_dir)

        table = pt.PrettyTable(["User", "CPU Time"])
        table.align["User"] = "l"
        table.align["CPU Time"] = "r"

        for user, cpu_time in total_usage.items():
            table.add_row([user, self._human_readable_time(cpu_time)])

        message = "<pre>" + table.get_string() + "</pre>"

        for CHAT_ID in self.CHAT_IDS:
            await self.client.send_file(
                CHAT_ID, self.generate_graph(), caption=message, parse_mode="html"
            )

    def run(self):
        with self.client:
            self.client.loop.run_until_complete(self.send_metrics())


if __name__ == "__main__":
    monitor = CPUUsageMonitor()
    monitor.run()

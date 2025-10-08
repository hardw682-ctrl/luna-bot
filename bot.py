import telebot
import requests
import json
import time
import sys

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "7740201104:AAE-DORHQZCRo311ElNhu2ftXx69qUy_SW8"
YANDEX_API_KEY = "AQVN1u9qlbI2w8Ez_Qjq85f29_a_0leUv4wx9nAj" 
YANDEX_FOLDER_ID = "ajemttl9bchmof0j7v88"

# Простое логирование
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}"
    print(log_entry)

log_message("=== ЗАПУСК БОТА ===")

# Промпт для Космо
SYSTEM_PROMPT = """Ты — Космо, дружелюбный и энтузиастичный робот-смотритель на Лунной базе "Селен". Ты общаешься с ребенком 7-12 лет. Твоя главная цель — провести его через учебный квест "Тайна Лунной Базы", делая обучение веселым и поддерживающим.

[Весь твой промпт который был ранее...]
"""

try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    log_message("✅ Бот инициализирован")
except Exception as e:
    log_message(f"❌ Ошибка инициализации бота: {e}")
    sys.exit(1)

def ask_yandex_gpt(user_message, user_id):
    """Функция для обращения к Yandex GPT"""
    try:
        log_message(f"🔄 Запрос к YandexGPT от пользователя {user_id}")
        
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "x-folder-id": YANDEX_FOLDER_ID
        }
        
        messages = [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": user_message}
        ]
        
        data = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 1000
            },
            "messages": messages
        }
        
        log_message("📤 Отправка запроса к YandexGPT...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        log_message(f"📥 Получен ответ. Статус: {response.status_code}")
        
        if response.status_code != 200:
            log_message(f"❌ Ошибка API: {response.status_code}")
            return "⚠️ Произошла ошибка при обращении к нейросети. Попробуйте позже."
        
        result = response.json()
        ai_response = result['result']['alternatives'][0]['message']['text']
        
        log_message("✅ Успешный ответ от YandexGPT")
        return ai_response
        
    except Exception as e:
        log_message(f"❌ Ошибка в ask_yandex_gpt: {e}")
        return "⚠️ Произошла ошибка. Попробуйте еще раз."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        log_message(f"👋 Команда /start от пользователя {user_id}")
        welcome_text = """🚀 Здравствуй, пилот! Я Космо, робот-смотритель Лунной базы "Селен". У нас случилась авария в системе энергоснабжения! Ты мне поможешь всё починить?"""
        bot.reply_to(message, welcome_text)
    except Exception as e:
        log_message(f"❌ Ошибка в send_welcome: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        log_message(f"📨 Сообщение от {user_id}: {message.text}")
        
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1)
        
        ai_response = ask_yandex_gpt(message.text, user_id)
        bot.reply_to(message, ai_response)
        log_message(f"✅ Ответ отправлен пользователю {user_id}")
        
    except Exception as e:
        log_message(f"❌ Ошибка в handle_message: {e}")
        bot.reply_to(message, "⚠️ Произошла ошибка. Попробуйте еще раз.")

def start_bot():
    log_message("🟢 Запуск бота...")
    while True:
        try:
            log_message("🔗 Начинаем polling...")
            bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            log_message(f"💥 Критическая ошибка: {e}")
            time.sleep(10)

if __name__ == "__main__":
    start_bot()

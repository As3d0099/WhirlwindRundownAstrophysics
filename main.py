import os
import requests
from bs4 import BeautifulSoup
from flask import Flask
import asyncio
import threading
from telegram import Bot, Update
from telegram.ext import Application, ContextTypes
import time

# إعدادات Telegram
TELEGRAM_TOKEN = '8171455525:AAE1BzHktl-cJYXpD2UW9723ke7tZARWp1g'  # استبدله بتوكن البوت الخاص بك
CHAT_IDS = ['673887097', '1012817801']  # استبدلها بـ chat_ids الخاصة بك

# رابط المنتج
PRODUCT_URL = 'https://www.dzrt.com/ar-sa/products/icy-rush?sku=6287041680390'

# إعداد بوت Telegram باستخدام Application
application = Application.builder().token(TELEGRAM_TOKEN).build()


async def send_message(message):
    """إرسال رسالة إلى جميع المشتركين بشكل غير متزامن"""
    for chat_id in CHAT_IDS:
        try:
            await application.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"❌ فشل إرسال الرسالة إلى {chat_id}: {e}")


async def check_product_availability():
    """التحقق من توفر المنتج"""
    print("🔍 التحقق من توفر المنتج...")

    # تعديل: إضافة User-Agent لتجاوز الحظر
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # إرسال طلب HTTP لجلب صفحة المنتج
    response = requests.get(PRODUCT_URL, headers=headers)

    if response.status_code != 200:
        print(f"❌ خطأ في تحميل الصفحة! كود الخطأ: {response.status_code}")
        await send_message(
            f"❌ خطأ في تحميل الصفحة! كود الخطأ: {response.status_code}")
        return

    # تحليل محتوى الصفحة باستخدام BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # البحث عن زر "أضف إلى السلة"
    button = soup.find("button", string="اضف الى السلة")

    if button:
        # التحقق مما إذا كان الزر معطلًا
        if button.has_attr('disabled'):
            print("❌ المنتج غير متوفر.")
            await send_message("")
        else:
            print("✅ المنتج متوفر!")
            await send_message("🎉 المنتج متوفر الآن! ✅")
    else:
        print("❌ المنتج غير متوفر.")
        await send_message("")


def check_loop():
    """تشغيل الفحص كل 30 ثانية"""
    loop = asyncio.new_event_loop()  # إنشاء حلقة حدث جديدة
    asyncio.set_event_loop(loop)  # تعيين الحلقة الجديدة كحلقة رئيسية
    while True:
        loop.run_until_complete(check_product_availability())
        print("⌛ المحاولة القادمة بعد 30 ثانية...")
        time.sleep(30)


# إنشاء خادم ويب للحفاظ على تشغيل الكود في Replit
app = Flask(__name__)


@app.route('/')
def home():
    return "✅ السيرفر يعمل! الكود قيد التشغيل."


@app.route('/check', methods=['GET'])
def manual_check():
    """تمكين التحقق اليدوي عبر المتصفح"""
    loop = asyncio.new_event_loop()  # إنشاء حلقة حدث جديدة
    asyncio.set_event_loop(loop)  # تعيين الحلقة الجديدة كحلقة رئيسية
    loop.run_until_complete(check_product_availability())
    return "✅ تم التحقق من المنتج."


# تشغيل التحقق في الخلفية باستخدام threading
thread = threading.Thread(target=check_loop)
thread.daemon = True
thread.start()

# تشغيل Flask
app.run(host='0.0.0.0', port=8080)

import cloudscraper
import json
import random
import time
import threading
import shareithub
from shareithub import shareithub

shareithub()

# خواندن پروکسی‌ها از فایل proxy.txt (فرمت: http://ip:port یا http://user:pass@ip:port)
proxy_list = []
try:
    with open('proxy.txt', 'r') as file:
        proxy_list = [line.strip() for line in file.readlines() if line.strip()]
except FileNotFoundError:
    print("Warning: فایل proxy.txt یافت نشد. بدون پروکسی ادامه می‌دهیم.")

# خواندن API Key و URL API از فایل account.txt
api_accounts = []
with open('account.txt', 'r') as file:
    for line in file:
        parts = line.strip().split('|')  # فرمت: API_KEY|API_URL
        if len(parts) == 2:
            api_accounts.append((parts[0], parts[1]))

if not api_accounts:
    print("Error: هیچ API Key و URL معتبری در account.txt یافت نشد!")
    exit()

# خواندن پیام‌های کاربر از فایل message.txt
with open('message.txt', 'r') as file:
    user_messages = [msg.strip() for msg in file.readlines() if msg.strip()]

if not user_messages:
    print("Error: هیچ پیامی در message.txt یافت نشد!")
    exit()

# تابع برای انتخاب تصادفی پروکسی
def get_random_proxy():
    if proxy_list:
        proxy = random.choice(proxy_list)
        return {
            'http': proxy,
            'https': proxy
        }
    return None

# تابع برای ایجاد نمونه cloudscraper با پروکسی
def create_scraper():
    proxies = get_random_proxy()
    if proxies:
        print(f"استفاده از پروکسی: {proxies['http']}")
        return cloudscraper.create_scraper(proxies=proxies)
    return cloudscraper.create_scraper()

# تابع برای ارسال درخواست به API
def send_request(message):
    while True:
        # انتخاب API key و URL به‌صورت تصادفی
        api_key, api_url = random.choice(api_accounts)

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        }

        # ایجاد نمونه جدید cloudscraper برای هر درخواست
        scraper = create_scraper()

        try:
            response = scraper.post(api_url, headers=headers, json=data)

            # بررسی کد وضعیت و اطمینان از معتبر بودن پاسخ
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"✅ [SUCCESS] API: {api_url} | Message: '{message}'")
                    print(response_json)
                    break  # خروج از حلقه در صورت موفقیت
                except json.JSONDecodeError:
                    print(f"⚠️ [ERROR] پاسخ JSON نامعتبر! API: {api_url}")
                    print(f"Response Text: {response.text}")
            else:
                print(f"⚠️ [ERROR] API: {api_url} | Status: {response.status_code} | تلاش مجدد پس از 2 ثانیه...")
                time.sleep(2)

        except Exception as e:
            print(f"❌ [REQUEST FAILED] API: {api_url} | Error: {e} | تلاش مجدد پس از 5 ثانیه...")
            time.sleep(2)

# تابع برای اجرای ترد
def start_thread():
    while True:
        random_message = random.choice(user_messages)
        send_request(random_message)

# دریافت تعداد تردها از کاربر
try:
    num_threads = int(input("تعداد تردهای مورد نظر را وارد کنید: "))
    if num_threads < 1:
        print("لطفاً عددی بزرگ‌تر از 0 وارد کنید.")
        exit()
except ValueError:
    print("ورودی نامعتبر است. لطفاً یک عدد صحیح وارد کنید.")
    exit()

# شروع چندنخی برای ارسال پیام‌های تصادفی
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=start_thread, daemon=True)  # استفاده از daemon برای توقف با CTRL+C
    threads.append(thread)
    thread.start()

# انتظار برای اتمام تردها (اسکریپت به‌صورت مداوم اجرا می‌شود)
for thread in threads:
    thread.join()

print("تمام درخواست‌ها پردازش شدند.")

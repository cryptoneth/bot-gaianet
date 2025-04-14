import cloudscraper
import json
import random
import time
import threading
import shareithub
from shareithub import shareithub

shareithub()

# Read proxies from proxy.txt (format: http://ip:port or http://user:pass@ip:port)
proxy_list = []
try:
    with open('proxy.txt', 'r') as file:
        proxy_list = [line.strip() for line in file.readlines() if line.strip()]
except FileNotFoundError:
    print("Warning: proxy.txt not found. Continuing without proxies.")

# Read API Key and URL from account.txt
api_accounts = []
with open('account.txt', 'r') as file:
    for line in file:
        parts = line.strip().split('|')  # Format: API_KEY|API_URL
        if len(parts) == 2:
            api_accounts.append((parts[0], parts[1]))

if not api_accounts:
    print("Error: No valid API Key and URL found in account.txt!")
    exit()

# Read user messages from message.txt
with open('message.txt', 'r') as file:
    user_messages = [msg.strip() for msg in file.readlines() if msg.strip()]

if not user_messages:
    print("Error: No messages found in message.txt!")
    exit()

# Function to select a random proxy
def get_random_proxy():
    if proxy_list:
        proxy = random.choice(proxy_list)
        return {
            'http': proxy,
            'https': proxy
        }
    return None

# Function to create a cloudscraper instance with proxy
def create_scraper():
    scraper = cloudscraper.create_scraper()  # Create instance without proxy argument
    proxies = get_random_proxy()
    if proxies:
        print(f"Using proxy: {proxies['http']}")
        scraper.proxies.update(proxies)  # Set proxies manually
    return scraper

# Function to send request to API
def send_request(message):
    while True:
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
        scraper = create_scraper()
        try:
            response = scraper.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"✅ [SUCCESS] API: {api_url} | Message: '{message}'")
                    print(response_json)
                    break
                except json.JSONDecodeError:
                    print(f"⚠️ [ERROR] Invalid JSON response! API: {api_url}")
                    print(f"Response Text: {response.text}")
            else:
                print(f"⚠️ [ERROR] API: {api_url} | Status: {response.status_code} | Retrying in 2 seconds...")
                time.sleep(2)
        except Exception as e:
            print(f"❌ [REQUEST FAILED] API: {api_url} | Error: {e} | Retrying in 5 seconds...")
            time.sleep(2)

# Function to run thread
def start_thread():
    while True:
        random_message = random.choice(user_messages)
        send_request(random_message)

# Get number of threads from user
try:
    num_threads = int(input("Enter the number of threads you want to use: "))
    if num_threads < 1:
        print("Please enter a number greater than 0.")
        exit()
except ValueError:
    print("Invalid input. Please enter an integer.")
    exit()

# Start multi-threading
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=start_thread, daemon=True)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("All requests have been processed.")

import os
import time
import json
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import requests

app = Flask(__name__)

def load_tokens(filename="data.txt"):
    try:
        with open(filename, "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
            return tokens
    except FileNotFoundError:
        return []

def check_balance(bearer_token):
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    url = "https://gold-eagle-api.fly.dev/user/me/progress"
    for _ in range(30):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"[+] User coins: {data.get('coins_amount', 0)}")
                return True
        except Exception as e:
            print(f"[-] API error: {e}")
        time.sleep(1)
    return False

def setup_driver(bearer_token):
    mobile_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"
    }
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": {"Authorization": f"Bearer {bearer_token}"}})
    return driver

def run_gold_eagle_tapper():
    tokens = load_tokens()
    if not tokens:
        print("[-] No tokens in data.txt")
        return
    bearer_token = tokens[0]

    if not check_balance(bearer_token):
        print("[-] Failed to load user data")
        return

    driver = setup_driver(bearer_token)
    mini_app_url = "https://telegram.geagle.online/#tgWebAppData=query_id=AAG8XExdAAAAALxcTF2ALyef&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212121%22%2C%22button_color%22%3A%22%238774e1%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23aaaaaa%22%2C%22link_color%22%3A%22%238774e1%22%2C%22secondary_bg_color%22%3A%22%23181818%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23212121%22%2C%22accent_text_color%22%3A%22%238774e1%22%2C%22section_bg_color%22%3A%22%23212121%22%2C%22section_header_text_color%22%3A%22%238774e1%22%2C%22subtitle_text_color%22%3A%22%23aaaaaa%22%2C%22destructive_text_color%22%3A%22%23ff595a%22%7D&tgWebAppVersion=7.10&tgWebAppPlatform=ios"
    driver.get(mini_app_url)
    time.sleep(5)

    driver.execute_script("""
        sessionStorage.setItem('tapps/launchParams', 'tgWebAppPlatform=ios&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212121%22%2C%22button_color%22%3A%22%238774e1%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23aaaaaa%22%2C%22link_color%22%3A%22%238774e1%22%2C%22secondary_bg_color%22%3A%22%23181818%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23212121%22%2C%22accent_text_color%22%3A%22%238774e1%22%2C%22section_bg_color%22%3A%22%23212121%22%2C%22section_header_text_color%22%3A%22%238774e1%22%2C%22subtitle_text_color%22%3A%22%23aaaaaa%22%2C%22destructive_text_color%22%3A%22%23ff595a%22%7D&tgWebAppVersion=7.10&tgWebAppData=query_id%3DAAG8XExdAAAAALxcTF2ALyef%26user%3D%257B%2522id%2522%253A1565285564%252C%2522first_name%2522%253A%2522%E6%B0%94DARTON%E4%B9%88%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522username%2522%253A%2522DartonTV%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D');
        sessionStorage.setItem('__telegram__initParams', '{"tgWebAppData":"query_id=AAG8XExdAAAAALxcTF2ALyef&user=%7B%22id%22%3A1565285564%2C%22first_name%22%3A%22%E6%B0%94DARTON%E4%B9%88%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22DartonTV%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https://t.me/i/userpic/320/iy3Hp0CdIo6mZaYfi83EHd7h2nPyXG1Fd5V50-SkD2I.svg%22%7D","auth_date":1741132592,"signature":"sGfdIFxIBcKtqrq2y6zzeUQNkypsglVlaN_LT8s1bp9EbnZVaNiSS7KapQx0llxh0IIjsx926e4oxpOyTPn5DA","hash":"970af2cd5d4ce4b680996870cf21e9762f1d387f096cf9eb1b58366724741d42"}');
        sessionStorage.setItem('__telegram__themeParams', '{"bg_color":"#212121","button_color":"#8774e1","button_text_color":"#ffffff","hint_color":"#aaaaaa","link_color":"#8774e1","secondary_bg_color":"#181818","text_color":"#ffffff","header_bg_color":"#212121","accent_text_color":"

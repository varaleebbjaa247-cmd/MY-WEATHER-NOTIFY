import json
import requests
import os
from datetime import datetime

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_accurate_rain_data(lat, lon):
    # ดึงข้อมูลรายชั่วโมง (hourly) และรายวัน (daily) จาก Open-Meteo
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation_probability&daily=precipitation_sum&timezone=Asia%2FBangkok"
    res = requests.get(url).json()
    
    # 1. [วิธีที่ 1] หา % ฝนตกสูงสุด เฉพาะช่วงเวลา 06:00 - 18:00 น. ของวันนี้
    hourly_probabilities = res["hourly"]["precipitation_probability"][:24] # ข้อมูล 24 ชม. ของวันนี้
    daytime_probabilities = hourly_probabilities[6:19] # ดึงเฉพาะช่วง 06:00 น. ถึง 18:00 น.
    max_daytime_n = max(daytime_probabilities) if daytime_probabilities else 0

    # 2. [วิธีที่ 2] ดึงปริมาณน้ำฝนสะสมรวมของวันนี้ (มิลลิเมตร)
    rain_mm = res["daily"]["precipitation_sum"][0]

    return max_daytime_n, rain_mm

def send_line_messaging_api(message, channel_access_token, user_id):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}, Response: {response.text}")

def main():
    config = load_config()
    threshold = config.get("threshold", 60)
    location_name = config["location"]["name"]
    lat = config["location"]["lat"]
    lon = config["location"]["lon"]

    # ดึงค่า % ฝนช่วงกลางวัน (n) และปริมาณน้ำฝนสะสม (rain_mm)
    n, rain_mm = get_accurate_rain_data(lat, lon)

    # เงื่อนไขรวม: % ฝนช่วงกลางวัน (6:00-18:00) >= threshold AND ปริมาณฝนรวม >= 0.5 มม.
    if n >= threshold and rain_mm >= 0.5:
        msg = f"📍 พื้นที่: {location_name}\nวันนี้ช่วง 06:00-18:00 น. มีโอกาสเกิดฝนสูงสุด {n}%\n(คาดการณ์ปริมาณฝนสะสม {rain_mm} มม.)\nแนะนำให้พกร่มก่อนออกจากบ้านนะครับ ☔"
    else:
        msg = f"📍 พื้นที่: {location_name}\nวันนี้ช่วง 06:00-18:00 น. มีโอกาสเกิดฝน {n}%\nหากจะออกจากบ้านไม่ต้องพกร่มก็ได้ครับ ☀️"

    # รับค่าการตรวจสอบสิทธิ์จาก GitHub Secrets
    line_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.getenv("LINE_USER_ID")

    if line_access_token and line_user_id:
        send_line_messaging_api(msg, line_access_token, line_user_id)
    else:
        print("Error: กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN และ LINE_USER_ID ใน GitHub Secrets")

if __name__ == "__main__":
    main()

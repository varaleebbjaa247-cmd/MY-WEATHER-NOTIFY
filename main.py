import json
import requests
import os

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_rain_probability(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_probability_max&timezone=Asia%2FBangkok"
    res = requests.get(url).json()
    return res["daily"]["precipitation_probability_max"][0]

def send_line_messaging_api(message, channel_access_token, user_id):
    # Endpoint สำหรับส่ง Push Message ตรงถึง User ID
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

    n = get_rain_probability(lat, lon)

    if n >= threshold:
        msg = f"📍 พื้นที่: {location_name}\nวันนี้มีโอกาสเกิดฝน {n}%\nแนะนำให้พกร่มก่อนออกจากบ้านนะครับ ☔"
    else:
        msg = f"📍 พื้นที่: {location_name}\nวันนี้มีโอกาสเกิดฝน {n}%\nหากจะออกจากบ้านไม่ต้องพกร่มก็ได้ครับ ☀️"

    # รับค่าการตรวจสอบสิทธิ์จาก GitHub Secrets
    line_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.getenv("LINE_USER_ID")

    if line_access_token and line_user_id:
        send_line_messaging_api(msg, line_access_token, line_user_id)
    else:
        print(" Error: กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN และ LINE_USER_ID ใน Secrets")

if __name__ == "__main__":
    main()

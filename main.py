import json
import requests
import os

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_rain_probability(lat, lon):
    # ดึงข้อมูลพยากรณ์โอกาสฝนตก (%) จาก Open-Meteo API
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_probability_max&timezone=Asia%2FBangkok"
    res = requests.get(url).json()
    return res["daily"]["precipitation_probability_max"][0]

def send_line_notify(message, token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    requests.post(url, headers=headers, data=data)

def main():
    config = load_config()
    threshold = config.get("threshold", 60)
    location_name = config["location"]["name"]
    lat = config["location"]["lat"]
    lon = config["location"]["lon"]

    # ดึงค่า % ฝนตก (n)
    n = get_rain_probability(lat, lon)

    # สร้างข้อความตามเงื่อนไข
    if n >= threshold:
        msg = f"\n📍 พื้นที่: {location_name}\nวันนี้มีโอกาสเกิดฝน {n}% แนะนำให้พกร่มก่อนออกจากบ้านนะครับ ☔"
    else:
        msg = f"\n📍 พื้นที่: {location_name}\nวันนี้มีโอกาสเกิดฝน {n}% หากจะออกจากบ้านไม่ต้องพกร่มก็ได้ครับ ☀️"

    # รับ Token จาก GitHub Secrets
    line_token = os.getenv("LINE_NOTIFY_TOKEN")
    if line_token:
        send_line_notify(msg, line_token)
        print(f"ส่งข้อความสำเร็จ: {msg}")
    else:
        print("ไม่พบ LINE_NOTIFY_TOKEN")

if __name__ == "__main__":
    main()

import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    "location": "37.586802,127.029906", # 정경대학 입구
    "radius": 300,
    "type": "restaurant",
    "key": GOOGLE_API_KEY,
    "language": "ko"
}

results = []
while True:
    resp = requests.get(url, params=params)
    data = resp.json()
    results.extend(data.get("results", []))
    
    next_page_token = data.get("next_page_token")
    if not next_page_token:
        break
    import time
    time.sleep(2)
    params = {"pagetoken": next_page_token, "key": GOOGLE_API_KEY}

has_price = sum(1 for p in results if 'price_level' in p)
no_price = len(results) - has_price

print(f"Total: {len(results)}")
print(f"Has Price Level: {has_price}")
print(f"No Price Level: {no_price}")

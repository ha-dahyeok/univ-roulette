import os
import requests
import time
import json

# ==========================================
# 1. 환경 변수 수동 로딩 (python-dotenv 없이)
# ==========================================
def load_env():
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error loading .env: {e}")
    return env_vars

env = load_env()
SUPABASE_URL = env.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = env.get('SUPABASE_SERVICE_KEY')
GOOGLE_API_KEY = env.get('GOOGLE_PLACES_API_KEY')

if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, GOOGLE_API_KEY]):
    print("Error: Missing required environment variables.")
    exit(1)

# ==========================================
# 2. Supabase API 헤더 설정 (Service Key 사용)
# ==========================================
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# ==========================================
# 3. 기존 고려대학교 데이터 삭제
# ==========================================
def delete_old_data():
    print("Deleting existing Korea University data from Supabase...")
    # Delete where univ=고려대학교 서울캠퍼스
    delete_url = f"{SUPABASE_URL}/rest/v1/restaurants?univ=eq.고려대학교 서울캠퍼스"
    resp = requests.delete(delete_url, headers=headers)
    if resp.status_code in [200, 204]:
        print("Successfully deleted old data.")
    else:
        print(f"Failed to delete old data: {resp.status_code} - {resp.text}")

# ==========================================
# 4. 가격 및 카테고리 매핑 로직
# ==========================================
def map_price_level(google_price):
    # Google: 0 (Free), 1 (Inexpensive), 2 (Moderate), 3 (Expensive), 4 (Very Expensive)
    # App: 1 (가성비), 2 (보통), 3 (플렉스)
    if google_price is None:
        return 2 # Default to 보통
    if google_price <= 1:
        return 1
    elif google_price == 2:
        return 2
    else:
        return 3

def map_category(types):
    if not types:
        return "식당"
    if "cafe" in types or "bakery" in types:
        return "카페/디저트"
    if "bar" in types or "liquor_store" in types:
        return "술집"
    if "meal_takeaway" in types or "meal_delivery" in types:
        return "포장/배달"
    return "음식점"

# ==========================================
# 5. 구글 맵 API에서 데이터 가져오기
# ==========================================
def fetch_google_places():
    print("Fetching data from Google Maps API...")
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # query: 고려대학교 서울캠퍼스 주변 식당
    params = {
        "query": "고려대학교 서울캠퍼스 맛집",
        "key": GOOGLE_API_KEY,
        "language": "ko"
    }
    
    all_results = []
    
    while True:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if data.get("status") != "OK":
            print(f"Google API Error: {data.get('status')} - {data.get('error_message', '')}")
            break
            
        results = data.get("results", [])
        all_results.extend(results)
        print(f"Fetched {len(results)} places. Total: {len(all_results)}")
        
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
            
        # Google requires a short delay before using the next_page_token
        time.sleep(3)
        params = {
            "pagetoken": next_page_token,
            "key": GOOGLE_API_KEY
        }
        
    return all_results

# ==========================================
# 6. Supabase에 데이터 삽입
# ==========================================
def insert_to_supabase(places):
    print(f"Inserting {len(places)} records into Supabase...")
    
    insert_url = f"{SUPABASE_URL}/rest/v1/restaurants"
    
    payload = []
    for place in places:
        # Check if it's an operational place
        if place.get('business_status') == 'CLOSED_PERMANENTLY':
            continue
            
        # Extract fields
        name = place.get('name', '이름 없음')
        google_price = place.get('price_level')
        app_price = map_price_level(google_price)
        types = place.get('types', [])
        category = map_category(types)
        place_id = place.get('place_id', '')
        
        # We use Google Maps URL with place_id so it opens properly on mobile
        map_url = f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"
        
        # Prepare record matching current schema
        record = {
            "univ": "고려대학교 서울캠퍼스",
            "name": name,
            "category": category,
            "url": map_url,
            "price_level": app_price,
            "distance": 0, # Placeholder
            "user_reports": 0,
            "price_reports": {}
        }
        payload.append(record)
    
    # Bulk insert
    if payload:
        # Supabase bulk insert requires payload to be a list
        resp = requests.post(insert_url, headers=headers, json=payload)
        if resp.status_code in [200, 201]:
            print(f"Successfully inserted {len(payload)} restaurants.")
        else:
            print(f"Failed to insert data: {resp.status_code} - {resp.text}")
    else:
        print("No valid places to insert.")

# ==========================================
# 실행
# ==========================================
if __name__ == "__main__":
    delete_old_data()
    places = fetch_google_places()
    insert_to_supabase(places)
    print("Done!")

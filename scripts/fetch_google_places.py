import os
import requests
import time
import json

# ==========================================
# 0. 설정: 대학교 및 출입구 좌표 (수정 가능)
# ==========================================
# 반경 300m 이내의 식당(type=restaurant)만 검색합니다.
UNIVERSITIES = {
    "서울대학교 관악캠퍼스": {
        "정문": {"lat": 37.4682, "lng": 126.9593},
        "샤로수길 입구": {"lat": 37.4795, "lng": 126.9530},
        "녹두거리(대학동)": {"lat": 37.4688, "lng": 126.9368}
    },
    "고려대학교 서울캠퍼스": {
        "정문": {"lat": 37.5894, "lng": 127.0323},
        "후문": {"lat": 37.5851, "lng": 127.0296},
        "자연계 캠퍼스 입구": {"lat": 37.5833, "lng": 127.0264}
    },
    "연세대학교 신촌캠퍼스": {
        "정문": {"lat": 37.5600, "lng": 126.9369},
        "서문": {"lat": 37.5645, "lng": 126.9304},
        "동문": {"lat": 37.5615, "lng": 126.9429}
    }
}
SEARCH_RADIUS = 300 # 반경 (미터)

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
# 2. Supabase API 헤더 설정
# ==========================================
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# ==========================================
# 3. 기존 데이터 삭제
# ==========================================
def delete_old_data(univ_name):
    print(f"Deleting existing data for {univ_name}...")
    delete_url = f"{SUPABASE_URL}/rest/v1/restaurants?univ=eq.{univ_name}"
    resp = requests.delete(delete_url, headers=headers)
    if resp.status_code not in [200, 204]:
        print(f"Failed to delete old data: {resp.status_code} - {resp.text}")

# ==========================================
# 4. 가격 및 카테고리 매핑 로직
# ==========================================
def map_price_level(google_price):
    if google_price is None:
        return 2 # 보통
    if google_price <= 1:
        return 1 # 가성비
    elif google_price == 2:
        return 2 # 보통
    else:
        return 3 # 플렉스

def map_category(types):
    if not types:
        return "식당"
    # Nearby search with type=restaurant will rarely return cafe/bar primarily,
    # but we map secondary types just in case.
    if "cafe" in types or "bakery" in types:
        return "카페/디저트"
    if "bar" in types or "liquor_store" in types:
        return "술집"
    if "meal_takeaway" in types or "meal_delivery" in types:
        return "포장/배달"
    return "음식점"

# ==========================================
# 5. 구글 맵 API에서 데이터 가져오기 (반경 검색)
# ==========================================
def fetch_nearby_restaurants(lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": SEARCH_RADIUS,
        "type": "restaurant", # 음식점만 엄격히 검색
        "key": GOOGLE_API_KEY,
        "language": "ko"
    }
    
    results = []
    while True:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
            print(f"Google API Error: {data.get('status')} - {data.get('error_message', '')}")
            break
            
        results.extend(data.get("results", []))
        
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
            
        time.sleep(2) # next_page_token 사용을 위한 잠시 대기
        params = {
            "pagetoken": next_page_token,
            "key": GOOGLE_API_KEY
        }
    return results

# ==========================================
# 6. 메인 로직 및 Supabase 삽입
# ==========================================
def process_university(univ_name, gates):
    delete_old_data(univ_name)
    
    places_db = {} # place_id -> data
    
    # 각 출입구별로 검색
    for gate_name, coords in gates.items():
        print(f"[{univ_name}] {gate_name} 주변 식당 검색 중...")
        results = fetch_nearby_restaurants(coords["lat"], coords["lng"])
        
        for place in results:
            if place.get('business_status') == 'CLOSED_PERMANENTLY':
                continue
                
            place_id = place['place_id']
            if place_id not in places_db:
                # 초기 저장
                places_db[place_id] = {
                    "univ": univ_name,
                    "name": place.get('name', '이름 없음'),
                    "category": map_category(place.get('types', [])),
                    "url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}",
                    "price_level": map_price_level(place.get('price_level')),
                    "distance": 0,
                    "user_reports": 0,
                    "price_reports": {},
                    "gates_list": [gate_name] # 내부에서 리스트로 관리
                }
            else:
                # 이미 저장된 식당이라면 현재 출입구도 소속에 추가 (교집합)
                if gate_name not in places_db[place_id]["gates_list"]:
                    places_db[place_id]["gates_list"].append(gate_name)
    
    # DB에 들어갈 Payload 구성
    payload = []
    for place_id, data in places_db.items():
        # gates_list를 콤마로 구분된 문자열 'gates' 필드로 변환하여 저장
        data["gates"] = ",".join(data.pop("gates_list"))
        payload.append(data)
        
    print(f"[{univ_name}] 총 {len(payload)}개의 유니크한 식당 발견. Supabase에 삽입합니다.")
    
    if payload:
        # Supabase 최대 1000개씩 청크 단위로 인서트하는 것이 안전
        insert_url = f"{SUPABASE_URL}/rest/v1/restaurants"
        resp = requests.post(insert_url, headers=headers, json=payload)
        if resp.status_code in [200, 201]:
            print(f"[{univ_name}] 삽입 성공!")
        else:
            print(f"[{univ_name}] 삽입 실패: {resp.status_code} - {resp.text}")

# ==========================================
# 실행
# ==========================================
if __name__ == "__main__":
    for univ_name, gates in UNIVERSITIES.items():
        process_university(univ_name, gates)
    print("All universities processed successfully!")

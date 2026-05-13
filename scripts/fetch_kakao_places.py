import os
import requests
import csv
import urllib.parse
from dotenv import load_dotenv

# ==========================================
# 0. 설정: 대학교 및 출입구 좌표 (수정 가능)
# ==========================================
# 반경 300m 이내의 식당(category_group_code=FD6)만 검색합니다.
# 사용자가 선택한 '옵션 1(상위 15개 가볍게)' 적용: 출입구당 1페이지만 가져옵니다.
UNIVERSITIES = {
    "고려대학교 서울캠퍼스": {
        "정문": {"lat": 37.588259, "lng": 127.034225},
        "법학관 입구": {"lat": 37.591217, "lng": 127.032994},
        "정경대학 입구": {"lat": 37.586802, "lng": 127.029906},
        "자연계캠퍼스 입구": {"lat": 37.586106, "lng": 127.027407},
        "정운오IT교양관 후문": {"lat": 37.584932, "lng": 127.028800},
        "자연계캠퍼스 후문": {"lat": 37.582515, "lng": 127.028167}
    }
}
SEARCH_RADIUS = 300 # 반경 (미터)

# ==========================================
# 1. 환경 변수 수동 로딩
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
KAKAO_API_KEY = env.get('KAKAO_REST_API_KEY')

if not KAKAO_API_KEY:
    print("Error: Missing KAKAO_REST_API_KEY in .env file.")
    exit(1)

headers = {
    "Authorization": f"KakaoAK {KAKAO_API_KEY}"
}

# ==========================================
# 2. 카카오맵 API에서 데이터 가져오기
# ==========================================
def fetch_kakao_restaurants(lat, lng):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    params = {
        "category_group_code": "FD6", # 음식점
        "x": lng, # 카카오는 x가 경도(lng)
        "y": lat, # y가 위도(lat)
        "radius": SEARCH_RADIUS,
        "sort": "accuracy", # 정확도순 (인기순)
        "page": 1,
        "size": 15 # 출입구당 상위 15개만 추출 (옵션 1)
    }
    
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json().get('documents', [])
    else:
        print(f"Kakao API Error: {resp.status_code} - {resp.text}")
        return []

# ==========================================
# 3. 메인 로직 및 CSV 저장
# ==========================================
def process_university():
    places_db = {} # place_id -> data
    
    for univ_name, gates in UNIVERSITIES.items():
        # 각 출입구별로 검색
        for gate_name, coords in gates.items():
            print(f"[{univ_name}] {gate_name} 주변 식당 검색 중...")
            results = fetch_kakao_restaurants(coords["lat"], coords["lng"])
            
            for place in results:
                place_id = place['id']
                place_name = place['place_name']
                
                # 네이버 지도 검색 URL 자동 생성
                encoded_name = urllib.parse.quote(place_name)
                naver_url = f"https://map.naver.com/v5/search/{encoded_name}"
                
                if place_id not in places_db:
                    # 초기 저장
                    places_db[place_id] = {
                        "univ": univ_name,
                        "name": place_name,
                        "category": place.get('category_name', '').split('>')[-1].strip(),
                        "gates_list": [gate_name],
                        "price_level": "", # 사용자가 엑셀에서 수기로 입력할 빈칸
                        "url": naver_url
                    }
                else:
                    # 이미 저장된 식당이라면 현재 출입구도 소속에 추가 (교집합)
                    if gate_name not in places_db[place_id]["gates_list"]:
                        places_db[place_id]["gates_list"].append(gate_name)
    
    # 엑셀(CSV) 저장을 위한 리스트 변환
    payload = []
    for place_id, data in places_db.items():
        data["gates"] = ",".join(data.pop("gates_list"))
        payload.append(data)
        
    print(f"\n총 {len(payload)}개의 유니크한 식당 발견! 엑셀 파일(CSV)로 추출합니다.")
    
    # CSV 저장 (엑셀 한글 깨짐 방지를 위해 utf-8-sig 사용)
    csv_filename = "restaurants_data.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['univ', 'name', 'category', 'gates', 'price_level', 'url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload)
        
    print(f"완료! '{csv_filename}' 파일이 생성되었습니다. 엑셀로 열어주세요.")

if __name__ == "__main__":
    process_university()

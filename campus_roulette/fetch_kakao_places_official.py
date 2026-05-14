import requests
import csv
import time
import os

# 0. 설정: 대학교 및 출입구 좌표
GATES = [
    {"name": "정문", "lat": 37.588259, "lng": 127.034225}, # Updated coordinates to be more precise based on previous scripts
    {"name": "법학관 입구", "lat": 37.591217, "lng": 127.032994},
    {"name": "정경대학 입구", "lat": 37.586802, "lng": 127.029906},
    {"name": "자연계캠퍼스 입구", "lat": 37.586106, "lng": 127.027407},
    {"name": "정운오IT교양관 후문,자연계캠퍼스 후문", "lat": 37.584932, "lng": 127.028800},
]

CSV_PATH = 'c:/Ha_dahyeok/2026_NEXT_CONTEST/korea_univ_restaurants.csv'
SEARCH_RADIUS = 300

def load_env():
    env_vars = {}
    try:
        with open('c:/Ha_dahyeok/2026_NEXT_CONTEST/.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Error: .env file not found.")
    return env_vars

def get_existing_names():
    existing = set()
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2 and row[1] != 'name' and row[1].strip():
                    existing.add(row[1])
    except FileNotFoundError:
        pass
    return existing

def is_banned(category):
    banned = ['술집', '호프', '요리주점', '주점', '포장마차', '바', '유흥', '카페', '커피전문점', '다방', '제과', '베이커리']
    for b in banned:
        if b in category:
            return True
    return False

def main():
    env_vars = load_env()
    kakao_key = env_vars.get('KAKAO_REST_API_KEY')
    if not kakao_key:
        print("Error: KAKAO_REST_API_KEY not found in .env")
        return

    headers = {
        'Authorization': f'KakaoAK {kakao_key}'
    }

    existing = get_existing_names()
    new_rows = []
    
    # Empty separator before appending
    new_rows.append([",,,,,"])
    
    total_added = 0
    for gate in GATES:
        print(f"Fetching restaurants near {gate['name']}...")
        count = 0
        
        # 카카오 공식 API는 한 페이지당 15개, 최대 3페이지(45개) 제공
        for page in range(1, 4):
            url = f"https://dapi.kakao.com/v2/local/search/category.json?category_group_code=FD6&x={gate['lng']}&y={gate['lat']}&radius={SEARCH_RADIUS}&page={page}"
            try:
                res = requests.get(url, headers=headers)
                data = res.json()
                
                places = data.get('documents', [])
                if not places:
                    break
                    
                for p in places:
                    name = p.get('place_name')
                    category = p.get('category_name', '')
                    url_link = p.get('place_url')
                    
                    # Remove trailing branches for deduplication
                    clean_name = name.replace(" 안암점", "").replace(" 고대점", "").replace(" 본점", "").replace(" 안암본점", "")
                    
                    if name in existing or clean_name in existing:
                        continue
                        
                    if is_banned(category):
                        continue
                        
                    # Format: univ,name,category,gates,price_level,url
                    # Category from Kakao usually looks like "음식점 > 한식 > 국밥" -> we extract the second/third part
                    cat_parts = category.split(' > ')
                    short_cat = cat_parts[-1] if len(cat_parts) > 1 else category
                    
                    row = ["고려대학교 서울캠퍼스", name, short_cat, gate['name'], "", url_link]
                    new_rows.append(row)
                    existing.add(name)
                    existing.add(clean_name)
                    count += 1
                    
                    if count >= 10: # limit to 10 unique good places per gate
                        break
                        
                if count >= 10:
                    break
                    
            except Exception as e:
                print(f"Error fetching data: {e}")
            time.sleep(0.2)
            
        print(f" -> Added {count} new restaurants for {gate['name']}")
        total_added += count

    if total_added > 0:
        with open(CSV_PATH, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for row in new_rows:
                if row == [",,,,,"]:
                    f.write(",,,,,\n")
                else:
                    writer.writerow(row)
        print(f"\nSuccessfully appended {total_added} total new places to {CSV_PATH}.")
    else:
        print("No new unique places found to append.")

if __name__ == "__main__":
    main()

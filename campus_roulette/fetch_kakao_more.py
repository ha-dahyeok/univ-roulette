import requests
import csv
import time

GATES = [
    {"name": "정문", "lat": 37.588259, "lng": 127.034225},
    {"name": "법학관 입구", "lat": 37.591217, "lng": 127.032994},
    {"name": "정경대학 입구", "lat": 37.586802, "lng": 127.029906},
    {"name": "자연계캠퍼스 입구", "lat": 37.586106, "lng": 127.027407},
    {"name": "정운오IT교양관 후문,자연계캠퍼스 후문", "lat": 37.584932, "lng": 127.028800},
]

CSV_PATH = 'c:/Ha_dahyeok/2026_NEXT_CONTEST/korea_univ_restaurants.csv'
SEARCH_RADIUS = 300

# Pre-defined known prices for Anam restaurants (Level 1 <= 12k, Level 2 = 12k-20k, Level 3 >= 20k)
# Gukbap/Tonkatsu/Kimbap/Fastfood usually 1. Meat/Sashimi/Dining usually 2 or 3.
KNOWN_PRICES = {
    '고래돈까스': '1',
    '마이셰프': '1',
    '이공김밥 안암본점': '1',
    '야마토텐동': '1',
    '용초수': '1',
    '미각': '1',
    '백소정 안암본점': '1',
    '칠백집': '2',
    '고려대 미각 본점': '1',
    '영철버거': '1',
    '동우설렁탕': '1',
    '토담': '1',
    '고른햇살': '1',
    '오거리콩나물국밥': '1',
    '정만빙수': '', # Cafe but if it slips through
    '아비꼬 고려대안암점': '1',
    '애정마라샹궈 안암점': '2',
    '춘자': '1',
    '신포우리만두 안암점': '1',
    '서기치킨': '2',
    '두찜 고려대점': '2',
    '해장국': '1',
    '특별식당': '1',
    '서울쌈냉면 고대점': '1',
    '우정초밥': '3', # Premium Omakase
    '마늘과올리브': '2',
    '야끼도리 찬': '2',
    '은화수식당 고대안암점': '1',
    '일미통닭': '2',
    '삼성통닭': '2',
    '신안동찜닭': '2',
    '미스터피자 고대점': '2',
    '수유리우동집 고대점': '1',
    '봉구스밥버거 고려대점': '1',
    '한솥도시락 고대안암점': '1',
    '버거킹 안암오거리점': '1',
    '맥도날드 고대점': '1',
    '맘스터치 안암점': '1',
    '서브웨이 안암점': '1',
    '서브웨이 고려대점': '1',
    '싸다김밥 고대안암점': '1',
    '마라탕': '1',
}

def load_env():
    env_vars = {}
    try:
        with open('c:/Ha_dahyeok/2026_NEXT_CONTEST/.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
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

def determine_price(name, category):
    # Check strict mapping
    if name in KNOWN_PRICES:
        return KNOWN_PRICES[name]
    
    # Check partial mappings for common chains or very clear categories
    if '국밥' in name or '국수' in name or '김밥' in name or '버거' in name or '도시락' in name or '떡볶이' in name:
        return '1'
    if '고기' in name or '삼겹' in name or '갈비' in name or '횟집' in name or '수산' in name or '참치' in name:
        return '2'
    if '오마카세' in name:
        return '3'
        
    return '' # Unknown

def main():
    env_vars = load_env()
    kakao_key = env_vars.get('KAKAO_REST_API_KEY')
    headers = {'Authorization': f'KakaoAK {kakao_key}'}

    existing = get_existing_names()
    new_rows = []
    
    new_rows.append([",,,,,"])
    
    total_added = 0
    for gate in GATES:
        print(f"Fetching more restaurants near {gate['name']}...")
        count = 0
        
        # Go deeper up to page 10 (150 places) to get more distinct ones
        for page in range(1, 11):
            url = f"https://dapi.kakao.com/v2/local/search/category.json?category_group_code=FD6&x={gate['lng']}&y={gate['lat']}&radius={SEARCH_RADIUS}&page={page}"
            try:
                res = requests.get(url, headers=headers)
                data = res.json()
                places = data.get('documents', [])
                if not places:
                    break # No more pages
                    
                for p in places:
                    name = p.get('place_name')
                    category = p.get('category_name', '')
                    url_link = p.get('place_url')
                    
                    clean_name = name.replace(" 안암점", "").replace(" 고대점", "").replace(" 본점", "").replace(" 안암본점", "")
                    if name in existing or clean_name in existing:
                        continue
                    if is_banned(category):
                        continue
                        
                    cat_parts = category.split(' > ')
                    short_cat = cat_parts[-1] if len(cat_parts) > 1 else category
                    
                    price = determine_price(name, short_cat)
                    
                    row = ["고려대학교 서울캠퍼스", name, short_cat, gate['name'], price, url_link]
                    new_rows.append(row)
                    existing.add(name)
                    existing.add(clean_name)
                    count += 1
                    
                    if count >= 20: # Fetch 20 more per gate
                        break
                        
                if count >= 20:
                    break
                    
            except Exception as e:
                pass
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
        print("No new unique places found.")

if __name__ == "__main__":
    main()

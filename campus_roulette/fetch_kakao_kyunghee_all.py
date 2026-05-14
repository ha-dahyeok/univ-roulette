import requests
import csv
import time

GATES = [
    {"name": "정문", "lat": 37.593623, "lng": 127.052674},
    {"name": "법학관 후문", "lat": 37.598090, "lng": 127.054121},
    {"name": "의과대학 입구", "lat": 37.598090, "lng": 127.054121}
]

CSV_PATH = 'c:/Ha_dahyeok/2026_NEXT_CONTEST/kyunghee_restaurants.csv'
SEARCH_RADIUS = 300

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

def is_banned(category, name):
    banned = ['술집', '호프', '요리주점', '주점', '포장마차', '바', '유흥', '카페', '커피전문점', '다방', '제과', '베이커리', '떡집', '아이스크림', '디저트']
    for b in banned:
        if b in category:
            return True
    
    if '떡방' in name or '카페' in name or '커피' in name or '노래' in name or '주점' in name or '호프' in name or '맥주' in name:
        return True
    return False

def determine_price(name, category):
    level2_keywords = ['고기', '갈비', '삼겹', '소곱창', '대창', '막창', '치킨', '통닭', '참치', '수산', '횟집', '찜닭', '샤브', '훠궈', '양꼬치', '장어', '아구찜', '해물찜', '스테이크', '양식', '파스타', '이탈리안']
    level3_keywords = ['오마카세', '파인다이닝', '우마카세', '한우', '아웃백']
    level1_keywords = ['국밥', '국수', '김밥', '도시락', '떡볶이', '분식', '버거', '샌드위치', '토스트', '백반', '짬뽕', '짜장', '우동', '마라탕', '마라샹궈', '돈까스', '돈가스', '칼국수', '라멘', '케밥']
    
    for k in level3_keywords:
        if k in name or k in category:
            return '3'
    for k in level2_keywords:
        if k in name or k in category:
            return '2'
    for k in level1_keywords:
        if k in name or k in category:
            return '1'
            
    if category in ['중식', '분식', '패스트푸드', '도시락', '치킨,닭강정']:
        return '1'
        
    return '2'

def main():
    env_vars = load_env()
    kakao_key = env_vars.get('KAKAO_REST_API_KEY')
    headers = {'Authorization': f'KakaoAK {kakao_key}'}

    # Initialize CSV header if not exists
    try:
        with open(CSV_PATH, 'x', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['univ', 'name', 'category', 'gates', 'price_level', 'url'])
    except FileExistsError:
        pass

    existing = get_existing_names()
    new_rows = []
    total_added = 0
    urls_seen = set()

    for gate in GATES:
        print(f"Fetching exhaustive restaurants near {gate['name']}...")
        count = 0
        
        for page in range(1, 46):
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
                    
                    if url_link in urls_seen:
                        continue
                    urls_seen.add(url_link)

                    clean_name = name.replace(" 경희대점", "").replace(" 회기점", "").replace(" 본점", "")
                    if name in existing or clean_name in existing:
                        continue
                    if is_banned(category, name):
                        continue
                        
                    cat_parts = category.split(' > ')
                    short_cat = cat_parts[-1] if len(cat_parts) > 1 else category
                    
                    price = determine_price(name, short_cat)
                    
                    row = ["경희대학교 서울캠퍼스", name, short_cat, gate['name'], price, url_link]
                    new_rows.append(row)
                    existing.add(name)
                    existing.add(clean_name)
                    count += 1
                    
                if data.get('meta', {}).get('is_end'):
                    break
                    
            except Exception as e:
                pass
            time.sleep(0.1)
            
        print(f" -> Exhaustively added {count} new restaurants for {gate['name']}")
        total_added += count

    if total_added > 0:
        with open(CSV_PATH, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(new_rows)
        print(f"\nSuccessfully appended {total_added} total new places to {CSV_PATH}.")
    else:
        print("No new unique places found.")

if __name__ == "__main__":
    main()

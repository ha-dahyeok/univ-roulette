import requests
import re
import json
import csv
import time

GATES = [
    {"name": "정문", "lat": 37.5894, "lng": 127.0323},
    {"name": "법학관 입구", "lat": 37.5910, "lng": 127.0340},
    {"name": "정경대학 입구", "lat": 37.5862, "lng": 127.0290},
    {"name": "자연계캠퍼스 입구", "lat": 37.5855, "lng": 127.0300},
    {"name": "정운오IT교양관 후문,자연계캠퍼스 후문", "lat": 37.5830, "lng": 127.0305},
]

CSV_PATH = 'c:/Ha_dahyeok/2026_NEXT_CONTEST/korea_univ_restaurants.csv'

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

def fetch_places_around(lat, lng, query="맛집", max_pages=3):
    headers = {'Referer': 'https://map.kakao.com/', 'User-Agent': 'Mozilla/5.0'}
    all_places = []
    
    for page in range(1, max_pages + 1):
        url = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery&q={query}&radius=300&location={lat},{lng}&msFlag=A&sort=0&page={page}"
        try:
            res = requests.get(url, headers=headers)
            match = re.search(r'jQuery\((.*)\)', res.text)
            if match:
                data = json.loads(match.group(1))
                places = data.get('place', [])
                if not places:
                    break
                all_places.extend(places)
        except Exception as e:
            print(f"Error fetching data: {e}")
        time.sleep(0.5)
    return all_places

def is_banned(category):
    banned = ['술집', '호프', '주점', '포장마차', '바', '유흥', '카페', '커피전문점', '다방', '제과', '베이커리']
    for b in banned:
        if b in category:
            return True
    return False

def main():
    existing = get_existing_names()
    new_rows = []
    
    # Empty separator before appending
    new_rows.append([",,,,,"])
    
    total_added = 0
    for gate in GATES:
        print(f"Fetching restaurants near {gate['name']}...")
        places = fetch_places_around(gate['lat'], gate['lng'])
        
        count = 0
        for p in places:
            name = p.get('name')
            confirmid = p.get('confirmid')
            category = p.get('subcategory', '')
            
            if not name or not confirmid:
                continue
            
            clean_name = name.replace(" 안암점", "").replace(" 고대점", "").replace(" 본점", "").replace(" 안암본점", "")
            
            if name in existing or clean_name in existing:
                continue
                
            if is_banned(category):
                continue
                
            url = f"https://place.map.kakao.com/{confirmid}"
            row = ["고려대학교 서울캠퍼스", name, category, gate['name'], "", url]
            new_rows.append(row)
            existing.add(name)
            existing.add(clean_name)
            count += 1
            
            if count >= 10: # Add up to 10 *unique* new restaurants per gate
                break
                
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

import os
import csv
import requests
import time
from dotenv import load_dotenv

load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")

if not KAKAO_API_KEY:
    print("Error: Missing KAKAO_REST_API_KEY in .env file.")
    exit(1)

headers = {
    "Authorization": f"KakaoAK {KAKAO_API_KEY}"
}

def get_place_url(name, univ_prefix):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    query = f"{univ_prefix} {name}"
    params = {
        "query": query,
        "size": 1
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            docs = resp.json().get('documents', [])
            if docs:
                return docs[0].get('place_url')
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        
    return None

def process_file(file_path, univ_prefix):
    print(f"[{file_path}] 처리 중...")
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None: fieldnames = []
        rows = list(reader)
        
    updated_count = 0
    for row in rows:
        name = row.get('name', '')
        if not name:
            continue
            
        print(f"검색 중: {name} ... ", end="")
        place_url = get_place_url(name, univ_prefix)
        
        if place_url:
            row['url'] = place_url
            print(f"성공! ({place_url})")
            updated_count += 1
        else:
            # 실패 시 기존 URL 유지
            print("실패 (기존 URL 유지)")
            
        time.sleep(0.1) # 카카오 API Rate Limit 방지
        
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"[{file_path}] URL 업데이트 완료 (총 {updated_count}개 갱신)\n")

if __name__ == "__main__":
    process_file('yonsei_restaurants.csv', '신촌')
    process_file('korea_univ_restaurants.csv', '안암')

import requests
def check_kakao_place(query):
    # 1. Search place
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    headers = {'Authorization': 'KakaoAK e5ba2b9169d648e73a93e941931bae93'}
    res = requests.get(url, params={'query': query}, headers=headers).json()
    if not res.get('documents'):
        print(f"Not found: {query}")
        return
    place_id = res['documents'][0]['id']
    name = res['documents'][0]['place_name']
    
    # 2. Extract real menu
    detail_url = f"https://place.map.kakao.com/main/v/{place_id}"
    headers_req = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://place.map.kakao.com/'}
    detail_res = requests.get(detail_url, headers=headers_req)
    if detail_res.status_code != 200 or not detail_res.text.startswith('{'):
        import sys
        print(f"Error getting json: {detail_res.text[:200]}")
        sys.exit(1)
    detail_res = detail_res.json()
    
    print(f"[{name}] (ID: {place_id})")
    
    if 'menuInfo' in detail_res and 'menuList' in detail_res['menuInfo']:
        menus = detail_res['menuInfo']['menuList']
        print("--- Menu List ---")
        for m in menus[:5]:
            print(f"- {m.get('menu', '')}: {m.get('price', 'No Price')}")
    else:
        print("No menu info found")

check_kakao_place("신촌 달링스테이크")
check_kakao_place("회기 홍곱창")
check_kakao_place("안암 고른햇살")

import requests
import re
import json

def search_kakao(query):
    url = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery&q={query}&msFlag=A&sort=0"
    headers = {
        'Referer': 'https://map.kakao.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    res = requests.get(url, headers=headers)
    text = res.text
    match = re.search(r'jQuery\((.*)\)', text)
    if match:
        data = json.loads(match.group(1))
        places = data.get('place', [])
        if places:
            p = places[0]
            print(f"Found: {p.get('name')} / ID: {p.get('confirmid')} / Address: {p.get('address')}")
            return p.get('confirmid')
    print(f"[{query}] Not found")
    return None

search_kakao('고려대 동우설렁탕')
search_kakao('고려대 지오파스타')
search_kakao('고려대 무르무르 드 구스토')
search_kakao('고려대 일곱평')

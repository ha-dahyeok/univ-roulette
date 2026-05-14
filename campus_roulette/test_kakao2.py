import requests
import re
import json

def search(query):
    url = f'https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery&q={query}&msFlag=A&sort=0'
    headers = {'Referer': 'https://map.kakao.com/', 'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    match = re.search(r'jQuery\((.*)\)', res.text)
    if match:
        data = json.loads(match.group(1))
        places = data.get('place', [])
        if places:
            print(f"[{query}] Found: {places[0]['name']} / {places[0]['address']}")
            return
    print(f"[{query}] NOT FOUND")

search('고려대 매스플레이트')
search('안암 매스플레이트')
search('매스플레이트 안암점')
search('고려대 일미통닭')
search('안암 일미통닭')
search('고려대 전주식당')
search('안암 전주식당')
search('안암 마사')

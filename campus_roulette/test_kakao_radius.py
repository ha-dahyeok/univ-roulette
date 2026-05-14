import requests
import re
import json

lat = 37.5862
lng = 127.0290

url = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery&q=맛집&radius=300&location={lat},{lng}&msFlag=A&sort=0"
headers = {'Referer': 'https://map.kakao.com/', 'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
match = re.search(r'jQuery\((.*)\)', res.text)
if match:
    data = json.loads(match.group(1))
    places = data.get('place', [])
    for p in places[:5]:
        print(f"Found: {p.get('name')} / {p.get('address')} / {p.get('confirmid')}")

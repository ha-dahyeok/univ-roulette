import requests
import json
import csv

CSV_PATH = 'c:/Ha_dahyeok/2026_NEXT_CONTEST/korea_univ_restaurants.csv'
existing = set()
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    for row in csv.reader(f):
        if len(row) > 1: existing.add(row[1])

headers = {'Authorization': 'KakaoAK e5ba2b9169d648e73a93e941931bae93'}
url = "https://dapi.kakao.com/v2/local/search/category.json?category_group_code=FD6&x=127.029906&y=37.586802&radius=300&page=2"
res = requests.get(url, headers=headers)
places = res.json().get('documents', [])
for p in places:
    name = p['place_name']
    cat = p['category_name']
    clean_name = name.replace(' 안암점', '')
    print(f"{name} ({cat}): Existing={name in existing or clean_name in existing}")

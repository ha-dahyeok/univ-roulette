import requests

def get_coords(query):
    key = 'AIzaSyB7SQ9_KVNF5M9SXsBksmQww7qDJ8Top1k'
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    resp = requests.get(url, params={'query': query, 'key': key, 'language': 'ko'})
    data = resp.json()
    if data['status'] == 'OK' and len(data['results']) > 0:
        loc = data['results'][0]['geometry']['location']
        print(f"{query}: {loc['lat']}, {loc['lng']}")
    else:
        print(f"{query}: Not found")

get_coords('고려대학교 서울캠퍼스 정문')
get_coords('고려대학교 안암캠퍼스 후문')
get_coords('고려대학교 이공대 입구')
get_coords('고려대학교 안암병원')

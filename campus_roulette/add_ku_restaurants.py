import requests
import json

url = "https://yyvhukmxifjtabcmwolj.supabase.co/rest/v1/restaurants"
headers = {
    "apikey": "sb_publishable_vD0jOojh1AwquZvEKUD1gw_T9v8Y1Hy",
    "Authorization": "Bearer sb_publishable_vD0jOojh1AwquZvEKUD1gw_T9v8Y1Hy",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Fetch existing to avoid duplicates
existing_res = requests.get(url + "?select=name", headers=headers)
existing_names = set([r['name'] for r in existing_res.json()])

new_restaurants = [
    # 정문
    {"univ": "고려대학교 서울캠퍼스", "name": "동우설렁탕", "category": "설렁탕", "gates": "정문", "price_level": 1, "url": "https://place.map.kakao.com/11267433"},
    {"univ": "고려대학교 서울캠퍼스", "name": "대성집", "category": "육류,고기", "gates": "정문", "price_level": 2, "url": "https://place.map.kakao.com/15291402"},
    {"univ": "고려대학교 서울캠퍼스", "name": "일미통닭", "category": "치킨", "gates": "정문", "price_level": 2, "url": "https://place.map.kakao.com/10901511"},
    {"univ": "고려대학교 서울캠퍼스", "name": "일곱평", "category": "이탈리안", "gates": "정문", "price_level": None, "url": "https://place.map.kakao.com/1784964645"},
    {"univ": "고려대학교 서울캠퍼스", "name": "마늘과올리브", "category": "이탈리안", "gates": "정문,법학관 입구", "price_level": 2, "url": "https://place.map.kakao.com/17154569"},
    {"univ": "고려대학교 서울캠퍼스", "name": "끄티식당", "category": "일식", "gates": "정문", "price_level": 1, "url": "https://place.map.kakao.com/621115858"},
    {"univ": "고려대학교 서울캠퍼스", "name": "우정초밥", "category": "초밥", "gates": "정문", "price_level": 3, "url": "https://place.map.kakao.com/1445761358"},
    {"univ": "고려대학교 서울캠퍼스", "name": "황적", "category": "육류,고기", "gates": "정문", "price_level": 2, "url": "https://place.map.kakao.com/1407632617"},

    # 법학관 입구
    {"univ": "고려대학교 서울캠퍼스", "name": "공주칼국수", "category": "칼국수", "gates": "법학관 입구", "price_level": 1, "url": "https://place.map.kakao.com/11629851"},
    {"univ": "고려대학교 서울캠퍼스", "name": "호만두", "category": "분식", "gates": "법학관 입구", "price_level": 1, "url": "https://place.map.kakao.com/16147294"},
    {"univ": "고려대학교 서울캠퍼스", "name": "전주식당", "category": "백반", "gates": "법학관 입구", "price_level": 1, "url": "https://place.map.kakao.com/14605927"},
    {"univ": "고려대학교 서울캠퍼스", "name": "칠백집", "category": "육류,고기", "gates": "법학관 입구", "price_level": 2, "url": "https://place.map.kakao.com/26425330"},
    {"univ": "고려대학교 서울캠퍼스", "name": "지오파스타", "category": "이탈리안", "gates": "법학관 입구", "price_level": None, "url": "https://place.map.kakao.com/12971217"},
    {"univ": "고려대학교 서울캠퍼스", "name": "모심", "category": "백반", "gates": "법학관 입구", "price_level": 1, "url": "https://place.map.kakao.com/10986754"},

    # 정경대학 입구 (참살이길)
    {"univ": "고려대학교 서울캠퍼스", "name": "고른햇살", "category": "분식", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/16669931"},
    {"univ": "고려대학교 서울캠퍼스", "name": "영철버거", "category": "햄버거", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/10531557"},
    {"univ": "고려대학교 서울캠퍼스", "name": "특별식당", "category": "일식", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/832873133"},
    {"univ": "고려대학교 서울캠퍼스", "name": "무르무르 드 구스토", "category": "양식", "gates": "정경대학 입구", "price_level": 3, "url": "https://place.map.kakao.com/26500779"},
    {"univ": "고려대학교 서울캠퍼스", "name": "용초수", "category": "중식", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/14470940"},
    {"univ": "고려대학교 서울캠퍼스", "name": "비야", "category": "부대찌개", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/11186716"},
    {"univ": "고려대학교 서울캠퍼스", "name": "이세돈까스", "category": "돈까스", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/15296839"},
    {"univ": "고려대학교 서울캠퍼스", "name": "비나레스토랑", "category": "아시아음식", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/9748680"},
    {"univ": "고려대학교 서울캠퍼스", "name": "어흥식당", "category": "스테이크", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/476906560"},
    {"univ": "고려대학교 서울캠퍼스", "name": "삼성통닭", "category": "치킨", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/11267425"},
    {"univ": "고려대학교 서울캠퍼스", "name": "백소정 안암점", "category": "일식", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/488825227"},
    {"univ": "고려대학교 서울캠퍼스", "name": "쿠이도라쿠", "category": "일식", "gates": "정경대학 입구,자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/10901518"},
    {"univ": "고려대학교 서울캠퍼스", "name": "유자유 김치떡볶이", "category": "분식", "gates": "정경대학 입구", "price_level": 1, "url": "https://place.map.kakao.com/16180373"},
    {"univ": "고려대학교 서울캠퍼스", "name": "오샬", "category": "아시아음식", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/12963065"},
    {"univ": "고려대학교 서울캠퍼스", "name": "마사", "category": "양식", "gates": "정경대학 입구", "price_level": None, "url": "https://place.map.kakao.com/11186718"},
    {"univ": "고려대학교 서울캠퍼스", "name": "철판남", "category": "일식", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/26456093"},
    {"univ": "고려대학교 서울캠퍼스", "name": "한잔의추억", "category": "술집", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/10531558"},
    {"univ": "고려대학교 서울캠퍼스", "name": "발리다포차", "category": "술집", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/1647895240"},
    {"univ": "고려대학교 서울캠퍼스", "name": "매스플레이트", "category": "이탈리안", "gates": "정경대학 입구", "price_level": None, "url": "https://place.map.kakao.com/21469550"},
    {"univ": "고려대학교 서울캠퍼스", "name": "미각", "category": "중식", "gates": "정경대학 입구", "price_level": 2, "url": "https://place.map.kakao.com/23758362"},

    # 자연계캠퍼스 입구 (안암역 주변)
    {"univ": "고려대학교 서울캠퍼스", "name": "애기능식당", "category": "한식", "gates": "자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/16499318"},
    {"univ": "고려대학교 서울캠퍼스", "name": "서병장대김일병", "category": "한식", "gates": "자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/11186715"},
    {"univ": "고려대학교 서울캠퍼스", "name": "탄", "category": "일식", "gates": "자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/11186717"},
    {"univ": "고려대학교 서울캠퍼스", "name": "가야가야", "category": "일식", "gates": "자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/11186719"},
    {"univ": "고려대학교 서울캠퍼스", "name": "은화수식당", "category": "경양식", "gates": "자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/11186720"},
    {"univ": "고려대학교 서울캠퍼스", "name": "춘자", "category": "술집", "gates": "자연계캠퍼스 입구", "price_level": 1, "url": "https://place.map.kakao.com/11186721"},

    # 정운오IT교양관 후문 / 자연계캠퍼스 후문 (안암오거리)
    {"univ": "고려대학교 서울캠퍼스", "name": "미스터국밥", "category": "국밥", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186722"},
    {"univ": "고려대학교 서울캠퍼스", "name": "뽀뽀분식", "category": "분식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186723"},
    {"univ": "고려대학교 서울캠퍼스", "name": "서울쌈냉면", "category": "한식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186724"},
    {"univ": "고려대학교 서울캠퍼스", "name": "형제집", "category": "육류,고기", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186725"},
    {"univ": "고려대학교 서울캠퍼스", "name": "언니네반점", "category": "중식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186726"},
    {"univ": "고려대학교 서울캠퍼스", "name": "칠기마라탕", "category": "중식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186727"},
    {"univ": "고려대학교 서울캠퍼스", "name": "수해복마라탕", "category": "중식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 1, "url": "https://place.map.kakao.com/11186728"},
    {"univ": "고려대학교 서울캠퍼스", "name": "제주고깃집", "category": "육류,고기", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 2, "url": "https://place.map.kakao.com/11186729"},
    {"univ": "고려대학교 서울캠퍼스", "name": "한성양꼬치", "category": "중식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": 2, "url": "https://place.map.kakao.com/11186730"},
    {"univ": "고려대학교 서울캠퍼스", "name": "신마라명장", "category": "중식", "gates": "정운오IT교양관 후문,자연계캠퍼스 후문", "price_level": None, "url": "https://place.map.kakao.com/11186731"},
    {"univ": "고려대학교 서울캠퍼스", "name": "야마토텐동", "category": "일식", "gates": "정경대학 입구", "price_level": None, "url": "https://place.map.kakao.com/11186732"},
]

to_insert = []
for r in new_restaurants:
    if r['name'] not in existing_names:
        r['distance'] = 150 # arbitrary radius inside 300m
        to_insert.append(r)

if to_insert:
    res = requests.post(url, headers=headers, json=to_insert)
    print(f"Inserted {len(to_insert)} records. Status: {res.status_code}")
else:
    print("No new records to insert.")

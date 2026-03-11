import requests
import json
import time
import os
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
if not KAKAO_API_KEY:
    print("⚠️ KAKAO_API_KEY 가 .env 파일에 설정되지 않았습니다.")

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 
    return c * r * 1000

KOREAN_UNIVS = [
    "가천대학교 (글로벌)", "가천대학교 (메디컬)", "가톨릭대학교 (성심)", "가톨릭대학교 (성의)", "가톨릭대학교 (성신)",
    "강원대학교 (춘천)", "강원대학교 (삼척)", "건국대학교 (서울)", "건국대학교 (글로컬)", "경기대학교 (수원)", "경기대학교 (서울)",
    "경북대학교 (대구)", "경북대학교 (상주)", "경상국립대학교", "경희대학교 (서울)", "경희대학교 (국제)", 
    "계명대학교 (성서)", "계명대학교 (대명)", "고려대학교 (서울)", "고려대학교 (세종)", "광운대학교", 
    "국민대학교", "단국대학교 (죽전)", "단국대학교 (천안)", "대구가톨릭대학교", "대구대학교", 
    "동국대학교 (서울)", "동국대학교 (WISE)", "동아대학교 (승학)", "동아대학교 (부민)", "동아대학교 (구덕)",
    "명지대학교 (인문)", "명지대학교 (자연)", "부경대학교 (대연)", "부경대학교 (용당)", "부산대학교 (부산)", "부산대학교 (밀양)", "부산대학교 (양산)",
    "서강대학교", "서울과학기술대학교", "서울대학교 (관악)", "서울대학교 (연건)", "서울시립대학교", 
    "성균관대학교 (인문사회과학)", "성균관대학교 (자연과학)", "성신여자대학교 (돈암)", "성신여자대학교 (미아)", 
    "세종대학교", "숙명여자대학교", "숭실대학교", "아주대학교", 
    "연세대학교 (신촌)", "연세대학교 (미래)", "연세대학교 (국제)", "영남대학교", "원광대학교",
    "이화여자대학교", "인천대학교", "인하대학교", 
    "전남대학교 (광주)", "전남대학교 (여수)", "전북대학교 (전주)", "전북대학교 (특성화)", "제주대학교", 
    "조선대학교", "중앙대학교 (서울)", "중앙대학교 (다빈치)", 
    "충남대학교 (대덕)", "충남대학교 (보운)", "충북대학교 (개신)", "충북대학교 (오송)", 
    "한국공학대학교", "한국외국어대학교 (서울)", "한국외국어대학교 (글로벌)", "한국항공대학교", 
    "한남대학교", "한림대학교", "한양대학교 (서울)", "한양대학교 (ERICA)", "홍익대학교 (서울)", "홍익대학교 (세종)",
    "카이스트 (KAIST)", "포스텍 (POSTECH)", "유니스 (UNIST)", "지스트 (GIST)", "디지스트 (DGIST)"
]

def estimate_price_level(category_name, restaurant_name):
    cat = category_name.strip().lower()
    name = restaurant_name.strip().lower()
    cheap_keywords = ['분식', '김밥', '떡볶이', '순대', '튀김', '만두', '라면', '국수', '우동', '모밀', '토스트', '샌드위치', '핫도그', '햄버거', '패스트푸드', '도시락', '컵밥', '한식뷔페', '기사식당', '백반', '정식', '국밥', '해장국', '순대국', '콩나물국밥', '짜장', '짬뽕', '중식', '중화요리', '치킨', '닭강정', '피자', '베이커리', '제과', '샐러드']
    expensive_keywords = ['소고기', '한우', '갈비', '불고기', '스테이크', '오마카세', '코스', '다이닝', '파인다이닝', '레스토랑', '이탈리안', '프랑스', '유럽', '와인', '랍스타', '킹크랩', '참치', '사시미', '일식회', '스시', '초밥', '한정식', '장어', '오리', '염소', '양고기', '양꼬치', '곱창', '대창', '막창', '뷔페', '파스타', '화로구이', '랍스터']
    if any(keyword in cat or keyword in name for keyword in cheap_keywords): return 1
    if any(keyword in cat or keyword in name for keyword in expensive_keywords): return 3
    return 2

def make_kakao_query(univ_name):
    if '(' in univ_name:
        main, camp = univ_name.split('(')
        main = main.strip()
        camp = camp.replace(')', '').strip()
        if camp == '서울': return main
        if camp == '연건': return f"{main} 연건캠퍼스"
        if camp == 'ERICA': return f"{main} ERICA"
        if camp == '특성화': return f"{main} 특성화캠퍼스"
        return f"{main} {camp}캠퍼스"
    return univ_name

def process_univ(univ_name):
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    query_univ = make_kakao_query(univ_name)
    
    # Needs central coordinate to calculate distance
    center_coord = None
    try:
        c_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={univ_name}&size=1"
        res = requests.get(c_url, headers=headers, timeout=5)
        if res.status_code == 200 and res.json().get('documents'):
            doc = res.json()['documents'][0]
            center_coord = (float(doc['x']), float(doc['y']))
    except: pass
    
    anchor_coords = []
    search_radius = 1000
    is_fallback = False

    if center_coord:
        cx, cy = center_coord
        
        # Step 1: Strict query with full campus name
        anchors_strict = [f"{query_univ} 입구", f"{query_univ} 정문", f"{query_univ} 후문"]
        for a_query in anchors_strict:
            try:
                u_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={a_query}&size=1"
                res = requests.get(u_url, headers=headers, timeout=5)
                if res.status_code == 200 and res.json().get('documents'):
                    doc = res.json()['documents'][0]
                    if doc['place_name'].strip() != query_univ: # Don't just get center again
                        gx, gy = float(doc['x']), float(doc['y'])
                        if haversine(cx, cy, gx, gy) <= 1200: # Final safety check
                            anchor_coords.append((gx, gy))
            except: pass

        # Step 2: Flexible positive query (e.g. "[Univ]대 정문")
        if not anchor_coords:
            base_univ = univ_name.split(' (')[0].split()[0]
            anchors_flex = []
            if base_univ.endswith("대학교"):
                short_base = base_univ.replace("대학교", "대")
                anchors_flex.extend([f"{short_base} 정문", f"{short_base} 입구", f"{base_univ} 정문", f"{base_univ} 입구"])
            elif base_univ.endswith("과대학교"):
                short_base = base_univ.replace("과대학교", "공대")
                anchors_flex.extend([f"{short_base} 정문", f"{short_base} 입구", f"{base_univ} 정문", f"{base_univ} 입구"])
            else:
                anchors_flex.extend([f"{base_univ} 정문", f"{base_univ} 입구"])

            for a_query in anchors_flex:
                try:
                    u_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={a_query}&size=3"
                    res = requests.get(u_url, headers=headers, timeout=5)
                    if res.status_code == 200 and res.json().get('documents'):
                        for doc in res.json()['documents']:
                            p_name = doc['place_name']
                            gx, gy = float(doc['x']), float(doc['y'])
                            
                            # 1. 1차 관문: 장소 이름에 해당 대학교 이름이 무조건 포함되어 있어야 함
                            has_univ_name = (base_univ in p_name)
                            if 'short_base' in locals() and short_base in p_name:
                                has_univ_name = True
                                
                            if not has_univ_name:
                                continue # 대학교 이름 자체가 없으면 바로 버림 (예: 반도보라아파트)

                            # 2. 2차 관문 & 3차 구명조끼
                            if haversine(cx, cy, gx, gy) <= 1200:
                                if not any(bad in p_name for bad in ['아파트', '빌리지', '원룸', '상가', '어린이집', '유치원']):
                                    anchor_coords.append((gx, gy))
                except: pass

    unique_coords = list(set(anchor_coords))
    
    # Step 3: Fallback if everything failed (or if center_coord failed to fetch initially)
    if not unique_coords:
        if center_coord:
            unique_coords = [center_coord]
            search_radius = 1500
            is_fallback = True
        else:
            return {"results": [], "fallback": False}

    univ_results = []
    local_seen = set()
    
    for u_x, u_y in unique_coords:
        # 1. Categorical Search (FD6 - Food)
        # 2. Broad Keyword Search ("음식점", "식당") to handle miscategorized places
        queries = [
            ("category", {"category_group_code": "FD6"}),
            ("keyword", {"query": "음식점"}),
            ("keyword", {"query": "식당"})
        ]
        
        for q_type, q_params in queries:
            for page in range(1, 4):
                if q_type == "category":
                    url = f"https://dapi.kakao.com/v2/local/search/category.json?category_group_code={q_params['category_group_code']}&x={u_x}&y={u_y}&radius={search_radius}&page={page}&size=15"
                else:
                    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={q_params['query']}&x={u_x}&y={u_y}&radius={search_radius}&page={page}&size=15"
                
                try:
                    res = requests.get(url, headers=headers, timeout=5)
                    if res.status_code != 200: break
                    docs = res.json().get('documents', [])
                    if not docs: break
                    for doc in docs:
                        pid = doc.get('id')
                        # Ensure it's a food place if using keyword search
                        if q_type == "keyword":
                            cat_full = doc.get('category_name', '')
                            if '음식점' not in cat_full and '카페' not in cat_full: # Accept basic food categories
                                continue
                        
                        if pid and pid not in local_seen:
                            category = doc['category_name'].split('>')[-1].strip()
                            name = doc['place_name']
                            univ_results.append({
                                "id": pid,
                                "univ": univ_name,
                                "name": name,
                                "category": category,
                                "url": doc['place_url'],
                                "price_level": estimate_price_level(category, name),
                                "distance": int(doc.get('distance', 0)) if doc.get('distance') else 0,
                                "user_reports": 0
                            })
                            local_seen.add(pid)
                except: break
    print(f"✅ {univ_name} 완료 ({len(univ_results)}개)", flush=True)
    return {"results": univ_results, "fallback": is_fallback}

def build_database():
    db_file = 'restaurant_db.json'
    all_data = []
    global_seen = set()
    fallback_univs = []
    
    print(f"🚀 전국 {len(KOREAN_UNIVS)}개 대학교 주변 맛집 최적화 수집을 시작합니다 (Dual-Search 1000m/1500m)...", flush=True)
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(process_univ, univ): univ for univ in KOREAN_UNIVS}
        for future in as_completed(futures):
            try:
                out = future.result()
                univ_name = futures[future]
                if out.get('fallback'):
                    fallback_univs.append(univ_name)
                    
                for r in out.get('results', []):
                    # Deduplicate by URL as a safe unique identifier
                    if r['url'] not in global_seen:
                        r.pop('id', None)
                        all_data.append(r)
                        global_seen.add(r['url'])
                
                # Intermediate save
                with open(db_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"❌ Error processing future: {e}")

    print(f"\n🎉 수집 완료! 총 {len(all_data)}개의 맛집이 '{db_file}'에 저장되었습니다.")
    print("\n--- 1500m 반경이 적용된 대학교 목록 (Fallback) ---")
    for fu in sorted(fallback_univs):
        print(f" - {fu}")

if __name__ == '__main__':
    build_database()
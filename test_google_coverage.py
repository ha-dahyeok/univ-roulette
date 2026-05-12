import json
import os
import random
import requests
import time
from dotenv import load_dotenv

def check_coverage(sample_size=100):
    load_dotenv()
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not GOOGLE_PLACES_API_KEY:
        print("❌ Error: GOOGLE_PLACES_API_KEY 가 .env 파일에 설정되지 않았습니다.")
        print("무료 크레딧이 있는 구글 클라우드 API 키를 발급받아주세요.")
        return

    try:
        with open('restaurant_db.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return

    # 대학교 이름 등 불필요한 검색어 오염 방지를 위해 랜덤 샘플링 
    sampled_data = random.sample(data, min(sample_size, len(data)))
    
    total_found_in_google = 0
    total_with_price = 0
    
    print(f"🚀 {sample_size}개의 카카오맵 식당 데이터로 구글맵 price_level 응답률(Coverage) 테스트 시작...\n")
    
    for idx, restaurant in enumerate(sampled_data):
        name = restaurant.get('name', '')
        univ = restaurant.get('univ', '')
        # 구글에서 정확도 높이기 위해 "대학교이름 상호명"으로 검색
        query = f"{univ} {name}"
        
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GOOGLE_PLACES_API_KEY}"
        
        try:
            res = requests.get(url, timeout=5)
            res_data = res.json()
            
            if res_data.get('status') == 'OK' and len(res_data.get('results', [])) > 0:
                total_found_in_google += 1
                first_result = res_data['results'][0]
                
                if 'price_level' in first_result:
                    total_with_price += 1
                    print(f"[{idx+1}/{sample_size}] ✅ {name} -> price_level: {first_result['price_level']}")
                else:
                    print(f"[{idx+1}/{sample_size}] ⚠️ {name} -> 구글맵에 존재하나 price_level 없음(Null)")
            else:
                print(f"[{idx+1}/{sample_size}] ❌ {name} -> 구글맵 검색 실패(등록되지 않음)")
                
        except Exception as e:
            print(f"API 에러: {e}")
            
        time.sleep(0.5) # 구글 API Rate Limit(초당 요청 수) 보호
        
    print("\n" + "="*40)
    print("📊 [ 테스트 분석 결과 ]")
    print(f"- 카카오 기반 원본 샘플: {sample_size}개")
    print(f"- 구글맵에서 식당 자체를 찾은 비율: {total_found_in_google}/{sample_size} ({(total_found_in_google/sample_size)*100:.1f}%)")
    print(f"- ⭐ 그 중 price_level 가격 정보가 존재하는 비율: {total_with_price}/{sample_size} ({(total_with_price/sample_size)*100:.1f}%)")
    if total_found_in_google > 0:
        print(f"- (구글맵에 있는 식당 중 가격 정보가 있는 확률: {(total_with_price/total_found_in_google)*100:.1f}%)")
    print("="*40)

if __name__ == "__main__":
    check_coverage(100)

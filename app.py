from flask import Flask, render_template, request, jsonify
import os
import time
from collections import defaultdict
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 보안 2: 간단한 IP 기반 Rate Limiting (봇 공격 방어)
request_history = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 20  # 제보 요청 한도 (엄격)
SEARCH_MAX_REQUESTS_PER_MINUTE = 100  # 검색 요청 한도 (여유)

def is_rate_limited(ip, limit_type='report'):
    now = time.time()
    cache_key = f"{ip}_{limit_type}"
    request_history[cache_key] = [t for t in request_history[cache_key] if now - t < 60]
    
    limit = SEARCH_MAX_REQUESTS_PER_MINUTE if limit_type == 'search' else MAX_REQUESTS_PER_MINUTE
    if len(request_history[cache_key]) >= limit:
        return True
    request_history[cache_key].append(now)
    return False

@app.after_request
def apply_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sw.js')
def serve_sw():
    return app.send_static_file('sw.js')

@app.route('/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json')

@app.route('/search')
def search():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    if is_rate_limited(client_ip, limit_type='search'):
        return jsonify({'error': '너무 많은 검색 요청이 발생했습니다. 1분 후에 다시 시도해주세요.'}), 429
        
    univ = request.args.get('univ')
    try:
        target_price_level = int(request.args.get('target_price_level', 0))
    except (ValueError, TypeError):
        target_price_level = 0
    
    # Supabase에서 실시간 검색
    try:
        query = supabase.table("restaurants").select("*")
        if univ:
            query = query.eq("univ", univ)
        if target_price_level != 0:
            query = query.eq("price_level", target_price_level)
        
        response = query.execute()
        restaurant_data = response.data
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({'error': '데이터베이스 조회 중 오류가 발생했습니다.'}), 500
    
    filtered_results = []
    for doc in restaurant_data:
        result_doc = dict(doc)
        result_doc['place_name'] = doc['name']
        result_doc['category_name'] = f"음식점 > {doc['category']}"
        result_doc['place_url'] = doc['url']
        filtered_results.append(result_doc)
                
    return jsonify(filtered_results)

@app.route('/report_price', methods=['POST'])
def report_price():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
        
    if is_rate_limited(client_ip, limit_type='report'):
        return jsonify({'success': False, 'message': '너무 많은 요청이 발생했습니다. 1분 후에 다시 시도해주세요.'}), 429

    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'})
        
    name = data.get('restaurant_name')
    try:
        new_price_level = int(data.get('suggested_price_level'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid price format'})

    try:
        # 즉각 반영 로직
        response = supabase.table("restaurants").update({
            "price_level": new_price_level
        }).eq("name", name).execute()
        
        if response.data:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '식당을 찾을 수 없습니다.'})
            
    except Exception as e:
        print(f"DB Update Error: {e}")
        return jsonify({'success': False, 'message': '데이터베이스 업데이트 중 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=False, port=port)
from flask import Flask, render_template, request, jsonify
import json
import os
import threading
import time
from collections import defaultdict

app = Flask(__name__)
db_lock = threading.Lock()

DB_PATH = 'restaurant_db.json'
restaurant_data = []

# 보안 1: DB 메모리 캐싱 (동시 접속자 대비 하드디스크 I/O 최소화)
def load_db():
    global restaurant_data
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            restaurant_data = json.load(f)

load_db()

# 보안 2: 간단한 IP 기반 Rate Limiting (봇 공격 방어)
request_history = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 5

def is_rate_limited(ip):
    now = time.time()
    # 1분(60초) 지난 기록 지우기
    request_history[ip] = [t for t in request_history[ip] if now - t < 60]
    if len(request_history[ip]) >= MAX_REQUESTS_PER_MINUTE:
        return True
    request_history[ip].append(now)
    return False

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
    univ = request.args.get('univ')
    try:
        target_price_level = int(request.args.get('target_price_level', 0))
    except (ValueError, TypeError):
        target_price_level = 0
    
    filtered_results = []
    
    # 캐시된 메모리 데이터에서 초고속 검색
    for doc in restaurant_data:
        if doc.get('univ') == univ:
            if target_price_level == 0 or doc.get('price_level', 3) == target_price_level:
                # dict 복사본에 포맷팅해서 전달 (원본 훼손 방지)
                result_doc = dict(doc)
                result_doc['place_name'] = doc['name']
                result_doc['category_name'] = f"음식점 > {doc['category']}"
                result_doc['place_url'] = doc['url']
                filtered_results.append(result_doc)
                
    return jsonify(filtered_results)

@app.route('/report_price', methods=['POST'])
def report_price():
    # 봇(Bot) 무차별 제보 방어
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({'success': False, 'message': '너무 많은 요청이 발생했습니다. 1분 후에 다시 시도해주세요.'}), 429

    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'})
        
    name = data.get('restaurant_name')
    try:
        new_price_level = int(data.get('suggested_price_level'))
        if new_price_level not in [1, 2, 3]:
            return jsonify({'success': False, 'message': 'Invalid price level'})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid price format'})
    
    updated = False
    
    with db_lock:
        for doc in restaurant_data:
            if doc.get('name') == name:
                # 보안 3: 신뢰성 확보 (제보 횟수가 3회 누적되어야 실제 가격대 변경)
                # 우선 제보 카운트만 수집
                reports = doc.get('price_reports', {})
                level_str = str(new_price_level)
                reports[level_str] = reports.get(level_str, 0) + 1
                doc['price_reports'] = reports
                doc['user_reports'] = doc.get('user_reports', 0) + 1
                
                # 특정 가격대 제보가 3회 이상 쌓이면 실제 가격대 변경!
                if reports[level_str] >= 3:
                    doc['price_level'] = new_price_level
                    # 누적 후 초기화
                    doc['price_reports'] = {}
                    
                updated = True
                break
                
        if updated:
            with open(DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(restaurant_data, f, ensure_ascii=False, indent=4)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Restaurant not found'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False, port=5000)
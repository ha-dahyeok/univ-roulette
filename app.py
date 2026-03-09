from flask import Flask, render_template, request, jsonify
import json
import os
import threading

app = Flask(__name__)
db_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    univ = request.args.get('univ')
    try:
        target_price_level = int(request.args.get('target_price_level', 0))
    except ValueError:
        target_price_level = 0
    
    db_path = 'restaurant_db.json'
    if not os.path.exists(db_path):
        return jsonify([])
        
    with open(db_path, 'r', encoding='utf-8') as f:
        all_results = json.load(f)
        
    filtered_results = []
    
    for doc in all_results:
        # 1. 대학 이름이 일치하는지 확인
        if doc.get('univ') == univ:
            # 2. 가격 범주 필터링 (0이면 전체, 아니면 정확히 일치)
            if target_price_level == 0 or doc.get('price_level', 3) == target_price_level:
                # 3. 프론트엔드가 기존 카카오 API 응답 형태를 기대하므로 필드명 매핑
                doc['place_name'] = doc['name']
                doc['category_name'] = f"음식점 > {doc['category']}"
                doc['place_url'] = doc['url']
                filtered_results.append(doc)
                
    return jsonify(filtered_results)

@app.route('/report_price', methods=['POST'])
def report_price():
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
    
    db_path = 'restaurant_db.json'
    if not os.path.exists(db_path):
        return jsonify({'success': False, 'message': 'DB not found'})
        
    with db_lock:
        with open(db_path, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
            
        updated = False
        for doc in all_results:
            # 상호명으로 식당 탐색
            if doc.get('name') == name:
                doc['user_reports'] = doc.get('user_reports', 0) + 1
                # 프로토타입: 제보가 들어오면 즉시 해당 등급으로 변경 반영
                doc['price_level'] = new_price_level
                updated = True
                break
                
        if updated:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=4)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Restaurant not found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
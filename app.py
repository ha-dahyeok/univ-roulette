from flask import Flask, render_template, request, jsonify
import os
import subprocess
import threading
import re
import sys
import time
from typing import Any
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Rate Limiter 설정
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri="memory://"
)

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL") or ""
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.after_request
def apply_security_headers(response):
    """보안 강화를 위한 HTTP 헤더 설정"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.route('/')
def index():
    return render_template('index.html')

# PWA 지원을 위한 서비스 워커 및 매니페스트 제공
@app.route('/sw.js')
def serve_sw():
    response = app.send_static_file('sw.js')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/manifest.json')
def serve_manifest():
    response = app.send_static_file('manifest.json')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/search')
@limiter.limit("100 per minute")
def search():
    """대학교 및 가격대별 식당 검색"""
    univ = request.args.get('univ')
    try:
        target_price_level = int(request.args.get('target_price_level', 0))
    except (ValueError, TypeError):
        target_price_level = 0
    
    try:
        if not univ:
            return jsonify({'error': '대학교 이름이 필요합니다.'}), 400
            
        query = supabase.table("restaurants").select("*").eq("univ", univ)
        
        if target_price_level != 0:
            query = query.eq("price_level", target_price_level)
        
        response = query.execute()
        # 타입 안전성을 위해 명시적으로 빈 리스트 처리
        restaurant_data = response.data if response.data else []
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({'error': '데이터베이스 조회 중 오류가 발생했습니다.'}), 500
    
    filtered_results = []
    for doc in restaurant_data:
        # doc이 dict임을 보장하고 안전하게 필드 추출 (Any 캐스팅으로 Pyright의 잘못된 bytes 추론 방지)
        item: Any = doc
        
        # 기본 필드 추출 (안전을 위해 dict 체크 포함)
        is_dict = isinstance(item, dict)
        name = item.get('name', '이름 없음') if is_dict else '이름 없음'
        category = item.get('category', '기타') if is_dict else '기타'
        url = item.get('url', '#') if is_dict else '#'
        
        result: dict[str, Any] = {
            'place_name': str(name),
            'category_name': f"음식점 > {str(category)}",
            'place_url': str(url)
        }
        
        # 나머지 모든 원본 필드 포함
        if is_dict:
            for k, v in item.items():
                if k not in ['name', 'category', 'url']:
                    result[str(k)] = v
        
        filtered_results.append(result)
                
    return jsonify(filtered_results)

@app.route('/report_price', methods=['POST'])
@limiter.limit("20 per minute", error_message='너무 많은 요청이 발생했습니다. 1분 후에 다시 시도해주세요.')
def report_price():
    """사용자의 가격 변동 제보 반영"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON'})
        
    name = data.get('restaurant_name')
    try:
        new_price_level = int(data.get('suggested_price_level'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid price format'})

    try:
        response = supabase.table("restaurants").update({
            "price_level": new_price_level
        }).eq("name", name if name else "").execute()
        
        if response.data:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '식당을 찾을 수 없습니다.'})
            
    except Exception as e:
        print(f"DB Update Error: {e}")
        return jsonify({'success': False, 'message': '데이터베이스 업데이트 중 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    # 배포 환경(Render 등) 감지
    if os.environ.get("PORT") or os.environ.get("RENDER"):
        app.run(host='0.0.0.0', debug=False, port=port)
    else:
        # 로컬 개발 환경: 자동 재시작 및 Cloudflare 터널 자동 실행
        def start_tunnel():
            cloudflared_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloudflared.exe')
            if not os.path.exists(cloudflared_path):
                return
            
            for _ in range(3): # 재시도 횟수 축소
                try:
                    process = subprocess.Popen(
                        [cloudflared_path, 'tunnel', '--url', f'http://localhost:{port}'],
                        stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding='utf-8'
                    )
                    start_time = time.time()
                    if process.stderr:
                        for line in process.stderr:
                            if time.time() - start_time > 20:
                                break
                            if 'trycloudflare.com' in line:
                                match = re.search(r'(https://\S+\.trycloudflare\.com)', line)
                                if match:
                                    print(f" * Tunnel URL: {match.group(1)}")
                                    sys.stdout.flush()
                                    return
                    process.kill()
                    time.sleep(5)
                except Exception:
                    pass
            print(" * Tunnel: 연결 실패 (Cloudflare API 응답 없음)")
            sys.stdout.flush()

        # 리로더 메인 프로세스에서만 터널 실행
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            threading.Thread(target=start_tunnel, daemon=True).start()
        
        app.run(host='127.0.0.1', debug=True, port=port)
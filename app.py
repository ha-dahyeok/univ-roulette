from flask import Flask, render_template, request, jsonify
import os
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
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
@limiter.limit("20 per minute", error_message='너무 많은 요청이 발생했습니다. 1분 후에 다시 시도해주세요.')
def report_price():
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
    
    # 클라우드 배포 환경(Render 등)에서는 터널 없이 실행
    if os.environ.get("PORT"):
        app.run(host='0.0.0.0', debug=False, port=port)
    else:
        # 로컬 개발: Cloudflare 터널 자동 실행
        import subprocess
        import threading
        import re
        import sys
        import time

        def start_tunnel():
            cloudflared_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloudflared.exe')
            if not os.path.exists(cloudflared_path):
                return
            
            for _ in range(5):
                try:
                    process = subprocess.Popen(
                        [cloudflared_path, 'tunnel', '--url', f'http://localhost:{port}'],
                        stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True
                    )
                    start_time = time.time()
                    for line in process.stderr:
                        if time.time() - start_time > 30:
                            break
                        if 'trycloudflare.com' in line:
                            match = re.search(r'(https://\S+\.trycloudflare\.com)', line)
                            if match:
                                print(f" * Tunnel: {match.group(1)}")
                                sys.stdout.flush()
                                for line in process.stderr:
                                    pass
                                return
                    process.kill()
                    time.sleep(10)
                except Exception:
                    pass
            print(" * Tunnel: 연결 실패 (Cloudflare API 장애)")
            sys.stdout.flush()

        tunnel_thread = threading.Thread(target=start_tunnel, daemon=True)
        tunnel_thread.start()
        
        app.run(host='127.0.0.1', debug=False, port=port)
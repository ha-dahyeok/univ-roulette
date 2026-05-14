import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경 변수 로드
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") # 관리자 권한이 있는 서비스 키 사용

if not SUPABASE_URL or not SUPABASE_KEY:
    print("오류: .env 파일에 SUPABASE_URL 또는 SUPABASE_SERVICE_KEY가 없습니다.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_csv(file_path):
    if not os.path.exists(file_path):
        print(f"경고: {file_path} 파일이 존재하지 않습니다. 스킵합니다.")
        return
        
    print(f"[{file_path}] 데이터 읽는 중...")
    payload = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 빈 줄이나 빈 데이터는 스킵
            if not row.get('name') or not row.get('price_level'):
                continue
            
            # price_level을 숫자로 변환
            try:
                row['price_level'] = int(row['price_level'])
            except ValueError:
                continue # 가격 레벨이 숫자가 아니면 스킵
                
            payload.append(row)
            
    if not payload:
        print(f"[{file_path}] 업로드할 유효한 데이터가 없습니다.")
        return
        
    print(f"[{file_path}] DB에 업로드 중... ({len(payload)}개)")
    try:
        data, count = supabase.table('restaurants').insert(payload).execute()
        print(f"[{file_path}] 업로드 완료!")
    except Exception as e:
        print(f"업로드 에러: {e}")

def main():
    # 1. 기존 데이터 모두 삭제 (초기화)
    print("기존 Supabase 데이터를 모두 삭제합니다...")
    try:
        # univ가 null이 아닌 모든 행을 지우는 방식으로 전체 삭제
        supabase.table('restaurants').delete().neq('univ', 'none').execute()
        print("초기화 완료!")
    except Exception as e:
        print(f"초기화 에러: {e}")
        return

    # 2. 새로운 CSV 데이터 업로드
    upload_csv('yonsei_restaurants.csv')
    upload_csv('korea_univ_restaurants.csv')
    
    print("\n🎉 모든 데이터가 성공적으로 Supabase에 동기화되었습니다!")

if __name__ == "__main__":
    main()

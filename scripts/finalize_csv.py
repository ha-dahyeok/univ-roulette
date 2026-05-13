import csv
from collections import defaultdict

csv_filename = 'restaurants_data.csv'

# 1. 지울 식당 목록
delete_keywords = ['대성집', '두부촌', '보배곱창', '유정식당', '형제집', '홍도야빈대떡']

rows = []
fieldnames = []

with open(csv_filename, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        # 빈 줄 무시
        if not any(row.values()):
            continue
            
        name = row['name']
        
        # 지울 식당인지 확인
        should_delete = False
        for kw in delete_keywords:
            if kw in name:
                should_delete = True
                break
                
        if not should_delete:
            rows.append(row)

# 2. 가나다 순 정렬
rows.sort(key=lambda x: x['name'])

# 3. 출입구 및 가격대별 개수 계산
# 딕셔너리 구조: counts[gate][price_level] = count
counts = defaultdict(lambda: defaultdict(int))

for row in rows:
    gates = [g.strip() for g in row['gates'].split(',') if g.strip()]
    price = row['price_level'].strip()
    
    # 만약 가격이 비어있는게 있다면 무시하거나 카운트
    if not price:
        price = '미정'
        
    for gate in gates:
        counts[gate][price] += 1

# 4. 파일 덮어쓰기
with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# 5. 결과 분석 출력
print(f"작업 완료! {len(delete_keywords)}개 식당을 삭제하고, 총 {len(rows)}개의 식당을 가나다순으로 정렬했습니다.\n")

print("--- ⚠️ 검색 결과가 10개 이하인 위험 구간 (게이트 + 가격대) ---")
warning_found = False

for gate, price_counts in counts.items():
    for price, count in price_counts.items():
        if count <= 10:
            print(f"[{gate}] 출입구 - [{price}단계]: {count}개 식당")
            warning_found = True

if not warning_found:
    print("다행히 모든 출입구와 가격대 조합에서 10개 초과의 식당이 확보되어 있습니다!")
    

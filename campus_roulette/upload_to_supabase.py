import os
import requests
import csv

def load_env():
    env_vars = {}
    try:
        with open('c:/Ha_dahyeok/2026_NEXT_CONTEST/.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env_vars

def main():
    env_vars = load_env()
    supabase_url = env_vars.get('SUPABASE_URL')
    service_key = env_vars.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        print("Supabase credentials not found in .env")
        return

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    url = f"{supabase_url}/rest/v1/restaurants"

    # 1. Delete all existing records
    print("Deleting existing records in Supabase...")
    del_res = requests.delete(url + "?id=gt.0", headers=headers)
    print(f"Delete response: {del_res.status_code}")

    # 2. Read CSVs
    csv_files = [
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/korea_univ_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/yonsei_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/konkuk_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/hongik_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/hanyang_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/sogang_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/inha_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/cau_restaurants.csv',
        'c:/Ha_dahyeok/2026_NEXT_CONTEST/kyunghee_restaurants.csv'
    ]
    
    payload = []
    for cf in csv_files:
        with open(cf, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if len(row) >= 5 and row[0].strip() and row[0] != ',,,,,':
                    univ = row[0].strip()
                    name = row[1].strip()
                    category = row[2].strip()
                    gates = row[3].strip()
                    price = row[4].strip()
                    link = row[5].strip() if len(row) > 5 else ""
                    
                    if not name or not price:
                        continue # Skip empty or missing price
                        
                    payload.append({
                        "univ": univ,
                        "name": name,
                        "category": category,
                        "gates": gates,
                        "price_level": int(price),
                        "url": link
                    })

    # 3. Insert new records in batches
    print(f"Uploading {len(payload)} records to Supabase...")
    batch_size = 50
    for i in range(0, len(payload), batch_size):
        batch = payload[i:i+batch_size]
        post_res = requests.post(url, headers=headers, json=batch)
        if post_res.status_code not in (200, 201):
            print(f"Error on batch {i}: {post_res.status_code} {post_res.text}")
        else:
            print(f"Uploaded batch {i} to {i+len(batch)}")

    print("Supabase update complete.")

if __name__ == "__main__":
    main()

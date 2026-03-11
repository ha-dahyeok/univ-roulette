import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

supabase: Client = create_client(url, key)

def migrate():
    # 1. Load data from JSON
    if not os.path.exists('restaurant_db.json'):
        print("❌ Error: restaurant_db.json not found.")
        return

    with open('restaurant_db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"🚀 Starting migration of {len(data)} records to Supabase...")

    # 2. Upload in batches (to avoid request limits)
    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        # Prepare data (match Supabase column names)
        # Assuming table name is 'restaurants'
        # We use 'upsert' to avoid duplicates if rerun
        try:
            response = supabase.table("restaurants").upsert(batch).execute()
            print(f"✅ Uploaded batch {i//batch_size + 1} ({min(i+batch_size, len(data))}/{len(data)})")
        except Exception as e:
            print(f"❌ Error uploading batch: {e}")
            break

    print("🎉 Migration completed!")

if __name__ == "__main__":
    migrate()

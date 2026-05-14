import csv
import requests
import re
import json
import time

def search_kakao(query):
    url = f"https://search.map.kakao.com/mapsearch/map.daum?callback=jQuery&q={query}&msFlag=A&sort=0"
    headers = {
        'Referer': 'https://map.kakao.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        res = requests.get(url, headers=headers)
        match = re.search(r'jQuery\((.*)\)', res.text)
        if match:
            data = json.loads(match.group(1))
            places = data.get('place', [])
            if places:
                p = places[0] # Take the top result
                # Make sure the name roughly matches or it's in the same area
                # Sometimes closed places aren't returned and it returns a random place
                return p.get('confirmid'), p.get('name')
    except Exception as e:
        print(f"Error searching {query}: {e}")
    return None, None

input_file = 'c:/Ha_dahyeok/2026_NEXT_CONTEST/korea_univ_restaurants.csv'

lines = []
not_found = []

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader, None)
    if header:
        lines.append(header)
    
    for row in reader:
        if len(row) < 3:
            lines.append(row)
            continue
            
        # Check if it's our target (e.g. newly added ones or existing ones)
        # We will check all of them to be safe
        univ = row[0]
        name = row[1]
        
        # Don't search empty rows or separator rows like ,,,,,
        if not name.strip():
            lines.append(row)
            continue
            
        # Skip searching if name is just 'name' or row is a separator
        if name == 'name':
            lines.append(row)
            continue

        query = f"고려대 {name}"
        if "연세대학교" in univ:
            query = f"연세대 {name}"
            
        print(f"Searching: {query}...")
        confirmid, found_name = search_kakao(query)
        
        if confirmid:
            # Reconstruct the row with new URL
            row[5] = f"https://place.map.kakao.com/{confirmid}"
            lines.append(row)
            print(f" -> Found: {found_name} ({confirmid})")
        else:
            print(f" -> NOT FOUND! Removing {name}.")
            not_found.append(name)
            
        time.sleep(0.2) # be polite to the API

with open(input_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(lines)

print("\n--- Summary ---")
print(f"Total updated: {len(lines)}")
print(f"Total removed (Not Found or Closed): {len(not_found)}")
print(f"Removed restaurants: {', '.join(not_found)}")

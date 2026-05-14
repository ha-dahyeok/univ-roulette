import csv

def process_file(filename):
    # Read the file
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            fieldnames = []
        rows = list(reader)

    # Filter out empty rows (like the visual separator we added earlier)
    # and filter out rows where price_level is empty (the ones to delete)
    filtered_rows = [r for r in rows if r.get('name') and r.get('price_level', '').strip() != '']

    # Sort: first by price_level (1, 2, 3), then by name (가나다순)
    # Cast price_level to int for sorting just in case, though string sort is fine for "1","2","3"
    filtered_rows.sort(key=lambda x: (int(x['price_level']), x['name']))

    # Write back with blank lines separating price levels
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        current_level = None
        for row in filtered_rows:
            level = row['price_level']
            # If the level changes (e.g., from 1 to 2) and it's not the first item, insert a blank row
            if current_level is not None and level != current_level:
                # write an empty row
                writer.writerow({k: '' for k in fieldnames})
            
            writer.writerow(row)
            current_level = level

if __name__ == "__main__":
    process_file('yonsei_restaurants.csv')
    process_file('korea_univ_restaurants.csv')
    print("정렬 및 분리 완료!")

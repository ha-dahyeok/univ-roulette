import requests
import json
from collections import defaultdict

url = "https://yyvhukmxifjtabcmwolj.supabase.co/rest/v1/restaurants?select=*"
headers = {
    "apikey": "sb_publishable_vD0jOojh1AwquZvEKUD1gw_T9v8Y1Hy",
    "Authorization": "Bearer sb_publishable_vD0jOojh1AwquZvEKUD1gw_T9v8Y1Hy"
}

response = requests.get(url, headers=headers)
data = response.json()

univ_gates = {
    '고려대학교 서울캠퍼스': ['정문', '법학관 입구', '정경대학 입구', '자연계캠퍼스 입구', '정운오IT교양관 후문', '자연계캠퍼스 후문'],
    '연세대학교 신촌캠퍼스': ['정문', '서문', '동문', '북문']
}

budget_names = {
    1: "가성비",
    2: "보통",
    3: "플렉스"
}

results = {}
for univ, gates in univ_gates.items():
    results[univ] = []
    for gate in gates:
        for budget in [1, 2, 3]:
            count = 0
            for r in data:
                if r.get('univ') == univ and r.get('price_level') == budget:
                    gates_str = r.get('gates') or ""
                    if gate in gates_str:
                        count += 1
            if count < 10:
                results[univ].append({"gate": gate, "budget": budget_names[budget], "count": count})

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

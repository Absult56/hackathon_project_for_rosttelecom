# parse_excel.py - Update initial_data.json from Excel data
import json
json_path = 'backend/data/initial_data.json'

with open(json_path, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Update companies is_white_spot to False for IDs 8-54
for company in data['companies']:
    if 8 <= company.get('id', 0) <= 54:
        company['is_white_spot'] = False

# Add new projects
new_projects = [
    {'id': 51, 'title': 'Модернизация теплосети', 'industry': 'ТЭК', 'scale': 1500000, 'base_cost': 25000000, 'margin_percent': 22, 'status': 'planning', 'description': 'Проект'},
    {'id': 52, 'title': 'Строительство логистического центра', 'industry': 'Логистика', 'scale': 800000, 'base_cost': 15000000, 'margin_percent': 18, 'status': 'planning', 'description': 'Проект'},
    {'id': 53, 'title': 'Автоматизация производства', 'industry': 'Производство', 'scale': 500000, 'base_cost': 10000000, 'margin_percent': 25, 'status': 'approval', 'description': 'Проект'},
    {'id': 54, 'title': 'Расширение торгового центра', 'industry': 'Торговля', 'scale': 2000000, 'base_cost': 35000000, 'margin_percent': 20, 'status': 'planning', 'description': 'Проект'},
    {'id': 55, 'title': 'Умный транспорт', 'industry': 'ТЭК', 'scale': 3000000, 'base_cost': 50000000, 'margin_percent': 23, 'status': 'research', 'description': 'Проект'}
]

existing_projects = data.get('projects', [])
existing_projects.extend(new_projects)
data['projects'] = existing_projects

data['white_spot_zones'] = ['Центральный', 'Северо-Западный', 'Ярославль-1', 'Ярославль-2']

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Updated {json_path}')
print(f'Companies: {len(data["companies"])}')
print(f'Projects: {len(data["projects"])}')
print(f'White spot zones: {data["white_spot_zones"]}')
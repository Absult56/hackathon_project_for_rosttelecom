import json

data = json.load(open('backend/data/initial_data.json', encoding='utf-8'))
companies = data['companies']
white_zones = ['Порт', 'Батайск', 'Новый Аксай', 'Таганрог-Пром']

zones = {}
for c in companies:
    zone = c.get('cluster_zone', '')
    if zone in white_zones:
        zones.setdefault(zone, []).append(c)

print("=== Белые пятна (cluster_zone) ===")
for zone in white_zones:
    zone_cs = zones.get(zone, [])
    total = len(zone_cs)
    rtk = sum(1 for c in zone_cs if c.get('is_rtk_client'))
    is_white = sum(1 for c in zone_cs if c.get('is_white_spot'))
    print(f"{zone}: {total} companies, {rtk} RTK clients, {is_white} is_white_spot")

print("\n=== All 4 white spots total ===")
total_ws = sum(len(zones.get(z, [])) for z in white_zones)
total_ws_rtk = sum(sum(1 for c in zones.get(z, []) if c.get('is_rtk_client')) for z in white_zones)
print(f"Total white spot companies: {total_ws}")
print(f"Total white spot RTK clients: {total_ws_rtk}")

print("\n=== Other zones ===")
other_zones = [c.get('cluster_zone', '') for c in companies if c.get('cluster_zone') not in white_zones]
for zone in sorted(set(other_zones)):
    zone_cs = [c for c in companies if c.get('cluster_zone') == zone]
    total = len(zone_cs)
    rtk = sum(1 for c in zone_cs if c.get('is_rtk_client'))
    print(f"{zone}: {total} companies, {rtk} RTK clients")
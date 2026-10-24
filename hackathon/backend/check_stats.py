import json
from collections import Counter, defaultdict

with open('data/initial_data.json', encoding='utf-8') as f:
    data = json.load(f)
companies = data['companies']

total_rev = sum(c['revenue'] for c in companies)
print('Total revenue: %.1f млн руб' % total_rev)
print('Avg revenue: %.1f млн руб' % (total_rev/len(companies)))
print('Min revenue: %.1f млн руб' % min(c['revenue'] for c in companies))
print('Max revenue: %.1f млн руб' % max(c['revenue'] for c in companies))

print('\n--- По отраслям ---')
ind = defaultdict(lambda: {'count':0,'rev':0.0,'rtk':0})
for c in companies:
    ind[c['industry']]['count'] += 1
    ind[c['industry']]['rev'] += c['revenue']
    if c.get('is_rtk_client'):
        ind[c['industry']]['rtk'] += 1
for k in sorted(ind, key=lambda x: -ind[x]['count']):
    v=ind[k]
    print('%s: %d компаний, %.1f млн, %.1f%%, RTK=%d' % (k, v['count'], v['rev'], v['rev']/total_rev*100, v['rtk']))

print('\n--- По кластерам ---')
cl = defaultdict(lambda: {'count':0,'rev':0.0,'rtk':0,'ws':0})
for c in companies:
    cl[c['cluster_zone']]['count'] += 1
    cl[c['cluster_zone']]['rev'] += c['revenue']
    if c.get('is_rtk_client'):
        cl[c['cluster_zone']]['rtk'] += 1
    if c.get('is_white_spot'):
        cl[c['cluster_zone']]['ws'] += 1
for k in sorted(cl, key=lambda x: -cl[x]['count']):
    v=cl[k]
    print('%s: %d комп, %.1f млн, %.1f%%, RTK=%d, WS=%d' % (k, v['count'], v['rev'], v['count']/len(companies)*100, v['rtk'], v['ws']))

rtk = [c for c in companies if c.get('is_rtk_client')]
leads = [c for c in companies if not c.get('is_rtk_client')]
rtk_rev = sum(c['revenue'] for c in rtk)
lead_rev = sum(c['revenue'] for c in leads)
print('\n--- Покрытие ---')
print('RTK клиенты: %d (%.1f%%)' % (len(rtk), len(rtk)/len(companies)*100))
print('Лиды: %d (%.1f%%)' % (len(leads), len(leads)/len(companies)*100))
print('Доля покрытия: %.1f%%' % (len(rtk)/len(companies)*100))
print('Выручка клиентов: %.1f млн' % rtk_rev)
print('Выручка лидов: %.1f млн' % lead_rev)

print('\n--- Белые пятна ---')
ws_zones={'Порт','Батайск','Новый Аксай','Таганрог-Пром'}
for z in sorted(ws_zones):
    zc=[c for c in companies if c['cluster_zone']==z]
    zrev=sum(c['revenue'] for c in zc)
    inds=Counter(c['industry'] for c in zc)
    top3=', '.join('%s (%d)' % (k,v) for k,v in inds.most_common(3))
    print('%s: %d комп, %.1f млн, RTK=0, Топ-3: %s' % (z, len(zc), zrev, top3))
total_ws_rev=sum(c['revenue'] for c in companies if c['cluster_zone'] in ws_zones)
print('Всего в белых пятнах: %d комп, %.1f млн' % (sum(1 for c in companies if c['cluster_zone'] in ws_zones), total_ws_rev))
print('Потенциал белых пятен: %.1f млн руб = %.2f млрд руб' % (total_ws_rev, total_ws_rev/1000))
print('Доля белых пятен: %.1f%%' % (sum(1 for c in companies if c['cluster_zone'] in ws_zones)/len(companies)*100))
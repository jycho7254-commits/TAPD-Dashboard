"""Fetch all TAPD bugs and save as tapd_data.json"""
import json, time, urllib.request

TAPD_TOKEN = '54cca09820e19852abb03cdce3fde10be7f81905'
WS = '46691872'
FIELDS = 'id,title,status,severity,version_report,version_fix,created,current_owner,reporter,participator,cc,te,de,fixer,priority_label'

all_bugs = []
page = 1
total = 0

while True:
    url = f'https://api.tapd.cn/bugs?workspace_id={WS}&limit=200&fields={FIELDS}&page={page}&order=id'
    auth = f'Bearer {TAPD_TOKEN}'
    req = urllib.request.Request(url, headers={'Authorization': auth, 'User-Agent': 'Mozilla/5.0'})
    
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f'  Page {page} error: {e}')
        break
    
    if data.get('status') != 1 or not data.get('data'):
        break
    
    batch = [d['Bug'] for d in data['data'] if d.get('Bug')]
    if not batch:
        break
    
    all_bugs.extend(batch)
    total = data.get('data_total', '?')
    print(f'  Page {page}: +{len(batch)}건 (누적 {len(all_bugs)}/{total})')
    
    if len(batch) < 200:
        break
    page += 1
    time.sleep(0.5)

result = {
    'success': True,
    'meta': {
        'workspace_id': WS,
        'total': len(all_bugs),
        'fetched_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    },
    'data': all_bugs
}

out_path = 'C:/Users/user/dashboards-repo/tapd/tapd_data.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'\n✅ 총 {len(all_bugs)}건 저장 → {out_path}')

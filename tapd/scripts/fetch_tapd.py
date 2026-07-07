"""TAPD 데이터 수집 — GitHub Actions 전용
환경변수 TAPD_TOKEN 필요
tapd_data.json에 저장
"""
import json, time, urllib.request, os

TOKEN = os.environ['TAPD_TOKEN']
WS = '46691872'
FIELDS = 'id,title,status,severity,version_report,version_fix,created,current_owner,reporter,participator,cc,te,de,fixer,priority_label'
BASE = f'https://api.tapd.cn/bugs?workspace_id={WS}&limit=200&fields={FIELDS}'

all_bugs = []
page = 1
while True:
    url = f'{BASE}&page={page}&order=id'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f'Page {page} error: {e}')
        break
    if data.get('status') != 1 or not data.get('data'):
        break
    batch = [d['Bug'] for d in data['data'] if d.get('Bug')]
    if not batch:
        break
    all_bugs.extend(batch)
    if len(batch) < 200:
        break
    page += 1
    time.sleep(0.3)

result = {
    'success': True,
    'meta': {
        'workspace_id': WS,
        'total': len(all_bugs),
        'fetched_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'source': 'github-actions'
    },
    'data': all_bugs
}

out_path = os.path.join(os.path.dirname(__file__), '..', 'tapd_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f'Fetched {len(all_bugs)} bugs from TAPD')

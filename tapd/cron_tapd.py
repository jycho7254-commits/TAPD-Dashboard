"""TAPD 데이터 수집 + GitHub Pages 자동 배포 (no_agent 크론용)
프록시 없이도 GitHub Pages에 최신 TAPD 데이터 유지
"""
import json, time, urllib.request, subprocess, os

TAPD_TOKEN = '54cca09820e19852abb03cdce3fde10be7f81905'
WS = '46691872'
FIELDS = 'id,title,status,severity,version_report,version_fix,created,current_owner,reporter,participator,cc,te,de,fixer,priority_label'
TAPD_BASE = f'https://api.tapd.cn/bugs?workspace_id={WS}&limit=200&fields={FIELDS}'

def fetch_all():
    all_bugs = []
    page = 1
    while True:
        url = f'{TAPD_BASE}&page={page}&order=id'
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {TAPD_TOKEN}',
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
    return all_bugs

def main():
    bugs = fetch_all()
    result = {
        'success': True,
        'meta': {
            'workspace_id': WS,
            'total': len(bugs),
            'fetched_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'source': 'cron'
        },
        'data': bugs
    }

    # tapd_data.json 저장
    repo = 'C:/Users/user/dashboards-repo/tapd'
    out = os.path.join(repo, 'tapd_data.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)

    # git push
    subprocess.run(['git', 'add', '.'], cwd=repo, capture_output=True)
    r = subprocess.run(['git', 'commit', '-m', f'auto: TAPD 갱신 ({len(bugs)}건)'], cwd=repo, capture_output=True)
    if r.returncode == 0:
        subprocess.run(['git', 'push'], cwd=repo, capture_output=True)
        print(f'Updated GitHub Pages: {len(bugs)} bugs')
    else:
        print('No changes or commit failed')

if __name__ == '__main__':
    main()

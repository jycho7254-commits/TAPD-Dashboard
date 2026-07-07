"""TAPD API proxy server — CORS proxy for browser-side TAPD fetch.
Run: python3 tapd_proxy.py
Serves /api/tapd (proxy) and ./index.html (dashboard) on port 8080.
"""
import json, time, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

TAPD_TOKEN = '54cca09820e19852abb03cdce3fde10be7f81905'
WS = '46691872'
FIELDS = 'id,title,status,severity,version_report,version_fix,created,current_owner,reporter,participator,cc,te,de,fixer,priority_label'
TAPD_BASE = f'https://api.tapd.cn/bugs?workspace_id={WS}&limit=200&fields={FIELDS}'

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/tapd' or self.path.startswith('/api/tapd?'):
            self._proxy_tapd()
        else:
            self._serve_file()
    
    def _proxy_tapd(self):
        """Fetch all TAPD bugs and return JSON (proxy with CORS headers)."""
        all_bugs = []
        page = 1
        while True:
            url = f'{TAPD_BASE}&page={page}&order=id'
            auth = f'Bearer {TAPD_TOKEN}'
            req = urllib.request.Request(url, headers={'Authorization': auth, 'User-Agent': 'Mozilla/5.0'})
            try:
                resp = urllib.request.urlopen(req, timeout=30)
                data = json.loads(resp.read().decode('utf-8'))
            except Exception as e:
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
                'source': 'live'
            },
            'data': all_bugs
        }
        
        # Also save to tapd_data.json for consistency
        out_path = 'C:/Users/user/dashboards-repo/tapd/tapd_data.json'
        try:
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False)
        except:
            pass
        
        body = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def _serve_file(self):
        """Serve index.html or tapd_data.json."""
        import os
        if self.path == '/' or self.path == '':
            fpath = 'C:/Users/user/dashboards-repo/tapd/index.html'
        elif self.path == '/tapd_data.json':
            fpath = 'C:/Users/user/dashboards-repo/tapd/tapd_data.json'
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        
        try:
            with open(fpath, 'rb') as f:
                body = f.read()
            ct = 'text/html; charset=utf-8' if fpath.endswith('.html') else 'application/json; charset=utf-8'
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', ct)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_response(404)
            self._cors()
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8081), Handler)
    print('🚀 TAPD proxy running on http://localhost:8081')
    print('   API proxy: http://localhost:8081/api/tapd')
    server.serve_forever()

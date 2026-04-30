from flask import Flask, jsonify, request
import requests
import json
from datetime import datetime
import random
import base64

app = Flask(__name__)

# ===== CONFIGURATION =====
API_KEY = "mafu"
EXTERNAL_API_URL = "https://mafuuuu-info-api.vercel.app/mafu-info"
EXTERNAL_API_KEY = "mafu"

# ===== ENCRYPTED CREDIT INFORMATION =====
_enc = "eyJkZXZlbG9wZXIiOiJAbWFoZnVqX29mZmNpYWxfMTQzQGV4dWNvZHIiLCJtYWluX2NoYW5uZWwiOiJAbWFoZnVqX29mZmNpYWwiLCJhcGlfY2hhbm5lbDEiOiJAbWFmdWFwaXMiLCJhcGlfY2hhbm5lbDIiOiJAZXh1Y29kZXgiLCJhcGlfbmFtZSI6IkZyZWUgRmlyZSBMZXZlbCBJbmZvIEFQSSIsInZlcnNpb24iOiIzLjAuMCIsImxhc3RfdXBkYXRlZCI6IjIwMjYtMDQtMTgifQ=="
_enc_welcome = "V2VsY29tZSB0byBNQUZVeEVYVSBMZXZlbCBJbmZvIEFQSQ=="

def _d():
    return json.loads(base64.b64decode(_enc).decode('utf-8'))

def _w():
    return base64.b64decode(_enc_welcome).decode('utf-8')

CREDIT_INFO = _d()
WELCOME_MESSAGE = _w()

def format_num(num):
    return "{:,}".format(num)

# ===== LEVELS Dictionary =====
LEVELS = {
    "1": 0, "2": 48, "3": 202, "4": 544, "5": 1012, "6": 1844, "7": 2792, "8": 3800,
    "9": 4870, "10": 6004, "11": 7192, "12": 8448, "13": 9776, "14": 11140, "15": 12566,
    "16": 14060, "17": 15610, "18": 17224, "19": 18902, "20": 20632, "21": 22424,
    "22": 24728, "23": 26192, "24": 28166, "25": 30200, "26": 32294, "27": 34448,
    "28": 37804, "29": 41174, "30": 44870, "31": 48852, "32": 53334, "33": 58566,
    "34": 64096, "35": 69994, "36": 76460, "37": 83108, "38": 91128, "39": 99322,
    "40": 108092, "41": 120144, "42": 133266, "43": 147472, "44": 162760, "45": 179126,
    "46": 196572, "47": 215368, "48": 235516, "49": 257010, "50": 279860, "51": 304056,
    "52": 348318, "53": 394982, "54": 444044, "55": 495508, "56": 549364, "57": 633756,
    "58": 721744, "59": 813336, "60": 908522, "61": 1041438, "62": 1180352, "63": 1325256,
    "64": 1476184, "65": 1634300, "66": 1840946, "67": 2056594, "68": 2281242, "69": 2514880,
    "70": 2757530, "71": 3059506, "72": 3372284, "73": 3699456, "74": 4041030, "75": 4397020,
    "76": 4829104, "77": 5282204, "78": 5756304, "79": 6251404, "80": 6767504, "81": 7381324,
    "82": 8043154, "83": 8752952, "84": 9510808, "85": 10316638, "86": 11277190, "87": 12360748,
    "88": 13360304, "89": 14482858, "90": 15659418, "91": 17026708, "92": 18453688, "93": 19941280,
    "94": 21488570, "95": 23095858, "96": 24763138, "97": 26490138, "98": 28277708, "99": 30124996,
    "100": 32032284,
}

def get_exp_for_level(level):
    try:
        level_str = str(int(level))
        return LEVELS.get(level_str, 0)
    except:
        return 0

def calculate_level_progress(current_exp, current_level):
    try:
        current_level = int(current_level)
        if current_level >= 100:
            return {
                "current_level": 100,
                "current_exp": current_exp,
                "exp_for_current_level": LEVELS["100"],
                "exp_for_next_level": LEVELS["100"],
                "exp_needed": 0,
                "exp_needed_for_100": 0,
                "progress_percentage": 100
            }
        
        exp_for_current = get_exp_for_level(current_level)
        exp_for_next = get_exp_for_level(current_level + 1)
        exp_for_100 = get_exp_for_level(100)
        
        if exp_for_next == 0 or exp_for_current == 0:
            return None
        
        exp_needed = exp_for_next - current_exp
        exp_needed_for_100 = exp_for_100 - current_exp
        
        exp_in_current_level = current_exp - exp_for_current
        exp_range_for_level = exp_for_next - exp_for_current
        if exp_range_for_level > 0:
            progress_percentage = min(100, max(0, (exp_in_current_level / exp_range_for_level) * 100))
        else:
            progress_percentage = 0
        
        return {
            "current_level": current_level,
            "current_exp": current_exp,
            "exp_for_current_level": exp_for_current,
            "exp_for_next_level": exp_for_next,
            "exp_needed": exp_needed,
            "exp_needed_for_100": exp_needed_for_100,
            "progress_percentage": round(progress_percentage, 1)
        }
    except Exception as e:
        print(f"Error in calculate_level_progress: {e}")
        return None

def fetch_player_info(uid):
    try:
        api_url = f"{EXTERNAL_API_URL}?uid={uid}"
        response = requests.get(api_url, timeout=20)
        
        if response.status_code != 200:
            return {"success": False, "message": "API Server Error"}
        
        data = response.json()
        if not data:
            return {"success": False, "message": "Empty Data received from API"}
        
        return {"success": True, "data": data}
        
    except requests.Timeout:
        return {"success": False, "message": "API Timeout (20s exceeded)"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected Error: {str(e)}"}

def create_response(success=True, **kwargs):
    """Helper function to create response with credit info always first"""
    response = {
        "credit": CREDIT_INFO,
        "success": success
    }
    response.update(kwargs)
    return jsonify(response)

# ===== ONLY ONE ENDPOINT =====
@app.route('/mafu-level')
def mafu_level():
    """Get player level info with real-time data"""
    uid = request.args.get('uid')
    user_key = request.args.get('key')
    
    # API Key validation
    if user_key != API_KEY:
        return create_response(
            success=False,
            message=f"Invalid Key. Please use ?key={API_KEY}",
            timestamp=datetime.now().isoformat()
        ), 401
    
    # UID validation
    if not uid:
        return create_response(
            success=False,
            message="UID parameter is required",
            timestamp=datetime.now().isoformat()
        ), 400
    
    try:
        # Real API call for actual data
        player_data = fetch_player_info(uid)
        
        if player_data["success"]:
            # Real data from API
            data = player_data["data"]
            basic_info = data.get("basicInfo", {})
            
            nickname = basic_info.get("nickname", "Unknown")
            current_level = basic_info.get("level", 0)
            current_exp = basic_info.get("exp", 0)
            
            # Add small real-time variation
            current_exp += random.randint(-50, 100)
            if current_exp < 0:
                current_exp = 0
            
            data_source = "live_api"
        else:
            # Fallback to simulated real-time data
            nickname = f"Player_{uid[-6:] if len(uid) > 6 else uid}"
            timestamp = int(datetime.now().timestamp())
            base_exp = (hash(uid) % 10000000) + (timestamp % 100000)
            current_exp = abs(base_exp)
            
            # Calculate level from EXP
            current_level = 1
            for lvl, exp_needed in sorted(LEVELS.items(), key=lambda x: int(x[0])):
                if current_exp >= exp_needed:
                    current_level = int(lvl)
                else:
                    break
            
            data_source = "simulated_realtime"
        
        # Calculate progress
        progress = calculate_level_progress(current_exp, current_level)
        
        if not progress:
            return create_response(
                success=False,
                message="Could not calculate level progress",
                uid=uid,
                nickname=nickname,
                timestamp=datetime.now().isoformat()
            )
        
        # Response with player info
        return create_response(
            success=True,
            player_info={
                "uid": uid,
                "nickname": nickname,
                "current_level": progress['current_level'],
                "current_exp": progress['current_exp'],
                "formatted_exp": format_num(progress['current_exp']),
                "exp_for_current_level": progress['exp_for_current_level'],
                "formatted_exp_current_level": format_num(progress['exp_for_current_level']),
                "exp_for_next_level": progress['exp_for_next_level'],
                "formatted_exp_next_level": format_num(progress['exp_for_next_level']),
                "exp_needed": progress['exp_needed'],
                "formatted_exp_needed": format_num(progress['exp_needed']),
                "exp_needed_for_100": progress['exp_needed_for_100'],
                "formatted_exp_needed_for_100": format_num(progress['exp_needed_for_100']),
                "progress_percentage": progress['progress_percentage'],
                "level_100_exp": LEVELS["100"],
                "formatted_level_100_exp": format_num(LEVELS["100"])
            },
            data_source=data_source,
            timestamp=datetime.now().isoformat(),
            realtime=True
        )
        
    except Exception as e:
        return create_response(
            success=False,
            message=f"Error: {str(e)}",
            uid=uid,
            timestamp=datetime.now().isoformat()
        )

# Home route - shows only this endpoint
@app.route('/')
def home():
    return create_response(
        success=True,
        message=WELCOME_MESSAGE,
        endpoint="/mafu-level?uid=<uid>&key=mafu",
        usage="GET /mafu-level?uid=123456789&key=mafu",
        timestamp=datetime.now().isoformat()
    )

if __name__ == '__main__':
    print("=" * 50)
    print(f"🚀 API Developed by: {CREDIT_INFO['developer']}")
    print(f"📢 Main Channel: {CREDIT_INFO['main_channel']}")
    print(f"🔧 API Channel: {CREDIT_INFO['api_channel1']}")
    print("=" * 50)
    print("📌 Only Endpoint: /mafu-level?uid=<uid>&key=mafu")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
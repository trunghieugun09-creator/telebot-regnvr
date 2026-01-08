#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, random, string, datetime, re, requests, threading, os
import sys
import gzip
import platform
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs

# ================= CONFIG =================
# Lấy BOT_TOKEN từ biến môi trường - KHÔNG HARDCODE
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables")
    print("ℹ️ Please set BOT_TOKEN in .env file or environment variables")
    sys.exit(1)

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
UID_FILE = "tele_uid.txt"
OFFSET = 0
REG_DELAY = 10
LAST_REG_TIME = {}
RUNNING_CHAT = set()

# ================= REQUESTS REG CONFIG =================
user_agent_reg = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
]

proxy_reg = [
    "103.121.89.199:10698:1R9p7:68145"
]

# ================= TELEGRAM UTILS =================
def build_proxy(proxy_str):
    """
    Input:  host:port:user:pass
    Output: dict dùng cho requests
    """
    host, port, user, pwd = proxy_str.split(":")
    proxy_auth = f"http://{user}:{pwd}@{host}:{port}"
    return {
        "http": proxy_auth,
        "https": proxy_auth
    }
    
def self_destruct_message(chat_id, sent_msg_id, original_msg_id, delay=120):
    time.sleep(delay)
    tg_delete_message(chat_id, sent_msg_id)
    tg_delete_message(chat_id, original_msg_id)

def tg_delete_message(chat_id, message_id):
    try:
        requests.post(
            f"{API}/deleteMessage",
            data={"chat_id": chat_id, "message_id": message_id},
            timeout=5
        )
    except:
        pass

def log_theodoi(text):
    try:
        with open("theodoi.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except:
        pass

def save_tele_uid(user_id):
    try:
        uid_str = str(user_id).strip()

        if not os.path.exists(UID_FILE):
            with open(UID_FILE, "w", encoding="utf-8") as f:
                f.write(uid_str + "\n")
            return True

        with open(UID_FILE, "r", encoding="utf-8") as f:
            saved_uids = set(line.strip() for line in f if line.strip())

        if uid_str in saved_uids:
            return False

        with open(UID_FILE, "a", encoding="utf-8") as f:
            f.write(uid_str + "\n")

        return True
    except Exception as e:
        print(f"[Lỗi UID] {e}")
        return False


def html_escape(s):
    if s is None:
        s = "None"
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tg_send(chat_id, text, parse_mode="HTML", reply_to_message_id=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id

    try:
        r = requests.post(
            f"{API}/sendMessage",
            data=data,
            timeout=15
        ).json()
        return r.get("result", {}).get("message_id")
    except Exception as e:
        print(f"[Send Error] {e}")
        return None

def tg_edit(chat_id, msg_id, text, parse_mode="HTML"):
    try:
        requests.post(
            f"{API}/editMessageText",
            data={"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode},
            timeout=10
        )
    except Exception as e:
        print(f"[Edit Error] {e}")
        pass

def get_updates():
    global OFFSET
    try:
        r = requests.get(f"{API}/getUpdates", params={"offset": OFFSET, "timeout": 30}, timeout=35).json()
        if r.get("result"):
            OFFSET = r["result"][-1]["update_id"] + 1
            return r["result"]
    except Exception as e:
        print(f"[Update Error] {e}")
    return []

# ================= SYSTEM UTILS =================

def get_buoi():
    h = datetime.datetime.now().hour
    if 5 <= h < 11: return "buổi sáng"
    elif 11 <= h < 13: return "buổi trưa"
    elif 13 <= h < 18: return "buổi chiều"
    else: return "buổi tối"

def get_bot_username():
    try:
        r = requests.get(f"{API}/getMe", timeout=10).json()
        if r.get("ok") and r.get("result"):
            return "@" + r["result"]["username"]
    except:
        pass
    return "Không xác định"

BOT_USERNAME = get_bot_username()

def get_random_user_agent():
    return random.choice(user_agent_reg)

def get_time_tag():
    return datetime.datetime.now().strftime("[%H:%M:%S]")

# ================= RANDOM DATA =================

def remove_accents(input_str):
    s = input_str.lower()
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[đ]', 'd', s)
    return s

def ten_gha():
    first = ["Bạch","Uyển","Cố","Sở","Trạch","Lam","Thanh","Mặc","Kim","Thiên","Hồng","Kính","Thủy","Kiều","Minh","Nhật","Băng","Hải","Tâm","Phi"]
    mid = ["Vũ","Hạ","Tỉnh","Vân","Khúc","Ảnh","Huyết","Vô","Tuyệt","Mệnh","Ngản","Ngạn","Bi","Lưu","Tĩnh","Lộ","Phong","Tư","Khiết","Vĩ"]
    last = ["Khách","Xuẫn","Nghi","Ninh","Nhạn","Quân","Hiên","Lâm","歌","琴","Lang","Tiêu","Lâu","Tháp","Diệp","Yến","Phủ","Đồ","Hào"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def birth():
    year = random.randint(1995, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"

def matkhau():
    fixed_prefix = "tghieux₫!"
    random_characters = string.ascii_letters + string.digits
    fixed_suffix = "#@!"
    random_part = ''.join(random.choice(random_characters) for _ in range(7))
    return fixed_prefix + random_part + fixed_suffix

def mail_ao(fullname):
    domains = ["gmail.com", "hotmail.com"]
    clean_name = remove_accents(fullname).replace(" ", "")
    number = str(random.randint(1000,9999))
    domain = random.choice(domains)
    return f"{clean_name}{number}@{domain}"

# ================= SIMPLE REGISTRATION =================
def decode_response_content(response):
    try:
        if 'gzip' in response.headers.get('Content-Encoding', ''):
            return gzip.decompress(response.content).decode('utf-8', errors='ignore')
        else:
            return response.content.decode('utf-8', errors='ignore')
    except:
        return response.text

def create_simple_session():
    session = requests.Session()

    # ===== GẮN PROXY NGAY KHI TẠO SESSION =====
    if proxy_reg:
        proxy = build_proxy(random.choice(proxy_reg))
        session.proxies.update(proxy)

    session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
    })

    return session

def extract_all_form_fields(soup):
    """Lấy tất cả form và field từ trang"""
    forms = soup.find_all('form')
    if not forms:
        return None, {}

    # Tìm form đăng ký
    reg_form = None
    for form in forms:
        form_html = str(form).lower()
        if any(keyword in form_html for keyword in ['register', 'sign up', 'đăng ký', 'tạo tài khoản']):
            reg_form = form
            break

    if not reg_form:
        reg_form = forms[0]  # Lấy form đầu tiên nếu không tìm thấy

    fields = {}
    # Lấy tất cả input, select, textarea
    for inp in reg_form.find_all(['input', 'select', 'textarea']):
        name = inp.get('name')
        if name:
            if inp.name == 'select':
                # Lấy option đầu tiên cho select
                option = inp.find('option', selected=True)
                if option:
                    fields[name] = option.get('value', '')
                else:
                    first_option = inp.find('option')
                    if first_option:
                        fields[name] = first_option.get('value', '')
            else:
                fields[name] = inp.get('value', '')

    return reg_form, fields

def simple_facebook_reg(fullname, email, password, birthday):
    session = None
    try:
        # Tạo session
        session = create_simple_session()

        # Lấy trang đăng ký
        print(f" {get_time_tag()} [1/3] Đang lấy trang đăng ký...")
        response = session.get("https://www.facebook.com/reg/", timeout=20)

        if response.status_code != 200:
            # Thử URL khác
            response = session.get("https://mbasic.facebook.com/reg/", timeout=20)
            if response.status_code != 200:
                print(f" {get_time_tag()} [ERROR] HTTP {response.status_code}")
                return False, f"Lỗi HTTP {response.status_code}", session

        content = decode_response_content(response)
        soup = BeautifulSoup(content, 'html.parser')
        form, fields = extract_all_form_fields(soup)

        if not form:
            print(f" {get_time_tag()} [ERROR] Không tìm thấy form")
            return False, "Không tìm thấy form đăng ký", session

        # Tách thông tin
        parts = fullname.split()
        firstname = parts[0]
        lastname = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        day, month, year = birthday.split("/")
        gender = random.choice(['1', '2'])  # 1: nam, 2: nữ

        # Điền form - chỉ điền các field cơ bản
        print(f" {get_time_tag()} [2/3] Đang điền thông tin...")
        basic_fields = {
            'firstname': firstname,
            'lastname': lastname,
            'reg_email__': email,
            'reg_email_confirmation__': email,
            'reg_passwd__': password,
            'birthday_day': day,
            'birthday_month': month,
            'birthday_year': year,
            'sex': gender,
        }

        # Giữ lại các field ẩn từ form gốc
        for key, value in fields.items():
            if key not in basic_fields:
                basic_fields[key] = value

        # Gửi form
        action = form.get('action', '')
        if action.startswith('/'):
            if 'mbasic' in response.url:
                action_url = 'https://www.facebook.com' + action
            else:
                action_url = 'https://mbasic.facebook.com' + action
        elif action.startswith('http'):
            action_url = action
        else:
            if 'mbasic' in response.url:
                action_url = 'https://www.facebook.com/reg/'
            else:
                action_url = 'https://mbasic.facebook.com/reg/'

        print(f" {get_time_tag()} [3/3] Đang gửi form...")
        response = session.post(action_url, data=basic_fields, timeout=30)

        # Chờ 2 giây
        time.sleep(0.1)

        # Kiểm tra response
        if response.status_code == 200:
            print(f" {get_time_tag()} [DONE] Đã gửi form thành công! Status: 200")
            return True, "✅ Thành công!", session
        else:
            print(f" {get_time_tag()} [WARNING] Status: {response.status_code}")
            # Vẫn trả về thành công nếu đã gửi được request
            return True, f"✅ Thành công!", session

    except Exception as e:
        error_msg = f"❌ Lỗi: {str(e)[:100]}"
        print(f" {get_time_tag()} [ERROR] {error_msg}")
        return False, error_msg, session

def get_cookies_from_session(session):
    if not session:
        return {}

    try:
        cookies = session.cookies.get_dict()

        # Chọn cookies quan trọng
        result = {}
        if 'c_user' in cookies:
            result['c_user'] = cookies['c_user']
        if 'xs' in cookies:
            result['xs'] = cookies['xs']
        elif 'fr' in cookies:
            result['fr'] = cookies['fr']

        return result
    except:
        return {}

def cookies_to_string(cookies_dict):
    if not cookies_dict:
        return "Không có"
    return "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])


# ================= HANDLE REG COMMAND =================
def reg_single_account(chat_id, user_id, user_name, message_id):
    if chat_id in RUNNING_CHAT:
        tg_send(chat_id, "⏱️ Đợi lệnh kia chạy xong đã.", reply_to_message_id=message_id)
        return

    now = time.time()
    last = LAST_REG_TIME.get(user_id, 0) 
    if now - last < REG_DELAY:
        wait = int(REG_DELAY - (now - last))
        tg_send(chat_id, f"⏱️ Cỡ {wait}s nữa mới được reg tiếp.", reply_to_message_id=message_id)
        return

    LAST_REG_TIME[user_id] = now
    RUNNING_CHAT.add(chat_id)

    msg_id = tg_send(chat_id, f"{get_time_tag()} 🚀 Đang reg...", reply_to_message_id=message_id) 
    if not msg_id:
        RUNNING_CHAT.remove(chat_id)
        return

    session = None
    try:
        # Tạo thông tin account
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 📝 Đang reg...")
        fullname = ten_gha()
        email = mail_ao(fullname)
        password = matkhau()
        birthday = birth()

        # Gửi form
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🗞️ Đang reg...")
        success, message, session = simple_facebook_reg(fullname, email, password, birthday)

        # Lấy cookies và UID
        cookies_dict = get_cookies_from_session(session)
        uid = cookies_dict.get('c_user', '0')
        cookie_str = cookies_to_string(cookies_dict)

        # In log console
        print(f"——————————————————————————————")
        print(f" {get_time_tag()} TK: {email}\nMK: {password}\nTrạng thái: {message}")
        print(f"——————————————————————————————")

        log_theodoi(
            f"{get_time_tag()}\n"
            f"USER: {user_name}\n"
            f"ID: {user_id}\n"
            f"EMAIL: {email}\n"
            f"PASS: {password}\n"
        )


        # Format kết quả
        result = {
            "name": fullname,
            "email": email,
            "password": password,
            "status": message,
            "uid": uid,
            "cookies": cookie_str,
            "user_name": user_name
        }

        # Gửi kết quả
        tg_edit(chat_id, msg_id, format_result(result, success))

    except Exception as e:
        error_result = {
            "user_name": user_name,
            "status": f"❌ Lỗi hệ thống: {str(e)[:50]}"
        }
        tg_edit(chat_id, msg_id, format_result(error_result, False))
        print(f" {get_time_tag()} [LỖI] {e}")

    finally:
        RUNNING_CHAT.remove(chat_id)
        if session:
            try:
                session.close()
            except:
                pass

# ================= FORMAT RESULT =================
def format_result(d, success):
    now = datetime.datetime.now().strftime("%H:%M:%S | %d/%m/%y")
    user_name = html_escape(d.get('user_name', 'Unknown User'))

    if not success:
        return f"👤 Người sử dụng bot: <b>{user_name}</b>\n❌ Reg thất bại\n⏰ {now}\nLỗi: {html_escape(d.get('status', 'Không xác định'))}"

    # Đảm bảo có tất cả các key
    for k in ["name", "email", "password", "status", "uid", "cookies"]:
        if k not in d or d[k] is None:
            d[k] = "None"

    footer = html_escape(
        """
        ⟡ ⊹₊˚‧︵‿₊୨ᰔ୧₊‿︵‧˚₊⊹ ⟡
           --  MY INFO --
            ─────୨ৎ─────
   𐔌. FB    : /tg.nux — Trung Hiếu
   𐔌. Zalo : 0338316701 — TghieuX
   𐔌. Tele : @tghieuX — Trungg Hieuu
   """
    )

    return (
        "<b>🎉 REG THÀNH CÔNG 🎊</b>\n"
        "<code><i>Thông tin acc bên dưới:</i></code>      ᓚ₍⑅^..^₎ฅ\n"
        "╭────-_Ი𐑼_-─────────⭓\n"
        f"│ 👤 Tên: ⤷ ゛<code>{html_escape(d['name'])}</code>  ˎˊ˗\n"
        f"│ 📧 Email: <code>{html_escape(d['email'])}</code>\n"
        f"│ 🔑 Mật khẩu: <tg-spoiler><code>{html_escape(d['password'])}</code></tg-spoiler>\n"
        f"│ 📌 Trạng thái: <b>{html_escape(d['status'])}</b>      ୨ৎ⊹ˑ ֗\n"
        f"│ 🍪 Cookies: <code>{html_escape(d['cookies'])}</code>...\n"
        f"├───────.────\n"
        f"│ 🌐 IP: <b>▒▒▒▒▒▒▒▒▒▒</b>       ᶻ 𝗓 𐰁 .ᐟ\n"
        f"│ 🌎 Quốc gia: <b>Việt Nam (VN)</b>\n"
        f"│ ⏰ Thời gian: <b>{now}</b>        ◟ ͜ ׁ ˙\n"
        "╰───｡𖦹°‧──────˙⟡────⭓\n"
        f"<b><i>Chúc bạn một {get_buoi()} tốt lành!</i></b>\n"
        f"<b><i>Người sử dụng bot: {user_name}</i></b>  /ᐠ - ˕-マ⌒\n" 
        f"<b><i>Bot phục vụ bạn:{BOT_USERNAME}</i></b>\n\n"
        f"<pre>{footer}</pre>"
    )

# ================= OTHER HANDLERS =================
def handle_start(chat_id, user_name, message_id):
    text = (
        f"<b><i>🎉 Chào mừng {html_escape(user_name)} đã đến!👋</i></b>\n"
        f"<b><i>💌 Hãy sử dụng lệnh /help để xem hướng dẫn!</i></b>"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

def handle_help(chat_id, message_id):
    text = (
        "<b>📌NUXW_BOT XIN HỖ TRỢ BẠN:</b>\n\n"
        "—————————————\n\n"
        "<b><i>☁️ /regfb — dùng để tạo 1 acc fb.</i></b>\n\n"
        "—————————————\n\n"
        "<b><i>☁️ /myinfo — dùng để xem thông tin của bạn.</i></b>\n\n"
        "—————————————\n\n"
        "<b><i>☁️ /symbols — dùng để lấy các kí tự symbols</i></b>\n\n"
        "—————————————\n\n"
        "<b><i>⚠️Các lệnh như /myinfo và /symbols sẽ tự động xoá sau 2 phút tránh lạm dụng và loãng box, tks!⚠️</i></b>"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

def format_myinfo(user_info):
    uid = user_info.get("id")
    full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
    username = user_info.get("username")
    
    info_text = (
        "<b>✅DƯỚI ĐÂY LÀ THÔNG TIN CỦA BẠN:</b>\n"
        "<b><i>🆔 UID:</i></b> <code>{}</code>\n".format(uid) +
        "<b><i>🏷️ Tên:</i></b> <code>{}</code>\n".format(html_escape(full_name))
    )
    
    if username:
        info_text += "<b><i>💳 User: @{}</i></b>\n".format(html_escape(username))
    else:
        info_text += "<b><i>💳 User:</i></b> <code>Không có</code>\n"
        
    info_text += "\n<b><i>⚠️ Chú ý: Bot sẽ tự động xoá tin nhắn này sau 1 phút (60 giây)!</i></b>"
    return info_text

def handle_myinfo(chat_id, user_info, message_id):
    text = format_myinfo(user_info)
    sent_msg_id = tg_send(chat_id, text, reply_to_message_id=message_id)
    
    if sent_msg_id:
        threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()

# ================= MAIN BOT LOOP =================
def bot_main_loop():
    print("\n- - - RUN BOT TELE BY TGHIEUX - - -")
    print("╭─────────────⭓")
    print(f"│ 👤 Tên bot: {BOT_USERNAME}")
    print(f"│ 🚀 Đang run bot tele...")
    print("│ ⚠️ BOT_TOKEN loaded from environment")
    print("╰─────────────⭓\n")

    while True:
        try:
            for u in get_updates():
                msg = u.get("message")
                if not msg or "text" not in msg or "from" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                user_info = msg["from"]
                user_id = user_info.get("id")
                text = msg["text"].strip()
                message_id = msg.get("message_id")

                username_str = user_info.get("username")
                first_name_str = user_info.get("first_name", "Unknown")
                user_name = "@" + username_str if username_str else first_name_str

                print(f"{get_time_tag()} | USER: {user_name} | ID: {user_id} | CMD: {text}")

                cmd = text.split()[0]

                # ===== REG FB =====
                if cmd == "/regfb" or cmd == f"/regfb{BOT_USERNAME}":
                    threading.Thread(
                        target=reg_single_account,
                        args=(chat_id, user_id, user_name, message_id),
                        daemon=True
                    ).start()

                elif cmd == "/start":
                    handle_start(chat_id, user_name, message_id)
                elif text == "/myinfo":
                    handle_myinfo(chat_id, user_info, message_id)    
                elif cmd == "/help":
                    handle_help(chat_id, message_id)

            time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"{get_time_tag()} [MAIN LOOP ERROR] {e}")
            time.sleep(5)

# ================= HTTP SERVER FOR RENDER/UPTIMEROBOT =================
def run_http_server(port=8080):
    """Chạy HTTP server đơn giản để Render không kill process"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Bot is running')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Telegram Bot is alive')
        
        def log_message(self, format, *args):
            pass  # Tắt log
    
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"🌐 HTTP Server running on port {port}")
    server.serve_forever()

# ================= MAIN ENTRY POINT =================
if __name__ == "__main__":
    # Lấy PORT từ biến môi trường (Render cung cấp)
    PORT = int(os.environ.get("PORT", 8080))
    
    # Khởi động bot trong thread riêng
    bot_thread = threading.Thread(target=bot_main_loop, daemon=True)
    bot_thread.start()
    
    print(f"🤖 Bot started in background thread")
    print(f"🔧 Using PORT: {PORT}")
    print(f"📞 Bot Token: {'*' * 10}{BOT_TOKEN[-5:] if BOT_TOKEN else 'None'}")
    
    # Chạy HTTP server để giữ process sống
    try:
        run_http_server(PORT)
    except Exception as e:
        print(f"❌ HTTP Server Error: {e}")
        # Nếu không chạy được server, vẫn chạy bot
        bot_thread.join()

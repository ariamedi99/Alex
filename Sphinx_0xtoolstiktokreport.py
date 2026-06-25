#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                      
║                    telegram   Sphinx_0x                      ║
║                   Modernized by Sphinx_0x                        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import requests
import re
import time
import json
import random
import threading
import hashlib
from hashlib import md5
from time import time as _time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Tuple
import urllib.parse
import sys
import os

class XBogusSigner:
    SHIFT_ARRAY = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe"
    MAGIC = 536919696
    KEY_TABLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

    @staticmethod
    def md5_2x(s):
        return md5(md5(s.encode()).digest()).hexdigest()

    @staticmethod
    def rc4_encrypt(pt, key):
        s_box = list(range(256))
        j = 0
        for i in range(256):
            j = (j + s_box[i] + key[i % len(key)]) % 256
            s_box[i], s_box[j] = s_box[j], s_box[i]
        i = j = 0
        out = ""
        for c in pt:
            i = (i + 1) % 256
            j = (j + s_box[i]) % 256
            s_box[i], s_box[j] = s_box[j], s_box[i]
            out += chr(ord(c) ^ s_box[(s_box[i] + s_box[j]) % 256])
        return out

    @staticmethod
    def b64_encode(s, kt=None):
        if kt is None:
            kt = XBogusSigner.KEY_TABLE
        parts = []
        for i in range(0, len(s), 3):
            a = ord(s[i])
            b = ord(s[i+1]) if i+1 < len(s) else 0
            c = ord(s[i+2]) if i+2 < len(s) else 0
            n1 = a >> 2
            n2 = ((3 & a) << 4) | (b >> 4)
            n3 = ((15 & b) << 2) | (c >> 6) if i+1 < len(s) else 64
            n4 = 63 & c if i+2 < len(s) else 64
            parts += [n1, n2, n3, n4]
        return "".join(kt[v] for v in parts)

    @staticmethod
    def _filter(lst):
        idx = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        return [lst[x-1] for x in idx]

    @staticmethod
    def _scramble(*a):
        idxs = [a[0], a[10], a[1], a[11], a[2], a[12], a[3], a[13],
                a[4], a[14], a[5], a[15], a[6], a[16], a[7], a[17], a[8], a[18], a[9]]
        return "".join(chr(x) for x in idxs)

    @staticmethod
    def _cksum(salt):
        c = 64
        for x in salt[3:]:
            c ^= x
        return c

    @classmethod
    def _x_bogus(cls, params, ua, ts, data=""):
        md5_data = cls.md5_2x(data)
        md5_params = cls.md5_2x(params)
        md5_ua = md5(cls.b64_encode(cls.rc4_encrypt(ua, [0, 1, 14])).encode()).hexdigest()
        salt = [ts, cls.MAGIC, 64, 0, 1, 14,
                bytes.fromhex(md5_params)[-2], bytes.fromhex(md5_params)[-1],
                bytes.fromhex(md5_data)[-2], bytes.fromhex(md5_data)[-1],
                bytes.fromhex(md5_ua)[-2], bytes.fromhex(md5_ua)[-1]]
        salt += [(ts >> i) & 0xFF for i in range(24, -1, -8)]
        salt += [(salt[1] >> i) & 0xFF for i in range(24, -1, -8)]
        salt += [cls._cksum(salt), 255]
        num_list = cls._filter(salt)
        return cls.b64_encode("\x02\xff" + cls.rc4_encrypt(cls._scramble(*num_list), [255]), cls.SHIFT_ARRAY)

    @classmethod
    def sign(cls, params, ua):
        return f"{params}&X-Bogus={cls._x_bogus(params, ua, int(_time()))}"



BANNER = r"""
   _______                     _____ _______
  |__   __|                  ) | | |
     / _ \/ _` | '_ ` _ \  |  ___/  | |
     (_| | | | | | | | |      | |
     ___|\__,_|_| |_| |_| |_|      |_|
             telegram   Sphinx_0x
           Modernized by Sphinx_0x
"""

REPORT_TYPES = {
    1: {"name": "General Report",    "reason": "310"},
    2: {"name": "Hate Speech",       "reason": "306"},
    3: {"name": "Self-Harm/Suicide", "reason": "3051"},
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
]

def rand_id():
    """Generate a 19-digit device ID string. Pure int math, no floats."""
    return str(random.randint(1000000000000000000, 9999999999999999999))

def rand_csrf():
    return "".join(random.choice("abcdef0123456789") for _ in range(24))

def rand_secsdk():
    return "000100000001" + hashlib.sha256(str(random.random()).encode()).hexdigest()[:56]


# =============================================================================
# SESSION
# =============================================================================

class TikTokSession:
    def __init__(self, proxy=None, ua=None, cookies_str=None):
        self.s = requests.Session()
        self.ua = ua or random.choice(USER_AGENTS)
        if proxy:
            self.s.proxies = {"http": proxy, "https": proxy}

        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.tiktok.com",
            "referer": "https://www.tiktok.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.ua,
        }

        wid = rand_id()
        self.s.cookies.update({"tt_webid_v2": wid, "tt_webid": wid, "tt_csrf_token": rand_csrf()})

        if cookies_str:
            self._load_cookies(cookies_str)

    def _load_cookies(self, cookie_str):
        """Parse cookies from a raw string (e.g. from browser devtools)."""
        for part in cookie_str.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                self.s.cookies.set(k.strip(), v.strip())

    def get_user_info(self, username):
        try:
            resp = self.s.get(f"https://www.tiktok.com/@{username}", headers=self.headers, timeout=20)
            if resp.status_code != 200:
                return None

            # Method 1: __UNIVERSAL_DATA_FOR_REHYDRATION__
            m = re.search(
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
                resp.text, re.DOTALL
            )
            if m:
                try:
                    d = json.loads(m.group(1))
                    u = d.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo", {}).get("user", {})
                    if u and "id" in u:
                        return u
                except:
                    pass

            # Method 2: SIGI_STATE
            m = re.search(r'<script id="SIGI_STATE"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
            if m:
                try:
                    d = json.loads(m.group(1))
                    users = d.get("UserModule", {}).get("users", {})
                    if users:
                        return next(iter(users.values()))
                except:
                    pass

            # Method 3: regex fallback
            for p in [r'"id":"(\d+)"', r'"userId":"(\d+)"', r'"pageId":"(\d+)"']:
                ma = re.search(p, resp.text)
                if ma:
                    return {"id": ma.group(1), "uniqueId": username}
            return None
        except:
            return None


# =============================================================================
# REPORTER
# =============================================================================

class TikTokReporter:
    def __init__(self, session):
        self.session = session
        self.base = "https://www.tiktok.com/node/report/reasons_put"

    def _sign_url(self, params):
        qs = "&".join(f"{k}={urllib.parse.quote(str(v), '')}" for k, v in params.items())
        return f"{self.base}?{XBogusSigner.sign(qs, self.session.ua)}"

    def send(self, uid, username, reason, rtype="user"):
        try:
            params = {
                "aid": "1988", "app_name": "tiktok_web", "device_platform": "web",
                "referer": f"https://www.tiktok.com/@{username}",
                "root_referer": "https://www.google.com/",
                "user_agent": self.session.ua,
                "cookie_enabled": "true", "screen_width": "1920", "screen_height": "1080",
                "browser_language": "en-US", "browser_platform": "Win32",
                "browser_name": "Mozilla", "browser_online": "true", "ac": "4g",
                "timezone_name": "America/New_York", "appId": "1233", "region": "US",
                "appType": "m", "isAndroid": "false", "isMobile": "false", "isIOS": "false",
                "OS": "windows",
                "did": rand_id(),
                "_": str(int(time.time() * 1000)),
            }

            payload = {"object_id": uid, "owner_id": uid, "reason": reason, "report_type": rtype}

            headers = dict(self.session.headers)
            headers["content-length"] = str(len(json.dumps(payload)))
            headers["referer"] = f"https://www.tiktok.com/@{username}"
            headers["x-secsdk-csrf-token"] = rand_secsdk()
            headers["tt-csrf-token"] = self.session.s.cookies.get("tt_csrf_token", rand_csrf())

            resp = self.session.s.post(self._sign_url(params), json=payload, headers=headers, timeout=20)

            if resp.status_code == 200:
                d = resp.json()
                if d.get("statusCode") == 0:
                    return True, "OK"
                return False, f"API: {d}"
            elif resp.status_code == 403:
                return False, "Blocked"
            elif resp.status_code == 429:
                return False, "Rate-limited"
            elif resp.status_code == 401:
                return False, "Unauthorized (need valid cookies)"
            return False, f"HTTP {resp.status_code}"
        except requests.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)[:50]


# =============================================================================
# COOKIE HELPER
# =============================================================================

def get_cookies_from_user():
    """Ask user to paste cookies from their browser."""
    print("\n" + "=" * 60)
    print("  TikTok requires a logged-in session to send reports.")
    print("  To get your cookies:")
    print("  1. Open Chrome/Firefox and login to TikTok.com")
    print("  2. Open DevTools (F12) -> Application/Storage -> Cookies")
    print("  3. Right-click -> Copy All -> Paste below")
    print("  (Or copy the full 'Cookie' header from a request)")
    print("=" * 60)
    print("\n  [>] Paste cookies (or press Enter to try without): ")
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
    except EOFError:
        pass
    return " ".join(lines).strip()


# =============================================================================
# BATCH
# =============================================================================

class BatchEngine:
    def __init__(self, threads=5, proxies=None, cookies_str=None):
        self.threads = min(max(threads, 1), 30)
        self.proxies = proxies or []
        self.cookies_str = cookies_str
        self.stats = {"ok": 0, "fail": 0, "total": 0}
        self.lock = threading.Lock()

    def _work(self, uid, user, reason, proxy=None):
        ses = TikTokSession(proxy=proxy, cookies_str=self.cookies_str)
        rep = TikTokReporter(ses)
        ok, msg = rep.send(uid, user, reason)
        with self.lock:
            self.stats["total"] += 1
            if ok:
                self.stats["ok"] += 1
            else:
                self.stats["fail"] += 1
        return {"ok": ok, "msg": msg}

    def run(self, username, reasons, count):
        ses = TikTokSession(cookies_str=self.cookies_str)
        user = ses.get_user_info(username)
        if not user:
            print("  [-] Could not find user on TikTok")
            return

        uid = user.get("id") or user.get("userId") or user.get("pageId")
        print(f"  [+] Found: @{username} | ID: {uid}")
        print(f"  [+] Sending {count} reports with {self.threads} threads...")

        pool = self.proxies if self.proxies else [None]
        items = [(uid, username, random.choice(reasons), random.choice(pool)) for _ in range(count)]
        random.shuffle(items)

        start = time.time()
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as ex:
                futs = [ex.submit(self._work, *i) for i in items]
                for n, f in enumerate(as_completed(futs), 1):
                    r = f.result()
                    print(f"  {'[+]' if r['ok'] else '[-]'} #{n}/{count}: {r['msg']}", end="\r" if n < count else "\n")
                    if n % (self.threads * 2) == 0 and n < count:
                        time.sleep(random.uniform(0.5, 1.5))
        except KeyboardInterrupt:
            print("\n  [!] Interrupted")

        t = time.time() - start
        rps = self.stats["total"] / t if t > 0 else 0
        print(f"\n  [+] Time: {t:.1f}s | OK: {self.stats['ok']} | Fail: {self.stats['fail']} | {rps:.1f}/s")


# =============================================================================
# MODES
# =============================================================================

def setup_session():
    """Create a TikTokSession, asking for cookies if needed."""
    cookies = get_cookies_from_user()
    ses = TikTokSession(cookies_str=cookies if cookies else None)
    if cookies:
        print("  [+] Cookies loaded")
    else:
        print("  [!] No cookies - reports will likely fail (401 Unauthorized)")
    return ses

def mode_mass():
    username = input("  [>] Username: ").strip().lstrip("@")
    if not username:
        return
    ses = setup_session()
    user = ses.get_user_info(username)
    if not user:
        print("  [-] User not found")
        return
    uid = user.get("id") or user.get("userId") or user.get("pageId")
    print(f"  [+] @{username} -> ID: {uid}")
    rep = TikTokReporter(ses)
    c = 0
    try:
        while True:
            for _, info in REPORT_TYPES.items():
                ok, msg = rep.send(uid, username, info["reason"])
                c += 1
                mark = "+" if ok else "-"
                print(f"  [{mark}] #{c} [{info['name']}] {msg[:35]}")
                time.sleep(random.uniform(1.5, 4.0))
    except KeyboardInterrupt:
        print(f"\n  [+] Stopped at #{c}")

def mode_single():
    for k, v in REPORT_TYPES.items():
        print(f"  [{k}] {v['name']}")
    ch = input("  [>] Type: ").strip()
    if ch not in ("1", "2", "3"):
        return
    info = REPORT_TYPES[int(ch)]
    username = input("  [>] Username: ").strip().lstrip("@")
    if not username:
        return
    ses = setup_session()
    user = ses.get_user_info(username)
    if not user:
        print("  [-] User not found")
        return
    uid = user.get("id") or user.get("userId") or user.get("pageId")
    print(f"  [+] @{username} -> ID: {uid}")
    rep = TikTokReporter(ses)
    c = 0
    try:
        while True:
            ok, msg = rep.send(uid, username, info["reason"])
            c += 1
            mark = "+" if ok else "-"
            print(f"  [{mark}] #{c} {msg[:35]}")
            time.sleep(random.uniform(1.5, 4.0))
    except KeyboardInterrupt:
        print(f"\n  [+] Stopped at #{c}")

def mode_batch():
    username = input("  [>] Username: ").strip().lstrip("@")
    if not username:
        return
    for k, v in REPORT_TYPES.items():
        print(f"  [{k}] {v['name']}")
    print("  [4] All types")
    ch = input("  [>] Type: ").strip()
    if ch == "4":
        reasons = [v["reason"] for v in REPORT_TYPES.values()]
    elif ch in ("1", "2", "3"):
        reasons = [REPORT_TYPES[int(ch)]["reason"]]
    else:
        return
    try:
        cnt = int(input("  [>] Count: ") or "30")
        thr = max(1, min(30, int(input("  [>] Threads (1-30): ") or "5")))
    except:
        return
    cookies = get_cookies_from_user()
    pf = input("  [>] Proxy file (Enter to skip): ").strip()
    proxies = None
    if pf:
        try:
            with open(pf) as f:
                proxies = [l.strip() for l in f if l.strip()]
            print(f"  [+] Loaded {len(proxies)} proxies")
        except:
            print("  [-] Can't load proxies")
    BatchEngine(threads=thr, proxies=proxies, cookies_str=cookies if cookies else None).run(username, reasons, cnt)


# =============================================================================
# MENU
# =============================================================================

def menu():
    print()
    print("  [1] Mass report - All 3 types (infinite loop)")
    print("  [2] Single type   - Pick one type (infinite loop)")
    print("  [3] Batch mode    - Multi-threaded (N reports)")
    print("  [4] Exit")
    ch = input("  [>] Choice: ").strip()
    if ch == "1":
        mode_mass()
    elif ch == "2":
        mode_single()
    elif ch == "3":
        mode_batch()
    elif ch == "4":
        print("  [+] Bye.")
        sys.exit(0)
    else:
        print("  [-] Invalid")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Authorized Security Testing Tool - Sphinx_0x     ║")
    print("║  Original by @Sphinx_0x | X-Bogus Signer Integrated       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    while True:
        menu()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import requests
from seleniumbase import SB

# ============================================================
#  环境变量配置
# ============================================================
ACCOUNTS = []
if os.environ.get("EML_1") and os.environ.get("PWD_1"):
    ACCOUNTS.append({"email": os.environ.get("EML_1"), "pwd": os.environ.get("PWD_1"), "tag": "账号 A"})
if os.environ.get("EML_2") and os.environ.get("PWD_2"):
    ACCOUNTS.append({"email": os.environ.get("EML_2"), "pwd": os.environ.get("PWD_2"), "tag": "账号 B"})

TG_TOKEN = os.environ.get("TG_TOKEN")
TG_ID    = os.environ.get("TG_ID")

if not ACCOUNTS:
    print("❌ 致命错误：未检测到有效环境变量（EML_1/PWD_1 或 EML_2/PWD_2）")
    sys.exit(1)

DYNAMIC_APP_NAME = "未知应用"

# ============================================================
#  JS 逻辑
# ============================================================
_EXPAND_JS = """(function() { var ts = document.querySelector('input[name="cf-turnstile-response"]'); if (!ts) return 'no-turnstile'; var el = ts; for (var i = 0; i < 20; i++) { el = el.parentElement; if (!el) break; var s = window.getComputedStyle(el); if (s.overflow === 'hidden' || s.overflowX === 'hidden' || s.overflowY === 'hidden') el.style.overflow = 'visible'; el.style.minWidth = 'max-content'; } document.querySelectorAll('iframe').forEach(function(f){ if (f.src && f.src.includes('challenges.cloudflare.com')) { f.style.width = '300px'; f.style.height = '65px'; f.style.minWidth = '300px'; f.style.visibility = 'visible'; f.style.opacity = '1'; } }); return 'done'; })()"""
_SOLVED_JS = """(function(){ var i = document.querySelector('input[name="cf-turnstile-response"]'); return !!(i && i.value && i.value.length > 20); })()"""
_EXISTS_JS = """(function(){ return document.querySelector('input[name="cf-turnstile-response"]') !== null; })()"""
_COORDS_JS = """(function(){ var iframes = document.querySelectorAll('iframe'); for (var i = 0; i < iframes.length; i++) { var src = iframes[i].src || ''; if (src.includes('cloudflare') || src.includes('turnstile') || src.includes('challenges')) { var r = iframes[i].getBoundingClientRect(); if (r.width > 0 && r.height > 0) return {cx: Math.round(r.x + 30), cy: Math.round(r.y + r.height / 2)}; } } return null; })()"""
_WININFO_JS = """(function(){ return {sx: window.screenX || 0, sy: window.screenY || 0, oh: window.outerHeight, ih: window.innerHeight}; })()"""

# ============================================================
#  辅助函数
# ============================================================
def _activate_window():
    for cls in ["chrome", "chromium", "Chromium", "Chrome"]:
        try:
            r = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", cls], capture_output=True, text=True, timeout=3)
            wids = [w for w in r.stdout.strip().split("\n") if w.strip()]
            if wids:
                subprocess.run(["xdotool", "windowactivate", "--sync", wids[0]], timeout=3)
                return True
        except: pass
    return False

def _xdotool_click(x, y):
    _activate_window()
    try:
        subprocess.run(["xdotool", "mousemove", "--sync", str(x), str(y)], timeout=3)
        time.sleep(0.15)
        subprocess.run(["xdotool", "click", "1"], timeout=2)
    except:
        os.system(f"xdotool mousemove {x} {y} click 1 2>/dev/null")

def handle_turnstile(sb):
    print("🔍 处理 Cloudflare Turnstile 验证...")
    sb.execute_script(_EXPAND_JS)
    for i in range(1, 11):
        if sb.execute_script(_SOLVED_JS):
            print("  ✅ Turnstile 通过")
            return True
        try:
            c, wi = sb.execute_script(_COORDS_JS), sb.execute_script(_WININFO_JS)
            if c:
                bar = wi["oh"] - wi["ih"]
                ax, ay = c["cx"] + wi["sx"], c["cy"] + wi["sy"] + (bar if bar > 0 else 0)
                print(f"  🖱️ 模拟点击坐标 ({ax}, {ay})")
                _xdotool_click(ax, ay)
        except: pass
        time.sleep(5)
    return False

# 采用更安全的参数传递方式，防止特殊字符导致 JS 语法错误
def safe_js_fill(sb, selector, text):
    script = """
        var el = document.querySelector(arguments[0]);
        if (el) {
            el.value = arguments[1];
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    """
    sb.execute_script(script, selector, text)

def send_msg(status, timer):
    if not TG_TOKEN or not TG_ID: return
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()+8*3600))
    text = f"🖥 {DYNAMIC_APP_NAME}\\n{status}\\n⏱️ 剩余: {timer}\\n📅 {now}"
    try: requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", json={"chat_id": TG_ID, "text": text}, timeout=10)
    except: pass

# ============================================================
#  主流程
# ============================================================
def run_task(sb, acc):
    global DYNAMIC_APP_NAME
    print(f"\n🚀 [ {acc['tag']} ] 正在处理: {acc['email']}")
    
    sb.uc_open_with_reconnect("https://justrunmy.app/id/Account/Login")
    sb.wait_for_element('input[name="Email"]')
    
    # 使用新版安全填充函数
    safe_js_fill(sb, 'input[name="Email"]', acc['email'])
    safe_js_fill(sb, 'input[name="Password"]', acc['pwd'])
    
    if sb.execute_script(_EXISTS_JS): 
        handle_turnstile(sb)
    
    sb.press_keys('input[name="Password"]', '\n')
    time.sleep(5)
    
    if "Login" in sb.get_current_url():
        sb.save_screenshot("login_failed.png")
        raise Exception("仍处于登录页，可能是验证码未过或账号密码错")

    sb.open("https://justrunmy.app/panel")
    sb.wait_for_element('h3.font-semibold')
    DYNAMIC_APP_NAME = sb.get_text('h3.font-semibold')
    sb.click('h3.font-semibold')
    time.sleep(3)
    
    sb.click('button:contains("Reset Timer")')
    time.sleep(3)
    if sb.execute_script(_EXISTS_JS): 
        handle_turnstile(sb)
    
    sb.click('button:contains("Just Reset")')
    time.sleep(8)
    
    sb.refresh()
    time.sleep(4)
    res = sb.get_text('span.font-mono.text-xl')
    print(f"✅ {acc['tag']} 成功！剩余: {res}")
    send_msg("✅ 续期完成", res)

def main():
    use_proxy = os.environ.get("USE_PROXY", "false").lower() == "true"
    kwargs = {"uc": True, "test": True, "headless": False}
    if use_proxy: 
        kwargs["proxy"] = "http://127.0.0.1:8080"
    
    with SB(**kwargs) as sb:
        for acc in ACCOUNTS:
            try:
                run_task(sb, acc)
                sb.delete_all_cookies()
                time.sleep(2)
            except Exception as e:
                print(f"❌ {acc['tag']} 失败: {e}")
                sb.save_screenshot(f"error_{acc['tag']}.png")
                send_msg("❌ 运行失败", str(e)[:30])

if __name__ == "__main__":
    main()

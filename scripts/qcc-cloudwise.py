"""企查查云智慧公司资讯采集 — 非 headless（用户手工登录）。
用法: python3 /tmp/qcc-cloudwise.py（30s 登录窗口，登录后自动提取）"""
import json, re, sys, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CH = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
URL = 'https://www.qcc.com/firm/21b5b8a3bef7ae6ab441c9e8b60b94a8.html'

opts = Options()
# 非 headless：用户手工登录
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1400,1000')
# 减少 webdriver 特征（企查查反爬）
opts.add_argument('--disable-blink-features=AutomationControlled')
opts.add_experimental_option('excludeSwitches', ['enable-automation'])
opts.add_experimental_option('useAutomationExtension', False)

drv = webdriver.Chrome(service=Service(CH), options=opts)
try:
    drv.get(URL)
    time.sleep(6)
    # 判断登录态：企查查未登录会跳转/弹登录
    page = drv.page_source
    logged_in = ('云智慧' in page) or ('法定代表人' in page) or ('成立日期' in page)
    login_popup = ('登录' in drv.title) or ('login' in drv.current_url.lower())
    print(f'[判断] 页面标题: {drv.title[:60]}')
    print(f'[判断] 登录态: {"已登录" if logged_in and not login_popup else "未登录/需登录"}')
    if not logged_in or login_popup:
        print('[等待] 请在浏览器中手工登录企查查，等待 30 秒...')
        time.sleep(30)
        # 登录后重新加载/等待
        try:
            WebDriverWait(drv, 10).until(lambda d: '云智慧' in d.page_source or '法定代表人' in d.page_source)
        except Exception:
            pass
        print('[登录后] 继续提取')

    time.sleep(3)
    page = drv.page_source
    text = drv.find_element(By.TAG_NAME, 'body').text
    # 提取公司核心信息
    print('\n===== 公司页面文本（前 2500 字）=====')
    t = re.sub(r'\n{3,}', '\n\n', text)
    print(t[:2500])

    # 保存全量文本
    with open('/tmp/qcc-cloudwise-full.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print('\n[保存] 全量文本 → /tmp/qcc-cloudwise-full.txt')
finally:
    input('\n[完成] 按回车关闭浏览器...')
    drv.quit()

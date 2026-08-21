import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# 🚨 비밀금고 접근 권한
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 8호기 팩트 데이터 장착
APP_NAME = "올인원 QR 바코드 스캐너 - 와이파이 링크 생성" 
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.scanner"
BASE_KEYWORD = "QR코드 스캐너 어플"

def get_app_description(url):
    print("🔍 QR 스캐너 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "QR 코드와 바코드를 1초 만에 스캔하고, 나만의 와이파이/링크 QR 코드를 쉽게 생성할 수 있는 필수 앱입니다."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    response = requests.get(url)
    suggestions = json.loads(response.text)[1]
    return suggestions[-1] if suggestions else base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 스마트폰 유틸리티 어플 전문 블로거야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.
    
    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}
    
    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.
    
    [지정 목차]
    ## 1. 일상생활 속 QR코드, 답답하게 스캔하고 있다면?
    ## 2. 1초 컷 스캔부터 생성까지: '{APP_NAME}'
    ## 3. 와이파이 공유, 명함 등 추천 활용 꿀팁
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    # 🚨 파일 이름이 겹치지 않게 '-scanner-post'로 변경!
    filename = f"{today}-scanner-post.md"
    
    # QR코드/스마트폰 테마 고화질 이미지 주입
    top_image = "![QR코드 스캔](https://images.unsplash.com/photo-1595054224523-93666d3a8637?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 📲 아직도 카메라 앱으로 답답하게 스캔하시나요?
어두운 곳에서도 빠르고 정확하게! 나만의 QR코드 생성까지 지원하는 올인원 스캐너를 지금 바로 만나보세요.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 1초 만에 스캔하는 올인원 꿀앱'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 8호기 QR 스캐너 전용 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: API 키가 없습니다!")
        exit(1)
    print("🤖 봇 8호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 8호기 QR 스캐너 포스팅 팩트 장착 완료!")

import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# 🚨 비밀금고 접근 권한
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 12호기 팩트 데이터 장착
APP_NAME = "픽셀 핏 - 사진 크기 변환 & 용량 줄이기 압축" 
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.pixel"
BASE_KEYWORD = "사진 용량 줄이기 어플"

def get_app_description(url):
    print("🔍 사진 압축 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "화질 손실 없이 사진 용량을 확 줄여주고, 원하는 크기로 쉽게 변환해 주는 필수 사진 편집 앱입니다."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    response = requests.get(url)
    suggestions = json.loads(response.text)[1]
    return suggestions[-1] if suggestions else base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 스마트폰 활용법, IT 유틸리티 전문 블로거야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.
    
    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}
    
    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.
    
    [지정 목차]
    ## 1. 스마트폰 용량 부족, 원인은 바로 고화질 사진?
    ## 2. 화질 저하 없이 용량만 쏙 줄이는 법: '{APP_NAME}'
    ## 3. 이력서 사진, 웹 업로드 시 필수 꿀팁
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    # 🚨 파일 이름이 겹치지 않게 '-pixel-post'로 변경!
    filename = f"{today}-pixel-post.md"
    
    # 사진/스마트폰 테마 고화질 이미지 주입
    top_image = "![사진 압축](https://images.unsplash.com/photo-1502920917128-1aa500764cbd?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 🖼️ 용량 제한 때문에 업로드 안 되는 사진, 이제 1초 만에 해결!
복잡한 PC 프로그램 켤 필요 없이, 스마트폰에서 터치 몇 번으로 사진 크기와 용량을 확 줄여보세요.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 화질 손실 없이 사진 용량 줄이는 법'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 12호기 픽셀 핏 전용 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: API 키가 없습니다!")
        exit(1)
    print("🤖 봇 12호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 12호기 픽셀 핏 포스팅 팩트 장착 완료!")

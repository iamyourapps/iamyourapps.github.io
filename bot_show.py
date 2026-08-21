import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# 🚨 비밀금고 접근 권한
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 11호기 팩트 데이터 장착
APP_NAME = "전국공연정보 - 뮤지컬 데이트, 어린이 연극 일정" 
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.show"
BASE_KEYWORD = "공연 정보 어플"

def get_app_description(url):
    print("🔍 공연 정보 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "전국 방방곡곡의 뮤지컬, 연극, 콘서트 일정을 한눈에 확인하고 데이트 코스를 계획할 수 있는 앱입니다."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    response = requests.get(url)
    suggestions = json.loads(response.text)[1]
    return suggestions[-1] if suggestions else base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 문화생활, 데이트 코스, 가족 나들이 전문 블로거야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.
    
    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}
    
    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.
    
    [지정 목차]
    ## 1. 주말 데이트, 매번 똑같은 코스가 지겹다면?
    ## 2. 전국 공연 일정을 한눈에: '{APP_NAME}'
    ## 3. 커플 뮤지컬부터 어린이 연극까지 100% 활용법
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    # 🚨 파일 이름이 겹치지 않게 '-show-post'로 변경!
    filename = f"{today}-show-post.md"
    
    # 공연/무대 테마 고화질 이미지 주입
    top_image = "![공연 무대](https://images.unsplash.com/photo-1514525253161-7a46d19cd819?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 🎟️ 이번 주말, 특별한 추억을 만들어보세요!
로맨틱한 뮤지컬부터 우리 아이가 좋아하는 연극까지, 전국 모든 공연 정보를 지금 바로 확인해 보세요.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 주말 데이트 어린이 연극 일정 찾기'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 11호기 공연 정보 전용 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: API 키가 없습니다!")
        exit(1)
    print("🤖 봇 11호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 11호기 공연 정보 포스팅 팩트 장착 완료!")

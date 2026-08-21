import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# 🚨 비밀금고 접근 권한
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 9호기 팩트 데이터 장착
APP_NAME = "올인원 도서 스캐너 - AI 책스캔, 텍스트추출 OCR" 
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.pdf"
BASE_KEYWORD = "도서 스캐너 어플"

def get_app_description(url):
    print("🔍 도서 스캐너 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "무거운 책을 가볍게! AI 기술로 도서를 스캔하고 텍스트(OCR)를 추출해 주는 올인원 스캐너 앱입니다."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    response = requests.get(url)
    suggestions = json.loads(response.text)[1]
    return suggestions[-1] if suggestions else base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 대학생, 직장인 생산성 어플 전문 블로거야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.
    
    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}
    
    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.
    
    [지정 목차]
    ## 1. 전공서적과 서류, 무겁게 들고 다닐 필요 없는 이유
    ## 2. 텍스트 추출까지 한 번에: '{APP_NAME}'
    ## 3. 스마트한 대학생과 직장인에게 추천하는 꿀팁
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    # 🚨 파일 이름이 겹치지 않게 '-pdf-post'로 변경!
    filename = f"{today}-pdf-post.md"
    
    # 책상/공부/스마트폰 테마 고화질 이미지 주입
    top_image = "![도서 스캔](https://images.unsplash.com/photo-1544383835-bda2bc66a55d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 📚 무거운 책, 이제 폰 안에 가볍게 넣고 다니세요!
깨끗한 AI 스캔부터 텍스트 추출(OCR)까지, 스마트한 일상을 위한 필수 앱을 지금 바로 만나보세요.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 무거운 책 가볍게 AI 책스캔'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 9호기 도서 스캐너 전용 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: API 키가 없습니다!")
        exit(1)
    print("🤖 봇 9호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 9호기 도서 스캐너 포스팅 팩트 장착 완료!")

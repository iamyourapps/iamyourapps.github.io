import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

APP_NAME = "단위변환기 - 평수, 돈, 길이 단위 환산 계산기"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.converter"
BASE_KEYWORD = "단위변환 계산기 어플"

def get_app_description(url):
    print("🔍 단위변환기 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "복잡한 평수, 돈, 길이 단위를 쉽고 빠르게 환산해주는 필수 계산기 앱입니다."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    response = requests.get(url)
    suggestions = json.loads(response.text)[1]
    return suggestions[-1] if suggestions else base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 IT/생활 편의 어플 전문 블로거야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.

    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}

    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.

    [지정 목차]
    ## 1. 일상 속 헷갈리는 단위 계산, 1초 만에 해결하는 법
    ## 2. 필수 단위 환산기: '{APP_NAME}'
    ## 3. 이럴 때 꼭 활용해 보세요! (부동산 평수, 금돈 계산 등)
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{today}-converter-post.md"
    
    top_image = "![계산기](https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 📏 복잡한 단위 변환, 이제 머리 아프게 계산하지 마세요!
평수부터 금돈까지 터치 한 번으로 끝내는 마법의 계산기, 지금 바로 확인해 보세요.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 헷갈리는 평수 돈 길이 완벽 정리'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 4호기 단위변환기 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: API 키가 없습니다!")
        exit(1)
    print("🤖 봇 4호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 4호기 포스팅 완료!")

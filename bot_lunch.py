import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# 🚨 깃허브 비밀금고에서 꺼내오기!
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 2호기 팩트 데이터 장착
APP_NAME = "오늘급식메뉴 - 학교 급식 식단 정보" 
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.lunch"
BASE_KEYWORD = "학교 급식 어플"

def get_app_description(url):
    print("🔍 급식 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "전국 초중고 학교의 오늘 급식 메뉴를 빠르고 간편하게 확인하세요."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    response = requests.get(url)
    suggestions = json.loads(response.text)[1]
    return suggestions[-1] if suggestions else base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 IT/어플 전문 블로거야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.
    
    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}
    
    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.
    
    [지정 목차]
    ## 1. 매일 아침 아이 학교 급식 메뉴가 궁금할 때
    ## 2. 전국 학교 식단표를 한 번에: '{APP_NAME}'
    ## 3. 학생과 학부모 모두에게 추천하는 이유
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    # 🚨 성경 앱 글이랑 파일 이름이 겹쳐서 덮어써지지 않게 '-lunch-post'로 변경!
    filename = f"{today}-lunch-post.md"
    
    # 맛있는 점심/식단 테마 이미지 주입
    top_image = "![학교 급식](https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 🍱 오늘 우리 학교 급식 메뉴는 뭘까?
복잡한 검색 없이 터치 한 번으로 빠르고 편하게 확인해 보세요!

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 매일 확인하는 전국 초중고 식단표'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 사진과 링크가 완벽하게 박힌 급식 전용 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: 깃허브 비밀금고에 API 키가 없습니다! (로컬 테스트 시 세팅 필요)")
        exit(1)
    print("🤖 봇 2호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 2호기 급식 앱 포스팅 팩트 장착 완료!")

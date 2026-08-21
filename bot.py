import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# 🚨 깃허브 보안 쉴드 완벽 대응: API 키를 직접 안 쓰고 비밀금고(환경변수)에서 꺼내 쓰기!
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

APP_NAME = "오늘 성경 말씀 - 듣기 편한 매일 성경 구절" 
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.today_bible"
BASE_KEYWORD = "매일 성경 어플"

def get_app_description(url):
    print("🔍 플레이스토어에서 최신 앱 설명을 긁어오는 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "앱 설명을 긁어오지 못했습니다. 기본 오디오 성경 기능만 강조해 주세요."

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
    ## 1. 바쁜 일상 속에서 성경 묵상이 필요한 이유
    ## 2. 매일 성경을 가장 편하게 접하는 방법: '{APP_NAME}'
    ## 3. 이런 분들에게 강력 추천합니다
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{today}-auto-post.md"
    
    top_image = "![평안과 위로](https://images.unsplash.com/photo-1490730141103-6cac27aaab94?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"
    
    cta_link = f"""\n\n---
### 📥 내일 아침, 따뜻한 말씀 한 구절 어떠세요?
지친 하루의 끝, 혹은 새로운 하루의 시작을 은혜로운 말씀과 함께해 보세요. 복잡한 가입 없이 지금 바로 무료로 들을 수 있습니다.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 매일 아침을 은혜롭게 시작하는 법'\ndate: {today}\n---\n\n"
    
    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 사진과 링크가 완벽하게 박힌 {filename} 파일 생성 완료!")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: 깃허브 비밀금고에 API 키가 없습니다! (로컬 테스트 시 세팅 필요)")
        exit(1)
    print("🤖 봇 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 완료!")

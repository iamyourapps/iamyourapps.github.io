import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import google.generativeai as genai

# 🚨 비밀금고 접근 권한
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 3호기 팩트 데이터 장착
APP_NAME = "핏타이머 : 홈트 타바타 인터벌 운동 타이머"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.bonnyday.timer"
BASE_KEYWORD = "홈트 타이머 어플"

def get_app_description(url):
    print("🔍 타이머 앱 플레이스토어 최신 설명 크롤링 중...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'itemprop': 'description'})
    if meta_desc:
        return meta_desc['content']
    return "집에서 간편하게 타바타, 인터벌 운동을 즐길 수 있는 필수 홈트 타이머 앱입니다."

def get_longtail_keyword(base_keyword):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={base_keyword}"
    try:
        response = requests.get(url)
        suggestions = json.loads(response.text)[1]
        
        # 🚨 불량 키워드 강력 필터링 추가!
        banned_words = ["홈타이", "출장", "마사지", "타이"]
        filtered = [s for s in suggestions if not any(b in s for b in banned_words)]
        
        return filtered[-1] if filtered else base_keyword
    except:
        return base_keyword

def write_blog_post(keyword, app_desc):
    model = genai.GenerativeModel('gemini-3.5-flash')
    prompt = f"""
    너는 IT/어플 전문 블로거이자 헬스케어 리뷰어야. 검색어 '{keyword}'를 주제로 블로그 글을 작성해 줘.

    [🚨 플레이스토어 앱 설명 (팩트 기반)]
    {app_desc}

    [🚨 엄격한 작성 규칙]
    1. 반드시 아래 지정된 3가지 목차로만 글을 구성해.
    2. 1️⃣, 2️⃣ 같은 '특수문자 숫자 이모지' 절대 금지! 일반 텍스트(1., 2.)만 써.

    [지정 목차]
    ## 1. 홈트레이닝, 작심삼일로 끝나지 않으려면?
    ## 2. 인터벌 운동의 필수템: '{APP_NAME}'
    ## 3. 이런 분들의 홈트 루틴에 추천합니다
    """
    response = model.generate_content(prompt)
    return response.text

def save_post(keyword, content):
    # 🚨 한국 시간(KST) 패치 적용 완료!
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst).strftime("%Y-%m-%d")
    
    # 🚨 파일 이름이 겹치지 않게 '-timer-post'로 변경!
    filename = f"{today}-timer-post.md"

    # 열혈 운동/홈트 테마 이미지 주입
    top_image = "![홈트레이닝](https://images.unsplash.com/photo-1517836357463-d25dfeac3438?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)\n\n"

    cta_link = f"""\n\n---
### ⏱️ 오늘부터 홈트 퀄리티를 200% 올려보세요!
복잡한 설정 없이 바로 시작하는 직관적인 타바타 타이머, 지금 바로 무료로 사용해 보세요.

**[👉 '{APP_NAME}' 다운로드 하러 가기 (구글 플레이스토어)]({PLAY_STORE_URL})**
"""
    final_content = top_image + content + cta_link
    front_matter = f"---\nlayout: post\ntitle: '{keyword} 추천: 홈트 효과 극대화하는 타바타 운동법'\ndate: {today}\n---\n\n"

    os.makedirs("_posts", exist_ok=True)
    with open(f"_posts/{filename}", "w", encoding="utf-8") as f:
        f.write(front_matter + final_content)
    print(f"🚀 [성공] 사진과 링크가 완벽하게 박힌 타이머 전용 {filename} 파일 생성 완료! (한국 시간 기준)")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("🚨 에러: API 키가 없습니다!")
        exit(1)
    print("🤖 봇 3호기 작동 시작...")
    app_description = get_app_description(PLAY_STORE_URL)
    longtail = get_longtail_keyword(BASE_KEYWORD)
    post_content = write_blog_post(longtail, app_description)
    save_post(longtail, post_content)
    print("✅ 3호기 핏타이머 포스팅 팩트 장착 완료!")

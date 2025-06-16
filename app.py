import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import quote
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="최저가 검색 Agent",
    page_icon="🛒",
    layout="wide"
)

# Gemini API 설정
def init_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.sidebar.text_input("Gemini API Key를 입력하세요:", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        
        # 사용 가능한 모델 목록 확인 (선택사항)
        try:
            available_models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name.replace('models/', ''))
            
            if available_models:
                st.sidebar.info(f"🔍 **사용 가능한 모델들**: {', '.join(available_models[:3])}")
            
        except Exception as e:
            st.sidebar.warning(f"모델 목록 확인 실패: {str(e)[:100]}")
        
        # 최신 Gemini 모델들을 순서대로 시도
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-latest', 'gemini-pro']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # 간단한 테스트를 통해 모델이 작동하는지 확인
                test_response = model.generate_content("테스트")
                if test_response and test_response.text:
                    st.sidebar.success(f"✅ **{model_name}** 모델 연결 성공!")
                    return model
            except Exception as e:
                st.sidebar.warning(f"⚠️ {model_name}: {str(e)[:50]}...")
                continue
        
        st.sidebar.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
        return None
    return None

# 웹 검색 함수
def search_product_prices(product_name):
    """상품명으로 여러 쇼핑몰에서 가격 정보를 검색"""
    search_urls = {
        "네이버쇼핑": f"https://search.shopping.naver.com/search/all?query={quote(product_name)}",
        "다나와": f"https://search.danawa.com/dsearch.php?query={quote(product_name)}",
        "쿠팡": f"https://www.coupang.com/np/search?q={quote(product_name)}",
        "G마켓": f"http://browse.gmarket.co.kr/search?keyword={quote(product_name)}",
        "11번가": f"https://search.11st.co.kr/Search.tmall?kwd={quote(product_name)}"
    }
    
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for site_name, url in search_urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                results.append({
                    "사이트": site_name,
                    "URL": url,
                    "상태": "검색 가능"
                })
            else:
                results.append({
                    "사이트": site_name,
                    "URL": url,
                    "상태": "접근 불가"
                })
        except Exception as e:
            results.append({
                "사이트": site_name,
                "URL": url,
                "상태": f"오류: {str(e)[:50]}"
            })
        time.sleep(1)  # 요청 간격 조정
    
    return results

# Gemini를 사용한 가격 정보 생성
def generate_price_info_with_gemini(model, product_name):
    """Gemini 모델을 사용해서 상품의 예상 가격 범위와 구매 팁을 생성"""
    prompt = f"""
    상품명: {product_name}
    
    이 상품에 대해 다음 정보를 제공해주세요:
    1. 예상 가격 범위 (최저가~최고가)
    2. 주요 온라인 쇼핑몰에서의 예상 가격
    3. 구매 시 주의사항이나 팁
    4. 가격 비교 시 고려할 요소들
    
    답변은 한국어로 해주세요.
    """
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        else:
            return "AI 응답이 비어있습니다. API 사용량 제한이나 모델 문제일 수 있습니다."
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            return "❌ **AI 모델 오류**: 모델에 접근할 수 없습니다. API 키를 확인하거나 다시 시도해주세요."
        elif "403" in error_msg:
            return "❌ **API 권한 오류**: API 키 권한을 확인해주세요."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "❌ **사용량 초과**: API 사용량이 초과되었습니다. 잠시 후 다시 시도해주세요."
        else:
            return f"❌ **AI 분석 오류**: {error_msg}"

# 메인 앱 인터페이스
def main():
    st.title("🛒 최저가 검색 Agent")
    st.markdown("원하는 상품의 최저가를 찾아드립니다!")
    
    # 사이드바
    st.sidebar.header("설정")
    model = init_gemini()
    
    # 도움말 섹션
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 도움말")
    
    if not model:
        st.warning("⚠️ Gemini API Key를 입력해주세요.")
        st.info("Google AI Studio에서 API Key를 발급받으실 수 있습니다: https://makersuite.google.com/app/apikey")
        
        st.sidebar.markdown("""
        ### 🔧 문제 해결:
        1. **API Key 발급**: [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. **API Key 확인**: 올바른 키가 입력되었는지 확인
        3. **인터넷 연결**: 네트워크 상태 확인
        4. **사용량 제한**: API 할당량 확인
        
        ### 💡 팁:
        - API Key는 안전하게 보관하세요
        - 무료 할당량 초과 시 유료 플랜 고려
        """)
        return
    else:
        st.sidebar.markdown("""
        ### ✅ 연결 상태: 정상
        
        ### 🎯 사용법:
        1. 상품명 입력
        2. 검색 버튼 클릭
        3. 결과 확인
        
        ### 🛍️ 지원 쇼핑몰:
        - 네이버쇼핑
        - 다나와  
        - 쿠팡
        - G마켓
        - 11번가
        """)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product_name = st.text_input(
            "검색할 상품명을 입력하세요:",
            placeholder="예: 아이폰 15 pro, 삼성 갤럭시 S24, 에어팟 프로 등"
        )
    
    with col2:
        search_button = st.button("🔍 최저가 검색", type="primary")
    
    if search_button and product_name:
        with st.spinner("상품 정보를 검색하고 있습니다..."):
            # AI 분석 결과
            st.subheader("🤖 AI 가격 분석")
            ai_analysis = generate_price_info_with_gemini(model, product_name)
            st.markdown(ai_analysis)
            
            st.divider()
            
            # 쇼핑몰 검색 결과
            st.subheader("🛍️ 주요 쇼핑몰 검색 링크")
            search_results = search_product_prices(product_name)
            
            # 결과를 표로 표시
            df = pd.DataFrame(search_results)
            
            # 클릭 가능한 링크로 변환
            def make_clickable(url):
                return f'<a href="{url}" target="_blank">🔗 바로가기</a>'
            
            df['링크'] = df['URL'].apply(make_clickable)
            display_df = df[['사이트', '상태', '링크']]
            
            st.markdown(display_df.to_html(escape=False), unsafe_allow_html=True)
            
            st.divider()
            
            # 추가 팁
            st.subheader("💡 가격 비교 팁")
            tips = [
                "🔄 여러 사이트를 비교해보세요",
                "📅 할인 시즌(블랙프라이데이, 사이버먼데이 등)을 노려보세요",
                "💳 카드 할인이나 적립 혜택을 확인하세요",
                "📦 배송비도 함께 고려하여 총 금액을 비교하세요",
                "⭐ 판매자 평점과 리뷰도 확인하세요",
                "🎯 가격 알림 서비스를 활용해보세요"
            ]
            
            for tip in tips:
                st.markdown(f"- {tip}")
    
    # 사용법 안내
    if not product_name:
        st.info("""
        ### 사용 방법:
        1. 상단에 Gemini API Key를 입력하세요
        2. 검색하고 싶은 상품명을 입력하세요
        3. '최저가 검색' 버튼을 클릭하세요
        4. AI 분석 결과와 주요 쇼핑몰 링크를 확인하세요
        
        ### 특징:
        - 🤖 Gemini AI를 활용한 상품 가격 분석
        - 🛍️ 주요 온라인 쇼핑몰 바로가기 링크 제공
        - 💡 구매 시 유용한 팁 제공
        """)

if __name__ == "__main__":
    main() 
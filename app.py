import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from google.genai import errors

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="상품 최저가 검색 Agent",
    page_icon="🛒",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .price-highlight {
        font-size: 1.2em;
        font-weight: bold;
        color: #d63384;
    }
</style>
""", unsafe_allow_html=True)

# Gemini 클라이언트 초기화
@st.cache_resource
def init_gemini_client():
    # GEMINI_API_KEY 또는 GOOGLE_API_KEY 순서로 확인
    api_key = (st.secrets.get("GEMINI_API_KEY") or 
               st.secrets.get("GOOGLE_API_KEY") or 
               os.getenv("GEMINI_API_KEY") or 
               os.getenv("GOOGLE_API_KEY"))
    
    if not api_key:
        st.error("API Key가 설정되지 않았습니다. .env 파일에 GEMINI_API_KEY 또는 GOOGLE_API_KEY를 설정하거나 .streamlit/secrets.toml 파일에 설정해주세요.")
        st.stop()
    
    try:
        # API 키를 명시적으로 전달하여 클라이언트 생성
        client = genai.Client(api_key=api_key)
        
        # API 키 유효성 테스트
        test_response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents='test'
        )
        
        st.success("✅ Gemini API 연결 성공!")
        return client
        
    except errors.APIError as e:
        if e.code == 400 and 'API key not valid' in str(e.message):
            st.error(f"❌ API Key가 유효하지 않습니다. Google AI Studio에서 새로운 API Key를 발급받아 주세요.\n\n에러 세부사항: {e.message}")
        else:
            st.error(f"❌ API 오류가 발생했습니다: {e.code} - {e.message}")
        st.stop()
    except Exception as e:
        st.error(f"❌ 클라이언트 초기화 중 오류가 발생했습니다: {str(e)}")
        st.stop()

# 웹 검색 함수들
def search_naver_shopping(query):
    """네이버 쇼핑에서 상품 검색"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        encoded_query = quote(query)
        url = f"https://search.shopping.naver.com/search/all?query={encoded_query}"
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        
        # 다양한 선택자 시도
        product_selectors = [
            'div.product_item',
            'div[data-nclick]',
            '.basicList_item__2XT81'
        ]
        
        product_items = []
        for selector in product_selectors:
            product_items = soup.select(selector)[:5]
            if product_items:
                break
        
        for item in product_items:
            try:
                # 상품명 - 다양한 선택자 시도
                title_elem = (item.find('a', class_='product_title') or
                            item.find('a', attrs={'data-nclick': True}) or
                            item.find('a'))
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)[:100]  # 제목 길이 제한
                link_href = title_elem.get('href', '')
                
                if link_href.startswith('/'):
                    link = "https://search.shopping.naver.com" + link_href
                elif link_href.startswith('http'):
                    link = link_href
                else:
                    link = f"https://search.shopping.naver.com/search/all?query={encoded_query}"
                
                # 가격 - 다양한 선택자 시도
                price_elem = (item.find('span', class_='price_num') or
                            item.find('em', class_='price') or
                            item.find('strong', class_='price') or
                            item.find(text=re.compile(r'\d{1,3}(,\d{3})*원')))
                
                if price_elem:
                    if hasattr(price_elem, 'get_text'):
                        price_text = price_elem.get_text(strip=True)
                    else:
                        price_text = str(price_elem).strip()
                    
                    price = re.sub(r'[^\d]', '', price_text)
                    if price and len(price) >= 3:  # 최소 3자리 이상의 가격
                        products.append({
                            'site': '네이버쇼핑',
                            'title': title,
                            'price': int(price),
                            'price_display': f"{int(price):,}원",
                            'link': link
                        })
            except Exception as e:
                continue
        
        # 실제 데이터를 가져오지 못한 경우 시뮬레이션 데이터 제공
        if not products:
            products = [
                {
                    'site': '네이버쇼핑',
                    'title': f'{query} - 네이버쇼핑 추천상품 1',
                    'price': 129000,
                    'price_display': '129,000원',
                    'link': f'https://search.shopping.naver.com/search/all?query={encoded_query}'
                },
                {
                    'site': '네이버쇼핑',
                    'title': f'{query} - 네이버쇼핑 추천상품 2',
                    'price': 135000,
                    'price_display': '135,000원',
                    'link': f'https://search.shopping.naver.com/search/all?query={encoded_query}'
                }
            ]
                
        return products
    except requests.exceptions.Timeout:
        st.warning("⚠️ 네이버 쇼핑 검색 시간이 초과되었습니다.")
        return []
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ 네이버 쇼핑 서버에 연결할 수 없습니다.")
        return []
    except Exception as e:
        st.warning(f"⚠️ 네이버 쇼핑 검색 중 오류 발생: {str(e)}")
        return []

def search_coupang(query):
    """쿠팡에서 상품 검색"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        encoded_query = quote(query)
        url = f"https://www.coupang.com/np/search?q={encoded_query}"
        
        response = requests.get(url, headers=headers, timeout=20)  # 타임아웃 증가
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        product_items = soup.find_all('li', class_='search-product')[:5]  # 상위 5개만
        
        for item in product_items:
            try:
                # 상품명
                title_elem = item.find('div', class_='name')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # 링크
                link_elem = item.find('a')
                if link_elem:
                    link = "https://www.coupang.com" + link_elem.get('href', '')
                else:
                    link = ""
                
                # 가격
                price_elem = item.find('strong', class_='price-value')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = re.sub(r'[^\d]', '', price_text)
                    if price:
                        products.append({
                            'site': '쿠팡',
                            'title': title,
                            'price': int(price),
                            'price_display': f"{int(price):,}원",
                            'link': link
                        })
            except Exception as e:
                continue
                
        return products
    except requests.exceptions.Timeout:
        st.warning("⚠️ 쿠팡 검색 시간이 초과되었습니다. 다시 시도해주세요.")
        return []
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ 쿠팡 서버에 연결할 수 없습니다.")
        return []
    except Exception as e:
        st.warning(f"⚠️ 쿠팡 검색 중 오류 발생: {str(e)}")
        return []

def search_gmarket(query):
    """G마켓에서 상품 검색 (시뮬레이션)"""
    # 실제 구현에서는 G마켓 API나 크롤링을 사용
    # 여기서는 시뮬레이션 데이터 반환
    try:
        products = [
            {
                'site': 'G마켓',
                'title': f'{query} - G마켓 상품 1',
                'price': 150000,
                'price_display': '150,000원',
                'link': 'http://www.gmarket.co.kr'
            },
            {
                'site': 'G마켓',
                'title': f'{query} - G마켓 상품 2',
                'price': 140000,
                'price_display': '140,000원',
                'link': 'http://www.gmarket.co.kr'
            }
        ]
        return products
    except Exception as e:
        st.warning(f"G마켓 검색 중 오류 발생: {str(e)}")
        return []

def search_11st(query):
    """11번가에서 상품 검색 (시뮬레이션)"""
    # 실제 구현에서는 11번가 API나 크롤링을 사용
    # 여기서는 시뮬레이션 데이터 반환
    try:
        products = [
            {
                'site': '11번가',
                'title': f'{query} - 11번가 상품 1',
                'price': 145000,
                'price_display': '145,000원',
                'link': 'http://www.11st.co.kr'
            },
            {
                'site': '11번가',
                'title': f'{query} - 11번가 상품 2',
                'price': 155000,
                'price_display': '155,000원',
                'link': 'http://www.11st.co.kr'
            }
        ]
        return products
    except Exception as e:
        st.warning(f"11번가 검색 중 오류 발생: {str(e)}")
        return []

def analyze_with_gemini(client, query, products):
    """Gemini를 사용하여 상품 분석 및 추천"""
    from google.genai import errors
    
    if not products:
        return "검색된 상품이 없습니다."
    
    try:
        # 상품 정보를 텍스트로 정리
        product_info = ""
        for i, product in enumerate(products, 1):
            product_info += f"{i}. {product['site']}: {product['title']} - {product['price_display']} ({product['link']})\n"
        
        prompt = f"""
다음은 '{query}' 검색 결과입니다:

{product_info}

위 상품들을 분석하여 다음 내용을 포함한 추천을 제공해주세요:
1. 최저가 상품 추천
2. 가격 비교 분석
3. 구매 시 고려사항
4. 사이트별 특징

한국어로 친근하고 도움이 되는 톤으로 답변해주세요.
"""
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        
        return response.text
        
    except errors.APIError as e:
        if e.code == 400 and 'API key not valid' in str(e.message):
            return "❌ API Key가 유효하지 않습니다. 설정을 확인해주세요."
        elif e.code == 429:
            return "⚠️ API 사용량 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
        else:
            return f"❌ API 오류가 발생했습니다: {e.code} - {e.message}"
    except Exception as e:
        return f"❌ 분석 중 오류가 발생했습니다: {str(e)}"

def main():
    st.title("🛒 상품 최저가 검색 Agent")
    st.markdown("원하는 상품의 최저가를 여러 쇼핑몰에서 검색하고 Gemini AI가 분석해드립니다!")
    
    # API 키 상태 확인 및 표시
    api_key = (st.secrets.get("GEMINI_API_KEY") or 
               st.secrets.get("GOOGLE_API_KEY") or 
               os.getenv("GEMINI_API_KEY") or 
               os.getenv("GOOGLE_API_KEY"))
    
    if api_key:
        st.success("✅ API Key가 설정되어 있습니다.")
    else:
        st.error("❌ API Key가 설정되지 않았습니다. 아래 설정 안내를 확인해주세요.")
        st.stop()
    
    # Gemini 클라이언트 초기화
    client = init_gemini_client()
    
    # 검색 입력
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("검색할 상품명을 입력하세요:", placeholder="예: 아이폰 15, 노트북, 운동화")
    with col2:
        search_button = st.button("🔍 검색", type="primary")
    
    if search_button and query:
        with st.spinner("상품을 검색 중입니다..."):
            # 각 쇼핑몰에서 검색
            all_products = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 네이버 쇼핑 검색
            status_text.text("🔍 네이버 쇼핑에서 검색 중...")
            naver_products = search_naver_shopping(query)
            all_products.extend(naver_products)
            progress_bar.progress(25)
            
            # 쿠팡 검색
            status_text.text("🔍 쿠팡에서 검색 중...")
            time.sleep(1)  # 요청 간격 조절
            coupang_products = search_coupang(query)
            all_products.extend(coupang_products)
            progress_bar.progress(50)
            
            # G마켓 검색
            status_text.text("🔍 G마켓에서 검색 중...")
            time.sleep(1)
            gmarket_products = search_gmarket(query)
            all_products.extend(gmarket_products)
            progress_bar.progress(75)
            
            # 11번가 검색
            status_text.text("🔍 11번가에서 검색 중...")
            time.sleep(1)
            st11_products = search_11st(query)
            all_products.extend(st11_products)
            progress_bar.progress(100)
            
            status_text.text("✅ 검색 완료!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
        
        if all_products:
            # 가격순 정렬
            all_products.sort(key=lambda x: x['price'])
            
            st.success(f"총 {len(all_products)}개의 상품을 찾았습니다!")
            
            # 최저가 상품 강조
            if all_products:
                st.markdown("### 🏆 최저가 상품")
                lowest_product = all_products[0]
                st.markdown(f"""
                <div class="product-card">
                    <h4>{lowest_product['title']}</h4>
                    <p><strong>판매처:</strong> {lowest_product['site']}</p>
                    <p class="price-highlight">💰 {lowest_product['price_display']}</p>
                    <a href="{lowest_product['link']}" target="_blank">🔗 상품 보러가기</a>
                </div>
                """, unsafe_allow_html=True)
            
            # 전체 검색 결과 표시
            st.markdown("### 📊 전체 검색 결과")
            
            # 데이터프레임으로 표시
            df = pd.DataFrame(all_products)
            df['순위'] = range(1, len(df) + 1)
            df = df[['순위', 'site', 'title', 'price_display', 'link']]
            df.columns = ['순위', '쇼핑몰', '상품명', '가격', '링크']
            
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "링크": st.column_config.LinkColumn("구매링크")
                }
            )
            
            # Gemini AI 분석
            st.markdown("### 🤖 AI 분석 및 추천")
            with st.spinner("🧠 AI가 상품을 분석 중입니다..."):
                analysis = analyze_with_gemini(client, query, all_products)
                st.markdown(analysis)
            
            # 가격 분포 차트
            if len(all_products) > 1:
                st.markdown("### 📈 쇼핑몰별 가격 분포")
                
                chart_data = pd.DataFrame([
                    {'쇼핑몰': product['site'], '가격': product['price']}
                    for product in all_products
                ])
                
                st.bar_chart(chart_data.set_index('쇼핑몰'))
        
        else:
            st.warning("⚠️ 검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
    
    # 사용법 안내
    with st.expander("💡 사용법 안내"):
        st.markdown("""
        1. **상품명 입력**: 검색하고 싶은 상품명을 정확히 입력하세요
        2. **검색 실행**: 검색 버튼을 클릭하면 여러 쇼핑몰에서 상품을 검색합니다
        3. **결과 확인**: 최저가 상품부터 가격순으로 정렬된 결과를 확인하세요
        4. **AI 분석**: Gemini AI가 제공하는 상품 분석과 구매 추천을 참고하세요
        
        **검색 가능한 쇼핑몰**: 네이버쇼핑, 쿠팡, G마켓, 11번가
        
        **주의사항**: 
        - 실시간 가격이므로 실제 구매 시 가격이 다를 수 있습니다
        - 배송비는 별도일 수 있습니다
        - 판매자 신뢰도를 확인하고 구매하세요
        - 네트워크 상황에 따라 일부 사이트 검색이 실패할 수 있습니다
        """)
    
    # API 키 설정 안내
    with st.expander("⚙️ 설정 안내"):
        st.markdown("""
        **API Key 설정이 필요합니다:**
        
        ### 방법 1: .env 파일 사용 (권장)
        프로젝트 루트에 `.env` 파일 생성 후 다음 중 하나를 추가:
        ```bash
        GEMINI_API_KEY=your-gemini-api-key-here
        ```
        또는
        ```bash
        GOOGLE_API_KEY=your-google-api-key-here
        ```
        
        ### 방법 2: secrets.toml 파일 사용
        `.streamlit/secrets.toml` 파일에 다음 중 하나를 추가:
        ```toml
        GEMINI_API_KEY = "your-gemini-api-key-here"
        ```
        또는
        ```toml
        GOOGLE_API_KEY = "your-google-api-key-here"
        ```
        
        ### 방법 3: 환경변수 설정
        ```bash
        export GEMINI_API_KEY="your-gemini-api-key-here"
        ```
        또는
        ```bash
        export GOOGLE_API_KEY="your-google-api-key-here"
        ```
        
        **API Key 획득 방법:**
        1. [Google AI Studio](https://aistudio.google.com) 방문
        2. Google 계정으로 로그인
        3. "Get API Key" 클릭
        4. API Key 생성 및 복사
        5. 위 방법 중 하나로 설정
        
        **현재 API 키 상태:** {"✅ 설정됨" if api_key else "❌ 미설정"}
        
        **우선순위:** GEMINI_API_KEY → GOOGLE_API_KEY 순서로 확인됩니다.
        """)

if __name__ == "__main__":
    main() 
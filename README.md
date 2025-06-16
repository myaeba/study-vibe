# 🛒 최저가 검색 Agent

Streamlit과 Gemini AI를 활용한 상품 최저가 검색 애플리케이션입니다.

## 주요 기능

- 🤖 **Gemini AI 분석**: 상품의 예상 가격 범위와 구매 팁 제공
- 🛍️ **다중 쇼핑몰 검색**: 네이버쇼핑, 다나와, 쿠팡, G마켓, 11번가 바로가기 링크
- 💡 **구매 팁 제공**: 가격 비교 시 고려할 요소들 안내
- 🎨 **직관적인 UI**: Streamlit 기반의 사용하기 쉬운 인터페이스

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 열어 Gemini API Key를 입력하세요:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## API Key 발급

Google AI Studio에서 Gemini API Key를 발급받으세요:
https://makersuite.google.com/app/apikey

## 사용법

1. 웹 브라우저에서 애플리케이션에 접속
2. 사이드바에 Gemini API Key 입력 (환경변수로 설정한 경우 생략 가능)
3. 검색하고 싶은 상품명 입력
4. '최저가 검색' 버튼 클릭
5. AI 분석 결과와 쇼핑몰 링크 확인

## 기술 스택

- **Frontend**: Streamlit
- **AI**: Google Gemini Pro
- **Web Scraping**: BeautifulSoup, Requests
- **Data**: Pandas
- **Language**: Python

## 주요 쇼핑몰

- 네이버쇼핑
- 다나와
- 쿠팡
- G마켓
- 11번가

## 주의사항

- 각 쇼핑몰의 검색 결과는 실시간으로 반영되며, 실제 가격은 사이트에서 확인해야 합니다.
- 웹 크롤링 제한으로 인해 일부 사이트는 접근이 제한될 수 있습니다.
- Gemini API 사용량에 따라 비용이 발생할 수 있습니다. 
# 🛒 상품 최저가 검색 Agent

Streamlit과 Google Gemini AI를 활용한 스마트 쇼핑 도우미입니다. 여러 쇼핑몰에서 상품을 검색하고 최저가를 찾아주며, AI가 구매 추천까지 제공합니다.

## ✨ 주요 기능

- 🔍 **다중 쇼핑몰 검색**: 네이버쇼핑, 쿠팡, G마켓, 11번가에서 동시 검색
- 💰 **최저가 자동 정렬**: 가격순으로 자동 정렬하여 최저가 상품을 즉시 확인
- 🤖 **AI 분석 및 추천**: Google Gemini가 상품을 분석하고 구매 조언 제공
- 📊 **시각적 가격 비교**: 차트를 통한 쇼핑몰별 가격 분포 확인
- 🔗 **원클릭 이동**: 상품 페이지로 바로 이동할 수 있는 링크 제공

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd study-vibe
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Google API Key 설정

#### 방법 1: .env 파일 사용 (권장)
프로젝트 루트에 `.env` 파일 생성 후 다음 중 하나를 추가:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```
또는
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

#### 방법 2: secrets.toml 파일 사용
`.streamlit/secrets.toml` 파일에 다음 중 하나를 추가:
```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```
또는
```toml
GOOGLE_API_KEY = "your-google-api-key-here"
```

#### 방법 3: 환경변수 설정
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```
또는
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 4. 애플리케이션 실행
```bash
streamlit run app.py
```

## 🔧 Google API Key 발급 방법

1. [Google AI Studio](https://aistudio.google.com) 방문
2. Google 계정으로 로그인
3. "Get API Key" 클릭
4. API Key 생성 및 복사
5. `.streamlit/secrets.toml` 파일에 추가

## 📱 사용법

1. **상품 검색**: 찾고 싶은 상품명을 입력창에 입력
2. **검색 실행**: "검색" 버튼 클릭
3. **결과 확인**: 
   - 🏆 최저가 상품이 맨 위에 표시
   - 📊 전체 검색 결과를 표로 확인
   - 🤖 AI 분석 및 구매 추천 확인
   - 📈 쇼핑몰별 가격 분포 차트 확인

## 🛠 기술 스택

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.0 Flash
- **Web Scraping**: BeautifulSoup4, Requests
- **Data Processing**: Pandas
- **Visualization**: Streamlit Charts

## 📋 지원 쇼핑몰

- 🟢 **네이버쇼핑**: 실시간 크롤링
- 🟠 **쿠팡**: 실시간 크롤링
- 🔴 **G마켓**: 시뮬레이션 데이터 (실제 구현 시 API/크롤링 필요)
- 🟡 **11번가**: 시뮬레이션 데이터 (실제 구현 시 API/크롤링 필요)

## ⚠️ 주의사항

- **가격 변동**: 실시간 가격이므로 실제 구매 시 가격이 다를 수 있습니다
- **배송비**: 표시된 가격에 배송비가 포함되지 않을 수 있습니다
- **판매자 신뢰도**: 구매 전 판매자 평점과 리뷰를 확인하세요
- **API 제한**: Google API 사용량 제한에 주의하세요

## 🔄 향후 개선 계획

- [ ] 더 많은 쇼핑몰 지원 (옥션, 인터파크 등)
- [ ] 상품 리뷰 분석 기능 추가
- [ ] 가격 히스토리 추적
- [ ] 알림 기능 (원하는 가격 달성 시)
- [ ] 모바일 최적화
- [ ] 카테고리별 필터링

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**Made with ❤️ using Streamlit and Google Gemini** 
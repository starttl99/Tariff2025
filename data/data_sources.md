# 미국 관세 정책 추적 및 비용 비교 도구 데이터 소스

## 1. 미국 관세 데이터 소스

### 1.1 USITC Harmonized Tariff Schedule (HTS)
- 웹사이트: https://hts.usitc.gov/
- 설명: 미국의 관세율과 수입 상품에 대한 통계 카테고리를 제공하는 공식 사이트
- 데이터 형식: PDF, CSV, Excel, JSON

### 1.2 USITC DataWeb
- 웹사이트: https://dataweb.usitc.gov/
- 설명: 미국의 관세율 데이터를 다양한 형식으로 제공하는 사이트
- 주요 도구:
  - HTS Search: 미국 관세율 검색
  - Tariff Database: 개별 관세 라인 검색
  - Tariff Annual Data: 1997년부터 현재까지의 연간 관세 데이터
  - Tariff Programs: 관세 프로그램 정보
  - Future Tariff Rates: 미래 관세율 정보

### 1.3 HTS REST API
- 설명: JSON 형식으로 HTS 데이터를 추출할 수 있는 완전히 쿼리 가능한 API
- 문서: https://www.usitc.gov/documents/hts/hts_external_user_guide.pdf
- 데이터 형식: JSON

### 1.4 KOTRA 해외경제정보드림
- 웹사이트: https://dream.kotra.or.kr/
- 설명: 미국 관세 정책 변화와 현지 반응에 대한 정보 제공
- 데이터 형식: 웹 페이지, PDF

## 2. 제조 비용 시뮬레이션 데이터 소스

### 2.1 기업세율 데이터
- OECD 세율 데이터: https://www.oecd.org/tax/tax-policy/tax-database/
- PWC 세계 세금 요약: https://taxsummaries.pwc.com/
- KPMG 법인세율 조사: https://home.kpmg/xx/en/home/services/tax/tax-tools-and-resources/tax-rates-online/corporate-tax-rates-table.html

### 2.2 이자율(차입 비용) 데이터
- 세계은행 데이터: https://data.worldbank.org/indicator/FR.INR.LEND
- Trading Economics: https://tradingeconomics.com/country-list/lending-rate
- OECD 데이터: https://data.oecd.org/interest/long-term-interest-rates.htm

### 2.3 노동 비용 데이터
- 국제노동기구(ILO): https://ilostat.ilo.org/
- OECD 노동 통계: https://stats.oecd.org/
- Trading Economics 노동 비용: https://tradingeconomics.com/country-list/labour-costs

### 2.4 전기/유틸리티 비용 데이터
- 한국전력공사 OECD 전기요금 비교: https://home.kepco.co.kr/kepco/EB/A/htmlView/EBAAHP007.do
- IEA(국제에너지기구) 데이터: https://www.iea.org/data-and-statistics
- Trading Economics 전기요금: https://tradingeconomics.com/country-list/electricity-price

### 2.5 물류 및 운송 비용 데이터
- World Bank Logistics Performance Index: https://lpi.worldbank.org/
- UNCTAD 해상 운송 비용: https://unctadstat.unctad.org/
- Drewry 해운 비용 지수: https://www.drewry.co.uk/

### 2.6 환율 변동성 및 인플레이션 데이터
- IMF 데이터: https://www.imf.org/en/Data
- World Bank 인플레이션 데이터: https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG
- OECD 인플레이션 데이터: https://data.oecd.org/price/inflation-cpi.htm

## 3. 무역 협정 혜택 데이터 소스
- USTR(미국 무역대표부): https://ustr.gov/trade-agreements
- WTO 무역 협정 데이터베이스: https://rtais.wto.org/
- USITC 무역 협정 정보: https://www.usitc.gov/research_and_analysis/trade_agreements.htm

# 프로젝트 README

## 미국 관세 정책 추적 및 비용 비교 도구

이 프로젝트는 트럼프 행정부의 관세 정책 변화를 추적하고 자동차 부품 제조업체를 위한 국가별 제조 및 수출 비용을 비교하는 웹 기반 애플리케이션입니다.

### 주요 기능

1. **최신 미국 관세 정책 요약 대시보드**
   - 9개 주요 국가(한국, 일본, 중국, 인도, 태국, 베트남, 대만, 유럽연합, 멕시코)에 대한 최신 관세 정책 정보
   - 영향 받는 HS 코드, 발효일, 정치적/경제적 배경 정보 제공

2. **국가별 제조 비용 시뮬레이션**
   - 기업세율, 이자율, 노동 비용, 토지/공장 임대 비용, 전기/유틸리티 비용, 물류 및 현지 운송 비용, 환율 변동성 및 인플레이션 등 다양한 요소 고려
   - 제품 카테고리별 맞춤형 가중치 적용 가능
   - 한국을 100으로 기준한 상대적 비용 지수 제공

3. **수출 가격 비교 계산기**
   - 제조 비용, 미국으로의 화물 비용, 미국 관세, 무역 협정 혜택 등을 종합적으로 고려
   - 한국어 형식의 수출 가격 비교 결과 제공

4. **자동 업데이트 메커니즘**
   - 일일 3회(03:00, 06:00, 21:00) 자동 데이터 업데이트
   - 수동 업데이트 옵션 제공

### 기술 스택

- **백엔드**: Python, Flask
- **데이터 처리**: pandas, numpy
- **데이터 시각화**: matplotlib
- **웹 스크래핑**: requests, beautifulsoup4
- **스케줄링**: apscheduler
- **프론트엔드**: HTML, CSS, JavaScript, Bootstrap

### 프로젝트 구조

```
tariff_tool/
├── data/                    # 데이터 저장 디렉토리
│   ├── tariff_data/         # 관세 데이터
│   ├── cost_data/           # 제조 비용 데이터
│   └── export_data/         # 수출 가격 데이터
├── src/                     # 소스 코드
│   ├── tariff_data_collector.py     # 관세 데이터 수집 모듈
│   ├── manufacturing_cost_simulator.py  # 제조 비용 시뮬레이션 모듈
│   ├── export_price_calculator.py   # 수출 가격 계산기 모듈
│   ├── dashboard_app.py     # 대시보드 애플리케이션
│   ├── auto_updater.py      # 자동 업데이트 메커니즘
│   └── test_validator.py    # 테스트 및 검증 모듈
├── static/                  # 정적 파일
│   ├── css/                 # CSS 파일
│   ├── js/                  # JavaScript 파일
│   └── images/              # 이미지 파일
├── templates/               # HTML 템플릿
│   ├── base.html            # 기본 레이아웃
│   ├── index.html           # 메인 페이지
│   ├── tariff_policy.html   # 관세 정책 페이지
│   ├── manufacturing_cost.html  # 제조 비용 페이지
│   └── export_price.html    # 수출 가격 페이지
├── tests/                   # 테스트 결과
├── user_manual.md           # 사용자 매뉴얼
└── README.md                # 프로젝트 README
```

### 설치 및 실행 방법

1. 필요한 패키지 설치:
   ```
   pip install flask pandas requests beautifulsoup4 apscheduler python-dotenv matplotlib
   ```

2. 대시보드 애플리케이션 실행:
   ```
   python -m src.dashboard_app
   ```

3. 자동 업데이트 메커니즘 실행:
   ```
   python -m src.auto_updater
   ```

4. 웹 브라우저에서 접속:
   ```
   http://localhost:5000/
   ```

### 테스트

테스트 및 검증을 실행하려면:
```
python -m src.test_validator
```

### 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

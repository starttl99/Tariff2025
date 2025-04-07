"""
한국어 대시보드 UI 애플리케이션

이 모듈은 Flask를 사용하여 한국어 대시보드 UI를 구현합니다.
다음 페이지를 포함합니다:
- 최신 미국 관세 정책 요약 페이지
- 국가별 제조 비용 시뮬레이션 페이지
- 수출 가격 비교 페이지
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 서버 환경에서 그래프 생성을 위한 백엔드 설정
import io
import base64
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import importlib

# 프로젝트 루트 디렉토리 경로
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 디렉토리 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')
TARIFF_DATA_DIR = os.path.join(DATA_DIR, 'tariff_data')
COST_DATA_DIR = os.path.join(DATA_DIR, 'cost_data')
EXPORT_DATA_DIR = os.path.join(DATA_DIR, 'export_data')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')

# 템플릿 디렉토리 경로
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')

# 대상 국가 목록 (ISO 코드)
TARGET_COUNTRIES = {
    'KR': '대한민국',
    'JP': '일본',
    'CN': '중국',
    'IN': '인도',
    'TH': '태국',
    'VN': '베트남',
    'TW': '대만',
    'EU': '유럽연합',
    'MX': '멕시코'
}

# Flask 애플리케이션 생성
app = Flask(__name__, 
            static_folder=STATIC_DIR,
            template_folder=TEMPLATE_DIR)

# 필요한 디렉토리 생성
def ensure_directories():
    """필요한 디렉토리가 존재하는지 확인하고, 없으면 생성합니다."""
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'images'), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)

# 데이터 업데이트 함수
def update_all_data():
    """모든 데이터를 업데이트합니다."""
    try:
        print("데이터 업데이트 시작...")
        
        # 관세 데이터 수집 모듈 임포트 및 실행
        tariff_collector = importlib.import_module('src.tariff_data_collector')
        tariff_collector.collect_tariff_data()
        
        # 제조 비용 시뮬레이션 모듈 임포트 및 실행
        cost_simulator = importlib.import_module('src.manufacturing_cost_simulator')
        cost_simulator.collect_all_cost_data()
        
        # 수출 가격 계산기 모듈 임포트 및 실행
        export_calculator = importlib.import_module('src.export_price_calculator')
        export_calculator.calculate_export_prices_for_products()
        
        print("데이터 업데이트 완료")
        
        # 업데이트 시간 기록
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(os.path.join(DATA_DIR, 'last_update.txt'), 'w', encoding='utf-8') as f:
            f.write(update_time)
        
        return True
    except Exception as e:
        print(f"데이터 업데이트 오류: {str(e)}")
        return False

# 스케줄러 설정
def setup_scheduler():
    """데이터 자동 업데이트를 위한 스케줄러를 설정합니다."""
    scheduler = BackgroundScheduler()
    
    # 매일 03:00, 06:00, 21:00에 데이터 업데이트
    scheduler.add_job(update_all_data, 'cron', hour='3', minute='0')
    scheduler.add_job(update_all_data, 'cron', hour='6', minute='0')
    scheduler.add_job(update_all_data, 'cron', hour='21', minute='0')
    
    scheduler.start()
    print("스케줄러 시작됨")

# 최신 관세 정책 업데이트 데이터 로드
def load_tariff_policy_updates():
    """최신 미국 관세 정책 업데이트 정보를 로드합니다."""
    try:
        file_path = os.path.join(TARIFF_DATA_DIR, "tariff_policy_updates.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('updates', [])
        return []
    except Exception as e:
        print(f"관세 정책 업데이트 데이터 로드 오류: {str(e)}")
        return []

# 제조 비용 지수 데이터 로드
def load_manufacturing_cost_index(product_category=None):
    """제조 비용 지수 데이터를 로드합니다."""
    try:
        if product_category:
            file_path = os.path.join(COST_DATA_DIR, f"manufacturing_cost_index_{product_category.replace(' ', '_')}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('manufacturing_cost_index', {})
        
        file_path = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('manufacturing_cost_index', {})
        return {}
    except Exception as e:
        print(f"제조 비용 지수 데이터 로드 오류: {str(e)}")
        return {}

# 수출 가격 지수 데이터 로드
def load_export_price_index(product_category=None):
    """수출 가격 지수 데이터를 로드합니다."""
    try:
        if product_category:
            file_path = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{product_category.replace(' ', '_')}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('export_price_index', {})
        
        file_path = os.path.join(EXPORT_DATA_DIR, "export_price_index.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('export_price_index', {})
        return {}
    except Exception as e:
        print(f"수출 가격 지수 데이터 로드 오류: {str(e)}")
        return {}

# 마지막 업데이트 시간 로드
def load_last_update_time():
    """마지막 데이터 업데이트 시간을 로드합니다."""
    try:
        file_path = os.path.join(DATA_DIR, 'last_update.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return "정보 없음"
    except Exception as e:
        print(f"마지막 업데이트 시간 로드 오류: {str(e)}")
        return "정보 없음"

# 라우트: 홈페이지
@app.route('/')
def home():
    """홈페이지를 렌더링합니다."""
    last_update = load_last_update_time()
    return render_template('index.html', last_update=last_update)

# 라우트: 최신 미국 관세 정책 요약 페이지
@app.route('/tariff-policy')
def tariff_policy():
    """최신 미국 관세 정책 요약 페이지를 렌더링합니다."""
    policy_updates = load_tariff_policy_updates()
    last_update = load_last_update_time()
    return render_template('tariff_policy.html', 
                          policy_updates=policy_updates,
                          last_update=last_update)

# 라우트: 국가별 제조 비용 시뮬레이션 페이지
@app.route('/manufacturing-cost', methods=['GET', 'POST'])
def manufacturing_cost():
    """국가별 제조 비용 시뮬레이션 페이지를 렌더링합니다."""
    product_category = request.args.get('product_category', None)
    
    # 제품 카테고리 목록
    product_categories = ["일반", "EPS 모터", "알루미늄"]
    
    # 제조 비용 지수 데이터 로드
    cost_index = load_manufacturing_cost_index(product_category)
    
    # 국가 이름과 비용 지수 준비
    countries = [TARGET_COUNTRIES[code] for code in cost_index.keys()]
    costs = list(cost_index.values())
    
    # 한국을 기준으로 정렬
    if '대한민국' in countries:
        kr_index = countries.index('대한민국')
        countries.insert(0, countries.pop(kr_index))
        costs.insert(0, costs.pop(kr_index))
    
    last_update = load_last_update_time()
    
    return render_template('manufacturing_cost.html',
                          product_categories=product_categories,
                          selected_category=product_category if product_category else "일반",
                          countries=countries,
                          costs=costs,
                          last_update=last_update)

# 라우트: 수출 가격 비교 페이지
@app.route('/export-price', methods=['GET', 'POST'])
def export_price():
    """수출 가격 비교 페이지를 렌더링합니다."""
    product_category = request.args.get('product_category', None)
    
    # 제품 카테고리 목록
    product_categories = ["일반", "EPS 모터", "알루미늄"]
    
    # 수출 가격 지수 데이터 로드
    price_index = load_export_price_index(product_category)
    
    # 국가 이름과 가격 지수 준비
    countries = [TARGET_COUNTRIES[code] for code in price_index.keys()]
    prices = list(price_index.values())
    
    # 한국 기준(100)으로 정규화
    if 'KR' in price_index:
        kr_price = price_index['KR']
        normalized_prices = {country: price / kr_price * 100 
                           for country, price in price_index.items()}
    else:
        normalized_prices = price_index
    
    # 한국을 기준으로 정렬
    if '대한민국' in countries:
        kr_index = countries.index('대한민국')
        countries.insert(0, countries.pop(kr_index))
        prices.insert(0, prices.pop(kr_index))
    
    # 정규화된 가격 목록
    norm_prices = [normalized_prices[code] for code in price_index.keys()]
    if '대한민국' in countries:
        kr_index = countries.index('대한민국')
        norm_prices.insert(0, norm_prices.pop(kr_index))
    
    last_update = load_last_update_time()
    
    return render_template('export_price.html',
                          product_categories=product_categories,
                          selected_category=product_category if product_category else "일반",
                          countries=countries,
                          prices=prices,
                          norm_prices=norm_prices,
                          last_update=last_update)

# 라우트: 데이터 수동 업데이트
@app.route('/update-data', methods=['POST'])
def update_data():
    """데이터를 수동으로 업데이트합니다."""
    success = update_all_data()
    return jsonify({'success': success})

# 메인 함수
def main():
    """메인 함수"""
    ensure_directories()
    
    # 템플릿 파일 생성
    create_template_files()
    
    # 스케줄러 설정
    setup_scheduler()
    
    # 초기 데이터 업데이트
    update_all_data()
    
    # Flask 애플리케이션 실행
    app.run(host='0.0.0.0', port=5000, debug=True)

# 템플릿 파일 생성
def create_template_files():
    """필요한 템플릿 파일을 생성합니다."""
    # 기본 레이아웃 템플릿
    create_base_template()
    
    # 인덱스 페이지 템플릿
    create_index_template()
    
    # 관세 정책 페이지 템플릿
    create_tariff_policy_template()
    
    # 제조 비용 페이지 템플릿
    create_manufacturing_cost_template()
    
    # 수출 가격 페이지 템플릿
    create_export_price_template()
    
    # CSS 파일 생성
    create_css_file()
    
    # JavaScript 파일 생성
    create_js_file()

# 기본 레이아웃 템플릿 생성
def create_base_template():
    """기본 레이아웃 템플릿을 생성합니다."""
    content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}미국 관세 정책 추적 및 비용 비교 도구{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <div class="container">
            <h1>미국 관세 정책 추적 및 비용 비교 도구</h1>
            <nav>
                <ul>
                    <li><a href="{{ url_for('home') }}">홈</a></li>
                    <li><a href="{{ url_for('tariff_policy') }}">관세 정책 요약</a></li>
                    <li><a href="{{ url_for('manufacturing_cost') }}">제조 비용 시뮬레이션</a></li>
                    <li><a href="{{ url_for('export_price') }}">수출 가격 비교</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>마지막 업데이트: {{ last_update }}</p>
            <button id="updateDataBtn" class="update-btn">데이터 업데이트</button>
            <p>&copy; 2025 자동차 부품 제조업체 전략 기획팀</p>
        </div>
    </footer>
    
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
"""
    
    file_path = os.path.join(TEMPLATE_DIR, 'base.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"기본 레이아웃 템플릿 생성 완료: {file_path}")

# 인덱스 페이지 템플릿 생성
def create_index_template():
    """인덱스 페이지 템플릿을 생성합니다."""
    content = """{% extends 'base.html' %}

{% block title %}홈 - 미국 관세 정책 추적 및 비용 비교 도구{% endblock %}

{% block content %}
<section class="hero">
    <h2>자동차 부품 제조업체를 위한 미국 수출 전략 도구</h2>
    <p>트럼프 행정부의 관세 정책 변화를 추적하고 국가별 제조 및 수출 비용을 비교하여 전략적 의사결정을 지원합니다.</p>
</section>

<section class="features">
    <div class="feature-card">
        <h3>최신 미국 관세 정책 요약</h3>
        <p>9개 주요 국가에 대한 최신 미국 관세 정책 변화와 영향을 한눈에 확인하세요.</p>
        <a href="{{ url_for('tariff_policy') }}" class="btn">자세히 보기</a>
    </div>
    
    <div class="feature-card">
        <h3>국가별 제조 비용 시뮬레이션</h3>
        <p>기업세율, 이자율, 노동 비용 등 다양한 요소를 고려한 국가별 제조 비용을 비교하세요.</p>
        <a href="{{ url_for('manufacturing_cost') }}" class="btn">자세히 보기</a>
    </div>
    
    <div class="feature-card">
        <h3>수출 가격 비교</h3>
        <p>제조 비용, 관세, 무역 협정 혜택을 모두 고려한 최종 수출 가격을 비교하세요.</p>
        <a href="{{ url_for('export_price') }}" class="btn">자세히 보기</a>
    </div>
</section>

<section class="update-info">
    <h3>데이터 업데이트 정보</h3>
    <p>이 도구는 매일 다음 시간에 자동으로 데이터를 업데이트합니다:</p>
    <ul>
        <li>03:00 AM (아시아 시장 개장)</li>
        <li>06:00 AM (EU 정책 업데이트)</li>
        <li>09:00 PM (미국 시장 마감 후)</li>
    </ul>
    <p>마지막 업데이트: {{ last_update }}</p>
</section>
{% endblock %}
"""
    
    file_path = os.path.join(TEMPLATE_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"인덱스 페이지 템플릿 생성 완료: {file_path}")

# 관세 정책 페이지 템플릿 생성
def create_tariff_policy_template():
    """관세 정책 페이지 템플릿을 생성합니다."""
    content = """{% extends 'base.html' %}

{% block title %}최신 미국 관세 정책 요약 - 미국 관세 정책 추적 및 비용 비교 도구{% endblock %}

{% block content %}
<section class="page-header">
    <h2>최신 미국 관세 정책 요약</h2>
    <p>트럼프 행정부의 최신 관세 정책 변화와 9개 주요 국가에 대한 영향을 확인하세요.</p>
</section>

<section class="policy-updates">
    <h3>최근 관세 정책 업데이트</h3>
    
    {% if policy_updates %}
        {% for update in policy_updates %}
        <div class="policy-card">
            <h4>{{ update.title }}</h4>
            <p class="date">{{ update.date }}</p>
            <p class="summary">{{ update.summary }}</p>
            <div class="details">
                <p><strong>영향 받는 HS 코드:</strong> {{ update.affected_hs_codes|join(', ') }}</p>
                <p><strong>발효일:</strong> {{ update.effective_date }}</p>
                <p><strong>출처:</strong> {{ update.source }}</p>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <p>최근 관세 정책 업데이트 정보가 없습니다.</p>
    {% endif %}
</section>

<section class="country-impact">
    <h3>국가별 관세 영향</h3>
    
    <div class="country-grid">
        <div class="country-card">
            <h4>🇰🇷 대한민국</h4>
            <p><strong>주요 영향:</strong> 한-미 FTA로 대부분의 자동차 부품에 대한 관세 면제 혜택을 유지하고 있으나, 일부 품목에 대한 원산지 규정 개정 논의가 진행 중입니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708, 8507, 8501</p>
        </div>
        
        <div class="country-card">
            <h4>🇯🇵 일본</h4>
            <p><strong>주요 영향:</strong> 자동차 및 자동차 부품에 대한 25% 추가 관세 부과로 수출 경쟁력이 약화되었습니다. 미-일 무역 불균형 해소를 위한 협상이 예정되어 있습니다.</p>
            <p><strong>주요 HS 코드:</strong> 8703, 8708</p>
        </div>
        
        <div class="country-card">
            <h4>🇨🇳 중국</h4>
            <p><strong>주요 영향:</strong> 기존 301조 관세에 더해 자동차 부품에 대한 25% 추가 관세가 부과되어 총 50% 이상의 관세율이 적용됩니다. 전기차 배터리에 대한 추가 관세도 검토 중입니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708, 8507</p>
        </div>
        
        <div class="country-card">
            <h4>🇮🇳 인도</h4>
            <p><strong>주요 영향:</strong> 자동차 부품에 대한 25% 추가 관세 부과로 수출 경쟁력이 약화되었습니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708</p>
        </div>
        
        <div class="country-card">
            <h4>🇹🇭 태국</h4>
            <p><strong>주요 영향:</strong> 자동차 부품에 대한 25% 추가 관세 부과로 수출 경쟁력이 약화되었습니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708</p>
        </div>
        
        <div class="country-card">
            <h4>🇻🇳 베트남</h4>
            <p><strong>주요 영향:</strong> 자동차 부품에 대한 25% 추가 관세 부과로 수출 경쟁력이 약화되었습니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708</p>
        </div>
        
        <div class="country-card">
            <h4>🇹🇼 대만</h4>
            <p><strong>주요 영향:</strong> 자동차 부품에 대한 25% 추가 관세 부과로 수출 경쟁력이 약화되었습니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708</p>
        </div>
        
        <div class="country-card">
            <h4>🇪🇺 유럽연합</h4>
            <p><strong>주요 영향:</strong> 자동차 부품에 대한 25% 추가 관세 부과로 수출 경쟁력이 약화되었으나, 관세 면제 연장 협상이 진행 중입니다.</p>
            <p><strong>주요 HS 코드:</strong> 8703, 8708</p>
        </div>
        
        <div class="country-card">
            <h4>🇲🇽 멕시코</h4>
            <p><strong>주요 영향:</strong> USMCA 협정으로 대부분의 자동차 부품에 대한 관세 면제 혜택을 유지하고 있어 상대적으로 유리한 위치에 있습니다.</p>
            <p><strong>주요 HS 코드:</strong> 8708</p>
        </div>
    </div>
</section>

<section class="political-analysis">
    <h3>정치적/경제적 배경 분석</h3>
    
    <div class="analysis-card">
        <h4>미국 제조업 활성화 정책</h4>
        <p>트럼프 행정부는 '미국 우선주의(America First)' 정책의 일환으로 자국 제조업 보호 및 활성화를 위해 외국산 자동차 및 자동차 부품에 대한 관세를 대폭 인상했습니다. 이는 미국 내 일자리 창출과 제조업 기반 강화를 목표로 합니다.</p>
    </div>
    
    <div class="analysis-card">
        <h4>중국과의 무역 갈등</h4>
        <p>미-중 무역 갈등이 지속되면서 중국산 제품에 대한 추가 관세가 유지되고 있으며, 특히 전기차 배터리와 같은 첨단 기술 분야에서의 중국 의존도를 낮추기 위한 정책이 강화되고 있습니다.</p>
    </div>
    
    <div class="analysis-card">
        <h4>무역 협정 재협상</h4>
        <p>USMCA(미국-멕시코-캐나다 협정)와 같은 무역 협정을 통해 북미 지역 내 공급망을 강화하려는 움직임이 있으며, 다른 국가들과의 무역 협정도 미국에 유리한 방향으로 재협상을 추진하고 있습니다.</p>
    </div>
</section>
{% endblock %}
"""
    
    file_path = os.path.join(TEMPLATE_DIR, 'tariff_policy.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"관세 정책 페이지 템플릿 생성 완료: {file_path}")

# 제조 비용 페이지 템플릿 생성
def create_manufacturing_cost_template():
    """제조 비용 페이지 템플릿을 생성합니다."""
    content = """{% extends 'base.html' %}

{% block title %}국가별 제조 비용 시뮬레이션 - 미국 관세 정책 추적 및 비용 비교 도구{% endblock %}

{% block content %}
<section class="page-header">
    <h2>국가별 제조 비용 시뮬레이션</h2>
    <p>다양한 비용 요소를 고려한 국가별 제조 비용을 비교하세요. (대한민국 = 100 기준)</p>
</section>

<section class="product-selector">
    <h3>제품 카테고리 선택</h3>
    <form action="{{ url_for('manufacturing_cost') }}" method="get">
        <select name="product_category" id="productCategory" onchange="this.form.submit()">
            {% for category in product_categories %}
            <option value="{{ category }}" {% if category == selected_category %}selected{% endif %}>{{ category }}</option>
            {% endfor %}
        </select>
    </form>
</section>

<section class="cost-comparison">
    <h3>{{ selected_category }} 제조 비용 비교</h3>
    
    <div class="chart-container">
        <canvas id="costChart"></canvas>
    </div>
    
    <div class="cost-table">
        <table>
            <thead>
                <tr>
                    <th>국가</th>
                    <th>제조 비용 지수</th>
                </tr>
            </thead>
            <tbody>
                {% for i in range(countries|length) %}
                <tr>
                    <td>{{ countries[i] }}</td>
                    <td>{{ costs[i]|round(1) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>

<section class="cost-factors">
    <h3>제조 비용 요소 설명</h3>
    
    <div class="factor-grid">
        <div class="factor-card">
            <h4>기업세율</h4>
            <p>각 국가의 법인세율로, 기업의 순이익에 부과되는 세금 비율입니다. 높은 기업세율은 제조 비용을 증가시킵니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>이자율(차입 비용)</h4>
            <p>기업이 자금을 차입할 때 부담하는 이자율로, 설비 투자 및 운영 자금 조달 비용에 영향을 미칩니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>노동 비용</h4>
            <p>시간당 임금, 사회보험, 복리후생 등을 포함한 총 노동 비용으로, 제조업에서 중요한 비용 요소입니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>토지/공장 임대 비용</h4>
            <p>제조 시설 부지 및 건물의 임대 또는 소유에 따른 비용으로, 지역에 따라 큰 차이가 있습니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>전기/유틸리티 비용</h4>
            <p>전기, 수도, 가스 등 제조 과정에 필요한 유틸리티 비용으로, 에너지 집약적 산업에서 중요합니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>물류 및 현지 운송 비용</h4>
            <p>원자재 조달 및 완제품 운송에 관련된 국내 물류 비용으로, 인프라 수준에 영향을 받습니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>환율 변동성 및 인플레이션</h4>
            <p>통화 가치의 불안정성과 물가 상승률로, 장기적인 비용 예측 및 계획에 영향을 미칩니다.</p>
        </div>
    </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('costChart').getContext('2d');
    
    const costChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ countries|tojson }},
            datasets: [{
                label: '제조 비용 지수',
                data: {{ costs|tojson }},
                backgroundColor: Array({{ countries|length }}).fill('rgba(54, 162, 235, 0.6)'),
                borderColor: Array({{ countries|length }}).fill('rgba(54, 162, 235, 1)'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '비용 지수 (대한민국 = 100)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '국가'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '{{ selected_category }} 제조 비용 지수 비교'
                }
            }
        }
    });
    
    // 한국 막대 강조
    if (costChart.data.labels.includes('대한민국')) {
        const krIndex = costChart.data.labels.indexOf('대한민국');
        costChart.data.datasets[0].backgroundColor[krIndex] = 'rgba(255, 99, 132, 0.6)';
        costChart.data.datasets[0].borderColor[krIndex] = 'rgba(255, 99, 132, 1)';
        costChart.update();
    }
});
</script>
{% endblock %}
"""
    
    file_path = os.path.join(TEMPLATE_DIR, 'manufacturing_cost.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"제조 비용 페이지 템플릿 생성 완료: {file_path}")

# 수출 가격 페이지 템플릿 생성
def create_export_price_template():
    """수출 가격 페이지 템플릿을 생성합니다."""
    content = """{% extends 'base.html' %}

{% block title %}수출 가격 비교 - 미국 관세 정책 추적 및 비용 비교 도구{% endblock %}

{% block content %}
<section class="page-header">
    <h2>수출 가격 비교</h2>
    <p>제조 비용, 관세, 무역 협정 혜택을 모두 고려한 최종 수출 가격을 비교하세요.</p>
</section>

<section class="product-selector">
    <h3>제품 카테고리 선택</h3>
    <form action="{{ url_for('export_price') }}" method="get">
        <select name="product_category" id="productCategory" onchange="this.form.submit()">
            {% for category in product_categories %}
            <option value="{{ category }}" {% if category == selected_category %}selected{% endif %}>{{ category }}</option>
            {% endfor %}
        </select>
    </form>
</section>

<section class="price-comparison">
    <h3>{{ selected_category }} 수출 가격 비교</h3>
    
    <div class="chart-container">
        <canvas id="priceChart"></canvas>
    </div>
    
    <div class="price-table">
        <table>
            <thead>
                <tr>
                    <th>국가</th>
                    <th>수출 가격 지수</th>
                    <th>한국 대비 비율</th>
                </tr>
            </thead>
            <tbody>
                {% for i in range(countries|length) %}
                <tr>
                    <td>{{ countries[i] }}</td>
                    <td>{{ prices[i]|round(1) }}</td>
                    <td>{{ norm_prices[i]|round(1) }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>

<section class="export-format">
    <h3>한국어 형식 수출 가격 비교</h3>
    
    <div class="format-box">
        <pre>
{% for i in range(countries|length) %}{{ countries[i] }} → 미국: {{ norm_prices[i]|round(0)|int }}
{% endfor %}</pre>
    </div>
</section>

<section class="price-factors">
    <h3>수출 가격 구성 요소</h3>
    
    <div class="factor-grid">
        <div class="factor-card">
            <h4>제조 비용</h4>
            <p>기업세율, 이자율, 노동 비용, 토지/공장 임대 비용, 전기/유틸리티 비용, 물류 및 현지 운송 비용, 환율 변동성 및 인플레이션을 고려한 종합 제조 비용입니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>미국으로의 화물 비용</h4>
            <p>각 국가에서 미국으로 제품을 운송하는 데 드는 국제 화물 비용으로, 거리와 운송 방식에 따라 달라집니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>미국 관세</h4>
            <p>미국이 각 국가의 제품에 부과하는 관세로, 트럼프 행정부의 최신 관세 정책이 반영되어 있습니다.</p>
        </div>
        
        <div class="factor-card">
            <h4>무역 협정 혜택</h4>
            <p>한-미 FTA, USMCA 등 무역 협정에 따른 관세 감면 혜택으로, 일부 국가는 관세가 크게 감소합니다.</p>
        </div>
    </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    const priceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ countries|tojson }},
            datasets: [{
                label: '수출 가격 지수 (한국 = 100)',
                data: {{ norm_prices|tojson }},
                backgroundColor: Array({{ countries|length }}).fill('rgba(255, 159, 64, 0.6)'),
                borderColor: Array({{ countries|length }}).fill('rgba(255, 159, 64, 1)'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '가격 지수 (대한민국 = 100)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '국가'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '{{ selected_category }} 수출 가격 지수 비교'
                }
            }
        }
    });
    
    // 한국 막대 강조
    if (priceChart.data.labels.includes('대한민국')) {
        const krIndex = priceChart.data.labels.indexOf('대한민국');
        priceChart.data.datasets[0].backgroundColor[krIndex] = 'rgba(54, 162, 235, 0.6)';
        priceChart.data.datasets[0].borderColor[krIndex] = 'rgba(54, 162, 235, 1)';
        priceChart.update();
    }
});
</script>
{% endblock %}
"""
    
    file_path = os.path.join(TEMPLATE_DIR, 'export_price.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"수출 가격 페이지 템플릿 생성 완료: {file_path}")

# CSS 파일 생성
def create_css_file():
    """CSS 파일을 생성합니다."""
    content = """/* 기본 스타일 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Noto Sans KR', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

/* 헤더 스타일 */
header {
    background-color: #1a3a6e;
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

header h1 {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
}

nav ul {
    display: flex;
    list-style: none;
}

nav ul li {
    margin-right: 1.5rem;
}

nav ul li a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}

nav ul li a:hover {
    color: #ffd700;
}

/* 메인 콘텐츠 스타일 */
main {
    padding: 2rem 0;
    min-height: calc(100vh - 180px);
}

section {
    margin-bottom: 2.5rem;
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h2 {
    color: #1a3a6e;
    margin-bottom: 1rem;
    font-size: 1.8rem;
}

h3 {
    color: #2c5282;
    margin-bottom: 1rem;
    font-size: 1.4rem;
    border-bottom: 2px solid #edf2f7;
    padding-bottom: 0.5rem;
}

h4 {
    color: #2d3748;
    margin-bottom: 0.5rem;
    font-size: 1.2rem;
}

p {
    margin-bottom: 1rem;
}

/* 버튼 스타일 */
.btn {
    display: inline-block;
    background-color: #3182ce;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #2c5282;
}

.update-btn {
    background-color: #38a169;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.3s;
}

.update-btn:hover {
    background-color: #2f855a;
}

/* 푸터 스타일 */
footer {
    background-color: #2d3748;
    color: white;
    padding: 1.5rem 0;
    text-align: center;
}

footer p {
    margin-bottom: 0.5rem;
}

/* 홈페이지 스타일 */
.hero {
    text-align: center;
    padding: 2rem 0;
}

.hero h2 {
    font-size: 2rem;
    margin-bottom: 1rem;
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.feature-card {
    background-color: #ebf8ff;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}

.update-info {
    background-color: #fefcbf;
    padding: 1.5rem;
}

.update-info ul {
    margin-left: 2rem;
    margin-bottom: 1rem;
}

/* 관세 정책 페이지 스타일 */
.page-header {
    text-align: center;
    margin-bottom: 2rem;
}

.policy-card {
    background-color: #f7fafc;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    border-left: 4px solid #3182ce;
}

.policy-card .date {
    color: #718096;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.policy-card .summary {
    font-weight: 500;
    margin-bottom: 1rem;
}

.policy-card .details {
    background-color: #edf2f7;
    padding: 1rem;
    border-radius: 4px;
}

.country-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.country-card {
    background-color: #f0fff4;
    padding: 1.5rem;
    border-radius: 8px;
    border-top: 4px solid #38a169;
}

.analysis-card {
    background-color: #fff5f5;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    border-left: 4px solid #e53e3e;
}

/* 제조 비용 페이지 스타일 */
.product-selector {
    text-align: center;
    margin-bottom: 2rem;
}

.product-selector select {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: 1px solid #cbd5e0;
    font-size: 1rem;
    width: 200px;
}

.chart-container {
    margin-bottom: 2rem;
    height: 400px;
}

.cost-table, .price-table {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1.5rem;
}

table th, table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

table th {
    background-color: #edf2f7;
    font-weight: 600;
}

table tr:nth-child(even) {
    background-color: #f7fafc;
}

.factor-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.factor-card {
    background-color: #f7fafc;
    padding: 1.5rem;
    border-radius: 8px;
    border-top: 3px solid #4299e1;
}

/* 수출 가격 페이지 스타일 */
.format-box {
    background-color: #1a202c;
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    font-family: monospace;
    overflow-x: auto;
}

.format-box pre {
    margin: 0;
}

/* 반응형 스타일 */
@media (max-width: 768px) {
    header h1 {
        font-size: 1.5rem;
    }
    
    nav ul {
        flex-direction: column;
    }
    
    nav ul li {
        margin-right: 0;
        margin-bottom: 0.5rem;
    }
    
    .features, .country-grid, .factor-grid {
        grid-template-columns: 1fr;
    }
}
"""
    
    os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
    file_path = os.path.join(STATIC_DIR, 'css', 'style.css')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"CSS 파일 생성 완료: {file_path}")

# JavaScript 파일 생성
def create_js_file():
    """JavaScript 파일을 생성합니다."""
    content = """// 데이터 업데이트 버튼 이벤트 리스너
document.addEventListener('DOMContentLoaded', function() {
    const updateDataBtn = document.getElementById('updateDataBtn');
    
    if (updateDataBtn) {
        updateDataBtn.addEventListener('click', function() {
            // 버튼 비활성화 및 텍스트 변경
            updateDataBtn.disabled = true;
            updateDataBtn.textContent = '업데이트 중...';
            
            // 데이터 업데이트 요청
            fetch('/update-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('데이터가 성공적으로 업데이트되었습니다. 페이지를 새로고침합니다.');
                    location.reload();
                } else {
                    alert('데이터 업데이트 중 오류가 발생했습니다.');
                    updateDataBtn.disabled = false;
                    updateDataBtn.textContent = '데이터 업데이트';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('데이터 업데이트 요청 중 오류가 발생했습니다.');
                updateDataBtn.disabled = false;
                updateDataBtn.textContent = '데이터 업데이트';
            });
        });
    }
});
"""
    
    os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)
    file_path = os.path.join(STATIC_DIR, 'js', 'script.js')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"JavaScript 파일 생성 완료: {file_path}")

if __name__ == "__main__":
    main()

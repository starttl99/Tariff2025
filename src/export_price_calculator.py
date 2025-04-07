"""
수출 가격 비교 계산기

이 모듈은 제조 비용과 관세 데이터를 결합하여 미국으로의 최종 수출 가격을 계산합니다.
다음 요소를 고려합니다:
- 국가별 제조 비용
- 미국으로의 화물 비용
- 현재 관세율
- 무역 협정 혜택
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# 데이터 저장 경로
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
COST_DATA_DIR = os.path.join(DATA_DIR, 'cost_data')
TARIFF_DATA_DIR = os.path.join(DATA_DIR, 'tariff_data')
EXPORT_DATA_DIR = os.path.join(DATA_DIR, 'export_data')

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

def ensure_data_dir():
    """데이터 디렉토리가 존재하는지 확인하고, 없으면 생성합니다."""
    os.makedirs(EXPORT_DATA_DIR, exist_ok=True)

def collect_freight_costs():
    """국가별 미국으로의 화물 비용 데이터를 수집합니다."""
    print("국가별 미국으로의 화물 비용 데이터 수집 중...")
    
    # 샘플 화물 비용 데이터 (2025년 기준 추정치, 40ft 컨테이너 기준 USD)
    freight_costs = {
        'KR': 4500,  # 대한민국 → 미국
        'JP': 4800,  # 일본 → 미국
        'CN': 5200,  # 중국 → 미국
        'IN': 6500,  # 인도 → 미국
        'TH': 6000,  # 태국 → 미국
        'VN': 5800,  # 베트남 → 미국
        'TW': 4600,  # 대만 → 미국
        'EU': 5500,  # 유럽연합 → 미국
        'MX': 3200   # 멕시코 → 미국 (육로 운송)
    }
    
    # 데이터 저장
    file_path = os.path.join(EXPORT_DATA_DIR, "freight_costs.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'data': freight_costs
        }, f, ensure_ascii=False, indent=2)
    
    print(f"화물 비용 데이터 저장 완료: {file_path}")
    return freight_costs

def get_tariff_rates():
    """국가별 미국 관세율 데이터를 가져옵니다."""
    print("국가별 미국 관세율 데이터 로드 중...")
    
    # 관세 데이터 파일 경로
    all_countries_file_path = os.path.join(TARIFF_DATA_DIR, "all_countries_tariff_data.json")
    
    if not os.path.exists(all_countries_file_path):
        print("관세 데이터 파일이 존재하지 않습니다. 샘플 데이터를 생성합니다.")
        return create_sample_tariff_rates()
    
    try:
        with open(all_countries_file_path, 'r', encoding='utf-8') as f:
            tariff_data = json.load(f)
        
        # 국가별 평균 관세율 계산
        tariff_rates = {}
        for country_code, country_info in tariff_data.get('countries', {}).items():
            rates = []
            for item in country_info.get('data', []):
                rate_str = item.get('general_rate', '0%')
                if rate_str.endswith('%'):
                    try:
                        rate = float(rate_str.rstrip('%'))
                        rates.append(rate)
                    except ValueError:
                        continue
            
            if rates:
                tariff_rates[country_code] = sum(rates) / len(rates)
            else:
                tariff_rates[country_code] = 0.0
        
        return tariff_rates
    except Exception as e:
        print(f"관세 데이터 로드 오류: {str(e)}")
        return create_sample_tariff_rates()

def create_sample_tariff_rates():
    """샘플 관세율 데이터를 생성합니다."""
    print("샘플 관세율 데이터 생성 중...")
    
    # 샘플 관세율 데이터 (2025년 기준 추정치, %)
    tariff_rates = {
        'KR': 0.0,   # 대한민국 (한-미 FTA)
        'JP': 27.5,  # 일본 (기본 관세 + 자동차 부품 25% 추가 관세)
        'CN': 52.5,  # 중국 (기본 관세 + 중국 특별 관세 25% + 자동차 부품 25% 추가 관세)
        'IN': 27.5,  # 인도 (기본 관세 + 자동차 부품 25% 추가 관세)
        'TH': 27.5,  # 태국 (기본 관세 + 자동차 부품 25% 추가 관세)
        'VN': 27.5,  # 베트남 (기본 관세 + 자동차 부품 25% 추가 관세)
        'TW': 27.5,  # 대만 (기본 관세 + 자동차 부품 25% 추가 관세)
        'EU': 27.5,  # 유럽연합 (기본 관세 + 자동차 부품 25% 추가 관세)
        'MX': 0.0    # 멕시코 (USMCA)
    }
    
    # 데이터 저장
    file_path = os.path.join(EXPORT_DATA_DIR, "tariff_rates.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'data': tariff_rates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"샘플 관세율 데이터 저장 완료: {file_path}")
    return tariff_rates

def get_trade_agreement_benefits():
    """국가별 무역 협정 혜택 데이터를 가져옵니다."""
    print("국가별 무역 협정 혜택 데이터 수집 중...")
    
    # 샘플 무역 협정 혜택 데이터 (관세 감면 %)
    trade_agreement_benefits = {
        'KR': 100.0,  # 대한민국 (한-미 FTA, 대부분 품목 100% 관세 면제)
        'JP': 0.0,    # 일본 (무역 협정 없음)
        'CN': 0.0,    # 중국 (무역 협정 없음)
        'IN': 0.0,    # 인도 (무역 협정 없음)
        'TH': 0.0,    # 태국 (무역 협정 없음)
        'VN': 0.0,    # 베트남 (무역 협정 없음)
        'TW': 0.0,    # 대만 (무역 협정 없음)
        'EU': 0.0,    # 유럽연합 (무역 협정 협상 중)
        'MX': 100.0   # 멕시코 (USMCA, 대부분 품목 100% 관세 면제)
    }
    
    # 데이터 저장
    file_path = os.path.join(EXPORT_DATA_DIR, "trade_agreement_benefits.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'data': trade_agreement_benefits
        }, f, ensure_ascii=False, indent=2)
    
    print(f"무역 협정 혜택 데이터 저장 완료: {file_path}")
    return trade_agreement_benefits

def get_manufacturing_cost_index(product_category=None):
    """제조 비용 지수 데이터를 가져옵니다."""
    print("제조 비용 지수 데이터 로드 중...")
    
    if product_category:
        file_path = os.path.join(COST_DATA_DIR, f"manufacturing_cost_index_{product_category.replace(' ', '_')}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['manufacturing_cost_index']
    
    # 기본 제조 비용 지수 파일
    file_path = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.json")
    
    if not os.path.exists(file_path):
        print("제조 비용 지수 파일이 존재하지 않습니다. 샘플 데이터를 생성합니다.")
        return create_sample_manufacturing_cost_index()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['manufacturing_cost_index']
    except Exception as e:
        print(f"제조 비용 지수 데이터 로드 오류: {str(e)}")
        return create_sample_manufacturing_cost_index()

def create_sample_manufacturing_cost_index():
    """샘플 제조 비용 지수 데이터를 생성합니다."""
    print("샘플 제조 비용 지수 데이터 생성 중...")
    
    # 샘플 제조 비용 지수 데이터 (한국 = 100 기준)
    manufacturing_cost_index = {
        'KR': 100.0,  # 대한민국
        'JP': 120.0,  # 일본
        'CN': 75.0,   # 중국
        'IN': 65.0,   # 인도
        'TH': 70.0,   # 태국
        'VN': 60.0,   # 베트남
        'TW': 90.0,   # 대만
        'EU': 130.0,  # 유럽연합
        'MX': 80.0    # 멕시코
    }
    
    return manufacturing_cost_index

def calculate_export_price_index(product_category=None):
    """국가별 미국 수출 가격 지수를 계산합니다."""
    print("국가별 미국 수출 가격 지수 계산 중...")
    
    # 필요한 데이터 수집
    manufacturing_cost_index = get_manufacturing_cost_index(product_category)
    freight_costs = collect_freight_costs()
    tariff_rates = get_tariff_rates()
    trade_agreement_benefits = get_trade_agreement_benefits()
    
    # 한국의 화물 비용을 기준으로 정규화
    normalized_freight_costs = {country: cost / freight_costs['KR'] * 20 for country, cost in freight_costs.items()}
    
    # 관세율에 무역 협정 혜택 적용
    effective_tariff_rates = {}
    for country in tariff_rates:
        benefit_pct = trade_agreement_benefits.get(country, 0.0)
        effective_tariff_rates[country] = tariff_rates[country] * (1 - benefit_pct / 100)
    
    # 최종 수출 가격 지수 계산 (제조 비용 + 화물 비용 + 관세)
    export_price_index = {}
    for country in TARGET_COUNTRIES:
        # 제조 비용 (80% 가중치)
        manufacturing_component = manufacturing_cost_index[country] * 0.8
        
        # 화물 비용 (10% 가중치)
        freight_component = normalized_freight_costs[country] * 0.1
        
        # 관세 (10% 가중치)
        # 관세는 제조 비용과 화물 비용의 합에 적용됨
        base_cost = manufacturing_cost_index[country] + normalized_freight_costs[country]
        tariff_component = base_cost * (effective_tariff_rates[country] / 100) * 0.1
        
        # 최종 수출 가격 지수
        export_price_index[country] = manufacturing_component + freight_component + tariff_component
    
    # 데이터 저장
    file_name = "export_price_index.json"
    if product_category:
        file_name = f"export_price_index_{product_category.replace(' ', '_')}.json"
    
    file_path = os.path.join(EXPORT_DATA_DIR, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'product_category': product_category,
            'manufacturing_cost_index': manufacturing_cost_index,
            'normalized_freight_costs': normalized_freight_costs,
            'tariff_rates': tariff_rates,
            'effective_tariff_rates': effective_tariff_rates,
            'export_price_index': export_price_index
        }, f, ensure_ascii=False, indent=2)
    
    print(f"수출 가격 지수 저장 완료: {file_path}")
    
    # 수출 가격 지수 CSV 파일 생성
    create_export_price_csv(export_price_index, manufacturing_cost_index, normalized_freight_costs, 
                           tariff_rates, effective_tariff_rates, product_category)
    
    # 수출 가격 지수 시각화
    create_export_price_visualization(export_price_index, product_category)
    
    return export_price_index

def create_export_price_csv(export_price_index, manufacturing_cost_index, normalized_freight_costs, 
                           tariff_rates, effective_tariff_rates, product_category=None):
    """수출 가격 지수를 CSV 파일로 저장합니다."""
    
    # 데이터프레임 생성을 위한 데이터 준비
    data = []
    for country_code, country_name in TARGET_COUNTRIES.items():
        data.append({
            '국가 코드': country_code,
            '국가명': country_name,
            '제조 비용 지수': manufacturing_cost_index[country_code],
            '화물 비용 지수': normalized_freight_costs[country_code],
            '기본 관세율(%)': tariff_rates[country_code],
            '실효 관세율(%)': effective_tariff_rates[country_code],
            '최종 수출 가격 지수': export_price_index[country_code]
        })
    
    # 데이터프레임 생성 및 CSV 저장
    df = pd.DataFrame(data)
    
    file_name = "export_price_index.csv"
    if product_category:
        file_name = f"export_price_index_{product_category.replace(' ', '_')}.csv"
    
    csv_file_path = os.path.join(EXPORT_DATA_DIR, file_name)
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    
    print(f"수출 가격 지수 CSV 파일 저장 완료: {csv_file_path}")
    return csv_file_path

def create_export_price_visualization(export_price_index, product_category=None):
    """수출 가격 지수를 시각화합니다."""
    
    # 국가 이름과 가격 지수 준비
    countries = [TARGET_COUNTRIES[code] for code in export_price_index.keys()]
    prices = list(export_price_index.values())
    
    # 한국을 기준으로 정렬
    kr_index = countries.index('대한민국')
    countries.insert(0, countries.pop(kr_index))
    prices.insert(0, prices.pop(kr_index))
    
    # 막대 그래프 생성
    plt.figure(figsize=(12, 8))
    bars = plt.bar(countries, prices, color='lightcoral')
    
    # 한국 막대 강조
    bars[0].set_color('blue')
    
    # 그래프 제목 및 레이블 설정
    title = '국가별 미국 수출 가격 지수 (대한민국 = 100)'
    if product_category:
        title = f'{product_category} - 국가별 미국 수출 가격 지수 (대한민국 = 100)'
    
    plt.title(title, fontsize=16)
    plt.xlabel('국가', fontsize=14)
    plt.ylabel('가격 지수', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # 값 표시
    for i, v in enumerate(prices):
        plt.text(i, v + 2, f'{v:.1f}', ha='center', fontsize=12)
    
    # 그리드 추가
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 여백 조정
    plt.tight_layout()
    
    # 이미지 저장
    file_name = "export_price_index.png"
    if product_category:
        file_name = f"export_price_index_{product_category.replace(' ', '_')}.png"
    
    img_file_path = os.path.join(EXPORT_DATA_DIR, file_name)
    plt.savefig(img_file_path, dpi=300)
    
    print(f"수출 가격 지수 시각화 저장 완료: {img_file_path}")
    return img_file_path

def format_export_price_comparison_korean(export_price_index):
    """수출 가격 비교 결과를 한국어 형식으로 포맷팅합니다."""
    
    # 한국 기준 (100)으로 정규화
    normalized_index = {country: price / export_price_index['KR'] * 100 
                       for country, price in export_price_index.items()}
    
    # 결과 문자열 생성
    result = []
    for country_code, country_name in TARGET_COUNTRIES.items():
        result.append(f"{country_name} → 미국: {normalized_index[country_code]:.0f}")
    
    return "\n".join(result)

def calculate_export_prices_for_products():
    """여러 제품 카테고리에 대한 수출 가격을 계산합니다."""
    ensure_data_dir()
    
    # 기본 수출 가격 지수 계산
    export_price_index = calculate_export_price_index()
    
    # 특정 제품 카테고리에 대한 수출 가격 지수 계산
    eps_motor_price_index = calculate_export_price_index("EPS 모터")
    
    # 한국어 형식으로 포맷팅된 결과 저장
    formatted_result = format_export_price_comparison_korean(export_price_index)
    file_path = os.path.join(EXPORT_DATA_DIR, "export_price_comparison_korean.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_result)
    
    print(f"한국어 형식의 수출 가격 비교 결과 저장 완료: {file_path}")
    
    return {
        'general': export_price_index,
        'eps_motor': eps_motor_price_index
    }

if __name__ == "__main__":
    print("수출 가격 비교 계산기 실행 중...")
    calculate_export_prices_for_products()
    print("수출 가격 비교 계산기 실행 완료")

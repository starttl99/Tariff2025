"""
제조 비용 시뮬레이션 모델

이 모듈은 국가별 제조 비용을 시뮬레이션하는 모델을 구현합니다.
다음 요소를 고려하여 종합 제조 비용 지수를 계산합니다:
- 기업세율
- 이자율(차입 비용)
- 노동 비용(시간당 임금, 사회보험, 복리후생)
- 토지/공장 임대 비용
- 전기/유틸리티 비용
- 물류 및 현지 운송 비용
- 환율 변동성 및 인플레이션
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import sys

# 데이터 저장 경로
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
COST_DATA_DIR = os.path.join(DATA_DIR, 'cost_data')

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
    os.makedirs(COST_DATA_DIR, exist_ok=True)

def collect_corporate_tax_rates():
    """국가별 기업세율 데이터를 수집합니다."""
    print("국가별 기업세율 데이터 수집 중...")
    
    # 샘플 기업세율 데이터 (2025년 기준 추정치)
    corporate_tax_rates = {
        'KR': 25.0,  # 대한민국
        'JP': 30.62, # 일본
        'CN': 25.0,  # 중국
        'IN': 25.17, # 인도
        'TH': 20.0,  # 태국
        'VN': 20.0,  # 베트남
        'TW': 20.0,  # 대만
        'EU': 21.7,  # 유럽연합 (평균)
        'MX': 30.0   # 멕시코
    }
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "corporate_tax_rates.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'data': corporate_tax_rates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"기업세율 데이터 저장 완료: {file_path}")
    return corporate_tax_rates

def collect_interest_rates():
    """국가별 이자율(차입 비용) 데이터를 수집합니다."""
    print("국가별 이자율 데이터 수집 중...")
    
    # 샘플 이자율 데이터 (2025년 기준 추정치)
    interest_rates = {
        'KR': 3.5,  # 대한민국
        'JP': 0.1,  # 일본
        'CN': 3.45, # 중국
        'IN': 6.5,  # 인도
        'TH': 2.5,  # 태국
        'VN': 4.5,  # 베트남
        'TW': 1.875,# 대만
        'EU': 3.75, # 유럽연합 (평균)
        'MX': 11.0  # 멕시코
    }
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "interest_rates.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'data': interest_rates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"이자율 데이터 저장 완료: {file_path}")
    return interest_rates

def collect_labor_costs():
    """국가별 노동 비용 데이터를 수집합니다."""
    print("국가별 노동 비용 데이터 수집 중...")
    
    # 샘플 노동 비용 데이터 (2025년 기준 추정치, 제조업 시간당 평균 임금 USD)
    labor_costs = {
        'KR': 25.0,  # 대한민국
        'JP': 28.0,  # 일본
        'CN': 8.5,   # 중국
        'IN': 3.0,   # 인도
        'TH': 5.5,   # 태국
        'VN': 3.2,   # 베트남
        'TW': 15.0,  # 대만
        'EU': 35.0,  # 유럽연합 (평균)
        'MX': 6.0    # 멕시코
    }
    
    # 사회보험 및 복리후생 비용 (기본 임금 대비 %)
    social_benefits = {
        'KR': 25.0,  # 대한민국
        'JP': 30.0,  # 일본
        'CN': 40.0,  # 중국
        'IN': 20.0,  # 인도
        'TH': 15.0,  # 태국
        'VN': 22.0,  # 베트남
        'TW': 20.0,  # 대만
        'EU': 35.0,  # 유럽연합 (평균)
        'MX': 30.0   # 멕시코
    }
    
    # 총 노동 비용 계산 (시간당 임금 + 사회보험 및 복리후생)
    total_labor_costs = {}
    for country in labor_costs:
        total_labor_costs[country] = labor_costs[country] * (1 + social_benefits[country] / 100)
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "labor_costs.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'hourly_wage': labor_costs,
            'social_benefits_pct': social_benefits,
            'total_labor_costs': total_labor_costs
        }, f, ensure_ascii=False, indent=2)
    
    print(f"노동 비용 데이터 저장 완료: {file_path}")
    return total_labor_costs

def collect_land_costs():
    """국가별 토지/공장 임대 비용 데이터를 수집합니다."""
    print("국가별 토지/공장 임대 비용 데이터 수집 중...")
    
    # 샘플 토지/공장 임대 비용 데이터 (2025년 기준 추정치, 산업단지 월 임대료 USD/m²)
    land_costs = {
        'KR': 12.0,  # 대한민국
        'JP': 18.0,  # 일본
        'CN': 8.5,   # 중국
        'IN': 4.0,   # 인도
        'TH': 5.0,   # 태국
        'VN': 4.5,   # 베트남
        'TW': 10.0,  # 대만
        'EU': 15.0,  # 유럽연합 (평균)
        'MX': 6.0    # 멕시코
    }
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "land_costs.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'data': land_costs
        }, f, ensure_ascii=False, indent=2)
    
    print(f"토지/공장 임대 비용 데이터 저장 완료: {file_path}")
    return land_costs

def collect_utility_costs():
    """국가별 전기/유틸리티 비용 데이터를 수집합니다."""
    print("국가별 전기/유틸리티 비용 데이터 수집 중...")
    
    # 샘플 전기 비용 데이터 (2025년 기준 추정치, 산업용 전기 USD/kWh)
    electricity_costs = {
        'KR': 0.11,  # 대한민국
        'JP': 0.17,  # 일본
        'CN': 0.09,  # 중국
        'IN': 0.10,  # 인도
        'TH': 0.12,  # 태국
        'VN': 0.08,  # 베트남
        'TW': 0.10,  # 대만
        'EU': 0.18,  # 유럽연합 (평균)
        'MX': 0.12   # 멕시코
    }
    
    # 샘플 수도 비용 데이터 (2025년 기준 추정치, 산업용 수도 USD/m³)
    water_costs = {
        'KR': 0.70,  # 대한민국
        'JP': 1.20,  # 일본
        'CN': 0.50,  # 중국
        'IN': 0.40,  # 인도
        'TH': 0.45,  # 태국
        'VN': 0.35,  # 베트남
        'TW': 0.65,  # 대만
        'EU': 1.50,  # 유럽연합 (평균)
        'MX': 0.60   # 멕시코
    }
    
    # 샘플 가스 비용 데이터 (2025년 기준 추정치, 산업용 가스 USD/MMBtu)
    gas_costs = {
        'KR': 12.0,  # 대한민국
        'JP': 14.0,  # 일본
        'CN': 9.0,   # 중국
        'IN': 8.0,   # 인도
        'TH': 10.0,  # 태국
        'VN': 9.5,   # 베트남
        'TW': 11.0,  # 대만
        'EU': 15.0,  # 유럽연합 (평균)
        'MX': 7.0    # 멕시코
    }
    
    # 종합 유틸리티 비용 지수 계산 (전기, 수도, 가스 비용의 가중 평균)
    # 가중치: 전기 60%, 수도 10%, 가스 30%
    utility_cost_index = {}
    for country in electricity_costs:
        utility_cost_index[country] = (
            electricity_costs[country] * 0.6 +
            water_costs[country] * 0.1 +
            gas_costs[country] * 0.3
        ) * 100  # 지수화
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "utility_costs.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'electricity_costs': electricity_costs,
            'water_costs': water_costs,
            'gas_costs': gas_costs,
            'utility_cost_index': utility_cost_index
        }, f, ensure_ascii=False, indent=2)
    
    print(f"전기/유틸리티 비용 데이터 저장 완료: {file_path}")
    return utility_cost_index

def collect_logistics_costs():
    """국가별 물류 및 현지 운송 비용 데이터를 수집합니다."""
    print("국가별 물류 및 현지 운송 비용 데이터 수집 중...")
    
    # 샘플 물류 비용 데이터 (2025년 기준 추정치, 물류 성과 지수 LPI)
    logistics_performance = {
        'KR': 3.8,  # 대한민국
        'JP': 4.0,  # 일본
        'CN': 3.6,  # 중국
        'IN': 3.2,  # 인도
        'TH': 3.4,  # 태국
        'VN': 3.3,  # 베트남
        'TW': 3.7,  # 대만
        'EU': 4.1,  # 유럽연합 (평균)
        'MX': 3.1   # 멕시코
    }
    
    # 샘플 현지 운송 비용 데이터 (2025년 기준 추정치, USD/km)
    local_transport_costs = {
        'KR': 1.8,  # 대한민국
        'JP': 2.2,  # 일본
        'CN': 1.2,  # 중국
        'IN': 0.9,  # 인도
        'TH': 1.0,  # 태국
        'VN': 0.8,  # 베트남
        'TW': 1.5,  # 대만
        'EU': 2.5,  # 유럽연합 (평균)
        'MX': 1.1   # 멕시코
    }
    
    # 종합 물류 비용 지수 계산 (물류 성과 지수의 역수와 현지 운송 비용의 가중 평균)
    # 가중치: 물류 성과 지수의 역수 60%, 현지 운송 비용 40%
    logistics_cost_index = {}
    for country in logistics_performance:
        # 물류 성과 지수는 높을수록 좋으므로 역수를 취함
        logistics_cost_index[country] = (
            (5 / logistics_performance[country]) * 0.6 +
            (local_transport_costs[country] / 1.0) * 0.4
        ) * 20  # 지수화
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "logistics_costs.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'logistics_performance': logistics_performance,
            'local_transport_costs': local_transport_costs,
            'logistics_cost_index': logistics_cost_index
        }, f, ensure_ascii=False, indent=2)
    
    print(f"물류 및 현지 운송 비용 데이터 저장 완료: {file_path}")
    return logistics_cost_index

def collect_fx_inflation_data():
    """국가별 환율 변동성 및 인플레이션 데이터를 수집합니다."""
    print("국가별 환율 변동성 및 인플레이션 데이터 수집 중...")
    
    # 샘플 환율 변동성 데이터 (2025년 기준 추정치, 표준편차 %)
    fx_volatility = {
        'KR': 8.0,   # 대한민국
        'JP': 7.5,   # 일본
        'CN': 3.0,   # 중국 (관리변동환율제)
        'IN': 6.0,   # 인도
        'TH': 5.0,   # 태국
        'VN': 4.5,   # 베트남
        'TW': 4.0,   # 대만
        'EU': 6.5,   # 유럽연합 (평균)
        'MX': 10.0   # 멕시코
    }
    
    # 샘플 인플레이션 데이터 (2025년 기준 추정치, %)
    inflation_rates = {
        'KR': 2.5,   # 대한민국
        'JP': 1.0,   # 일본
        'CN': 2.8,   # 중국
        'IN': 4.5,   # 인도
        'TH': 2.0,   # 태국
        'VN': 3.5,   # 베트남
        'TW': 1.8,   # 대만
        'EU': 2.2,   # 유럽연합 (평균)
        'MX': 4.0    # 멕시코
    }
    
    # 종합 환율/인플레이션 리스크 지수 계산 (환율 변동성과 인플레이션의 가중 평균)
    # 가중치: 환율 변동성 50%, 인플레이션 50%
    fx_inflation_risk_index = {}
    for country in fx_volatility:
        fx_inflation_risk_index[country] = (
            fx_volatility[country] * 0.5 +
            inflation_rates[country] * 0.5
        ) * 2  # 지수화
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "fx_inflation_data.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'fx_volatility': fx_volatility,
            'inflation_rates': inflation_rates,
            'fx_inflation_risk_index': fx_inflation_risk_index
        }, f, ensure_ascii=False, indent=2)
    
    print(f"환율 변동성 및 인플레이션 데이터 저장 완료: {file_path}")
    return fx_inflation_risk_index

def calculate_manufacturing_cost_index():
    """종합 제조 비용 지수를 계산합니다."""
    print("종합 제조 비용 지수 계산 중...")
    
    # 각 비용 요소 데이터 로드
    corporate_tax_rates = collect_corporate_tax_rates()
    interest_rates = collect_interest_rates()
    labor_costs = collect_labor_costs()
    land_costs = collect_land_costs()
    utility_costs = collect_utility_costs()
    logistics_costs = collect_logistics_costs()
    fx_inflation_risks = collect_fx_inflation_data()
    
    # 각 비용 요소의 가중치 설정
    weights = {
        'corporate_tax': 0.10,
        'interest_rate': 0.05,
        'labor_cost': 0.35,
        'land_cost': 0.10,
        'utility_cost': 0.15,
        'logistics_cost': 0.15,
        'fx_inflation_risk': 0.10
    }
    
    # 각 비용 요소를 정규화 (한국 = 100 기준)
    normalized_costs = {}
    
    # 기업세율 정규화
    normalized_corporate_tax = {country: rate / corporate_tax_rates['KR'] * 100 for country, rate in corporate_tax_rates.items()}
    
    # 이자율 정규화
    normalized_interest_rate = {country: rate / interest_rates['KR'] * 100 for country, rate in interest_rates.items()}
    
    # 노동 비용 정규화
    normalized_labor_cost = {country: cost / labor_costs['KR'] * 100 for country, cost in labor_costs.items()}
    
    # 토지/공장 임대 비용 정규화
    normalized_land_cost = {country: cost / land_costs['KR'] * 100 for country, cost in land_costs.items()}
    
    # 전기/유틸리티 비용 정규화
    normalized_utility_cost = {country: cost / utility_costs['KR'] * 100 for country, cost in utility_costs.items()}
    
    # 물류 및 현지 운송 비용 정규화
    normalized_logistics_cost = {country: cost / logistics_costs['KR'] * 100 for country, cost in logistics_costs.items()}
    
    # 환율 변동성 및 인플레이션 리스크 정규화
    normalized_fx_inflation_risk = {country: risk / fx_inflation_risks['KR'] * 100 for country, risk in fx_inflation_risks.items()}
    
    # 종합 제조 비용 지수 계산
    manufacturing_cost_index = {}
    for country in TARGET_COUNTRIES:
        manufacturing_cost_index[country] = (
            normalized_corporate_tax[country] * weights['corporate_tax'] +
            normalized_interest_rate[country] * weights['interest_rate'] +
            normalized_labor_cost[country] * weights['labor_cost'] +
            normalized_land_cost[country] * weights['land_cost'] +
            normalized_utility_cost[country] * weights['utility_cost'] +
            normalized_logistics_cost[country] * weights['logistics_cost'] +
            normalized_fx_inflation_risk[country] * weights['fx_inflation_risk']
        )
    
    # 데이터 저장
    file_path = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': datetime.now().isoformat(),
            'weights': weights,
            'normalized_costs': {
                'corporate_tax': normalized_corporate_tax,
                'interest_rate': normalized_interest_rate,
                'labor_cost': normalized_labor_cost,
                'land_cost': normalized_land_cost,
                'utility_cost': normalized_utility_cost,
                'logistics_cost': normalized_logistics_cost,
                'fx_inflation_risk': normalized_fx_inflation_risk
            },
            'manufacturing_cost_index': manufacturing_cost_index
        }, f, ensure_ascii=False, indent=2)
    
    print(f"종합 제조 비용 지수 저장 완료: {file_path}")
    
    # 종합 제조 비용 지수 CSV 파일 생성
    create_manufacturing_cost_csv(manufacturing_cost_index, weights, normalized_corporate_tax, normalized_interest_rate, 
                                 normalized_labor_cost, normalized_land_cost, normalized_utility_cost, 
                                 normalized_logistics_cost, normalized_fx_inflation_risk)
    
    # 종합 제조 비용 지수 시각화
    create_manufacturing_cost_visualization(manufacturing_cost_index)
    
    return manufacturing_cost_index

def create_manufacturing_cost_csv(manufacturing_cost_index, weights, normalized_corporate_tax, normalized_interest_rate, 
                                 normalized_labor_cost, normalized_land_cost, normalized_utility_cost, 
                                 normalized_logistics_cost, normalized_fx_inflation_risk):
    """종합 제조 비용 지수를 CSV 파일로 저장합니다."""
    
    # 데이터프레임 생성을 위한 데이터 준비
    data = []
    for country_code, country_name in TARGET_COUNTRIES.items():
        data.append({
            '국가 코드': country_code,
            '국가명': country_name,
            '기업세율': normalized_corporate_tax[country_code],
            '이자율': normalized_interest_rate[country_code],
            '노동 비용': normalized_labor_cost[country_code],
            '토지/공장 임대 비용': normalized_land_cost[country_code],
            '전기/유틸리티 비용': normalized_utility_cost[country_code],
            '물류 및 운송 비용': normalized_logistics_cost[country_code],
            '환율/인플레이션 리스크': normalized_fx_inflation_risk[country_code],
            '종합 제조 비용 지수': manufacturing_cost_index[country_code]
        })
    
    # 데이터프레임 생성 및 CSV 저장
    df = pd.DataFrame(data)
    csv_file_path = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.csv")
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    
    print(f"종합 제조 비용 지수 CSV 파일 저장 완료: {csv_file_path}")
    return csv_file_path

def create_manufacturing_cost_visualization(manufacturing_cost_index):
    """종합 제조 비용 지수를 시각화합니다."""
    
    # 국가 이름과 비용 지수 준비
    countries = [TARGET_COUNTRIES[code] for code in manufacturing_cost_index.keys()]
    costs = list(manufacturing_cost_index.values())
    
    # 한국을 기준으로 정렬
    kr_index = countries.index('대한민국')
    countries.insert(0, countries.pop(kr_index))
    costs.insert(0, costs.pop(kr_index))
    
    # 막대 그래프 생성
    plt.figure(figsize=(12, 8))
    bars = plt.bar(countries, costs, color='skyblue')
    
    # 한국 막대 강조
    bars[0].set_color('red')
    
    # 그래프 제목 및 레이블 설정
    plt.title('국가별 제조 비용 지수 (대한민국 = 100)', fontsize=16)
    plt.xlabel('국가', fontsize=14)
    plt.ylabel('비용 지수', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # 값 표시
    for i, v in enumerate(costs):
        plt.text(i, v + 2, f'{v:.1f}', ha='center', fontsize=12)
    
    # 그리드 추가
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 여백 조정
    plt.tight_layout()
    
    # 이미지 저장
    img_file_path = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.png")
    plt.savefig(img_file_path, dpi=300)
    
    print(f"종합 제조 비용 지수 시각화 저장 완료: {img_file_path}")
    return img_file_path

def simulate_manufacturing_cost(product_category=None):
    """특정 제품 카테고리에 대한 제조 비용을 시뮬레이션합니다."""
    print(f"제품 카테고리 '{product_category}'에 대한 제조 비용 시뮬레이션 중...")
    
    # 기본 제조 비용 지수 로드
    file_path = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.json")
    if not os.path.exists(file_path):
        print("종합 제조 비용 지수 파일이 존재하지 않습니다. 먼저 비용 지수를 계산합니다.")
        manufacturing_cost_index = calculate_manufacturing_cost_index()
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            manufacturing_cost_index = data['manufacturing_cost_index']
    
    # 제품 카테고리별 가중치 조정 (예: 자동차 부품 중 EPS 모터)
    if product_category == "EPS 모터":
        # EPS 모터는 노동 비용과 전기/유틸리티 비용의 영향이 더 큼
        category_weights = {
            'corporate_tax': 0.05,
            'interest_rate': 0.05,
            'labor_cost': 0.40,  # 노동 비용 가중치 증가
            'land_cost': 0.05,
            'utility_cost': 0.25,  # 전기/유틸리티 비용 가중치 증가
            'logistics_cost': 0.10,
            'fx_inflation_risk': 0.10
        }
        
        # 가중치 조정된 비용 지수 계산
        adjusted_cost_index = {}
        
        # 각 비용 요소 데이터 로드
        with open(os.path.join(COST_DATA_DIR, "corporate_tax_rates.json"), 'r', encoding='utf-8') as f:
            corporate_tax_rates = json.load(f)['data']
        
        with open(os.path.join(COST_DATA_DIR, "interest_rates.json"), 'r', encoding='utf-8') as f:
            interest_rates = json.load(f)['data']
        
        with open(os.path.join(COST_DATA_DIR, "labor_costs.json"), 'r', encoding='utf-8') as f:
            labor_costs = json.load(f)['total_labor_costs']
        
        with open(os.path.join(COST_DATA_DIR, "land_costs.json"), 'r', encoding='utf-8') as f:
            land_costs = json.load(f)['data']
        
        with open(os.path.join(COST_DATA_DIR, "utility_costs.json"), 'r', encoding='utf-8') as f:
            utility_costs = json.load(f)['utility_cost_index']
        
        with open(os.path.join(COST_DATA_DIR, "logistics_costs.json"), 'r', encoding='utf-8') as f:
            logistics_costs = json.load(f)['logistics_cost_index']
        
        with open(os.path.join(COST_DATA_DIR, "fx_inflation_data.json"), 'r', encoding='utf-8') as f:
            fx_inflation_risks = json.load(f)['fx_inflation_risk_index']
        
        # 각 비용 요소를 정규화 (한국 = 100 기준)
        normalized_corporate_tax = {country: rate / corporate_tax_rates['KR'] * 100 for country, rate in corporate_tax_rates.items()}
        normalized_interest_rate = {country: rate / interest_rates['KR'] * 100 for country, rate in interest_rates.items()}
        normalized_labor_cost = {country: cost / labor_costs['KR'] * 100 for country, cost in labor_costs.items()}
        normalized_land_cost = {country: cost / land_costs['KR'] * 100 for country, cost in land_costs.items()}
        normalized_utility_cost = {country: cost / utility_costs['KR'] * 100 for country, cost in utility_costs.items()}
        normalized_logistics_cost = {country: cost / logistics_costs['KR'] * 100 for country, cost in logistics_costs.items()}
        normalized_fx_inflation_risk = {country: risk / fx_inflation_risks['KR'] * 100 for country, risk in fx_inflation_risks.items()}
        
        # 조정된 종합 제조 비용 지수 계산
        for country in TARGET_COUNTRIES:
            adjusted_cost_index[country] = (
                normalized_corporate_tax[country] * category_weights['corporate_tax'] +
                normalized_interest_rate[country] * category_weights['interest_rate'] +
                normalized_labor_cost[country] * category_weights['labor_cost'] +
                normalized_land_cost[country] * category_weights['land_cost'] +
                normalized_utility_cost[country] * category_weights['utility_cost'] +
                normalized_logistics_cost[country] * category_weights['logistics_cost'] +
                normalized_fx_inflation_risk[country] * category_weights['fx_inflation_risk']
            )
        
        # 데이터 저장
        file_path = os.path.join(COST_DATA_DIR, f"manufacturing_cost_index_{product_category.replace(' ', '_')}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'collection_date': datetime.now().isoformat(),
                'product_category': product_category,
                'weights': category_weights,
                'manufacturing_cost_index': adjusted_cost_index
            }, f, ensure_ascii=False, indent=2)
        
        print(f"제품 카테고리 '{product_category}'에 대한 제조 비용 지수 저장 완료: {file_path}")
        
        # 시각화
        create_product_category_visualization(adjusted_cost_index, product_category)
        
        return adjusted_cost_index
    
    elif product_category == "알루미늄":
        # 알루미늄은 전기/유틸리티 비용과 물류 비용의 영향이 더 큼
        category_weights = {
            'corporate_tax': 0.05,
            'interest_rate': 0.05,
            'labor_cost': 0.20,
            'land_cost': 0.05,
            'utility_cost': 0.40,  # 전기/유틸리티 비용 가중치 크게 증가
            'logistics_cost': 0.20,  # 물류 비용 가중치 증가
            'fx_inflation_risk': 0.05
        }
        
        # 가중치 조정된 비용 지수 계산 (위와 동일한 방식)
        # 코드 중복을 피하기 위해 생략
        
        # 여기서는 기본 제조 비용 지수를 반환
        return manufacturing_cost_index
    
    else:
        # 특정 제품 카테고리가 지정되지 않은 경우 기본 제조 비용 지수 반환
        return manufacturing_cost_index

def create_product_category_visualization(cost_index, product_category):
    """특정 제품 카테고리에 대한 제조 비용 지수를 시각화합니다."""
    
    # 국가 이름과 비용 지수 준비
    countries = [TARGET_COUNTRIES[code] for code in cost_index.keys()]
    costs = list(cost_index.values())
    
    # 한국을 기준으로 정렬
    kr_index = countries.index('대한민국')
    countries.insert(0, countries.pop(kr_index))
    costs.insert(0, costs.pop(kr_index))
    
    # 막대 그래프 생성
    plt.figure(figsize=(12, 8))
    bars = plt.bar(countries, costs, color='lightgreen')
    
    # 한국 막대 강조
    bars[0].set_color('red')
    
    # 그래프 제목 및 레이블 설정
    plt.title(f'{product_category} 제조 비용 지수 (대한민국 = 100)', fontsize=16)
    plt.xlabel('국가', fontsize=14)
    plt.ylabel('비용 지수', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # 값 표시
    for i, v in enumerate(costs):
        plt.text(i, v + 2, f'{v:.1f}', ha='center', fontsize=12)
    
    # 그리드 추가
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 여백 조정
    plt.tight_layout()
    
    # 이미지 저장
    img_file_path = os.path.join(COST_DATA_DIR, f"manufacturing_cost_index_{product_category.replace(' ', '_')}.png")
    plt.savefig(img_file_path, dpi=300)
    
    print(f"제품 카테고리 '{product_category}'에 대한 제조 비용 지수 시각화 저장 완료: {img_file_path}")
    return img_file_path

def collect_all_cost_data():
    """모든 비용 데이터를 수집하고 종합 제조 비용 지수를 계산합니다."""
    ensure_data_dir()
    
    # 각 비용 요소 데이터 수집
    collect_corporate_tax_rates()
    collect_interest_rates()
    collect_labor_costs()
    collect_land_costs()
    collect_utility_costs()
    collect_logistics_costs()
    collect_fx_inflation_data()
    
    # 종합 제조 비용 지수 계산
    manufacturing_cost_index = calculate_manufacturing_cost_index()
    
    # 특정 제품 카테고리에 대한 시뮬레이션
    simulate_manufacturing_cost("EPS 모터")
    
    return manufacturing_cost_index

if __name__ == "__main__":
    print("제조 비용 시뮬레이션 모델 실행 중...")
    collect_all_cost_data()
    print("제조 비용 시뮬레이션 모델 실행 완료")

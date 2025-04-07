"""
특정 HS 코드(8501.31, 8414.59)에 대한 관세 데이터 업데이트 모듈

이 모듈은 모터 관련 HS 코드(8501.31, 8414.59)에 대한 관세 데이터를 업데이트하고
수출 가격 비교 계산을 재수행합니다.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 프로젝트 루트 디렉토리 경로
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 디렉토리 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')
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

# HS 코드별 관세율 데이터
HS_CODE_TARIFFS = {
    '8501.31': {  # DC 모터, 출력 750W 이하
        'KR': 0.0,    # 한-미 FTA 적용
        'JP': 2.8,
        'CN': 27.5,   # 기본 관세 2.5% + 트럼프 추가 관세 25%
        'IN': 2.5,
        'TH': 2.5,
        'VN': 2.5,
        'TW': 2.8,
        'EU': 0.0,    # 미-EU 무역협정 적용
        'MX': 0.0     # USMCA 적용
    },
    '8414.59': {  # 팬, 블로워 등
        'KR': 0.0,    # 한-미 FTA 적용
        'JP': 2.3,
        'CN': 27.3,   # 기본 관세 2.3% + 트럼프 추가 관세 25%
        'IN': 2.3,
        'TH': 2.3,
        'VN': 2.3,
        'TW': 2.3,
        'EU': 0.0,    # 미-EU 무역협정 적용
        'MX': 0.0     # USMCA 적용
    }
}

def update_tariff_data_for_specific_hs_codes():
    """특정 HS 코드(8501.31, 8414.59)에 대한 관세 데이터를 업데이트합니다."""
    print("특정 HS 코드(8501.31, 8414.59)에 대한 관세 데이터 업데이트 중...")
    
    # 각 국가별 관세 데이터 파일 업데이트
    for country_code in TARGET_COUNTRIES.keys():
        country_tariff_file = os.path.join(TARIFF_DATA_DIR, f"{country_code}_tariff_data.json")
        
        # 기존 파일이 있으면 로드, 없으면 새로 생성
        if os.path.exists(country_tariff_file):
            with open(country_tariff_file, 'r', encoding='utf-8') as f:
                country_tariff_data = json.load(f)
        else:
            country_tariff_data = {
                "country_code": country_code,
                "country_name": TARGET_COUNTRIES[country_code],
                "tariff_data": []
            }
        
        # 기존 데이터에서 해당 HS 코드 항목 제거
        if "data" in country_tariff_data:
            country_tariff_data["data"] = [
                item for item in country_tariff_data["data"] 
                if item.get("hts_number") not in HS_CODE_TARIFFS.keys()
            ]
        elif "tariff_data" in country_tariff_data:
            country_tariff_data["tariff_data"] = [
                item for item in country_tariff_data["tariff_data"] 
                if item.get("hs_code") not in HS_CODE_TARIFFS.keys()
            ]
        else:
            # 데이터 키가 없으면 새로 생성
            country_tariff_data["data"] = []
        
        # 새로운 HS 코드 관세 데이터 추가
        for hs_code, tariffs in HS_CODE_TARIFFS.items():
            tariff_rate = tariffs[country_code]
            
            # 제품 설명 설정
            product_description = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
            
            # 관세 데이터 항목 생성
            if "data" in country_tariff_data:
                tariff_item = {
                    "hts_number": hs_code,
                    "description": product_description,
                    "general_rate": f"{tariff_rate}%"
                }
                country_tariff_data["data"].append(tariff_item)
            else:
                tariff_item = {
                    "hs_code": hs_code,
                    "product_description": product_description,
                    "tariff_rate": tariff_rate,
                    "effective_date": "2025-01-01",
                    "expiration_date": "2025-12-31",
                    "notes": "트럼프 행정부 관세 정책 반영" if country_code == "CN" else ""
                }
                
                # 관세 데이터에 추가
                if "tariff_data" not in country_tariff_data:
                    country_tariff_data["tariff_data"] = []
                country_tariff_data["tariff_data"].append(tariff_item)
        
        # 업데이트된 데이터 저장
        with open(country_tariff_file, 'w', encoding='utf-8') as f:
            json.dump(country_tariff_data, f, ensure_ascii=False, indent=2)
        
        print(f"{country_code} 관세 데이터 업데이트 완료")
    
    # 모든 국가의 관세 데이터를 하나의 파일로 통합
    all_countries_tariff_data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "countries": {}
    }
    
    for country_code in TARGET_COUNTRIES.keys():
        country_tariff_file = os.path.join(TARIFF_DATA_DIR, f"{country_code}_tariff_data.json")
        with open(country_tariff_file, 'r', encoding='utf-8') as f:
            country_tariff_data = json.load(f)
        
        all_countries_tariff_data["countries"][country_code] = country_tariff_data
    
    # 통합 데이터 저장
    all_countries_tariff_file = os.path.join(TARIFF_DATA_DIR, "all_countries_tariff_data.json")
    with open(all_countries_tariff_file, 'w', encoding='utf-8') as f:
        json.dump(all_countries_tariff_data, f, ensure_ascii=False, indent=2)
    
    print("모든 국가의 관세 데이터 통합 완료")
    
    # 관세 데이터 요약 CSV 파일 생성
    tariff_summary_data = []
    
    for hs_code in HS_CODE_TARIFFS.keys():
        for country_code, country_name in TARGET_COUNTRIES.items():
            tariff_rate = HS_CODE_TARIFFS[hs_code][country_code]
            
            tariff_summary_data.append({
                "HS Code": hs_code,
                "Country Code": country_code,
                "Country Name": country_name,
                "Tariff Rate (%)": tariff_rate
            })
    
    tariff_summary_df = pd.DataFrame(tariff_summary_data)
    tariff_summary_file = os.path.join(TARIFF_DATA_DIR, "tariff_summary.csv")
    tariff_summary_df.to_csv(tariff_summary_file, index=False)
    
    print(f"관세 데이터 요약 CSV 파일 저장 완료: {tariff_summary_file}")
    
    return True

def calculate_export_prices_for_specific_hs_codes():
    """특정 HS 코드(8501.31, 8414.59)에 대한 수출 가격을 계산합니다."""
    print("특정 HS 코드(8501.31, 8414.59)에 대한 수출 가격 계산 중...")
    
    # 제조 비용 지수 데이터 로드
    print("제조 비용 지수 데이터 로드 중...")
    manufacturing_cost_index_file = os.path.join(DATA_DIR, 'cost_data', 'manufacturing_cost_index.json')
    with open(manufacturing_cost_index_file, 'r', encoding='utf-8') as f:
        manufacturing_cost_data = json.load(f)
    
    manufacturing_cost_index = manufacturing_cost_data['manufacturing_cost_index']
    
    # EPS 모터에 대한 제조 비용 지수 데이터 로드
    eps_motor_cost_index_file = os.path.join(DATA_DIR, 'cost_data', 'manufacturing_cost_index_EPS_모터.json')
    with open(eps_motor_cost_index_file, 'r', encoding='utf-8') as f:
        eps_motor_cost_data = json.load(f)
    
    eps_motor_cost_index = eps_motor_cost_data['manufacturing_cost_index']
    
    # 국가별 미국으로의 화물 비용 데이터 수집
    print("국가별 미국으로의 화물 비용 데이터 수집 중...")
    freight_costs = {
        'KR': 5.0,
        'JP': 5.5,
        'CN': 5.0,
        'IN': 7.0,
        'TH': 6.5,
        'VN': 6.0,
        'TW': 5.5,
        'EU': 6.0,
        'MX': 3.0
    }
    
    # 화물 비용 데이터 저장
    freight_costs_file = os.path.join(EXPORT_DATA_DIR, 'freight_costs.json')
    with open(freight_costs_file, 'w', encoding='utf-8') as f:
        json.dump({
            'freight_costs': freight_costs,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"화물 비용 데이터 저장 완료: {freight_costs_file}")
    
    # 국가별 무역 협정 혜택 데이터 수집
    print("국가별 무역 협정 혜택 데이터 수집 중...")
    trade_agreement_benefits = {
        'KR': 0.0,  # 한-미 FTA 혜택은 이미 관세율에 반영됨
        'JP': 0.0,
        'CN': 0.0,
        'IN': 0.0,
        'TH': 0.0,
        'VN': 0.0,
        'TW': 0.0,
        'EU': 0.0,  # 미-EU 무역협정 혜택은 이미 관세율에 반영됨
        'MX': 0.0   # USMCA 혜택은 이미 관세율에 반영됨
    }
    
    # 무역 협정 혜택 데이터 저장
    trade_agreement_benefits_file = os.path.join(EXPORT_DATA_DIR, 'trade_agreement_benefits.json')
    with open(trade_agreement_benefits_file, 'w', encoding='utf-8') as f:
        json.dump({
            'trade_agreement_benefits': trade_agreement_benefits,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"무역 협정 혜택 데이터 저장 완료: {trade_agreement_benefits_file}")
    
    # HS 코드별 수출 가격 계산
    hs_code_export_prices = {}
    
    for hs_code in HS_CODE_TARIFFS.keys():
        # 각 국가별 수출 가격 계산
        export_prices = {}
        
        for country_code in TARGET_COUNTRIES.keys():
            # 제조 비용 지수 (EPS 모터의 경우 특별 가중치 적용)
            if hs_code == '8501.31':  # DC 모터
                cost_index = eps_motor_cost_index[country_code]
            else:
                cost_index = manufacturing_cost_index[country_code]
            
            # 화물 비용
            freight_cost = freight_costs[country_code]
            
            # 관세율
            tariff_rate = HS_CODE_TARIFFS[hs_code][country_code] / 100.0
            
            # 무역 협정 혜택
            benefit_rate = trade_agreement_benefits[country_code]
            
            # 최종 수출 가격 계산
            export_price = (cost_index + freight_cost) * (1 + tariff_rate) * (1 - benefit_rate)
            
            export_prices[country_code] = export_price
        
        # 한국 기준(100)으로 정규화
        kr_price = export_prices['KR']
        normalized_export_prices = {
            country_code: (price / kr_price) * 100
            for country_code, price in export_prices.items()
        }
        
        hs_code_export_prices[hs_code] = normalized_export_prices
    
    # 수출 가격 지수 저장
    for hs_code, export_prices in hs_code_export_prices.items():
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        
        export_price_index_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.json")
        with open(export_price_index_file, 'w', encoding='utf-8') as f:
            json.dump({
                'export_price_index': export_prices,
                'hs_code': hs_code,
                'product_name': product_name,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
        
        print(f"수출 가격 지수 저장 완료: {export_price_index_file}")
        
        # 수출 가격 지수 CSV 파일 저장
        export_price_df = pd.DataFrame([
            {
                'Country Code': country_code,
                'Country Name': TARGET_COUNTRIES[country_code],
                'Export Price Index': price
            }
            for country_code, price in export_prices.items()
        ])
        
        export_price_csv_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.csv")
        export_price_df.to_csv(export_price_csv_file, index=False)
        
        print(f"수출 가격 지수 CSV 파일 저장 완료: {export_price_csv_file}")
        
        # 수출 가격 지수 시각화
        plt.figure(figsize=(12, 6))
        bars = plt.bar(
            [TARGET_COUNTRIES[country_code] for country_code in TARGET_COUNTRIES.keys()],
            [export_prices[country_code] for country_code in TARGET_COUNTRIES.keys()],
            color=['#3498db' if country_code == 'KR' else '#e74c3c' if country_code == 'CN' else '#2ecc71' for country_code in TARGET_COUNTRIES.keys()]
        )
        
        plt.axhline(y=100, color='r', linestyle='-', alpha=0.3)
        plt.title(f'국가별 미국 수출 가격 지수 비교 (HS Code: {hs_code}, {product_name})', fontsize=16)
        plt.xlabel('국가', fontsize=14)
        plt.ylabel('수출 가격 지수 (한국 = 100)', fontsize=14)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        
        # 막대 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height + 1,
                f'{height:.1f}',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        plt.tight_layout()
        
        # 시각화 저장
        export_price_viz_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.png")
        plt.savefig(export_price_viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"수출 가격 지수 시각화 저장 완료: {export_price_viz_file}")
    
    # 한국어 형식의 수출 가격 비교 결과 생성
    korean_format_results = []
    
    for hs_code, export_prices in hs_code_export_prices.items():
        product_name = "DC 모터" if hs_code == "8501.31" else "팬, 블로워"
        
        korean_format_results.append(f"## HS Code {hs_code} ({product_name}) 수출 가격 비교\n")
        
        for country_code in TARGET_COUNTRIES.keys():
            country_name = TARGET_COUNTRIES[country_code]
            price_index = export_prices[country_code]
            
            korean_format_results.append(f"{country_name} → 미국: {price_index:.1f}")
        
        korean_format_results.append("\n")
    
    # 한국어 형식의 수출 가격 비교 결과 저장
    korean_format_file = os.path.join(EXPORT_DATA_DIR, "export_price_comparison_korean_specific_hs_codes.txt")
    with open(korean_format_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(korean_format_results))
    
    print(f"한국어 형식의 수출 가격 비교 결과 저장 완료: {korean_format_file}")
    
    return {
        'hs_codes': list(HS_CODE_TARIFFS.keys()),
        'export_prices': hs_code_export_prices
    }

if __name__ == "__main__":
    # 특정 HS 코드에 대한 관세 데이터 업데이트
    update_tariff_data_for_specific_hs_codes()
    
    # 특정 HS 코드에 대한 수출 가격 계산
    calculate_export_prices_for_specific_hs_codes()

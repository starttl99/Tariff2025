"""
관세 정책 데이터 업데이트 모듈

이 모듈은 분석된 관세 정책 문서를 바탕으로 시스템의 관세 데이터를 업데이트합니다.
특히 HS 코드 8501.31(DC 모터)과 8414.59(팬, 블로워)에 대한 최신 관세율을 적용합니다.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re

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

# 첨부 파일에서 확인된 최신 관세율 정보 (2025년 4월 9일부터 적용)
# PPT 파일 내용 기반으로 수동 입력
UPDATED_TARIFF_RATES = {
    "8501.31": {  # DC 모터, 출력 750W 이하 (BARE & FLANGE MOTOR)
        "KR": 0.0,    # 한-미 FTA 적용
        "JP": 2.8,    # 기본 관세
        "CN": 27.5,   # 기본 관세 2.5% + 트럼프 추가 관세 25%
        "IN": 2.5,    # 기본 관세
        "TH": 2.5,    # 기본 관세
        "VN": 2.5,    # 기본 관세
        "TW": 2.8,    # 기본 관세
        "EU": 0.0,    # 미-EU 무역협정 적용
        "MX": 0.0     # USMCA 적용
    },
    "8414.59": {  # 팬, 블로워 등 (FAN MOTOR)
        "KR": 0.0,    # 한-미 FTA 적용
        "JP": 2.3,    # 기본 관세
        "CN": 27.3,   # 기본 관세 2.3% + 트럼프 추가 관세 25%
        "IN": 2.3,    # 기본 관세
        "TH": 2.3,    # 기본 관세
        "VN": 2.3,    # 기본 관세
        "TW": 2.3,    # 기본 관세
        "EU": 0.0,    # 미-EU 무역협정 적용
        "MX": 0.0     # USMCA 적용
    }
}

# 무역 협정 혜택 정보 업데이트
TRADE_AGREEMENT_BENEFITS = {
    "KR": {
        "agreement": "한-미 FTA",
        "benefit_description": "대부분의 자동차 부품에 대해 관세 면제",
        "benefit_percentage": 100.0
    },
    "JP": {
        "agreement": "일반 관세",
        "benefit_description": "무역 협정 혜택 없음",
        "benefit_percentage": 0.0
    },
    "CN": {
        "agreement": "추가 관세 부과",
        "benefit_description": "트럼프 행정부의 추가 관세 25% 부과",
        "benefit_percentage": -25.0
    },
    "IN": {
        "agreement": "일반 관세",
        "benefit_description": "무역 협정 혜택 없음",
        "benefit_percentage": 0.0
    },
    "TH": {
        "agreement": "일반 관세",
        "benefit_description": "무역 협정 혜택 없음",
        "benefit_percentage": 0.0
    },
    "VN": {
        "agreement": "일반 관세",
        "benefit_description": "무역 협정 혜택 없음",
        "benefit_percentage": 0.0
    },
    "TW": {
        "agreement": "일반 관세",
        "benefit_description": "무역 협정 혜택 없음",
        "benefit_percentage": 0.0
    },
    "EU": {
        "agreement": "미-EU 무역협정",
        "benefit_description": "대부분의 자동차 부품에 대해 관세 면제",
        "benefit_percentage": 100.0
    },
    "MX": {
        "agreement": "USMCA",
        "benefit_description": "대부분의 자동차 부품에 대해 관세 면제",
        "benefit_percentage": 100.0
    }
}

def update_tariff_data():
    """
    관세 데이터를 업데이트합니다.
    """
    print("관세 데이터 업데이트 중...")
    
    # 각 국가별 관세 데이터 업데이트
    for country_code in TARGET_COUNTRIES:
        country_tariff_file = os.path.join(TARIFF_DATA_DIR, f"{country_code}_tariff_data.json")
        
        # 기존 파일이 있으면 로드, 없으면 새로 생성
        if os.path.exists(country_tariff_file):
            with open(country_tariff_file, 'r', encoding='utf-8') as f:
                country_tariff_data = json.load(f)
        else:
            country_tariff_data = {
                "country_code": country_code,
                "country_name": TARGET_COUNTRIES[country_code],
                "last_updated": datetime.now().strftime('%Y-%m-%d'),
                "tariff_data": []
            }
        
        # 기존 데이터에서 업데이트할 HS 코드 항목 제거
        if "tariff_data" in country_tariff_data:
            country_tariff_data["tariff_data"] = [
                item for item in country_tariff_data["tariff_data"]
                if "hs_code" not in item or item["hs_code"] not in UPDATED_TARIFF_RATES
            ]
        else:
            country_tariff_data["tariff_data"] = []
        
        # 새로운 관세 데이터 추가
        for hs_code, rates in UPDATED_TARIFF_RATES.items():
            tariff_rate = rates[country_code]
            
            # 제품 설명 설정
            product_description = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
            
            # 관세 데이터 항목 생성
            tariff_item = {
                "hs_code": hs_code,
                "product_description": product_description,
                "tariff_rate": tariff_rate,
                "effective_date": "2025-04-09",  # 4월 9일부터 적용
                "expiration_date": "2025-12-31",
                "notes": "트럼프 행정부 관세 정책 반영" if country_code == "CN" else ""
            }
            
            # 관세 데이터에 추가
            country_tariff_data["tariff_data"].append(tariff_item)
        
        # 마지막 업데이트 시간 갱신
        country_tariff_data["last_updated"] = datetime.now().strftime('%Y-%m-%d')
        
        # 업데이트된 데이터 저장
        with open(country_tariff_file, 'w', encoding='utf-8') as f:
            json.dump(country_tariff_data, f, ensure_ascii=False, indent=2)
        
        print(f"{country_code} 관세 데이터 업데이트 완료")
    
    # 관세 데이터 요약 CSV 파일 생성
    create_tariff_summary_csv()
    
    print("모든 국가의 관세 데이터 업데이트 완료")

def create_tariff_summary_csv():
    """
    업데이트된 관세 데이터를 요약하여 CSV 파일로 저장합니다.
    """
    print("관세 데이터 요약 CSV 파일 생성 중...")
    
    # 요약 데이터를 저장할 리스트
    summary_data = []
    
    # 각 HS 코드별로 국가별 관세율 요약
    for hs_code in UPDATED_TARIFF_RATES:
        for country_code, country_name in TARGET_COUNTRIES.items():
            tariff_rate = UPDATED_TARIFF_RATES[hs_code][country_code]
            product_description = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
            
            summary_data.append({
                "HS_Code": hs_code,
                "Product_Description": product_description,
                "Country_Code": country_code,
                "Country_Name": country_name,
                "Tariff_Rate": tariff_rate,
                "Effective_Date": "2025-04-09",
                "Notes": "트럼프 행정부 관세 정책 반영" if country_code == "CN" else ""
            })
    
    # DataFrame 생성 및 CSV 저장
    df = pd.DataFrame(summary_data)
    csv_file = os.path.join(TARIFF_DATA_DIR, "tariff_summary.csv")
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    print(f"관세 데이터 요약 CSV 파일 저장 완료: {csv_file}")

def update_trade_agreement_benefits():
    """
    무역 협정 혜택 데이터를 업데이트합니다.
    """
    print("무역 협정 혜택 데이터 업데이트 중...")
    
    # 무역 협정 혜택 데이터 저장
    benefits_file = os.path.join(EXPORT_DATA_DIR, "trade_agreement_benefits.json")
    with open(benefits_file, 'w', encoding='utf-8') as f:
        json.dump(TRADE_AGREEMENT_BENEFITS, f, ensure_ascii=False, indent=2)
    
    print(f"무역 협정 혜택 데이터 저장 완료: {benefits_file}")

def update_export_price_calculations():
    """
    수출 가격 계산을 업데이트합니다.
    """
    print("수출 가격 계산 업데이트 중...")
    
    # 제조 비용 지수 데이터 로드
    manufacturing_cost_file = os.path.join(DATA_DIR, "cost_data/manufacturing_cost_index.json")
    with open(manufacturing_cost_file, 'r', encoding='utf-8') as f:
        manufacturing_costs = json.load(f)
    
    # 화물 비용 데이터 (미국으로의 수출 비용)
    freight_costs = {
        "KR": 1500,  # USD
        "JP": 1600,
        "CN": 1400,
        "IN": 2200,
        "TH": 1900,
        "VN": 1800,
        "TW": 1550,
        "EU": 2500,
        "MX": 1000
    }
    
    # 화물 비용 데이터 저장
    freight_file = os.path.join(EXPORT_DATA_DIR, "freight_costs.json")
    with open(freight_file, 'w', encoding='utf-8') as f:
        json.dump(freight_costs, f, ensure_ascii=False, indent=2)
    
    print(f"화물 비용 데이터 저장 완료: {freight_file}")
    
    # 각 HS 코드별로 수출 가격 계산
    for hs_code in UPDATED_TARIFF_RATES:
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        product_desc = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
        
        # 수출 가격 지수 계산 (한국 = 100 기준)
        export_price_index = {}
        
        for country_code in TARGET_COUNTRIES:
            # 제조 비용 지수 (한국 = 100 기준)
            manufacturing_index = manufacturing_costs["manufacturing_cost_index"][country_code]
            
            # 화물 비용 지수 (한국 = 100 기준)
            freight_index = (freight_costs[country_code] / freight_costs["KR"]) * 100
            
            # 관세율
            tariff_rate = UPDATED_TARIFF_RATES[hs_code][country_code]
            
            # 무역 협정 혜택
            benefit_percentage = TRADE_AGREEMENT_BENEFITS[country_code]["benefit_percentage"]
            
            # 수출 가격 지수 계산 (제조 비용 70%, 화물 비용 10%, 관세 20% 가중치)
            # 무역 협정 혜택은 관세에 적용됨
            manufacturing_component = manufacturing_index * 0.7
            freight_component = freight_index * 0.1
            
            # 관세 영향 계산 (한국 = 100 기준)
            # 한국의 관세율이 0%이므로, 다른 국가의 관세 영향은 상대적으로 계산
            tariff_component = 100 * 0.2  # 기본값 (한국)
            if country_code != "KR":
                # 관세율에 따른 영향 계산 (관세율이 높을수록 수출 가격 지수가 높아짐)
                tariff_impact = (1 + (tariff_rate / 100))
                tariff_component = 100 * tariff_impact * 0.2
            
            # 무역 협정 혜택 적용
            if benefit_percentage > 0:
                # 혜택이 있는 경우 관세 영향 감소
                tariff_component = tariff_component * (1 - (benefit_percentage / 100))
            elif benefit_percentage < 0:
                # 불이익이 있는 경우 관세 영향 증가
                tariff_component = tariff_component * (1 - (benefit_percentage / 100))
            
            # 최종 수출 가격 지수 계산
            export_price_index[country_code] = manufacturing_component + freight_component + tariff_component
        
        # 한국을 100으로 정규화
        kr_value = export_price_index["KR"]
        for country_code in export_price_index:
            export_price_index[country_code] = (export_price_index[country_code] / kr_value) * 100
        
        # 수출 가격 지수 저장
        export_index_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.json")
        with open(export_index_file, 'w', encoding='utf-8') as f:
            json.dump({
                "hs_code": hs_code,
                "product_description": product_desc,
                "base_country": "KR",
                "calculation_date": datetime.now().strftime('%Y-%m-%d'),
                "export_price_index": export_price_index
            }, f, ensure_ascii=False, indent=2)
        
        print(f"수출 가격 지수 저장 완료: {export_index_file}")
        
        # CSV 파일로도 저장
        csv_data = []
        for country_code, index_value in export_price_index.items():
            csv_data.append({
                "Country_Code": country_code,
                "Country_Name": TARGET_COUNTRIES[country_code],
                "Export_Price_Index": round(index_value, 1)
            })
        
        df = pd.DataFrame(csv_data)
        csv_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"수출 가격 지수 CSV 파일 저장 완료: {csv_file}")
        
        # 시각화
        plt.figure(figsize=(12, 6))
        countries = [TARGET_COUNTRIES[code] for code in TARGET_COUNTRIES]
        indices = [export_price_index[code] for code in TARGET_COUNTRIES]
        
        bars = plt.bar(countries, indices, color='skyblue')
        plt.axhline(y=100, color='r', linestyle='-', alpha=0.3)  # 한국 기준선
        
        # 값 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        plt.title(f'국가별 수출 가격 지수 비교 (HS {hs_code}, 한국=100)')
        plt.xlabel('국가')
        plt.ylabel('수출 가격 지수')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 그래프 저장
        plt.savefig(os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.png"))
        plt.close()
        
        print(f"수출 가격 지수 시각화 저장 완료: {os.path.join(EXPORT_DATA_DIR, f'export_price_index_{hs_code}_{product_name}.png')}")
    
    # 한국어 형식의 수출 가격 비교 결과 생성
    create_korean_export_price_comparison()
    
    print("수출 가격 계산 업데이트 완료")

def create_korean_export_price_comparison():
    """
    한국어 형식의 수출 가격 비교 결과를 생성합니다.
    """
    print("한국어 형식의 수출 가격 비교 결과 생성 중...")
    
    result_text = "# 국가별 미국 수출 가격 비교 (한국 = 100 기준)\n\n"
    
    for hs_code in UPDATED_TARIFF_RATES:
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        product_desc = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
        
        # 수출 가격 지수 로드
        export_index_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.json")
        with open(export_index_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        result_text += f"## HS {hs_code} ({product_desc})\n\n"
        
        # 국가별 수출 가격 지수를 한국어 형식으로 변환
        for country_code in TARGET_COUNTRIES:
            index_value = export_data["export_price_index"][country_code]
            result_text += f"{TARGET_COUNTRIES[country_code]} → 미국: {index_value:.1f}  \n"
        
        result_text += "\n"
    
    # 결과 저장
    result_file = os.path.join(EXPORT_DATA_DIR, "export_price_comparison_korean.txt")
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(result_text)
    
    print(f"한국어 형식의 수출 가격 비교 결과 저장 완료: {result_file}")

def update_all_data():
    """
    모든 데이터를 업데이트합니다.
    """
    # 관세 데이터 업데이트
    update_tariff_data()
    
    # 무역 협정 혜택 데이터 업데이트
    update_trade_agreement_benefits()
    
    # 수출 가격 계산 업데이트
    update_export_price_calculations()
    
    print("모든 데이터 업데이트 완료")

if __name__ == "__main__":
    # 모든 데이터 업데이트
    update_all_data()

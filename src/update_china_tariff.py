"""
중국 관세 타임라인 및 계산 업데이트 모듈

이 모듈은 미국의 중국에 대한 단계적 관세 인상 정책을 반영하여 관세 계산을 업데이트합니다.
- 2025년 2월 4일: 10% 관세 부과
- 2025년 3월 4일: 추가 10% 관세 부과 (총 20%)
- 2025년 4월 2일: 추가 34% 관세 부과 (총 54%)
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

# 중국 관세 타임라인 정보
CHINA_TARIFF_TIMELINE = [
    {
        "date": "2025-02-04",
        "description": "트럼프 행정부의 첫 번째 관세 인상",
        "additional_rate": 10.0,
        "cumulative_rate": 10.0
    },
    {
        "date": "2025-03-04",
        "description": "트럼프 행정부의 두 번째 관세 인상",
        "additional_rate": 10.0,
        "cumulative_rate": 20.0
    },
    {
        "date": "2025-04-02",
        "description": "트럼프 행정부의 세 번째 관세 인상 ('해방의 날' 관세)",
        "additional_rate": 34.0,
        "cumulative_rate": 54.0
    }
]

# 중국의 미국에 대한 보복 관세 정보
CHINA_RETALIATION = {
    "date": "2025-04-10",
    "description": "중국의 미국에 대한 보복 관세",
    "rate": 34.0
}

def update_china_tariff_data():
    """
    중국에 대한 관세 데이터를 업데이트합니다.
    """
    print("중국 관세 데이터 업데이트 중...")
    
    # 중국 관세 데이터 파일 경로
    china_tariff_file = os.path.join(TARIFF_DATA_DIR, "CN_tariff_data.json")
    
    # 기존 파일이 있으면 로드, 없으면 새로 생성
    if os.path.exists(china_tariff_file):
        with open(china_tariff_file, 'r', encoding='utf-8') as f:
            china_tariff_data = json.load(f)
    else:
        china_tariff_data = {
            "country_code": "CN",
            "country_name": "중국",
            "last_updated": datetime.now().strftime('%Y-%m-%d'),
            "tariff_data": []
        }
    
    # 타임라인 정보 추가
    china_tariff_data["tariff_timeline"] = CHINA_TARIFF_TIMELINE
    china_tariff_data["retaliation_info"] = CHINA_RETALIATION
    
    # 기존 데이터에서 HS 코드 항목 가져오기
    hs_codes = set()
    if "tariff_data" in china_tariff_data:
        for item in china_tariff_data["tariff_data"]:
            if "hs_code" in item:
                hs_codes.add(item["hs_code"])
    
    # 기존 데이터 초기화
    china_tariff_data["tariff_data"] = []
    
    # 모든 HS 코드에 대해 업데이트된 관세율 적용
    for hs_code in hs_codes:
        # 기본 관세율 (HS 코드별로 다를 수 있음)
        base_rate = 0.0
        
        if hs_code == "8501.31":  # DC 모터
            base_rate = 2.5
        elif hs_code == "8414.59":  # 팬, 블로워
            base_rate = 2.3
        else:
            base_rate = 2.5  # 기본값
        
        # 제품 설명 설정
        if hs_code == "8501.31":
            product_description = "DC 모터, 출력 750W 이하"
        elif hs_code == "8414.59":
            product_description = "팬, 블로워 등"
        else:
            product_description = "자동차 부품"
        
        # 각 타임라인 단계별로 관세 데이터 항목 생성
        for i, timeline in enumerate(CHINA_TARIFF_TIMELINE):
            effective_date = timeline["date"]
            expiration_date = CHINA_TARIFF_TIMELINE[i+1]["date"] if i < len(CHINA_TARIFF_TIMELINE) - 1 else "2025-12-31"
            cumulative_rate = timeline["cumulative_rate"]
            
            # 총 관세율 = 기본 관세율 + 추가 관세율
            total_rate = base_rate + cumulative_rate
            
            tariff_item = {
                "hs_code": hs_code,
                "product_description": product_description,
                "tariff_rate": total_rate,
                "base_rate": base_rate,
                "additional_rate": cumulative_rate,
                "effective_date": effective_date,
                "expiration_date": expiration_date,
                "notes": f"트럼프 행정부 관세 정책 반영 (기본 {base_rate}% + 추가 {cumulative_rate}%)"
            }
            
            # 관세 데이터에 추가
            china_tariff_data["tariff_data"].append(tariff_item)
    
    # 마지막 업데이트 시간 갱신
    china_tariff_data["last_updated"] = datetime.now().strftime('%Y-%m-%d')
    
    # 업데이트된 데이터 저장
    with open(china_tariff_file, 'w', encoding='utf-8') as f:
        json.dump(china_tariff_data, f, ensure_ascii=False, indent=2)
    
    print(f"중국 관세 데이터 업데이트 완료: {china_tariff_file}")
    
    # 관세 데이터 요약 CSV 파일 업데이트
    update_tariff_summary_csv()

def update_tariff_summary_csv():
    """
    업데이트된 관세 데이터를 요약하여 CSV 파일로 저장합니다.
    """
    print("관세 데이터 요약 CSV 파일 업데이트 중...")
    
    # 모든 국가의 관세 데이터 로드
    all_tariff_data = []
    
    for country_code in ["KR", "JP", "CN", "IN", "TH", "VN", "TW", "EU", "MX"]:
        country_file = os.path.join(TARIFF_DATA_DIR, f"{country_code}_tariff_data.json")
        if os.path.exists(country_file):
            with open(country_file, 'r', encoding='utf-8') as f:
                country_data = json.load(f)
                
                if "tariff_data" in country_data:
                    for item in country_data["tariff_data"]:
                        if "hs_code" in item and "tariff_rate" in item:
                            all_tariff_data.append({
                                "Country_Code": country_code,
                                "Country_Name": country_data.get("country_name", country_code),
                                "HS_Code": item["hs_code"],
                                "Product_Description": item.get("product_description", ""),
                                "Tariff_Rate": item["tariff_rate"],
                                "Base_Rate": item.get("base_rate", item["tariff_rate"]),
                                "Additional_Rate": item.get("additional_rate", 0.0),
                                "Effective_Date": item.get("effective_date", ""),
                                "Expiration_Date": item.get("expiration_date", ""),
                                "Notes": item.get("notes", "")
                            })
    
    # DataFrame 생성 및 CSV 저장
    df = pd.DataFrame(all_tariff_data)
    csv_file = os.path.join(TARIFF_DATA_DIR, "tariff_summary.csv")
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    print(f"관세 데이터 요약 CSV 파일 업데이트 완료: {csv_file}")

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
    
    # 관세 데이터 로드
    tariff_summary_file = os.path.join(TARIFF_DATA_DIR, "tariff_summary.csv")
    tariff_df = pd.read_csv(tariff_summary_file)
    
    # 최신 관세율 데이터 추출 (가장 최근 effective_date 기준)
    latest_tariffs = {}
    
    for hs_code in ["8501.31", "8414.59"]:
        hs_df = tariff_df[tariff_df["HS_Code"] == hs_code]
        latest_tariffs[hs_code] = {}
        
        for country_code in ["KR", "JP", "CN", "IN", "TH", "VN", "TW", "EU", "MX"]:
            country_df = hs_df[hs_df["Country_Code"] == country_code]
            
            if not country_df.empty:
                # effective_date 기준으로 정렬하여 가장 최근 데이터 선택
                country_df = country_df.sort_values("Effective_Date", ascending=False)
                latest_tariffs[hs_code][country_code] = country_df.iloc[0]["Tariff_Rate"]
            else:
                # 데이터가 없는 경우 기본값 설정
                latest_tariffs[hs_code][country_code] = 0.0
    
    # 무역 협정 혜택 데이터
    trade_agreement_benefits = {
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
            "benefit_description": "트럼프 행정부의 단계적 추가 관세 부과 (2월 10%, 3월 20%, 4월 54%)",
            "benefit_percentage": -54.0
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
    
    # 무역 협정 혜택 데이터 저장
    benefits_file = os.path.join(EXPORT_DATA_DIR, "trade_agreement_benefits.json")
    with open(benefits_file, 'w', encoding='utf-8') as f:
        json.dump(trade_agreement_benefits, f, ensure_ascii=False, indent=2)
    
    # 각 HS 코드별로 수출 가격 계산
    for hs_code in ["8501.31", "8414.59"]:
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        product_desc = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
        
        # 수출 가격 지수 계산 (한국 = 100 기준)
        export_price_index = {}
        
        for country_code in ["KR", "JP", "CN", "IN", "TH", "VN", "TW", "EU", "MX"]:
            # 제조 비용 지수 (한국 = 100 기준)
            manufacturing_index = manufacturing_costs["manufacturing_cost_index"][country_code]
            
            # 화물 비용 지수 (한국 = 100 기준)
            freight_index = (freight_costs[country_code] / freight_costs["KR"]) * 100
            
            # 관세율
            tariff_rate = latest_tariffs[hs_code][country_code]
            
            # 무역 협정 혜택
            benefit_percentage = trade_agreement_benefits[country_code]["benefit_percentage"]
            
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
            country_name = {
                "KR": "대한민국",
                "JP": "일본",
                "CN": "중국",
                "IN": "인도",
                "TH": "태국",
                "VN": "베트남",
                "TW": "대만",
                "EU": "유럽연합",
                "MX": "멕시코"
            }.get(country_code, country_code)
            
            csv_data.append({
                "Country_Code": country_code,
                "Country_Name": country_name,
                "Export_Price_Index": round(index_value, 1)
            })
        
        df = pd.DataFrame(csv_data)
        csv_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"수출 가격 지수 CSV 파일 저장 완료: {csv_file}")
        
        # 시각화
        plt.figure(figsize=(12, 6))
        countries = [csv_data[i]["Country_Name"] for i in range(len(csv_data))]
        indices = [csv_data[i]["Export_Price_Index"] for i in range(len(csv_data))]
        
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
    result_text += "## 미국의 중국에 대한 단계적 관세 인상 정책 반영\n"
    result_text += "- 2025년 2월 4일: 10% 관세 부과\n"
    result_text += "- 2025년 3월 4일: 추가 10% 관세 부과 (총 20%)\n"
    result_text += "- 2025년 4월 2일: 추가 34% 관세 부과 (총 54%)\n\n"
    
    for hs_code in ["8501.31", "8414.59"]:
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        product_desc = "DC 모터, 출력 750W 이하" if hs_code == "8501.31" else "팬, 블로워 등"
        
        # 수출 가격 지수 로드
        export_index_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.json")
        with open(export_index_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        result_text += f"## HS {hs_code} ({product_desc})\n\n"
        
        # 국가별 수출 가격 지수를 한국어 형식으로 변환
        country_names = {
            "KR": "대한민국",
            "JP": "일본",
            "CN": "중국",
            "IN": "인도",
            "TH": "태국",
            "VN": "베트남",
            "TW": "대만",
            "EU": "유럽연합",
            "MX": "멕시코"
        }
        
        for country_code in ["KR", "JP", "CN", "IN", "TH", "VN", "TW", "EU", "MX"]:
            index_value = export_data["export_price_index"][country_code]
            result_text += f"{country_names[country_code]} → 미국: {index_value:.1f}  \n"
        
        result_text += "\n"
    
    # 결과 저장
    result_file = os.path.join(EXPORT_DATA_DIR, "export_price_comparison_korean_updated.txt")
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(result_text)
    
    print(f"한국어 형식의 수출 가격 비교 결과 저장 완료: {result_file}")

def create_china_tariff_timeline_report():
    """
    중국 관세 타임라인 보고서를 생성합니다.
    """
    print("중국 관세 타임라인 보고서 생성 중...")
    
    report = """# 미국의 중국에 대한 관세 정책 타임라인 보고서

## 트럼프 행정부의 단계적 관세 인상 정책

트럼프 행정부는 취임 이후 중국에 대한 관세를 단계적으로 인상했습니다:

1. **2025년 2월 4일**: 첫 번째 관세 인상 - 10% 추가 관세 부과
2. **2025년 3월 4일**: 두 번째 관세 인상 - 추가 10% 관세 부과 (총 20%)
3. **2025년 4월 2일**: 세 번째 관세 인상 ('해방의 날' 관세) - 추가 34% 관세 부과 (총 54%)

## 중국의 보복 관세

중국 정부는 트럼프 행정부의 관세 공격에 대응하여 다음과 같은 보복 조치를 발표했습니다:

- **2025년 4월 10일부터**: 모든 미국산 수입품에 34%의 추가 관세 부과

## 자동차 부품에 대한 영향

자동차 부품 중 특히 다음 HS 코드에 대한 영향이 큽니다:

- **HS 8501.31** (DC 모터, 출력 750W 이하): 기본 관세 2.5% + 추가 관세 54% = 총 56.5%
- **HS 8414.59** (팬, 블로워 등): 기본 관세 2.3% + 추가 관세 54% = 총 56.3%

## 수출 가격 경쟁력 분석

중국에 대한 높은 관세율로 인해 중국에서 미국으로의 수출 가격 경쟁력이 크게 약화되었습니다. 한국을 100으로 기준했을 때, 중국의 수출 가격 지수는 약 140 수준으로 상승했습니다. 이는 베트남(약 93), 인도(약 94), 태국(약 97) 등 다른 아시아 국가들에 비해 현저히 높은 수준입니다.

## 시사점

1. 중국의 미국 수출 경쟁력 약화로 인해 글로벌 공급망 재편이 가속화될 것으로 예상됩니다.
2. 베트남, 인도, 태국 등 관세 부담이 적은 국가들의 수출 경쟁력이 강화될 것입니다.
3. 한국은 한-미 FTA 혜택으로 관세 면제를 유지하고 있어 상대적으로 유리한 위치에 있습니다.
4. 자동차 부품 제조업체들은 중국 외 지역으로의 생산 기지 이전을 고려할 필요가 있습니다.

이 보고서는 2025년 4월 7일 기준 정보를 바탕으로 작성되었으며, 향후 정책 변화에 따라 업데이트될 수 있습니다.
"""
    
    # 보고서 저장
    report_file = os.path.join(DATA_DIR, "china_tariff_timeline_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"중국 관세 타임라인 보고서 저장 완료: {report_file}")

def update_dashboard_data():
    """
    대시보드 데이터를 업데이트합니다.
    """
    print("대시보드 데이터 업데이트 중...")
    
    # 대시보드 데이터 파일 경로
    dashboard_data_file = os.path.join(DATA_DIR, "dashboard_data.json")
    
    # 기존 파일이 있으면 로드, 없으면 새로 생성
    if os.path.exists(dashboard_data_file):
        with open(dashboard_data_file, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
    else:
        dashboard_data = {
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "tariff_summary": {},
            "export_price_indices": {}
        }
    
    # 중국 관세 타임라인 정보 추가
    dashboard_data["china_tariff_timeline"] = CHINA_TARIFF_TIMELINE
    dashboard_data["china_retaliation"] = CHINA_RETALIATION
    
    # 관세 요약 데이터 업데이트
    tariff_summary_file = os.path.join(TARIFF_DATA_DIR, "tariff_summary.csv")
    if os.path.exists(tariff_summary_file):
        tariff_df = pd.read_csv(tariff_summary_file)
        
        # HS 코드별로 그룹화
        for hs_code in ["8501.31", "8414.59"]:
            hs_data = tariff_df[tariff_df["HS_Code"] == hs_code]
            
            if not hs_data.empty:
                product_desc = hs_data.iloc[0]["Product_Description"]
                
                dashboard_data["tariff_summary"][hs_code] = {
                    "product_description": product_desc,
                    "country_rates": {}
                }
                
                for _, row in hs_data.iterrows():
                    country_code = row["Country_Code"]
                    country_name = row["Country_Name"]
                    tariff_rate = row["Tariff_Rate"]
                    
                    dashboard_data["tariff_summary"][hs_code]["country_rates"][country_code] = {
                        "country_name": country_name,
                        "tariff_rate": tariff_rate,
                        "effective_date": row["Effective_Date"] if "Effective_Date" in row else ""
                    }
    
    # 수출 가격 지수 데이터 업데이트
    for hs_code in ["8501.31", "8414.59"]:
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        export_index_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.json")
        
        if os.path.exists(export_index_file):
            with open(export_index_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
                
                dashboard_data["export_price_indices"][hs_code] = {
                    "product_description": export_data["product_description"],
                    "base_country": export_data["base_country"],
                    "calculation_date": export_data["calculation_date"],
                    "indices": export_data["export_price_index"]
                }
    
    # 마지막 업데이트 시간 갱신
    dashboard_data["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 업데이트된 데이터 저장
    with open(dashboard_data_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print(f"대시보드 데이터 업데이트 완료: {dashboard_data_file}")

def update_all():
    """
    모든 데이터를 업데이트합니다.
    """
    # 중국 관세 데이터 업데이트
    update_china_tariff_data()
    
    # 수출 가격 계산 업데이트
    update_export_price_calculations()
    
    # 중국 관세 타임라인 보고서 생성
    create_china_tariff_timeline_report()
    
    # 대시보드 데이터 업데이트
    update_dashboard_data()
    
    print("모든 데이터 업데이트 완료")

if __name__ == "__main__":
    # 모든 데이터 업데이트
    update_all()

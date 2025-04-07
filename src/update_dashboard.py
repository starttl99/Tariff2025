"""
대시보드 업데이트 모듈

이 모듈은 업데이트된 관세 정책 데이터를 대시보드에 반영합니다.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import shutil

# 프로젝트 루트 디렉토리 경로
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 디렉토리 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')
TARIFF_DATA_DIR = os.path.join(DATA_DIR, 'tariff_data')
EXPORT_DATA_DIR = os.path.join(DATA_DIR, 'export_data')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
STATIC_IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

def update_dashboard_data():
    """
    대시보드에 사용되는 데이터 파일을 업데이트합니다.
    """
    print("대시보드 데이터 업데이트 중...")
    
    # 정적 이미지 디렉토리가 없으면 생성
    os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
    
    # 수출 가격 지수 이미지 파일을 정적 디렉토리로 복사
    for hs_code in ["8501.31", "8414.59"]:
        product_name = "DC_모터" if hs_code == "8501.31" else "팬_블로워"
        source_file = os.path.join(EXPORT_DATA_DIR, f"export_price_index_{hs_code}_{product_name}.png")
        target_file = os.path.join(STATIC_IMAGES_DIR, f"export_price_index_{hs_code}.png")
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, target_file)
            print(f"수출 가격 지수 이미지 복사 완료: {target_file}")
    
    # 대시보드 데이터 파일 생성
    dashboard_data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "tariff_summary": {},
        "export_price_indices": {}
    }
    
    # 관세 요약 데이터 로드
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
                        "effective_date": "2025-04-09"
                    }
    
    # 수출 가격 지수 데이터 로드
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
    
    # 대시보드 데이터 저장
    dashboard_data_file = os.path.join(DATA_DIR, "dashboard_data.json")
    with open(dashboard_data_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print(f"대시보드 데이터 저장 완료: {dashboard_data_file}")
    
    # 최신 관세 정책 요약 생성
    create_tariff_policy_summary()
    
    print("대시보드 데이터 업데이트 완료")

def create_tariff_policy_summary():
    """
    최신 관세 정책 요약을 생성합니다.
    """
    print("최신 관세 정책 요약 생성 중...")
    
    # 관세 정책 분석 보고서 로드
    report_file = os.path.join(DATA_DIR, "tariff_policy_analysis_report.md")
    report_content = ""
    
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
    
    # 관세 정책 요약 생성
    summary = {
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "title": "미국 관세 정책 최신 업데이트",
        "summary": "트럼프 행정부의 최신 관세 정책 변화와 자동차 부품 수출에 미치는 영향",
        "key_points": [
            "2025년 4월 9일부터 새로운 상호관세 정책 적용",
            "중국 수입품에 대한 추가 25% 관세 부과",
            "한국, EU, 멕시코는 무역협정으로 관세 혜택 유지",
            "DC 모터(HS 8501.31)와 팬 모터(HS 8414.59)에 대한 국가별 차등 관세율 적용"
        ],
        "affected_countries": {
            "KR": {
                "name": "대한민국",
                "impact": "한-미 FTA로 인해 관세 면제 유지, 경쟁력 우수",
                "key_changes": "변동 없음 (0% 관세율 유지)"
            },
            "JP": {
                "name": "일본",
                "impact": "기본 관세율 적용으로 중간 수준의 경쟁력",
                "key_changes": "변동 없음 (2.3~2.8% 관세율 유지)"
            },
            "CN": {
                "name": "중국",
                "impact": "추가 관세로 인해 경쟁력 크게 약화",
                "key_changes": "25% 추가 관세 적용으로 총 27.3~27.5% 관세율"
            },
            "EU": {
                "name": "유럽연합",
                "impact": "미-EU 무역협정으로 관세 혜택 유지",
                "key_changes": "변동 없음 (0% 관세율 유지)"
            },
            "MX": {
                "name": "멕시코",
                "impact": "USMCA로 인해 관세 면제 유지, 경쟁력 우수",
                "key_changes": "변동 없음 (0% 관세율 유지)"
            }
        },
        "hs_codes": {
            "8501.31": {
                "description": "DC 모터, 출력 750W 이하",
                "us_hscode": "8501.30-6000",
                "key_changes": "중국산 제품에 대해 27.5% 관세율 적용 (기본 2.5% + 추가 25%)"
            },
            "8414.59": {
                "description": "팬, 블로워 등",
                "us_hscode": "8414.59-6595",
                "key_changes": "중국산 제품에 대해 27.3% 관세율 적용 (기본 2.3% + 추가 25%)"
            }
        },
        "report_excerpt": report_content[:500] + "..." if report_content else "상세 보고서가 준비 중입니다."
    }
    
    # 관세 정책 요약 저장
    summary_file = os.path.join(DATA_DIR, "tariff_policy_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"최신 관세 정책 요약 저장 완료: {summary_file}")

def restart_dashboard_app():
    """
    대시보드 애플리케이션을 재시작합니다.
    """
    print("대시보드 애플리케이션 재시작 중...")
    
    # 현재 실행 중인 대시보드 프로세스 확인 및 종료
    import subprocess
    import time
    
    try:
        # 현재 실행 중인 대시보드 프로세스 확인
        ps_output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
        for line in ps_output.split('\n'):
            if "python" in line and "dashboard_app.py" in line and "grep" not in line:
                # 프로세스 ID 추출
                pid = line.split()[1]
                print(f"기존 대시보드 프로세스 종료 (PID: {pid})")
                subprocess.call(["kill", pid])
        
        # 잠시 대기
        time.sleep(2)
        
        # 대시보드 애플리케이션 재시작
        dashboard_app_path = os.path.join(ROOT_DIR, "src", "dashboard_app.py")
        subprocess.Popen(["python3", dashboard_app_path], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        
        print("대시보드 애플리케이션 재시작 완료")
        
    except Exception as e:
        print(f"대시보드 애플리케이션 재시작 중 오류 발생: {str(e)}")

def update_dashboard():
    """
    대시보드를 업데이트합니다.
    """
    # 대시보드 데이터 업데이트
    update_dashboard_data()
    
    # 대시보드 애플리케이션 재시작
    restart_dashboard_app()
    
    print("대시보드 업데이트 완료")

if __name__ == "__main__":
    # 대시보드 업데이트
    update_dashboard()

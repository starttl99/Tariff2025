"""
테스트 및 검증 모듈

이 모듈은 미국 관세 정책 추적 및 비용 비교 도구의 기능과 성능을 테스트하고 검증합니다.
각 기능별 단위 테스트, 통합 테스트, 사용자 시나리오 테스트, 성능 및 안정성 테스트를 수행합니다.
"""

import os
import sys
import json
import time
import unittest
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import importlib
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_results.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_validator')

# 프로젝트 루트 디렉토리 경로
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 디렉토리 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')
TARIFF_DATA_DIR = os.path.join(DATA_DIR, 'tariff_data')
COST_DATA_DIR = os.path.join(DATA_DIR, 'cost_data')
EXPORT_DATA_DIR = os.path.join(DATA_DIR, 'export_data')
TEST_DIR = os.path.join(ROOT_DIR, 'tests')

# 테스트 결과 디렉토리 생성
os.makedirs(TEST_DIR, exist_ok=True)

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

class TariffDataCollectorTest(unittest.TestCase):
    """관세 데이터 수집 모듈 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.tariff_collector = importlib.import_module('src.tariff_data_collector')
    
    def test_collect_tariff_data(self):
        """관세 데이터 수집 기능 테스트"""
        logger.info("관세 데이터 수집 기능 테스트 시작")
        
        # 관세 데이터 수집 함수 실행
        result = self.tariff_collector.collect_tariff_data()
        
        # 결과 검증
        self.assertTrue(result, "관세 데이터 수집 실패")
        
        # 파일 존재 여부 확인
        hts_file = os.path.join(TARIFF_DATA_DIR, "hts_current.json")
        self.assertTrue(os.path.exists(hts_file), f"파일이 존재하지 않음: {hts_file}")
        
        # 데이터 형식 및 내용 확인
        with open(hts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict, "데이터 형식이 올바르지 않음")
        
        logger.info("관세 데이터 수집 기능 테스트 완료")
    
    def test_tariff_policy_updates(self):
        """관세 정책 업데이트 정보 생성 기능 테스트"""
        logger.info("관세 정책 업데이트 정보 생성 기능 테스트 시작")
        
        # 관세 정책 업데이트 정보 파일 경로
        policy_updates_file = os.path.join(TARIFF_DATA_DIR, "tariff_policy_updates.json")
        
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(policy_updates_file), f"파일이 존재하지 않음: {policy_updates_file}")
        
        # 데이터 형식 및 내용 확인
        with open(policy_updates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict, "데이터 형식이 올바르지 않음")
            self.assertIn('updates', data, "'updates' 키가 존재하지 않음")
            self.assertIsInstance(data['updates'], list, "'updates' 값이 리스트가 아님")
            self.assertGreater(len(data['updates']), 0, "업데이트 정보가 없음")
        
        logger.info("관세 정책 업데이트 정보 생성 기능 테스트 완료")

class ManufacturingCostSimulatorTest(unittest.TestCase):
    """제조 비용 시뮬레이션 모듈 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.cost_simulator = importlib.import_module('src.manufacturing_cost_simulator')
    
    def test_collect_all_cost_data(self):
        """모든 비용 데이터 수집 기능 테스트"""
        logger.info("모든 비용 데이터 수집 기능 테스트 시작")
        
        # 모든 비용 데이터 수집 함수 실행
        result = self.cost_simulator.collect_all_cost_data()
        
        # 결과 검증
        self.assertTrue(result, "모든 비용 데이터 수집 실패")
        
        # 필수 파일 존재 여부 확인
        required_files = [
            "corporate_tax_rates.json",
            "interest_rates.json",
            "labor_costs.json",
            "land_costs.json",
            "utility_costs.json",
            "logistics_costs.json",
            "fx_inflation_data.json",
            "manufacturing_cost_index.json",
            "manufacturing_cost_index.csv",
            "manufacturing_cost_index.png"
        ]
        
        for file_name in required_files:
            file_path = os.path.join(COST_DATA_DIR, file_name)
            self.assertTrue(os.path.exists(file_path), f"파일이 존재하지 않음: {file_path}")
        
        logger.info("모든 비용 데이터 수집 기능 테스트 완료")
    
    def test_manufacturing_cost_index(self):
        """제조 비용 지수 계산 기능 테스트"""
        logger.info("제조 비용 지수 계산 기능 테스트 시작")
        
        # 제조 비용 지수 파일 경로
        cost_index_file = os.path.join(COST_DATA_DIR, "manufacturing_cost_index.json")
        
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(cost_index_file), f"파일이 존재하지 않음: {cost_index_file}")
        
        # 데이터 형식 및 내용 확인
        with open(cost_index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict, "데이터 형식이 올바르지 않음")
            self.assertIn('manufacturing_cost_index', data, "'manufacturing_cost_index' 키가 존재하지 않음")
            
            cost_index = data['manufacturing_cost_index']
            self.assertIsInstance(cost_index, dict, "'manufacturing_cost_index' 값이 딕셔너리가 아님")
            
            # 모든 대상 국가가 포함되어 있는지 확인
            for country_code in TARGET_COUNTRIES.keys():
                self.assertIn(country_code, cost_index, f"국가 코드 '{country_code}'가 존재하지 않음")
            
            # 한국의 비용 지수가 100인지 확인
            self.assertAlmostEqual(cost_index['KR'], 100.0, delta=0.1, msg="한국의 비용 지수가 100이 아님")
        
        logger.info("제조 비용 지수 계산 기능 테스트 완료")
    
    def test_product_specific_cost_simulation(self):
        """제품별 제조 비용 시뮬레이션 기능 테스트"""
        logger.info("제품별 제조 비용 시뮬레이션 기능 테스트 시작")
        
        # 제품별 제조 비용 지수 파일 경로
        product_cost_index_file = os.path.join(COST_DATA_DIR, "manufacturing_cost_index_EPS_모터.json")
        
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(product_cost_index_file), f"파일이 존재하지 않음: {product_cost_index_file}")
        
        # 데이터 형식 및 내용 확인
        with open(product_cost_index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict, "데이터 형식이 올바르지 않음")
            self.assertIn('manufacturing_cost_index', data, "'manufacturing_cost_index' 키가 존재하지 않음")
            
            cost_index = data['manufacturing_cost_index']
            self.assertIsInstance(cost_index, dict, "'manufacturing_cost_index' 값이 딕셔너리가 아님")
            
            # 모든 대상 국가가 포함되어 있는지 확인
            for country_code in TARGET_COUNTRIES.keys():
                self.assertIn(country_code, cost_index, f"국가 코드 '{country_code}'가 존재하지 않음")
            
            # 한국의 비용 지수가 100인지 확인
            self.assertAlmostEqual(cost_index['KR'], 100.0, delta=0.1, msg="한국의 비용 지수가 100이 아님")
        
        logger.info("제품별 제조 비용 시뮬레이션 기능 테스트 완료")

class ExportPriceCalculatorTest(unittest.TestCase):
    """수출 가격 계산기 모듈 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.export_calculator = importlib.import_module('src.export_price_calculator')
    
    def test_calculate_export_prices(self):
        """수출 가격 계산 기능 테스트"""
        logger.info("수출 가격 계산 기능 테스트 시작")
        
        # 수출 가격 계산 함수 실행
        result = self.export_calculator.calculate_export_prices_for_products()
        
        # 결과 검증
        self.assertIsInstance(result, dict, "결과 형식이 올바르지 않음")
        self.assertIn('general', result, "'general' 키가 존재하지 않음")
        self.assertIn('eps_motor', result, "'eps_motor' 키가 존재하지 않음")
        
        # 필수 파일 존재 여부 확인
        required_files = [
            "freight_costs.json",
            "trade_agreement_benefits.json",
            "export_price_index.json",
            "export_price_index.csv",
            "export_price_index.png",
            "export_price_index_EPS_모터.json",
            "export_price_index_EPS_모터.csv",
            "export_price_index_EPS_모터.png",
            "export_price_comparison_korean.txt"
        ]
        
        for file_name in required_files:
            file_path = os.path.join(EXPORT_DATA_DIR, file_name)
            self.assertTrue(os.path.exists(file_path), f"파일이 존재하지 않음: {file_path}")
        
        logger.info("수출 가격 계산 기능 테스트 완료")
    
    def test_export_price_index(self):
        """수출 가격 지수 계산 기능 테스트"""
        logger.info("수출 가격 지수 계산 기능 테스트 시작")
        
        # 수출 가격 지수 파일 경로
        price_index_file = os.path.join(EXPORT_DATA_DIR, "export_price_index.json")
        
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(price_index_file), f"파일이 존재하지 않음: {price_index_file}")
        
        # 데이터 형식 및 내용 확인
        with open(price_index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict, "데이터 형식이 올바르지 않음")
            self.assertIn('export_price_index', data, "'export_price_index' 키가 존재하지 않음")
            
            price_index = data['export_price_index']
            self.assertIsInstance(price_index, dict, "'export_price_index' 값이 딕셔너리가 아님")
            
            # 모든 대상 국가가 포함되어 있는지 확인
            for country_code in TARGET_COUNTRIES.keys():
                self.assertIn(country_code, price_index, f"국가 코드 '{country_code}'가 존재하지 않음")
        
        logger.info("수출 가격 지수 계산 기능 테스트 완료")
    
    def test_korean_format_output(self):
        """한국어 형식 출력 기능 테스트"""
        logger.info("한국어 형식 출력 기능 테스트 시작")
        
        # 한국어 형식 출력 파일 경로
        korean_format_file = os.path.join(EXPORT_DATA_DIR, "export_price_comparison_korean.txt")
        
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(korean_format_file), f"파일이 존재하지 않음: {korean_format_file}")
        
        # 파일 내용 확인
        with open(korean_format_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertGreater(len(content), 0, "파일 내용이 비어 있음")
            
            # 모든 대상 국가가 포함되어 있는지 확인
            for country_name in TARGET_COUNTRIES.values():
                self.assertIn(country_name, content, f"국가명 '{country_name}'이 존재하지 않음")
            
            # 형식이 올바른지 확인 (예: "대한민국 → 미국: 100")
            self.assertIn("대한민국 → 미국", content, "'대한민국 → 미국' 형식이 존재하지 않음")
        
        logger.info("한국어 형식 출력 기능 테스트 완료")

class DashboardAppTest(unittest.TestCase):
    """대시보드 애플리케이션 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.dashboard_app = importlib.import_module('src.dashboard_app')
    
    def test_template_files(self):
        """템플릿 파일 생성 기능 테스트"""
        logger.info("템플릿 파일 생성 기능 테스트 시작")
        
        # 템플릿 디렉토리 경로
        template_dir = os.path.join(ROOT_DIR, 'templates')
        
        # 필수 템플릿 파일 목록
        required_templates = [
            "base.html",
            "index.html",
            "tariff_policy.html",
            "manufacturing_cost.html",
            "export_price.html"
        ]
        
        # 파일 존재 여부 확인
        for template_name in required_templates:
            template_path = os.path.join(template_dir, template_name)
            self.assertTrue(os.path.exists(template_path), f"템플릿 파일이 존재하지 않음: {template_path}")
        
        logger.info("템플릿 파일 생성 기능 테스트 완료")
    
    def test_static_files(self):
        """정적 파일 생성 기능 테스트"""
        logger.info("정적 파일 생성 기능 테스트 시작")
        
        # 정적 파일 디렉토리 경로
        static_dir = os.path.join(ROOT_DIR, 'static')
        
        # 필수 정적 파일 목록
        required_static_files = [
            os.path.join('css', 'style.css'),
            os.path.join('js', 'script.js')
        ]
        
        # 파일 존재 여부 확인
        for static_file in required_static_files:
            static_path = os.path.join(static_dir, static_file)
            self.assertTrue(os.path.exists(static_path), f"정적 파일이 존재하지 않음: {static_path}")
        
        logger.info("정적 파일 생성 기능 테스트 완료")
    
    def test_flask_app(self):
        """Flask 애플리케이션 테스트"""
        logger.info("Flask 애플리케이션 테스트 시작")
        
        # 서버가 실행 중인지 확인
        try:
            response = requests.get('http://localhost:5000/')
            self.assertEqual(response.status_code, 200, "서버 응답 코드가 200이 아님")
            self.assertIn('text/html', response.headers['Content-Type'], "응답 콘텐츠 타입이 HTML이 아님")
            logger.info("Flask 서버가 정상적으로 실행 중입니다.")
        except requests.exceptions.ConnectionError:
            self.fail("Flask 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        
        logger.info("Flask 애플리케이션 테스트 완료")

class AutoUpdaterTest(unittest.TestCase):
    """자동 업데이트 메커니즘 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.auto_updater = importlib.import_module('src.auto_updater')
    
    def test_update_all_data(self):
        """데이터 업데이트 기능 테스트"""
        logger.info("데이터 업데이트 기능 테스트 시작")
        
        # 데이터 업데이트 함수 실행
        result = self.auto_updater.update_all_data()
        
        # 결과 검증
        self.assertTrue(result, "데이터 업데이트 실패")
        
        # 마지막 업데이트 시간 파일 확인
        last_update_file = os.path.join(DATA_DIR, 'last_update.txt')
        self.assertTrue(os.path.exists(last_update_file), f"파일이 존재하지 않음: {last_update_file}")
        
        # 업데이트 이력 파일 확인
        update_history_file = os.path.join(DATA_DIR, 'update_history.json')
        self.assertTrue(os.path.exists(update_history_file), f"파일이 존재하지 않음: {update_history_file}")
        
        # 업데이트 이력 데이터 확인
        with open(update_history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict, "데이터 형식이 올바르지 않음")
            self.assertIn('updates', data, "'updates' 키가 존재하지 않음")
            self.assertIsInstance(data['updates'], list, "'updates' 값이 리스트가 아님")
            self.assertGreater(len(data['updates']), 0, "업데이트 이력이 없음")
        
        logger.info("데이터 업데이트 기능 테스트 완료")

class IntegrationTest(unittest.TestCase):
    """통합 테스트"""
    
    def test_end_to_end_workflow(self):
        """엔드 투 엔드 워크플로우 테스트"""
        logger.info("엔드 투 엔드 워크플로우 테스트 시작")
        
        # 1. 관세 데이터 수집
        tariff_collector = importlib.import_module('src.tariff_data_collector')
        tariff_result = tariff_collector.collect_tariff_data()
        self.assertTrue(tariff_result, "관세 데이터 수집 실패")
        
        # 2. 제조 비용 시뮬레이션
        cost_simulator = importlib.import_module('src.manufacturing_cost_simulator')
        cost_result = cost_simulator.collect_all_cost_data()
        self.assertTrue(cost_result, "제조 비용 시뮬레이션 실패")
        
        # 3. 수출 가격 계산
        export_calculator = importlib.import_module('src.export_price_calculator')
        export_result = export_calculator.calculate_export_prices_for_products()
        self.assertIsInstance(export_result, dict, "수출 가격 계산 결과 형식이 올바르지 않음")
        
        # 4. 데이터 업데이트
        auto_updater = importlib.import_module('src.auto_updater')
        update_result = auto_updater.update_all_data()
        self.assertTrue(update_result, "데이터 업데이트 실패")
        
        # 5. 웹 서버 접속 테스트
        try:
            response = requests.get('http://localhost:5000/')
            self.assertEqual(response.status_code, 200, "서버 응답 코드가 200이 아님")
            
            # 각 페이지 접속 테스트
            pages = [
                '/',
                '/tariff-policy',
                '/manufacturing-cost',
                '/export-price'
            ]
            
            for page in pages:
                page_response = requests.get(f'http://localhost:5000{page}')
                self.assertEqual(page_response.status_code, 200, f"페이지 '{page}' 응답 코드가 200이 아님")
            
            logger.info("모든 페이지에 성공적으로 접속했습니다.")
        except requests.exceptions.ConnectionError:
            self.fail("Flask 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        
        logger.info("엔드 투 엔드 워크플로우 테스트 완료")

class PerformanceTest(unittest.TestCase):
    """성능 테스트"""
    
    def test_data_update_performance(self):
        """데이터 업데이트 성능 테스트"""
        logger.info("데이터 업데이트 성능 테스트 시작")
        
        # 데이터 업데이트 시간 측정
        auto_updater = importlib.import_module('src.auto_updater')
        
        start_time = time.time()
        auto_updater.update_all_data()
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"데이터 업데이트 실행 시간: {execution_time:.2f}초")
        
        # 실행 시간이 합리적인지 확인 (예: 60초 이내)
        self.assertLess(execution_time, 60, "데이터 업데이트 실행 시간이 너무 깁니다.")
        
        logger.info("데이터 업데이트 성능 테스트 완료")
    
    def test_web_server_response_time(self):
        """웹 서버 응답 시간 테스트"""
        logger.info("웹 서버 응답 시간 테스트 시작")
        
        # 각 페이지 응답 시간 측정
        pages = [
            '/',
            '/tariff-policy',
            '/manufacturing-cost',
            '/export-price'
        ]
        
        try:
            for page in pages:
                start_time = time.time()
                response = requests.get(f'http://localhost:5000{page}')
                end_time = time.time()
                
                response_time = end_time - start_time
                logger.info(f"페이지 '{page}' 응답 시간: {response_time:.2f}초")
                
                # 응답 시간이 합리적인지 확인 (예: 2초 이내)
                self.assertLess(response_time, 2, f"페이지 '{page}' 응답 시간이 너무 깁니다.")
        except requests.exceptions.ConnectionError:
            self.fail("Flask 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        
        logger.info("웹 서버 응답 시간 테스트 완료")

def run_tests():
    """모든 테스트를 실행합니다."""
    logger.info("테스트 및 검증 시작")
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 단위 테스트 추가
    test_suite.addTest(unittest.makeSuite(TariffDataCollectorTest))
    test_suite.addTest(unittest.makeSuite(ManufacturingCostSimulatorTest))
    test_suite.addTest(unittest.makeSuite(ExportPriceCalculatorTest))
    test_suite.addTest(unittest.makeSuite(DashboardAppTest))
    test_suite.addTest(unittest.makeSuite(AutoUpdaterTest))
    
    # 통합 테스트 추가
    test_suite.addTest(unittest.makeSuite(IntegrationTest))
    
    # 성능 테스트 추가
    test_suite.addTest(unittest.makeSuite(PerformanceTest))
    
    # 테스트 실행
    test_result_file = os.path.join(TEST_DIR, 'test_results.txt')
    with open(test_result_file, 'w', encoding='utf-8') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(test_suite)
    
    # 테스트 결과 요약
    logger.info(f"테스트 실행 완료: 총 {result.testsRun}개 테스트")
    logger.info(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    logger.info(f"실패: {len(result.failures)}개")
    logger.info(f"오류: {len(result.errors)}개")
    
    # 테스트 결과 파일 생성
    test_summary_file = os.path.join(TEST_DIR, 'test_summary.json')
    with open(test_summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': result.testsRun,
            'successes': result.testsRun - len(result.failures) - len(result.errors),
            'failures': len(result.failures),
            'errors': len(result.errors),
            'failure_details': [str(failure) for failure in result.failures],
            'error_details': [str(error) for error in result.errors]
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"테스트 결과 요약 저장 완료: {test_summary_file}")
    
    # 테스트 성공 여부 반환
    return len(result.failures) == 0 and len(result.errors) == 0

def run_user_scenario_tests():
    """사용자 시나리오 테스트를 실행합니다."""
    logger.info("사용자 시나리오 테스트 시작")
    
    # 시나리오 1: 특정 제품 카테고리에 대한 제조 비용 시뮬레이션
    logger.info("시나리오 1: 특정 제품 카테고리에 대한 제조 비용 시뮬레이션")
    try:
        response = requests.get('http://localhost:5000/manufacturing-cost?product_category=EPS+모터')
        assert response.status_code == 200, "서버 응답 코드가 200이 아님"
        assert 'EPS 모터' in response.text, "응답에 'EPS 모터'가 포함되어 있지 않음"
        logger.info("시나리오 1 테스트 성공")
    except Exception as e:
        logger.error(f"시나리오 1 테스트 실패: {str(e)}")
    
    # 시나리오 2: 특정 제품 카테고리에 대한 수출 가격 비교
    logger.info("시나리오 2: 특정 제품 카테고리에 대한 수출 가격 비교")
    try:
        response = requests.get('http://localhost:5000/export-price?product_category=EPS+모터')
        assert response.status_code == 200, "서버 응답 코드가 200이 아님"
        assert 'EPS 모터' in response.text, "응답에 'EPS 모터'가 포함되어 있지 않음"
        logger.info("시나리오 2 테스트 성공")
    except Exception as e:
        logger.error(f"시나리오 2 테스트 실패: {str(e)}")
    
    # 시나리오 3: 관세 정책 요약 페이지 확인
    logger.info("시나리오 3: 관세 정책 요약 페이지 확인")
    try:
        response = requests.get('http://localhost:5000/tariff-policy')
        assert response.status_code == 200, "서버 응답 코드가 200이 아님"
        assert '최신 미국 관세 정책 요약' in response.text, "응답에 '최신 미국 관세 정책 요약'이 포함되어 있지 않음"
        assert '대한민국' in response.text, "응답에 '대한민국'이 포함되어 있지 않음"
        logger.info("시나리오 3 테스트 성공")
    except Exception as e:
        logger.error(f"시나리오 3 테스트 실패: {str(e)}")
    
    logger.info("사용자 시나리오 테스트 완료")

if __name__ == "__main__":
    # 테스트 디렉토리 생성
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # 모든 테스트 실행
    test_success = run_tests()
    
    # 사용자 시나리오 테스트 실행
    run_user_scenario_tests()
    
    # 테스트 결과 출력
    if test_success:
        logger.info("모든 테스트가 성공적으로 완료되었습니다.")
    else:
        logger.warning("일부 테스트가 실패했습니다. 자세한 내용은 테스트 결과 파일을 확인하세요.")

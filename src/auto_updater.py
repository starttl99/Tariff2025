"""
자동 업데이트 메커니즘

이 모듈은 미국 관세 정책 추적 및 비용 비교 도구의 데이터를 자동으로 업데이트하는 메커니즘을 구현합니다.
일일 3회(03:00, 06:00, 21:00) 자동 업데이트 스케줄링을 설정하고, 데이터 새로고침 로직을 구현합니다.
"""

import os
import sys
import time
import json
import logging
import importlib
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'auto_updater.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('auto_updater')

# 프로젝트 루트 디렉토리 경로
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 디렉토리 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')

def update_all_data():
    """모든 데이터를 업데이트합니다."""
    try:
        logger.info("데이터 업데이트 시작...")
        
        # 관세 데이터 수집 모듈 임포트 및 실행
        logger.info("관세 데이터 수집 모듈 실행 중...")
        tariff_collector = importlib.import_module('src.tariff_data_collector')
        tariff_collector.collect_tariff_data()
        
        # 제조 비용 시뮬레이션 모듈 임포트 및 실행
        logger.info("제조 비용 시뮬레이션 모듈 실행 중...")
        cost_simulator = importlib.import_module('src.manufacturing_cost_simulator')
        cost_simulator.collect_all_cost_data()
        
        # 수출 가격 계산기 모듈 임포트 및 실행
        logger.info("수출 가격 계산기 모듈 실행 중...")
        export_calculator = importlib.import_module('src.export_price_calculator')
        export_calculator.calculate_export_prices_for_products()
        
        logger.info("데이터 업데이트 완료")
        
        # 업데이트 시간 기록
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(os.path.join(DATA_DIR, 'last_update.txt'), 'w', encoding='utf-8') as f:
            f.write(update_time)
        
        # 업데이트 이력 기록
        update_history_file = os.path.join(DATA_DIR, 'update_history.json')
        
        if os.path.exists(update_history_file):
            try:
                with open(update_history_file, 'r', encoding='utf-8') as f:
                    update_history = json.load(f)
            except:
                update_history = {'updates': []}
        else:
            update_history = {'updates': []}
        
        update_history['updates'].append({
            'timestamp': update_time,
            'status': 'success'
        })
        
        # 최대 100개의 업데이트 이력만 유지
        if len(update_history['updates']) > 100:
            update_history['updates'] = update_history['updates'][-100:]
        
        with open(update_history_file, 'w', encoding='utf-8') as f:
            json.dump(update_history, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"데이터 업데이트 오류: {str(e)}")
        
        # 업데이트 실패 이력 기록
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_history_file = os.path.join(DATA_DIR, 'update_history.json')
        
        if os.path.exists(update_history_file):
            try:
                with open(update_history_file, 'r', encoding='utf-8') as f:
                    update_history = json.load(f)
            except:
                update_history = {'updates': []}
        else:
            update_history = {'updates': []}
        
        update_history['updates'].append({
            'timestamp': update_time,
            'status': 'error',
            'error_message': str(e)
        })
        
        # 최대 100개의 업데이트 이력만 유지
        if len(update_history['updates']) > 100:
            update_history['updates'] = update_history['updates'][-100:]
        
        with open(update_history_file, 'w', encoding='utf-8') as f:
            json.dump(update_history, f, ensure_ascii=False, indent=2)
        
        return False

def setup_scheduler():
    """데이터 자동 업데이트를 위한 스케줄러를 설정합니다."""
    scheduler = BackgroundScheduler()
    
    # 매일 03:00, 06:00, 21:00에 데이터 업데이트
    scheduler.add_job(update_all_data, CronTrigger(hour=3, minute=0))
    scheduler.add_job(update_all_data, CronTrigger(hour=6, minute=0))
    scheduler.add_job(update_all_data, CronTrigger(hour=21, minute=0))
    
    # 스케줄러 시작
    scheduler.start()
    logger.info("스케줄러 시작됨 - 매일 03:00, 06:00, 21:00에 데이터 업데이트")
    
    return scheduler

def monitor_updates():
    """업데이트 상태를 모니터링합니다."""
    update_history_file = os.path.join(DATA_DIR, 'update_history.json')
    
    if os.path.exists(update_history_file):
        try:
            with open(update_history_file, 'r', encoding='utf-8') as f:
                update_history = json.load(f)
            
            updates = update_history.get('updates', [])
            
            if updates:
                logger.info(f"총 {len(updates)}개의 업데이트 이력이 있습니다.")
                
                # 최근 5개 업데이트 이력 출력
                logger.info("최근 5개 업데이트 이력:")
                for update in updates[-5:]:
                    status = update.get('status', '')
                    timestamp = update.get('timestamp', '')
                    
                    if status == 'success':
                        logger.info(f"[성공] {timestamp}")
                    else:
                        error_message = update.get('error_message', '알 수 없는 오류')
                        logger.info(f"[실패] {timestamp} - {error_message}")
            else:
                logger.info("업데이트 이력이 없습니다.")
        except Exception as e:
            logger.error(f"업데이트 이력 모니터링 오류: {str(e)}")
    else:
        logger.info("업데이트 이력 파일이 존재하지 않습니다.")

def run_updater():
    """자동 업데이트 메커니즘을 실행합니다."""
    logger.info("자동 업데이트 메커니즘 시작")
    
    # 초기 데이터 업데이트
    logger.info("초기 데이터 업데이트 실행")
    update_all_data()
    
    # 스케줄러 설정
    scheduler = setup_scheduler()
    
    try:
        # 업데이트 상태 모니터링
        while True:
            monitor_updates()
            time.sleep(3600)  # 1시간마다 모니터링
    except KeyboardInterrupt:
        logger.info("자동 업데이트 메커니즘 종료")
        scheduler.shutdown()

if __name__ == "__main__":
    run_updater()

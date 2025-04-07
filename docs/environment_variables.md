# 환경 변수 설정 가이드

이 문서는 미국 관세 정책 추적 및 비용 비교 도구의 환경 변수 설정 방법을 설명합니다.

## 로컬 개발 환경에서의 환경 변수 설정

1. 프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.
2. 다음과 같은 형식으로 필요한 환경 변수를 설정합니다:

```
# 애플리케이션 설정
FLASK_APP=src.dashboard_app
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your_secret_key_here

# 데이터 업데이트 스케줄 설정
UPDATE_SCHEDULE_MORNING=03:00
UPDATE_SCHEDULE_NOON=06:00
UPDATE_SCHEDULE_EVENING=21:00

# API 키 설정 (필요한 경우)
USITC_API_KEY=your_usitc_api_key_here
```

## Heroku에서의 환경 변수 설정

Heroku에 배포할 경우, 다음과 같은 방법으로 환경 변수를 설정할 수 있습니다:

1. Heroku CLI를 사용하는 경우:
   ```
   heroku config:set SECRET_KEY=your_secret_key_here
   heroku config:set FLASK_ENV=production
   ```

2. Heroku 대시보드를 사용하는 경우:
   - Heroku 대시보드에서 애플리케이션 선택
   - "Settings" 탭 클릭
   - "Config Vars" 섹션에서 "Reveal Config Vars" 클릭
   - 키-값 쌍으로 환경 변수 추가

## GitHub Actions에서의 환경 변수 설정

GitHub Actions를 사용하여 배포할 경우, 다음과 같은 방법으로 비밀 환경 변수를 설정할 수 있습니다:

1. GitHub 저장소 페이지에서 "Settings" 탭 클릭
2. 왼쪽 메뉴에서 "Secrets and variables" > "Actions" 선택
3. "New repository secret" 버튼 클릭
4. 다음 비밀 변수들을 추가:
   - `HEROKU_API_KEY`: Heroku API 키
   - `HEROKU_APP_NAME`: Heroku 애플리케이션 이름
   - `HEROKU_EMAIL`: Heroku 계정 이메일

## 주의사항

- `.env` 파일은 절대 Git 저장소에 커밋하지 마세요. 이 파일은 `.gitignore`에 이미 포함되어 있습니다.
- 실제 배포 환경에서는 강력한 무작위 문자열을 `SECRET_KEY`로 사용하세요.
- API 키와 같은 민감한 정보는 항상 환경 변수를 통해 관리하고, 코드에 직접 포함시키지 마세요.

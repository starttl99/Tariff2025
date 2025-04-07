# GitHub 배포 가이드

이 문서는 미국 관세 정책 추적 및 비용 비교 도구를 GitHub와 Heroku를 통해 배포하는 방법을 설명합니다.

## 사전 준비 사항

1. [GitHub](https://github.com/) 계정
2. [Heroku](https://www.heroku.com/) 계정
3. [Git](https://git-scm.com/) 설치

## GitHub 저장소 생성 및 코드 푸시

1. GitHub에 로그인하고 새 저장소(repository)를 생성합니다:
   - 저장소 이름: `tariff-tool` (또는 원하는 이름)
   - 설명: `미국 관세 정책 추적 및 비용 비교 도구`
   - 공개/비공개 설정 선택
   - README 파일 생성 옵션 체크

2. 로컬 환경에서 Git 저장소 초기화 및 GitHub 연결:
   ```bash
   cd /path/to/tariff_tool
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/tariff-tool.git
   git push -u origin main
   ```

## Heroku 배포 설정

1. Heroku CLI 설치 (아직 설치하지 않은 경우):
   - [Heroku CLI 설치 가이드](https://devcenter.heroku.com/articles/heroku-cli) 참조

2. Heroku에 로그인:
   ```bash
   heroku login
   ```

3. Heroku 앱 생성:
   ```bash
   heroku create your-app-name
   ```

4. Heroku에 환경 변수 설정:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key_here
   heroku config:set FLASK_ENV=production
   ```

5. Heroku에 직접 배포 (GitHub Actions를 사용하지 않는 경우):
   ```bash
   git push heroku main
   ```

## GitHub Actions를 통한 자동 배포

1. GitHub 저장소에 비밀 변수 설정:
   - GitHub 저장소 페이지에서 "Settings" 탭 클릭
   - 왼쪽 메뉴에서 "Secrets and variables" > "Actions" 선택
   - "New repository secret" 버튼 클릭
   - 다음 비밀 변수들을 추가:
     - `HEROKU_API_KEY`: Heroku API 키
     - `HEROKU_APP_NAME`: Heroku 애플리케이션 이름
     - `HEROKU_EMAIL`: Heroku 계정 이메일

2. GitHub Actions 워크플로우 파일이 이미 `.github/workflows/deploy.yml`에 생성되어 있습니다. 이 파일은 main 브랜치에 코드가 푸시될 때마다 자동으로 Heroku에 배포하도록 설정되어 있습니다.

3. 코드를 변경하고 GitHub에 푸시하면 자동으로 배포가 진행됩니다:
   ```bash
   git add .
   git commit -m "Update feature XYZ"
   git push origin main
   ```

4. GitHub 저장소의 "Actions" 탭에서 배포 진행 상황을 확인할 수 있습니다.

## 배포 후 확인

1. 배포가 완료되면 다음 URL에서 애플리케이션에 접근할 수 있습니다:
   ```
   https://your-app-name.herokuapp.com/
   ```

2. 애플리케이션 로그 확인:
   ```bash
   heroku logs --tail
   ```

## 문제 해결

1. 배포 실패 시 GitHub Actions 로그 확인
2. Heroku 로그 확인: `heroku logs --tail`
3. 로컬에서 애플리케이션 실행하여 문제 확인: `python -m src.dashboard_app`

## 참고 사항

- 이 프로젝트는 `requirements.txt`, `Procfile`, `.gitignore` 파일이 이미 설정되어 있어 Heroku 배포를 위한 준비가 완료되어 있습니다.
- 환경 변수 설정에 대한 자세한 내용은 `docs/environment_variables.md` 파일을 참조하세요.
- 데이터 업데이트 스케줄링은 Heroku의 경우 Heroku Scheduler 애드온을 사용하여 설정할 수 있습니다.

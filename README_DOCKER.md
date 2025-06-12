# MCRP-demo - Docker 사용 가이드

## 🐳 빠른 시작

```bash
# 프로젝트 클론
git clone <repository-url>
cd mcrp-demo

# 환경변수 설정 (선택사항)
cp env.example .env
# .env 파일을 편집하여 필요한 설정 변경

# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 🔧 환경변수 설정

| 환경변수            | 기본값                       | 설명                      |
| ------------------- | ---------------------------- | ------------------------- |
| `FLASK_DEBUG`       | `false`                      | 개발 모드 활성화          |
| `HOST_PORT`         | `5001`                       | 호스트에서 접근할 포트    |
| `DATA_DIR`          | `/app/data`                  | 채팅 데이터 저장 경로     |
| `EXTERNAL_API_BASE` | `http://your-ai-server:8000` | 외부 AI API 서버 주소     |
| `AI_API_TIMEOUT`    | `10`                         | AI API 요청 타임아웃 (초) |

## 🛠️ 개발 모드

개발할 때는 디버그 모드를 활성화하고 코드 변경을 실시간으로 반영할 수 있습니다:

```bash
# 개발 모드로 실행
export FLASK_DEBUG=true
docker-compose up

# 또는 .env 파일에 설정
echo "FLASK_DEBUG=true" >> .env
docker-compose up
```

코드 변경을 실시간으로 반영하려면 `docker-compose.yml`에서 볼륨 마운트를 활성화하세요:

```yaml
volumes:
  - chat_data:/app/data
  - .:/app # 이 줄의 주석을 해제
```

## 📁 데이터 영속성

채팅 데이터는 `chat_data` 볼륨에 저장되어 컨테이너 재시작 후에도 유지됩니다:

```bash
# 볼륨 확인
docker volume ls

# 데이터 백업
docker run --rm -v mcrp-demo_chat_data:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz -C /data .

# 데이터 복원
docker run --rm -v mcrp-demo_chat_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /data
```

## 🔧 문제 해결

### 포트 변경

```bash
export HOST_PORT=8080
docker-compose up
```

### AI API 서버 변경

```bash
export EXTERNAL_API_BASE=http://your-server:port
docker-compose up
```

### 데이터 리셋

```bash
# 주의: 모든 채팅 데이터가 삭제됩니다
docker-compose down -v
```

## 📊 모니터링

```bash
# 상태 확인
docker-compose ps

# 로그 보기
docker-compose logs -f

# 리소스 사용량
docker stats mcrp-demo-mcrp-demo-1
```

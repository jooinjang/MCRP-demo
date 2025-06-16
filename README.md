# 🤖 MCRP-demo

해당 시스템은 Neeko (https://github.com/weiyifan1023/Neeko) 프레임워크로 훈련된 모델을 서빙하는 API 서버와 통신하는 웹 서버 애플리케이션입니다.
Neeko 프레임워크를 통해 구현된 LLM 기반 Multi-Character Role Playing 시스템을 Chat Interface에서 사용해 볼 수 있도록 Flask 기반 웹 서버 + HTML을 통해 구현하였습니다.

## 🏗️ 시스템 아키텍처

**중요**: 이 애플리케이션은 독립적으로 작동하지 않습니다. Neeko 프레임워크가 아니더라도, 사용자의 입력에 대해 적절한 출력을 반환하는 API 엔드포인트를 제공하는 **별도의 서버가 필수적으로 필요**합니다.

```
┌─────────────────┐    HTTP API     ┌─────────────────┐
│                 │   ◄────────►    │                 │
│   MCRP-demo     │                 │   AI 서버        │
│  (웹 인터페이스)   │                 │ (ChatBot Engine)│
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘
        │                                   │
        │                                   │
   ┌─────────┐                         ┌─────────┐
   │ 사용자    │                         │ LLM/AI  │
   │ 브라우저  │                         │ Model   │
   └─────────┘                         └─────────┘
```

### 역할 분담

- **MCRP-demo (이 프로젝트)**:

  - 웹 기반 사용자 인터페이스 제공
  - 채팅 히스토리 관리
  - 캐릭터 선택 인터페이스
  - AI 서버와의 통신 중계

- **AI 서버 (별도 필요)**:
  - 실제 AI/LLM 모델 호스팅
  - Neeko 프레임워크 기반 캐릭터별 페르소나 구현
  - 자연어 처리 및 응답 생성

## ⚠️ 사전 요구사항

이 애플리케이션을 사용하기 전에 **반드시 AI 서버가 준비되어야 합니다**.

### AI 서버 요구사항

1. **OpenAPI 명세 준수**: AI 서버는 지정된 API 엔드포인트를 제공해야 합니다
2. **멀티 캐릭터 지원**: 9개 캐릭터 페르소나 구현
3. **HTTP API 제공**: RESTful API를 통한 통신 지원

### AI 서버가 없는 경우

AI 서버가 준비되지 않은 상태에서는:

- ❌ 실제 AI 응답을 받을 수 없습니다
- ✅ 웹 인터페이스는 정상 작동하며 시뮬레이션 응답을 제공합니다
- ✅ 개발 및 테스트 목적으로 사용 가능합니다

## ✨ 주요 기능

- 🎭 **멀티 캐릭터 시스템**: 9개의 서로 다른 AI 캐릭터 선택 가능
- 💬 **실시간 채팅**: 자연스러운 대화형 인터페이스
- 📱 **반응형 디자인**: 모바일과 데스크톱 모두 지원
- 💾 **채팅 히스토리**: 대화 내용 자동 저장 및 관리
- 🐳 **Docker 지원**: 간편한 배포 및 실행
- 🔧 **환경변수 설정**: 유연한 서버 구성

## 🎭 지원 캐릭터

LLM 기반 Chat을 제공하는 API 서버가 Neeko 프레임워크를 기반으로 구현되어 있으므로, Neeko 프레임워크에서 사용된 Character-LLM(https://github.com/choosewhatulike/trainable-agents) 데이터셋에 포함된 9개 캐릭터와의 채팅을 지원합니다.

- 🎼 **Beethoven** - 음악의 거장
- 👑 **Caesar** - 로마의 황제
- 🐍 **Cleopatra** - 이집트의 여왕
- 📚 **Hermione** - 마법사
- ✊ **Martin** - 시민권 운동가
- 🍎 **Newton** - 물리학자
- 🤔 **Socrates** - 철학자
- ⚔️ **Spartacus** - 검투사
- 🐍 **Voldemort** - 어둠의 마법사

## 🚀 빠른 시작

### 1단계: AI 서버 준비

**필수**: 먼저 AI 서버를 준비하고 실행해야 합니다.

AI 서버는 다음 요구사항을 만족해야 합니다:

- 포트에서 HTTP API 서비스 제공
- 아래 명시된 OpenAPI 엔드포인트 구현
- 9개 캐릭터 페르소나 지원

### 2단계: MCRP-demo 실행

#### Docker 사용 (권장)

```bash
# 저장소 클론
git clone <your-repository-url>
cd mcrp-demo

# 환경변수 설정
cp env.example .env

# .env 파일에서 AI 서버 정보 설정
# EXTERNAL_API_BASE=http://your-ai-server:port
nano .env

# Docker Compose로 실행
docker-compose up -d

# 웹 브라우저에서 http://localhost:5001 접속
```

#### 로컬 개발 환경

```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
export EXTERNAL_API_BASE=http://your-ai-server:port
export FLASK_DEBUG=true

# 서버 실행
python app.py
```

## ⚙️ 환경변수 설정

프로젝트에서 사용하는 주요 환경변수들:

| 변수명              | 기본값                  | 설명                      |
| ------------------- | ----------------------- | ------------------------- |
| `EXTERNAL_API_BASE` | `http://localhost:8000` | **AI 서버 주소 (필수)**   |
| `AI_API_TIMEOUT`    | `10`                    | AI API 요청 타임아웃 (초) |
| `FLASK_HOST`        | `0.0.0.0`               | Flask 서버 호스트         |
| `FLASK_PORT`        | `5001`                  | Flask 서버 포트           |
| `FLASK_DEBUG`       | `false`                 | 디버그 모드               |
| `DATA_DIR`          | `./chat_data`           | 채팅 데이터 저장 경로     |

## 🏗️ 프로젝트 구조

```
mcrp-demo/
├── app.py                 # 메인 Flask 애플리케이션
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 이미지 설정
├── docker-compose.yml    # Docker Compose 설정
├── index.html           # 프론트엔드 (SPA)
├── main.css            # 스타일시트
├── images/             # 캐릭터 이미지
│   └── characters/
├── chat_data/          # 채팅 데이터 저장소
└── README.md           # 프로젝트 문서
```

## 🔌 AI 서버 연동 (OpenAPI 명세)

이 애플리케이션은 **외부 AI 서버와 연동하여 작동**합니다. AI 서버는 **반드시** 다음 OpenAPI 명세를 준수해야 합니다:

### 필수 API 엔드포인트

#### 1. 캐릭터 목록 조회

```http
GET /characters
Content-Type: application/json
```

**응답 예시:**

```json
{
  "characters": [
    {
      "number": 1,
      "name": "Beethoven",
      "description": "음악의 거장 베토벤"
    },
    {
      "number": 2,
      "name": "Caesar",
      "description": "로마의 황제 시저"
    }
    // ... 총 9개 캐릭터
  ]
}
```

#### 2. 캐릭터 선택

```http
POST /select_character
Content-Type: application/json

{
  "character_number": 1
}
```

**응답 예시:**

```json
{
  "selected_character": "Beethoven",
  "message": "베토벤이 선택되었습니다."
}
```

#### 3. 채팅 응답 생성

```http
POST /generate
Content-Type: application/json

{
  "input_text": [
    {
      "role": "Man",
      "action": "(speaking)",
      "content": "안녕하세요!"
    }
  ],
  "max_new_tokens": 1024,
  "temperature": 1.0
}
```

**응답 예시:**

```json
{
  "generated_text": "Hello, My name is Beethoven.",
  "character": "Beethoven",
  "action": "(speaking)"
}
```

### API 호출 예시

```python
# 캐릭터 목록 조회
response = requests.get(f"{AI_SERVER_BASE}/characters")

# 캐릭터 선택
response = requests.post(f"{AI_SERVER_BASE}/select_character",
                        json={"character_number": 1})

# 채팅 응답 생성
response = requests.post(f"{AI_SERVER_BASE}/generate",
                        json={
                          "input_text": conversation_history,
                          "max_new_tokens": 1024,
                          "temperature": 1.0
                        })
```

## 🐳 Docker 사용법

자세한 Docker 사용법은 [README_DOCKER.md](README_DOCKER.md)를 참조하세요.

```bash
# 기본 실행
docker-compose up -d

# 개발 모드로 실행
FLASK_DEBUG=true docker-compose up

# 로그 확인
docker-compose logs -f

# 정리
docker-compose down
```

## 📝 개발 가이드

### 코드 구조

- **Flask 백엔드**: RESTful API 제공, AI 서버와의 중계 역할
- **바닐라 JavaScript 프론트엔드**: SPA (Single Page Application)
- **JSON 기반 데이터 저장**: 파일 시스템 사용 (채팅 히스토리)
- **Gunicorn**: 운영 환경용 WSGI 서버

### 주요 API 엔드포인트

- `GET /api/chats` - 채팅 목록 조회
- `POST /api/chats` - 새 채팅 생성
- `GET /api/chats/{id}` - 특정 채팅 조회
- `DELETE /api/chats/{id}` - 채팅 삭제
- `POST /api/chat` - 메시지 전송 (AI 서버로 중계)
- `GET /api/characters` - 캐릭터 목록 조회 (AI 서버에서 가져옴)

### 개발 시 주의사항

1. **AI 서버 의존성**: 모든 AI 관련 기능은 외부 AI 서버에 의존합니다
2. **에러 처리**: AI 서버 연결 실패 시 시뮬레이션 응답으로 대체됩니다
3. **시간 초과**: AI_API_TIMEOUT 설정으로 응답 시간을 제한합니다

## 🛠️ 문제 해결

### 일반적인 문제들

1. **AI 서버 연결 실패**

   - `EXTERNAL_API_BASE` 환경변수 확인
   - AI 서버 상태 및 네트워크 연결 확인
   - AI 서버의 OpenAPI 엔드포인트 구현 상태 확인

2. **캐릭터 선택 안됨**

   - AI 서버의 `/characters` 엔드포인트 확인
   - AI 서버의 `/select_character` 엔드포인트 확인

3. **AI 응답 없음**

   - AI 서버의 `/generate` 엔드포인트 확인
   - 요청 형식이 OpenAPI 명세와 일치하는지 확인

4. **포트 충돌**

   - `HOST_PORT` 환경변수로 다른 포트 사용

5. **권한 문제**
   - `DATA_DIR` 디렉토리 권한 확인

### 디버깅 팁

```bash
# AI 서버 연결 테스트
curl http://your-ai-server:port/characters

# 로그 확인
docker-compose logs -f mcrp-demo

# 개발 모드로 상세 로그 확인
FLASK_DEBUG=true docker-compose up
```

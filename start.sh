#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

printf "${GREEN}🚀 Neeko Chat 시작 중...${NC}\n"

# 기존 프로세스 정리 함수
cleanup() {
    printf "\n${YELLOW}📝 서버 종료 중...${NC}\n"
    if [ ! -z "$TAILWIND_PID" ]; then
        kill $TAILWIND_PID 2>/dev/null
        printf "${BLUE}✅ Tailwind CSS 프로세스 종료됨${NC}\n"
    fi
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
        printf "${BLUE}✅ Flask 서버 종료됨${NC}\n"
    fi
    printf "${GREEN}👋 모든 서버가 정상적으로 종료되었습니다.${NC}\n"
    exit 0
}

# Ctrl+C 시그널 처리
trap cleanup SIGINT SIGTERM

# Conda 환경 초기화 및 활성화
eval "$(conda shell.bash hook)"
conda activate alltheway

# 1. Tailwind CSS 빌드 & 워치 시작
printf "${BLUE}🎨 Tailwind CSS 빌드 시작...${NC}\n"
npx tailwindcss -i main.css -o dist/main.css --watch &
TAILWIND_PID=$!

# 2. Flask 서버 시작
printf "${BLUE}🌐 Flask 서버 시작...${NC}\n"
python app.py &
FLASK_PID=$!

# 잠시 대기 후 상태 확인
sleep 3

printf "${GREEN}✨ 준비 완료!${NC}\n"
printf "${BLUE}📱 웹사이트: ${YELLOW}http://localhost:5000${NC}\n"
printf "${BLUE}🎨 Tailwind CSS: ${YELLOW}실시간 빌드 중${NC}\n"
printf "${BLUE}🐍 Python 환경: ${YELLOW}alltheway (conda)${NC}\n"
printf "${RED}⚠️  종료하려면 Ctrl+C를 누르세요${NC}\n"

# 백그라운드 프로세스들이 종료될 때까지 대기
wait 
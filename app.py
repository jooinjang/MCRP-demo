from flask import Flask, request, jsonify, send_from_directory
import json
import os
import uuid
from datetime import datetime
import random
import requests
import subprocess

# ============================================================================
# 애플리케이션 설정 및 상수
# ============================================================================

app = Flask(__name__)

# 환경변수에서 설정 로드 (기본값 포함)
DATA_DIR = os.getenv("DATA_DIR", "chat_data")
CHATS_FILE = os.path.join(DATA_DIR, "chats.json")

# 외부 AI API 설정 - 환경변수에서 로드
EXTERNAL_API_BASE = os.getenv("EXTERNAL_API_BASE", "http://163.152.163.63:60027")
AI_API_TIMEOUT = int(os.getenv("AI_API_TIMEOUT", "10"))

# Flask 서버 설정
HOST = os.getenv("FLASK_HOST", "0.0.0.0")  # Docker 컨테이너에서는 0.0.0.0이 필요
PORT = int(os.getenv("FLASK_PORT", "5001"))
DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# 캐릭터별 프로필 이미지 매핑
CHARACTER_PROFILES = {
    1: {"name": "Beethoven", "image": "/images/characters/beethoven.png"},
    2: {"name": "Caesar", "image": "/images/characters/caesar.png"},
    3: {"name": "Cleopatra", "image": "/images/characters/cleopatra.png"},
    4: {"name": "Hermione", "image": "/images/characters/hermione.png"},
    5: {"name": "Martin", "image": "/images/characters/martin.png"},
    6: {"name": "Newton", "image": "/images/characters/newton.png"},
    7: {"name": "Socrates", "image": "/images/characters/socrates.png"},
    8: {"name": "Spartacus", "image": "/images/characters/spartacus.png"},
    9: {"name": "Voldemort", "image": "/images/characters/voldemort.png"},
}

# 시뮬레이션 응답 템플릿
SIMULATION_RESPONSES = [
    '"{}"에 대한 답변입니다. 실제 API를 연결하시면 더 정확한 답변을 받을 수 있습니다.',
    '흥미로운 질문이네요! "{}"에 대해 더 자세히 설명드리겠습니다.',
    '좋은 질문입니다. "{}"와 관련해서 다음과 같이 말씀드릴 수 있습니다.',
    '"{}"에 대한 제 의견은 다음과 같습니다. 더 구체적인 질문이 있으시면 언제든지 물어보세요.',
]

# 데이터 디렉토리 생성
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ============================================================================
# 파일 처리 유틸리티 함수
# ============================================================================


def _handle_file_error(file_path, operation="load"):
    """파일 오류 처리를 위한 공통 함수"""
    if os.path.exists(file_path):
        backup_file = file_path + ".backup"
        os.rename(file_path, backup_file)
        print(f"Corrupted file moved to {backup_file}")


def _safe_file_write(file_path, data):
    """안전한 파일 쓰기 (임시 파일 사용)"""
    try:
        temp_file = file_path + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, file_path)
        return True
    except (IOError, OSError) as e:
        print(f"Error: Failed to save {file_path}: {e}")
        return False


def load_chats():
    """채팅 목록 로드"""
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load chats.json: {e}")
        _handle_file_error(CHATS_FILE)
    return {}


def save_chats(chats):
    """채팅 목록 저장"""
    _safe_file_write(CHATS_FILE, chats)


def load_chat_messages(chat_id):
    """특정 채팅의 메시지 로드"""
    chat_file = os.path.join(DATA_DIR, f"chat_{chat_id}.json")
    try:
        if os.path.exists(chat_file):
            with open(chat_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load {chat_file}: {e}")
        _handle_file_error(chat_file)
    return []


def save_chat_messages(chat_id, messages):
    """특정 채팅의 메시지 저장"""
    chat_file = os.path.join(DATA_DIR, f"chat_{chat_id}.json")
    _safe_file_write(chat_file, messages)


# ============================================================================
# AI 통신 관련 함수
# ============================================================================


def _build_conversation_history(messages, character_name, max_messages=8):
    """대화 내역을 API 형식으로 변환"""
    input_text = []

    for msg in messages[-max_messages:]:
        role = "Man" if msg["is_user"] else character_name
        input_text.append(
            {"role": role, "action": "(speaking)", "content": msg["content"]}
        )

    return input_text


def _make_api_request(endpoint, payload, timeout=AI_API_TIMEOUT):
    """API 요청을 위한 공통 함수"""
    try:
        response = requests.post(
            f"{EXTERNAL_API_BASE}/{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        return response
    except requests.exceptions.Timeout:
        print(f"{endpoint} API 요청 시간 초과")
        return None
    except requests.exceptions.ConnectionError:
        print(f"{endpoint} API 연결 실패")
        return None
    except Exception as e:
        print(f"{endpoint} API 예외 발생: {str(e)}")
        return None


def get_ai_response(message, chat_id):
    """실제 AI 서버에서 응답을 받아오는 함수"""
    # 채팅 정보 및 메시지 로드
    messages = load_chat_messages(chat_id)
    chats = load_chats()
    chat_info = chats.get(chat_id, {})

    character_id = chat_info.get("character_id", "default")
    character_name = chat_info.get("character_name", "AI Assistant")

    # 대화 내역 구성
    input_text = _build_conversation_history(messages, character_name)
    input_text.append({"role": "Man", "action": "(speaking)", "content": message})

    # API 요청 데이터 구성
    payload = {"input_text": input_text, "max_new_tokens": 1024, "temperature": 1.0}

    print(f"AI API 요청 시작: {EXTERNAL_API_BASE}/generate")
    print(f"선택된 캐릭터 ID: {character_id}, 이름: {character_name}")
    print(f"요청 데이터: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    response = _make_api_request("generate", payload)

    if response is None:
        return "응답 시간이 초과되었습니다. 다시 시도해주세요."

    print(f"AI API 응답 상태: {response.status_code}")

    if response.status_code == 200:
        try:
            result = response.json()
            ai_response = result.get("generated_text", "응답을 생성할 수 없습니다.")
            character = result.get("character", "AI")
            action = result.get("action", "(speaking)")

            print(f"AI API 응답 성공:")
            print(f"  - 캐릭터: {character}")
            print(f"  - 행동: {action}")
            print(f"  - 생성된 텍스트: {ai_response[:100]}...")

            return ai_response
        except json.JSONDecodeError as e:
            print(f"AI API 응답 JSON 파싱 오류: {e}")
            return "AI 응답 파싱에 실패했습니다."
    else:
        print(f"AI API 오류: {response.status_code}")
        print(f"오류 응답 내용: {response.text}")

        # 상세 오류 정보 출력
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(
                    f"검증 오류 상세: {json.dumps(error_detail, ensure_ascii=False, indent=2)}"
                )
            except:
                pass

        # 특정 오류 상태에 대한 메시지
        if response.status_code == 500:
            return "AI 서버 내부 오류입니다. 캐릭터 선택이 필요할 수 있습니다."

        return f"AI 서버 오류 (상태코드: {response.status_code})"


def simulate_ai_response(message):
    """시뮬레이션 응답 (백업용)"""
    return random.choice(SIMULATION_RESPONSES).format(message)


def select_character_on_server(character_id):
    """서버에서 캐릭터 선택 (백그라운드 시도)"""
    if not character_id:
        return

    try:
        payload = {"character_number": character_id}
        print(f"캐릭터 선택 API 호출: {EXTERNAL_API_BASE}/select_character")
        print(f"페이로드: {payload}")

        response = _make_api_request("select_character", payload)
        if response and response.status_code == 200:
            print("캐릭터 선택 성공")
        else:
            print("캐릭터 선택 실패 - 웹페이지에서 선택한 캐릭터 이름 사용")

    except Exception as e:
        print(f"캐릭터 선택 API 예외: {str(e)} - 웹페이지에서 선택한 캐릭터 이름 사용")


# ============================================================================
# 헬퍼 함수
# ============================================================================


def _get_mime_type_for_image(file_path):
    """이미지 파일의 MIME 타입 확인"""
    try:
        result = subprocess.run(
            ["file", "-b", "--mime-type", file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "image/jpeg"  # 기본값


def _set_no_cache_headers(response):
    """캐시 방지 헤더 설정"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _format_chat_info(chat_id, chat_info, messages):
    """채팅 정보 포맷팅"""
    last_message = ""
    if messages:
        for msg in reversed(messages):
            if msg["is_user"]:
                content = msg["content"]
                last_message = content[:50] + ("..." if len(content) > 50 else "")
                break

    return {
        "id": chat_id,
        "title": chat_info.get("title", "새로운 채팅"),
        "last_message": last_message,
        "created_at": chat_info.get("created_at"),
        "updated_at": chat_info.get("updated_at"),
        "character_name": chat_info.get("character_name", "AI Assistant"),
        "character_id": chat_info.get("character_id"),
        "character_image": chat_info.get(
            "character_image", "/images/characters/default.png"
        ),
    }


# ============================================================================
# 정적 파일 서비스 라우트
# ============================================================================


@app.route("/")
def index():
    response = send_from_directory(".", "index.html")
    return _set_no_cache_headers(response)


@app.route("/dist/<path:filename>")
def dist_files(filename):
    response = send_from_directory("dist", filename)
    return _set_no_cache_headers(response)


@app.route("/images/<path:filename>")
def image_files(filename):
    """이미지 파일 서빙"""
    response = send_from_directory("images", filename)

    # MIME 타입 설정
    if filename.lower().endswith((".png", ".jpeg")):
        file_path = os.path.join("images", filename)
        if os.path.exists(file_path):
            mime_type = _get_mime_type_for_image(file_path)
            response.headers["Content-Type"] = mime_type
    elif filename.lower().endswith(".png"):
        response.headers["Content-Type"] = "image/png"

    response.headers["Cache-Control"] = "public, max-age=3600"  # 이미지는 1시간 캐시
    return response


# ============================================================================
# 채팅 관련 API 라우트
# ============================================================================


@app.route("/api/chats", methods=["GET"])
def get_chats():
    """채팅 목록 조회"""
    chats = load_chats()
    chat_list = []

    for chat_id, chat_info in chats.items():
        messages = load_chat_messages(chat_id)
        formatted_chat = _format_chat_info(chat_id, chat_info, messages)
        chat_list.append(formatted_chat)

    # 최근 업데이트 순으로 정렬
    chat_list.sort(key=lambda x: x["updated_at"], reverse=True)
    return jsonify({"chats": chat_list})


@app.route("/api/chats", methods=["POST"])
def create_chat():
    """새 채팅 생성"""
    data = request.json or {}
    character_id = data.get("character_id")
    character_name = data.get("character_name", "AI Assistant")

    print("수신된 character_id:", character_id)
    print("수신된 character_name:", character_name)

    # 캐릭터 선택 API 호출 (백그라운드에서 시도)
    select_character_on_server(character_id)

    # 새 채팅 생성
    chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    chats = load_chats()
    chats[chat_id] = {
        "title": "새로운 채팅",
        "created_at": now,
        "updated_at": now,
        "character_id": character_id,
        "character_name": character_name,
        "character_image": CHARACTER_PROFILES.get(character_id, {}).get(
            "image", "/images/characters/default.png"
        ),
        "character_selected": True,
    }
    save_chats(chats)
    save_chat_messages(chat_id, [])

    print(f"새 채팅 생성 완료 - ID: {chat_id}, 캐릭터: {character_name}")

    return jsonify(
        {
            "chat_id": chat_id,
            "character_id": character_id,
            "character_name": character_name,
            "character_image": CHARACTER_PROFILES.get(character_id, {}).get(
                "image", "/images/characters/default.png"
            ),
        }
    )


@app.route("/api/chats/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    """특정 채팅 조회"""
    chats = load_chats()
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404

    messages = load_chat_messages(chat_id)
    chat_info = chats[chat_id]

    return jsonify(
        {
            "id": chat_id,
            "title": chat_info.get("title", "새로운 채팅"),
            "messages": messages,
            "created_at": chat_info.get("created_at"),
            "updated_at": chat_info.get("updated_at"),
            "character_name": chat_info.get("character_name", "AI Assistant"),
            "character_id": chat_info.get("character_id"),
            "character_image": chat_info.get(
                "character_image", "/images/characters/default.png"
            ),
        }
    )


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    """채팅 삭제"""
    chats = load_chats()
    if chat_id in chats:
        del chats[chat_id]
        save_chats(chats)

        # 메시지 파일도 삭제
        chat_file = os.path.join(DATA_DIR, f"chat_{chat_id}.json")
        if os.path.exists(chat_file):
            os.remove(chat_file)

    return jsonify({"success": True})


@app.route("/api/chat", methods=["POST"])
def chat():
    """채팅 메시지 처리"""
    data = request.json
    message = data.get("message")
    chat_id = data.get("chat_id")

    if not message or not chat_id:
        return jsonify({"error": "Message and chat_id required"}), 400

    # 사용자 메시지 저장
    messages = load_chat_messages(chat_id)
    messages.append(
        {"content": message, "is_user": True, "timestamp": datetime.now().isoformat()}
    )

    # AI 응답 생성
    try:
        ai_response = get_ai_response(message, chat_id)

        # AI 서버 연결 실패나 오류 응답인 경우 시뮬레이션으로 대체
        error_indicators = (
            "AI 서버 오류",
            "응답 시간이 초과",
            "AI 서버에 연결할 수 없습니다",
            "오류가 발생했습니다",
        )
        if ai_response.startswith(error_indicators):
            print("AI 서버 오류로 인해 시뮬레이션 응답 사용")
            ai_response = simulate_ai_response(message)

    except Exception as e:
        print(f"AI 응답 생성 중 예외 발생: {e}")
        ai_response = simulate_ai_response(message)

    # AI 응답 저장
    messages.append(
        {
            "content": ai_response,
            "is_user": False,
            "timestamp": datetime.now().isoformat(),
        }
    )
    save_chat_messages(chat_id, messages)

    # 채팅 정보 업데이트
    chats = load_chats()
    if chat_id in chats:
        # 첫 번째 메시지면 제목을 사용자 메시지로 설정
        user_message_count = len([msg for msg in messages if msg["is_user"]])
        if user_message_count == 1:
            title = message[:30] + ("..." if len(message) > 30 else "")
            chats[chat_id]["title"] = title

        chats[chat_id]["updated_at"] = datetime.now().isoformat()
        save_chats(chats)

    return jsonify({"response": ai_response})


# ============================================================================
# 캐릭터 관련 API 라우트
# ============================================================================


@app.route("/api/characters", methods=["GET"])
def get_characters():
    """캐릭터 목록 조회"""
    try:
        response = requests.get(
            f"{EXTERNAL_API_BASE}/characters", timeout=AI_API_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            characters = data.get("characters", [])
            converted_characters = []

            for char in characters:
                char_id = char.get("number")
                profile = CHARACTER_PROFILES.get(char_id, {})
                converted_characters.append(
                    {
                        "id": char_id,
                        "name": char.get("name"),
                        "description": f"{char.get('description')}",
                        "image": profile.get("image", "/images/characters/default.png"),
                    }
                )

            return jsonify({"characters": converted_characters})
        else:
            return jsonify({"error": "Failed to fetch characters"}), 500

    except requests.exceptions.RequestException as e:
        print(f"캐릭터 목록 조회 실패: {e}")
        # 기본 캐릭터 목록 반환 (API 실패 시)
        default_characters = [
            {
                "id": 1,
                "name": "AI Assistant",
                "description": "일반적인 AI 어시스턴트",
                "image": "/images/characters/default.png",
            },
            {
                "id": 2,
                "name": "친근한 동반자",
                "description": "친근하고 따뜻한 대화 상대",
                "image": "/images/characters/default.png",
            },
            {
                "id": 3,
                "name": "전문 상담사",
                "description": "전문적인 조언을 제공하는 상담사",
                "image": "/images/characters/default.png",
            },
        ]
        return jsonify({"characters": default_characters})


@app.route("/api/select_character", methods=["POST"])
def select_character():
    """캐릭터 선택"""
    data = request.json
    character_number = data.get("character_number")

    if character_number is None:
        return jsonify({"error": "character_number required"}), 400

    try:
        payload = {"character_number": character_number}
        response = _make_api_request("select_character", payload)

        if response is None:
            return jsonify({"error": "캐릭터 선택 실패: 서버 연결 불가"}), 500

        if response.status_code == 200:
            try:
                result = response.json()
                return jsonify(
                    {
                        "selected_character": result.get("selected_character"),
                        "message": result.get("message", ""),
                    }
                )
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON response from AI server"}), 500
        else:
            print(f"캐릭터 선택 실패: {response.status_code} - {response.text}")
            return (
                jsonify(
                    {"error": f"Failed to select character: {response.status_code}"}
                ),
                500,
            )

    except Exception as e:
        print(f"캐릭터 선택 실패: {e}")
        return jsonify({"error": f"캐릭터 선택 실패: {str(e)}"}), 500


# ============================================================================
# 애플리케이션 실행
# ============================================================================

if __name__ == "__main__":
    print("🚀 Chat Server Starting...")
    print("📂 Chat data will be saved in:", os.path.abspath(DATA_DIR))
    print(f"🌐 Server running at: http://{HOST}:{PORT}")
    app.run(debug=DEBUG, host=HOST, port=PORT)

# ============================================================
# main.py - Slack 요약봇의 메인 실행 파일
# 역할: Slack에서 /요약 명령어를 받아 처리하는 진입점
# ============================================================

# .env 파일에서 환경변수(API 키, 토큰 등)를 불러옴
# 다른 모듈보다 먼저 실행해야 다른 파일에서도 환경변수 사용 가능
from dotenv import load_dotenv
load_dotenv()

# Slack 봇 프레임워크
from slack_bolt import App
import os
import logging
import traceback

# 직접 만든 모듈 가져오기
from slack_reader import collect_messages      # 채널 메시지 수집 함수
from summarize import summarize_messages       # AI 요약 함수

# 로깅 설정 - 서버에서 동작 상태를 확인하기 위한 로그 출력
logging.basicConfig(
    level=logging.INFO,                        # INFO 이상 레벨만 출력
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'  # 시간, 레벨, 메시지 형식
)
logger = logging.getLogger(__name__)

# .env에서 Slack 인증 정보 가져오기
bot_token = os.getenv("SLACK_BOT_TOKEN")             # 봇의 인증 토큰
signing_secret = os.getenv("SLACK_SIGNING_SECRET")   # 요청이 Slack에서 온 것인지 검증하는 키

# 환경변수가 비어있으면 경고 로그 출력
if not bot_token:
    logger.error("SLACK_BOT_TOKEN이 설정되지 않았습니다!")
if not signing_secret:
    logger.error("SLACK_SIGNING_SECRET이 설정되지 않았습니다!")

# Slack 앱 초기화 - 봇 토큰과 서명 비밀키로 인증
app = App(
    token=bot_token,
    signing_secret=signing_secret
)


# -----------------------------------------------
# /요약 슬래시 커맨드 핸들러
# Slack에서 사용자가 /요약 입력 시 이 함수가 실행됨
# -----------------------------------------------
@app.command("/요약")
def handle_summary_command(ack, say, command, client):
    # ack() = Slack에게 "명령어 잘 받았다"고 응답 (3초 내 필수)
    ack()

    # 명령어가 실행된 채널의 ID 가져오기
    channel_id = command['channel_id']
    logger.info(f"/요약 슬래시 커맨드 수신! 채널: {channel_id}")

    # 사용자에게 처리 중임을 알림
    say("요약중입니다... 잠시만 기다려주세요!")

    try:
        # 1단계: 채널에서 최근 8시간 메시지 수집
        messages = collect_messages(client, channel_id)
        logger.info(f"수집된 메시지 수: {len(messages)}")

        # 수집된 메시지가 없으면 안내
        if not messages:
            say("최근 8시간 동안의 메시지가 없습니다.")
            return

        # 2단계: 수집된 메시지를 AI(Gemini)로 요약
        summary = summarize_messages(messages)

        # 3단계: 요약 결과를 채널에 전송
        say(summary)
        logger.info("요약 완료!")
    except Exception as e:
        # 오류 발생 시 상세 로그 기록 + 사용자에게 에러 메시지 전달
        error_detail = traceback.format_exc()
        logger.error(f"요약 중 오류 발생: {error_detail}")
        say(f"요약 중 오류가 발생했습니다: {e}")


# -----------------------------------------------
# @봇이름 으로 멘션했을 때 안내 메시지 출력
# -----------------------------------------------
@app.event("app_mention")
def handle_app_mention(event, say):
    say("안녕하세요! /요약 이라고 입력하면 대화를 요약해드려요")


# -----------------------------------------------
# 일반 메시지 이벤트 핸들러 (무시 처리)
# 이 핸들러가 없으면 slack_bolt가 경고 로그를 출력하므로 빈 핸들러 등록
# -----------------------------------------------
@app.event("message")
def handle_message(event):
    pass


# -----------------------------------------------
# 봇 실행 (이 파일을 직접 실행할 때만 동작)
# -----------------------------------------------
if __name__ == "__main__":
    # Render가 PORT 환경변수를 자동 지정, 없으면 로컬 개발용 3000번 사용
    port = int(os.getenv("PORT", 3000))
    logger.info(f"Summary Bot 시작! (HTTP Mode - Port {port})")
    app.start(port=port)
from dotenv import load_dotenv
load_dotenv()

from slack_bolt import App
import os
import logging
import traceback

from slack_reader import collect_messages
from summarize import summarize_messages

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수 확인
bot_token = os.getenv("SLACK_BOT_TOKEN")
signing_secret = os.getenv("SLACK_SIGNING_SECRET")

if not bot_token:
    logger.error("SLACK_BOT_TOKEN이 설정되지 않았습니다!")
if not signing_secret:
    logger.error("SLACK_SIGNING_SECRET이 설정되지 않았습니다!")

app = App(
    token=bot_token,
    signing_secret=signing_secret
)


# /요약 슬래시 커맨드 처리
@app.command("/요약")
def handle_summary_command(ack, say, command, client):
    ack()
    channel_id = command['channel_id']
    logger.info(f"/요약 슬래시 커맨드 수신! 채널: {channel_id}")

    say("요약중입니다... 잠시만 기다려주세요!")

    try:
        messages = collect_messages(client, channel_id)
        logger.info(f"수집된 메시지 수: {len(messages)}")

        if not messages:
            say("최근 8시간 동안의 메시지가 없습니다.")
            return

        summary = summarize_messages(messages)
        say(summary)
        logger.info("요약 완료!")
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.error(f"요약 중 오류 발생: {error_detail}")
        say(f"요약 중 오류가 발생했습니다: {e}")


# 봇 멘션 시 안내
@app.event("app_mention")
def handle_app_mention(event, say):
    say("안녕하세요! /요약 이라고 입력하면 대화를 요약해드려요")


# 기타 메시지 이벤트 (무시 처리)
@app.event("message")
def handle_message(event):
    pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    logger.info(f"Summary Bot 시작! (HTTP Mode - Port {port})")
    app.start(port=port)
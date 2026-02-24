import time
import logging

logger = logging.getLogger(__name__)


def collect_messages(client, channel_id, hours=8):
    """지정된 채널에서 최근 N시간 동안의 메시지를 수집합니다."""
    oldest = str(time.time() - (hours * 3600))

    try:
        result = client.conversations_history(
            channel=channel_id,
            oldest=oldest,
            limit=100
        )
    except Exception as e:
        logger.error(f"conversations_history API 호출 실패: {e}")
        raise Exception(f"채널 메시지를 읽을 수 없습니다. 봇이 채널에 초대되었는지 확인하세요. 에러: {e}")

    if not result.get("ok"):
        error_msg = result.get("error", "알 수 없는 에러")
        logger.error(f"Slack API 에러: {error_msg}")
        raise Exception(f"Slack API 에러: {error_msg}")

    messages = []
    for msg in result.get("messages", []):
        # 봇 메시지와 /요약 명령어는 제외
        if msg.get("bot_id"):
            continue
        text = msg.get("text", "")
        if text and "/요약" not in text:
            messages.append(text)

    messages.reverse()  # 시간순 정렬 (오래된 것 → 최신)
    logger.info(f"채널 {channel_id}에서 {len(messages)}개 메시지 수집 완료")
    return messages
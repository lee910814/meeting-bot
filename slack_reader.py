import time
import logging

logger = logging.getLogger(__name__)


def collect_messages(client, channel_id, hours=8):
    """지정된 채널에서 최근 N시간 동안의 메시지를 수집합니다."""
    oldest = str(int(time.time() - (hours * 3600)))
    logger.info(f"메시지 수집 시작 - 채널: {channel_id}, oldest: {oldest}")

    try:
        result = client.conversations_history(
            channel=channel_id,
            oldest=oldest,
            limit=100
        )
    except Exception as e:
        logger.error(f"conversations_history API 호출 실패: {e}")
        raise Exception(f"채널 메시지를 읽을 수 없습니다. 봇이 채널에 초대되었는지 확인하세요. 에러: {e}")

    # API 응답 전체를 로그로 출력하여 디버깅
    logger.info(f"API 응답 타입: {type(result)}")
    logger.info(f"API 응답 data 타입: {type(result.data)}")
    logger.info(f"API 응답 ok: {result.data.get('ok')}")

    raw_messages = result.data.get("messages", [])
    logger.info(f"원본 메시지 수: {len(raw_messages)}")

    if not raw_messages:
        logger.warning("API가 빈 메시지 리스트를 반환했습니다!")
        logger.info(f"API 응답 전체: {result.data}")
        return []

    # 모든 메시지 로그 출력
    for i, msg in enumerate(raw_messages):
        logger.info(
            f"  [{i}] user={msg.get('user', 'N/A')}, "
            f"bot_id={msg.get('bot_id', 'None')}, "
            f"subtype={msg.get('subtype', 'None')}, "
            f"text={msg.get('text', '')[:80]}"
        )

    messages = []
    for msg in raw_messages:
        # 봇 메시지는 제외
        if msg.get("bot_id") or msg.get("subtype") == "bot_message":
            continue
        text = msg.get("text", "")
        if text:
            messages.append(text)

    messages.reverse()
    logger.info(f"필터링 후 최종 메시지 수: {len(messages)}")
    return messages
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

    # 응답 데이터 확인 로그
    logger.info(f"API 응답 ok: {result.get('ok')}")
    logger.info(f"API 응답 메시지 수: {len(result.get('messages', []))}")

    raw_messages = result.get("messages", [])

    # 필터링 없이 전체 메시지 로그
    for i, msg in enumerate(raw_messages):
        logger.info(f"  메시지 {i}: bot_id={msg.get('bot_id')}, text={msg.get('text', '')[:50]}")

    messages = []
    for msg in raw_messages:
        # 봇 메시지는 제외
        if msg.get("bot_id") or msg.get("subtype") == "bot_message":
            continue
        text = msg.get("text", "")
        if text:
            messages.append(text)

    messages.reverse()  # 시간순 정렬 (오래된 것 → 최신)
    logger.info(f"채널 {channel_id}에서 최종 {len(messages)}개 메시지 수집 완료")
    return messages
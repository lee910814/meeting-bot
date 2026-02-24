# ============================================================
# slack_reader.py - Slack 채널의 메시지를 수집하는 모듈
# 역할: 지정된 채널에서 최근 N시간 동안의 대화를 가져옴
# ============================================================

import time       # 현재 시간(Unix 타임스탬프)을 구하기 위한 모듈
import logging    # 로그 출력을 위한 모듈

logger = logging.getLogger(__name__)


def collect_messages(client, channel_id, hours=8):
    """
    지정된 채널에서 최근 N시간 동안의 메시지를 수집합니다.

    매개변수:
        client: Slack API를 호출할 수 있는 클라이언트 객체
        channel_id: 메시지를 읽을 채널의 고유 ID
        hours: 몇 시간 전까지의 메시지를 가져올지 (기본값: 8시간)

    반환값:
        시간순으로 정렬된 메시지 텍스트 리스트
    """

    # 현재 시간에서 hours만큼 뺀 시점을 계산
    # int()로 정수 변환 → 소수점이 있으면 Slack API에서 타임스탬프가 변형되는 버그 방지
    # 예: time.time() = 1771913346 → 8시간 전 = 1771884546
    oldest = str(int(time.time() - (hours * 3600)))
    logger.info(f"메시지 수집 시작 - 채널: {channel_id}, oldest: {oldest}")

    try:
        # Slack API 호출: 채널의 대화 기록 가져오기
        result = client.conversations_history(
            channel=channel_id,    # 읽을 채널
            oldest=oldest,         # 이 시점 이후의 메시지만 가져옴
            limit=100              # 최대 100개까지
        )
    except Exception as e:
        logger.error(f"conversations_history API 호출 실패: {e}")
        raise Exception(f"채널 메시지를 읽을 수 없습니다. 봇이 채널에 초대되었는지 확인하세요. 에러: {e}")

    # API 응답에서 메시지 리스트 꺼내기
    # result.data = API 응답의 원본 딕셔너리
    raw_messages = result.data.get("messages", [])
    logger.info(f"원본 메시지 수: {len(raw_messages)}")

    # 메시지가 없으면 빈 리스트 반환
    if not raw_messages:
        logger.warning("API가 빈 메시지 리스트를 반환했습니다!")
        logger.info(f"API 응답 전체: {result.data}")
        return []

    # 디버깅용: 수집된 메시지 내용 로그 출력
    for i, msg in enumerate(raw_messages):
        logger.info(
            f"  [{i}] user={msg.get('user', 'N/A')}, "
            f"bot_id={msg.get('bot_id', 'None')}, "
            f"subtype={msg.get('subtype', 'None')}, "
            f"text={msg.get('text', '')[:80]}"
        )

    # 봇 메시지를 제외하고 사람이 보낸 메시지만 수집
    messages = []
    for msg in raw_messages:
        # 봇이 보낸 메시지는 건너뛰기 (bot_id가 있거나 subtype이 bot_message)
        if msg.get("bot_id") or msg.get("subtype") == "bot_message":
            continue
        text = msg.get("text", "")
        if text:
            messages.append(text)

    # Slack API는 최신 메시지부터 반환하므로 뒤집어서 시간순 정렬
    messages.reverse()
    logger.info(f"필터링 후 최종 메시지 수: {len(messages)}")
    return messages
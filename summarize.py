from google import genai
import os
import logging

logger = logging.getLogger(__name__)


def summarize_messages(messages: list) -> str:
    """메시지 리스트를 받아 Gemini API로 요약합니다."""
    if not messages:
        return "📭 요약할 메시지가 없습니다."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY가 .env에 설정되지 않았습니다!")

    client = genai.Client(api_key=api_key)

    conversation = "\n".join(messages)
    logger.info(f"총 {len(messages)}개 메시지 요약 요청")

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"""당신은 회의 내용을 요약하는 전문가입니다. 한국어로 답변해주세요.

다음 슬랙 대화를 요약해주세요.

[대화 내용]
{conversation}

요약:
액션아이템:
"""
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API 호출 실패: {e}")
        raise Exception(f"AI 요약 실패: {e}")
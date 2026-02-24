# ============================================================
# summarize.py - AI를 이용한 메시지 요약 모듈
# 역할: 수집된 대화 내용을 Google Gemini AI에게 보내 요약을 받음
# ============================================================

from google import genai    # Google Gemini AI SDK
import os
import logging

logger = logging.getLogger(__name__)


def summarize_messages(messages: list) -> str:
    """
    메시지 리스트를 받아 Gemini API로 요약합니다.

    매개변수:
        messages: 요약할 메시지 텍스트 리스트 (예: ["안녕", "회의 시작합니다"])

    반환값:
        AI가 생성한 요약 텍스트 (문자열)
    """

    # 빈 리스트가 들어오면 안내 메시지 반환
    if not messages:
        return "요약할 메시지가 없습니다."

    # .env에서 Gemini API 키 가져오기
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY가 .env에 설정되지 않았습니다!")

    # Gemini AI 클라이언트 생성 (함수 내부에서 생성하여 환경변수 로드 보장)
    client = genai.Client(api_key=api_key)

    # 여러 개의 메시지를 줄바꿈으로 연결하여 하나의 텍스트로 만듦
    # 예: ["안녕", "회의 시작"] → "안녕\n회의 시작"
    conversation = "\n".join(messages)
    logger.info(f"총 {len(messages)}개 메시지 요약 요청")

    try:
        # Gemini AI에 요약 요청
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",   # 사용할 AI 모델 (무료 티어, 가볍고 빠름)
            contents=f"""당신은 회의 내용을 요약하는 전문가입니다. 한국어로 답변해주세요.

다음 슬랙 대화를 요약해주세요.

[대화 내용]
{conversation}

요약:
액션아이템:
"""
        )
        # AI 응답에서 텍스트만 추출하여 반환
        return response.text
    except Exception as e:
        logger.error(f"Gemini API 호출 실패: {e}")
        raise Exception(f"AI 요약 실패: {e}")
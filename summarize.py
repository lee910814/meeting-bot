import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def summarize_messages(messages: list) -> str:
    if not messages:
        return "메시지가 없습니다."
    
    #메세지를 하나의 텍스트로 합치기
    conversation = "\n".join(messages)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        system="당신은 회의 내용을 요약하는 전문가입니다.",
        messages=[
            {"role": "user",
             "content": f"""다음 슬랙 대화를 요약해주세요.
             
             [대화 내용]
             {conversation}
             
             요약:
             액션아이템:
             """}
        ]
    )
    return response.content[0].text

   
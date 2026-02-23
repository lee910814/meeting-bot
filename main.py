from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os

load_dotenv()

app = App(
    token=os.getenv("SLACK_BOT_TOKEN")
)


#/요약 명령어 감지
@app.message("/요약")
def say_hello(message, say, command):

    message() #슬랙에 받았다는 응답
    channel_id = command['channel_id']
    say("요약중입니다.")

    messages = collect_messages(channel_id) #메세지 수집
    summary = summarize_messages(messages) #메세지 요약
    say(summary) #요약 결과 출력

if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
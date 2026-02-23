def collect_messages(client,channel_id,hours=8):
    import time
    oldest = str(time.time() - (hours * 3600)) # 8시간 전

    result = client.conversations_history(
        channel=channel_id,
        oldest=oldest,
        limit=100   #최대 100개
    )

    messages = []
    for msg in result['messages']:
        if msg.get("text"): #텍스트 있는 것만 
            messages.append(msg["text"])
    return messages
    
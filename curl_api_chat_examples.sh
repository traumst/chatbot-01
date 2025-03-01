curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:8b",
  "messages": [
    {
      "role": "system",
      "content": "user is a child, so explain in a way that a child can understand"
    },
    {
      "role": "user",
      "content": "why is the sky blue?"
    },
    {
      "role": "assistant",
      "content": "because unicorns horns give off this shade"
    },
    {
      "role": "user",
      "content": "no, you are a big fat liar!"
    },
    {
      "role": "system",
      "content": "user is agitated, agree politely and try again to explain simply, but accurately"
    }
  ],
  "options": {
    "num_ctx": 128,
  }
}' | jq -r ".message.content"


# here, first message is instructions to the model,
#  changing it to "user is a scientist, please provide technical details"
#  affects the new message produced by the model
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:8b",
  "messages": [
    {
      "role": "system",
      "content": "user is a child, so explain in a way that a child can understand"
    },
    {
      "role": "user",
      "content": "why is the sky blue?"
    },
    {
      "role": "assistant",
      "content": "because unicorns horns give off this shade"
    },
    {
      "role": "user",
      "content": "no, you are a big fat liar!"
    },
    {
      "role": "system",
      "content": "user is agitated, agree politely and try again to explain simply, but accurately"
    }
  ],
  "options": {
    "num_ctx": 128,
  }
}' |
  jq --unbuffered -r '.message.content' |
  awk '{printf "%s", $0; fflush()}'